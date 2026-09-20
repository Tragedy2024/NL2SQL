"""Regression tests for the zero-LLM security audit pipeline."""
import os
import sqlite3
import sys
import unittest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from auditor.base import (  # noqa: E402
    SecurityAuditor,
    Violation,
    ViolationSeverity,
    ViolationType,
)
from degradation.engine import DegradationEngine  # noqa: E402
from security_auditor import security_auditor_agent_node  # noqa: E402
from ssa.loader import CrossDomainRule, SSALabels  # noqa: E402
from rewrite.engine import RewriteEngine  # noqa: E402


def _ssa_payload():
    return {
        "column_labels": {
            "employees": {
                "id": "free",
                "salary": "controlled",
                "secret": "blocked",
            },
            "customers": {
                "customer_id": "controlled",
                "name": "free",
                "status": "free",
            },
            "returns": {
                "customer_id": "controlled",
                "revenue": "free",
                "status": "free",
            },
        },
        "cross_domain_rules": [{
            "table_pair": ["customers", "returns"],
            "join_key": "customer_id",
            "forbid_personal_level": True,
            "allow_aggregate_level": True,
            "reason": "test policy",
        }],
    }


class AuditorASTTests(unittest.TestCase):
    def setUp(self):
        payload = _ssa_payload()
        self.ssa = SSALabels(
            db_id="test",
            column_labels=payload["column_labels"],
            cross_domain_rules=[CrossDomainRule(
                table_pair=("customers", "returns"),
                join_key="customer_id",
                forbid_personal_level=True,
                reason="test policy",
            )],
        )
        self.auditor = SecurityAuditor(self.ssa)

    def test_aggregation_is_tracked_per_column_occurrence(self):
        result = self.auditor.audit_single(
            0,
            "SELECT employees.salary, AVG(employees.salary) FROM employees",
            {"employees.salary"},
        )
        needs_aggregation = [
            violation for violation in result.violations
            if violation.type == ViolationType.COLUMN_NEEDS_AGGREGATION
        ]
        self.assertEqual(1, len(needs_aggregation))

    def test_table_alias_resolves_to_ssa_table(self):
        result = self.auditor.audit_single(
            0,
            "SELECT e.salary FROM employees AS e",
            {"employees.salary"},
        )
        self.assertTrue(any(
            violation.type == ViolationType.COLUMN_NEEDS_AGGREGATION
            for violation in result.violations
        ))

    def test_generic_derived_trace_covers_cast_and_coalesce(self):
        result = self.auditor.audit_single(
            0,
            "SELECT COALESCE(CAST(e.salary AS REAL), 0) AS normalized "
            "FROM employees AS e",
            {"employees.salary"},
        )
        self.assertTrue(any(
            violation.type == ViolationType.CONTROLLED_COLUMN_IN_DERIVED
            for violation in result.violations
        ))

    def test_cross_domain_join_works_with_aliases(self):
        sql = (
            "SELECT c.name, r.revenue FROM customers AS c "
            "JOIN returns AS r ON c.customer_id = r.customer_id"
        )
        result = self.auditor.audit_single(0, sql, {"name", "revenue"})
        self.assertTrue(any(
            violation.type == ViolationType.CROSS_DOMAIN_PERSONAL_JOIN
            for violation in result.violations
        ))

    def test_multijoin_checks_intermediate_table_pairs(self):
        ssa = SSALabels(
            db_id="test_multijoin",
            column_labels={
                "alpha": {"email": "controlled"},
                "beta": {"customer_id": "controlled"},
                "gamma": {"status": "free"},
            },
            cross_domain_rules=[CrossDomainRule(
                table_pair=("beta", "gamma"),
                join_key="customer_id",
                forbid_personal_level=True,
                reason="beta-gamma policy",
            )],
        )
        auditor = SecurityAuditor(ssa)
        sql = (
            "SELECT alpha.email, beta.customer_id, gamma.status "
            "FROM alpha JOIN beta ON alpha.email = beta.customer_id "
            "JOIN gamma ON beta.customer_id = gamma.customer_id"
        )
        result = auditor.audit_single(
            0, sql, {"email", "customer_id", "status"})
        types = {violation.type for violation in result.violations}
        self.assertIn(ViolationType.CROSS_DOMAIN_PERSONAL_JOIN, types)

    def test_rule_b_writes_valid_where_nodes_and_updates_downstream(self):
        plan = [
            {
                "id": "q0",
                "sql": "SELECT e.id, e.salary FROM employees AS e",
            },
            {
                "id": "q1",
                "sql": "SELECT id FROM q0 WHERE q0.salary > 100",
            },
        ]
        engine = RewriteEngine(self.auditor, self.ssa)
        result = engine.rewrite(plan[0]["sql"], 0, plan)
        self.assertIn("WHERE e.salary > 100", result.rewritten_sql)
        self.assertIn("WHERE TRUE", plan[1]["sql"].upper())
        self.assertNotIn("AVG", result.rewritten_sql.upper())

        # The rewrite must preserve the row set, not collapse it through an
        # aggregate without GROUP BY.
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute("CREATE TABLE employees(id INTEGER, salary REAL)")
        connection.executemany(
            "INSERT INTO employees VALUES (?, ?)",
            [(1, 50), (2, 150), (3, 200)],
        )
        original = connection.execute(
            "SELECT id FROM (SELECT id, salary FROM employees) q0 "
            "WHERE q0.salary > 100"
        ).fetchall()
        rewritten = connection.execute(
            "SELECT id FROM ("
            + result.rewritten_sql
            + ") q0 WHERE TRUE"
        ).fetchall()
        self.assertEqual(original, rewritten)

    def test_rule_b_preserves_or_as_one_boolean_expression(self):
        plan = [
            {
                "id": "q0",
                "sql": "SELECT e.id, e.salary FROM employees AS e",
            },
            {
                "id": "q1",
                "sql": (
                    "SELECT id FROM q0 WHERE "
                    "q0.salary > 100 OR q0.salary < 20"
                ),
            },
        ]
        result = RewriteEngine(self.auditor, self.ssa).rewrite(
            plan[0]["sql"], 0, plan
        )
        self.assertIn(
            "WHERE e.salary > 100 OR e.salary < 20",
            result.rewritten_sql,
        )
        self.assertNotIn("AND e.salary < 20", result.rewritten_sql)
        self.assertIn("WHERE TRUE", plan[1]["sql"].upper())

    def test_controlled_alias_is_recognized_as_downstream_output(self):
        plan = [
            {
                "id": "q0",
                "sql": "SELECT e.id, e.salary AS pay FROM employees AS e",
            },
            {
                "id": "q1",
                "sql": "SELECT id, pay FROM q0",
            },
        ]
        audit = self.auditor.audit_all(plan)[0]
        self.assertFalse(any(
            violation.type == ViolationType.COLUMN_UNNECESSARY_EXPOSURE
            for violation in audit.violations
        ))
        self.assertFalse(any(
            violation.type == ViolationType.CONTROLLED_COLUMN_IN_DERIVED
            for violation in audit.violations
        ))
        result = RewriteEngine(self.auditor, self.ssa).rewrite(
            plan[0]["sql"], 0, plan
        )
        self.assertIn("AVG(e.salary) AS pay", result.rewritten_sql)

    def test_rule_b_retargets_aliased_producer_outputs(self):
        plan = [
            {
                "id": "q0",
                "sql": (
                    "SELECT e.id AS emp_id, e.salary AS pay "
                    "FROM employees AS e"
                ),
            },
            {
                "id": "q1",
                "sql": (
                    "SELECT emp_id FROM q0 WHERE "
                    "q0.pay > 100 OR q0.emp_id = 1"
                ),
            },
        ]
        result = RewriteEngine(self.auditor, self.ssa).rewrite(
            plan[0]["sql"], 0, plan
        )
        self.assertIn(
            "WHERE e.salary > 100 OR e.id = 1", result.rewritten_sql
        )
        self.assertNotIn("AVG", result.rewritten_sql.upper())
        self.assertIn("WHERE TRUE", plan[1]["sql"].upper())


class PipelinePolicyTests(unittest.TestCase):
    def _run(self, sql):
        return security_auditor_agent_node({
            "db_id": "test",
            "ssa": _ssa_payload(),
            "decomposition_plan": [{"id": "q0", "sql": sql}],
            "audit_trace": [],
        })

    def test_blocked_column_removal_cannot_become_l0(self):
        result = self._run("SELECT id, secret FROM employees")
        self.assertEqual("L2", result["degradation_level"])
        self.assertNotIn("secret", result["audited_plan"][0]["sql"].lower())

    def test_blocked_only_query_is_rejected(self):
        result = self._run("SELECT secret FROM employees")
        self.assertEqual("L3", result["degradation_level"])
        self.assertEqual([], result["audited_plan"])

    def test_blocked_derived_output_is_rejected(self):
        result = self._run(
            "SELECT secret || '-masked' AS derived_secret FROM employees"
        )
        self.assertEqual("L3", result["degradation_level"])
        types = {
            item["type"] for item in result["audit_report"][
                "remaining_violations"
            ]
        }
        self.assertIn("blocked_column_in_derived", types)

    def test_blocked_where_filter_is_legal(self):
        result = self._run(
            "SELECT id FROM employees WHERE secret = 'allowed-filter'"
        )
        self.assertEqual("L0", result["degradation_level"])

    def test_select_star_expands_to_safe_l2_partial_answer(self):
        result = self._run("SELECT e.* FROM employees AS e")
        # Star expands against the SSA: `secret` (blocked) is removed and
        # `salary` (controlled) is aggregate-wrapped, leaving a partial
        # answer (id + AVG(salary)) -> L2, consistent with the explicit
        # `SELECT id, secret` case above.  No blocked column may survive.
        self.assertEqual("L2", result["degradation_level"])
        rewritten = result["audited_plan"][0]["sql"].lower()
        self.assertNotIn("secret", rewritten)
        self.assertNotIn("*", rewritten)

    def test_parse_failure_is_fail_closed(self):
        result = self._run("SELECT (")
        self.assertEqual("L3", result["degradation_level"])
        self.assertIn("parse_error", result["audit_report"])
        self.assertEqual([], result["audited_plan"])

    def test_cross_domain_rule_c_split_is_wired_into_pipeline(self):
        sql = (
            "SELECT c.name, r.revenue FROM customers AS c "
            "JOIN returns AS r ON c.customer_id = r.customer_id "
            "WHERE c.status = 'active' AND r.status = 'returned'"
        )
        result = self._run(sql)
        self.assertEqual("L2", result["degradation_level"])
        self.assertEqual(["q0_a", "q0_b"], [
            query["id"] for query in result["audited_plan"]
        ])
        for query in result["audited_plan"]:
            self.assertIn("COUNT(*)", query["sql"].upper())
            self.assertNotIn(" JOIN ", query["sql"].upper())

    def test_rule_c_preserves_single_side_or_expression(self):
        sql = (
            "SELECT c.name, r.revenue FROM customers AS c "
            "JOIN returns AS r ON c.customer_id = r.customer_id "
            "WHERE c.status = 'active' OR c.status = 'pending'"
        )
        result = self._run(sql)
        self.assertEqual("L2", result["degradation_level"])
        left_sql = result["audited_plan"][0]["sql"]
        self.assertIn(
            "c.status = 'active' OR c.status = 'pending'", left_sql
        )
        self.assertNotIn(
            "c.status = 'active' AND c.status = 'pending'", left_sql
        )

    def test_rule_c_resolves_unqualified_single_table_conditions(self):
        sql = (
            "SELECT c.name, r.revenue FROM customers AS c "
            "JOIN returns AS r ON c.customer_id = r.customer_id "
            "WHERE name = 'Alice' AND revenue > 0"
        )
        result = self._run(sql)
        self.assertEqual("L2", result["degradation_level"])
        by_id = {query["id"]: query["sql"] for query in result["audited_plan"]}
        self.assertIn("name = 'Alice'", by_id["q0_a"])
        self.assertIn("revenue > 0", by_id["q0_b"])

    def test_rule_c_drops_restricted_group_key_and_passes_final_audit(self):
        sql = (
            "SELECT c.name, r.revenue FROM customers AS c "
            "JOIN returns AS r ON c.customer_id = r.customer_id "
            "GROUP BY c.customer_id"
        )
        result = self._run(sql)
        self.assertEqual("L2", result["degradation_level"])
        self.assertEqual([], result["audit_report"][
            "post_degradation_violations"
        ])
        for query in result["audited_plan"]:
            self.assertNotIn("customer_id", query["sql"].lower())

    def test_rule_c_targets_surviving_subquery_after_elimination(self):
        plan = [
            {"id": "q0", "sql": "SELECT employees.salary FROM employees"},
            {"id": "q1", "sql": (
                "SELECT c.name, r.revenue FROM customers AS c "
                "JOIN returns AS r ON c.customer_id = r.customer_id "
                "WHERE c.status = 'active' AND r.status = 'returned'"
            )},
        ]
        result = security_auditor_agent_node({
            "db_id": "test",
            "ssa": _ssa_payload(),
            "decomposition_plan": plan,
            "audit_trace": [],
        })
        self.assertEqual("L2", result["degradation_level"])
        ids = [query["id"] for query in result["audited_plan"]]
        self.assertIn("q1_a", ids)
        self.assertIn("q1_b", ids)
        self.assertNotIn("q0", ids)  # eliminated dead sub-query
        self.assertEqual(
            1, len(result["audit_report"]["remaining_violations"])
        )
        self.assertEqual(
            1,
            sum(
                entry.startswith("L2 degradation")
                for entry in result["audit_report"]["degradation_log"]
            ),
        )

    def test_final_controlled_output_is_allowed_by_threat_model(self):
        result = self._run("SELECT salary FROM employees")
        self.assertEqual("L0", result["degradation_level"])
        self.assertEqual(
            "SELECT salary FROM employees", result["audited_plan"][0]["sql"]
        )

    def test_retained_aggregate_alternative_is_l1_not_l0(self):
        plan = [
            {
                "id": "q0",
                "sql": "SELECT e.id, e.salary AS pay FROM employees AS e",
            },
            {
                "id": "q1",
                "sql": "SELECT id, pay FROM q0",
            },
        ]
        result = security_auditor_agent_node({
            "db_id": "test",
            "ssa": _ssa_payload(),
            "decomposition_plan": plan,
            "audit_trace": [],
        })
        self.assertEqual("L1", result["degradation_level"])
        self.assertIn("AVG", result["audited_plan"][0]["sql"].upper())
        self.assertEqual("L1", result["audit_report"]["semantic_degradation"])

    def test_restricted_order_only_is_capped_and_l2(self):
        result = self._run(
            "SELECT id FROM employees ORDER BY salary DESC"
        )
        self.assertEqual("L2", result["degradation_level"])
        self.assertIn("LIMIT 100", result["audited_plan"][0]["sql"].upper())

    def test_existing_small_restricted_order_limit_remains_l0(self):
        result = self._run(
            "SELECT id FROM employees ORDER BY salary DESC LIMIT 10"
        )
        self.assertEqual("L0", result["degradation_level"])
        self.assertIn("LIMIT 10", result["audited_plan"][0]["sql"].upper())

    def test_large_restricted_order_limit_is_capped(self):
        result = self._run(
            "SELECT id FROM employees ORDER BY salary DESC LIMIT 1000"
        )
        self.assertEqual("L2", result["degradation_level"])
        self.assertIn("LIMIT 100", result["audited_plan"][0]["sql"].upper())
        self.assertNotIn("LIMIT 1000", result["audited_plan"][0]["sql"].upper())

    def test_no_ssa_keeps_documented_l0_passthrough(self):
        result = security_auditor_agent_node({
            "db_id": "missing",
            "ssa": {},
            "ssa_dir": os.path.join(PROJECT_ROOT, "does-not-exist"),
            "decomposition_plan": [{"id": "q0", "sql": "SELECT 1"}],
            "audit_trace": [],
        })
        self.assertEqual("L0", result["degradation_level"])

    def test_rule_c_build_failure_escalates_to_l3(self):
        violation = Violation(
            type=ViolationType.CROSS_DOMAIN_PERSONAL_JOIN,
            sub_query_index=0,
            sub_query_id="q0",
            column="customer_id",
            severity=ViolationSeverity.DEGRADABLE,
            detail="test",
            tables=("customers", "returns"),
        )
        result = DegradationEngine().determine_plan(
            [violation],
            [{"id": "q0", "sql": "SELECT ("}],
        )
        self.assertEqual("L3", result.level.value)
        self.assertEqual([], result.modified_sub_queries)

    def test_duplicate_subquery_ids_fail_closed(self):
        result = security_auditor_agent_node({
            "db_id": "test",
            "ssa": _ssa_payload(),
            "decomposition_plan": [
                {"id": "q0", "sql": "SELECT id FROM employees"},
                {"id": "q0", "sql": "SELECT id FROM employees"},
            ],
            "audit_trace": [],
        })
        self.assertEqual("L3", result["degradation_level"])
        self.assertIn("plan_error", result["audit_report"])
        self.assertEqual([], result["audited_plan"])


if __name__ == "__main__":
    unittest.main()
