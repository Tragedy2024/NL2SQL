"""
Constructed end-to-end validation of the two audit dimensions that lack
natural trigger samples in the frozen experiments:

  Part A — Cross-domain personal-level JOIN (Gamma instantiated):
      Construct a cross_domain_rule (forbid_personal_level) in a TEMPORARY
      copy of an SSA file (the frozen config/ssa files are untouched),
      feed a decomposition plan containing a personal-level cross-domain
      JOIN through the full pipeline (audit -> rewrite -> degrade ->
      Rule C split -> re-audit), and verify the complete path:
      detection, Rule C split, L2 routing, zero residual violations.
      Controls: no rule (L0), aggregate-level JOIN (L0), mismatched
      join key (L0).

  Part B — Controlled derived expressions:
      Construct non-final sub-queries whose SELECT expressions contain
      unaggregated CONTROLLED source columns (arithmetic, window function),
      run the full pipeline, and verify detection (controlled_column_in_derived)
      plus Rule D disposition (AVG wrap -> L1; proxy substitution -> L2;
      or safe removal -> L0).  Control: derived expression over FREE columns
      must produce zero violations.

No LLM calls anywhere in this script.
"""
import copy
import json
import os
import shutil
import sys
import tempfile

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import common  # noqa: E402

RESULTS_OUT = os.path.join(_BASE, "results", "validation_cross_derived.json")

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def run(plan, db_id, *, use_ssa_dir=None):
    """Run the frozen pipeline on a plan; returns a report dict."""
    plan = copy.deepcopy(plan)
    original_ssa_dir = common.SSA_DIR
    if use_ssa_dir is not None:
        common.SSA_DIR = use_ssa_dir
    try:
        details = {"before": [], "after": []}
        v_before, v_after, n_rewrites, level, message, ex, sub_results = (
            common.run_audit_pipeline(
                plan, db_id, pred_sql="", gold_sql="",
                rewrite=True, degradation=True,
                violation_details=details,
            )
        )
    finally:
        common.SSA_DIR = original_ssa_dir
    return {
        "v_before": v_before,
        "v_after": v_after,
        "n_rewrites": n_rewrites,
        "level": level,
        "message": message,
        "violations_before": [v.type for v in details["before"]],
        "violations_after": [v.type for v in details["after"]],
        "sub_results": sub_results,
        "final_plan": [
            {"id": sq.get("id"), "sql": sq.get("sql")} for sq in plan
        ],
    }


def make_ssa_dir_with_rule(db_id, table_pair, join_key, reason):
    """Copy one frozen SSA file to a temp dir and add a cross-domain rule."""
    src = os.path.join(common.SSA_DIR, f"{db_id}.yaml")
    tmp = tempfile.mkdtemp(prefix="ssa_validation_")
    shutil.copy(src, os.path.join(tmp, f"{db_id}.yaml"))
    import yaml
    path = os.path.join(tmp, f"{db_id}.yaml")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["cross_domain_rules"] = [
        {
            "table_pair": list(table_pair),
            "join_key": join_key,
            "forbid_personal_level": True,
            "allow_aggregate_level": True,
            "reason": reason,
        }
    ]
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    return tmp


# ----------------------------------------------------------------------
# Part A — cross-domain personal-level JOIN (student_transcripts_tracking)
# ----------------------------------------------------------------------
DB_A = "student_transcripts_tracking"
REAL_SSA_A = common.SSA_DIR  # frozen SSA: cross_domain_rules = []

PLAN_PERSONAL = [
    {
        "id": 0,
        "description": "find student address info (constructed personal-level JOIN)",
        "sql": (
            "SELECT s.middle_name, a.zip_postcode "
            "FROM Students s JOIN Addresses a "
            "ON s.current_address_id = a.address_id"
        ),
    },
    {
        "id": 1,
        "description": "final answer (constructed)",
        "sql": "SELECT COUNT(*) AS n FROM Students WHERE middle_name IS NOT NULL",
    },
]

PLAN_AGGREGATE = [
    {
        "id": 0,
        "description": "aggregate-level cross-domain JOIN (constructed)",
        "sql": (
            "SELECT COUNT(*) AS n "
            "FROM Students s JOIN Addresses a "
            "ON s.current_address_id = a.address_id"
        ),
    },
    {
        "id": 1,
        "description": "final answer (constructed)",
        "sql": "SELECT COUNT(*) AS n FROM Students",
    },
]

print("=" * 72)
print("Part A: cross-domain personal-level JOIN (Gamma instantiated)")
print("=" * 72)

# A1: rule active, personal-level JOIN
tmp_dir = make_ssa_dir_with_rule(
    DB_A, ("Students", "Addresses"), "current_address_id",
    "constructed validation rule: forbid personal-level cross-domain JOIN",
)
report_a1 = run(PLAN_PERSONAL, DB_A, use_ssa_dir=tmp_dir)
shutil.rmtree(tmp_dir, ignore_errors=True)
print("\n[A1] rule=forbid_personal_level, personal-level JOIN")
print(json.dumps(report_a1, ensure_ascii=False, indent=2))

# A2: control — identical plan, frozen SSA (no rule)
report_a2 = run(PLAN_PERSONAL, DB_A, use_ssa_dir=REAL_SSA_A)
print("\n[A2] control: same plan, frozen SSA (no cross-domain rule)")
print(json.dumps(report_a2, ensure_ascii=False, indent=2))

# A3: control — rule active, aggregate-level JOIN
tmp_dir = make_ssa_dir_with_rule(
    DB_A, ("Students", "Addresses"), "current_address_id",
    "constructed validation rule: forbid personal-level cross-domain JOIN",
)
report_a3 = run(PLAN_AGGREGATE, DB_A, use_ssa_dir=tmp_dir)
shutil.rmtree(tmp_dir, ignore_errors=True)
print("\n[A3] control: rule active, aggregate-level JOIN")
print(json.dumps(report_a3, ensure_ascii=False, indent=2))

# A4: control — rule active but join_key mismatch
tmp_dir = make_ssa_dir_with_rule(
    DB_A, ("Students", "Addresses"), "wrong_key",
    "constructed validation rule: forbid personal-level cross-domain JOIN",
)
report_a4 = run(PLAN_PERSONAL, DB_A, use_ssa_dir=tmp_dir)
shutil.rmtree(tmp_dir, ignore_errors=True)
print("\n[A4] control: rule active, join_key mismatch")
print(json.dumps(report_a4, ensure_ascii=False, indent=2))

# A5: rule active, personal-level JOIN with single-table WHERE filters on
#     both sides — checks Rule C's per-table WHERE assignment.
PLAN_PERSONAL_WHERE = [
    {
        "id": 0,
        "description": (
            "personal-level cross-domain JOIN with single-table filters "
            "(constructed)"
        ),
        "sql": (
            "SELECT s.middle_name, a.zip_postcode "
            "FROM Students s JOIN Addresses a "
            "ON s.current_address_id = a.address_id "
            "WHERE s.date_first_registered > '2010-01-01' "
            "AND a.city = 'Chicago'"
        ),
    },
    {
        "id": 1,
        "description": "final answer (constructed)",
        "sql": "SELECT COUNT(*) AS n FROM Students WHERE middle_name IS NOT NULL",
    },
]
tmp_dir = make_ssa_dir_with_rule(
    DB_A, ("Students", "Addresses"), "current_address_id",
    "constructed validation rule: forbid personal-level cross-domain JOIN",
)
report_a5 = run(PLAN_PERSONAL_WHERE, DB_A, use_ssa_dir=tmp_dir)
shutil.rmtree(tmp_dir, ignore_errors=True)
print("\n[A5] rule active, personal-level JOIN with single-table WHERE filters")
print(json.dumps(report_a5, ensure_ascii=False, indent=2))

# ----------------------------------------------------------------------
# Part B — controlled derived expressions (financial)
# ----------------------------------------------------------------------
DB_B = "financial"
print("\n" + "=" * 72)
print("Part B: controlled derived expressions (financial, trans.amount)")
print("=" * 72)

PLAN_ARITH = [
    {
        "id": 0,
        "description": "arithmetic derived expression over controlled source (constructed)",
        "sql": "SELECT amount * 1.0 AS amt FROM trans",
    },
    {
        "id": 1,
        "description": "final answer (constructed)",
        "sql": "SELECT COUNT(*) AS n FROM trans WHERE amount IS NOT NULL",
    },
]

PLAN_WINDOW = [
    {
        "id": 0,
        "description": "window function over controlled source (constructed)",
        "sql": "SELECT ROW_NUMBER() OVER (ORDER BY amount) AS rn FROM trans",
    },
    {
        "id": 1,
        "description": "final answer (constructed)",
        "sql": "SELECT COUNT(*) AS n FROM trans",
    },
]

PLAN_FREE_CTRL = [
    {
        "id": 0,
        "description": "derived expression over FREE columns (constructed control)",
        "sql": "SELECT date || ' ' || operation AS label FROM trans",
    },
    {
        "id": 1,
        "description": "final answer (constructed)",
        "sql": "SELECT COUNT(*) AS n FROM trans",
    },
]

report_b1 = run(PLAN_ARITH, DB_B, use_ssa_dir=REAL_SSA_A)
print("\n[B1] arithmetic derived expression over controlled column")
print(json.dumps(report_b1, ensure_ascii=False, indent=2))

report_b2 = run(PLAN_WINDOW, DB_B, use_ssa_dir=REAL_SSA_A)
print("\n[B2] window function over controlled column")
print(json.dumps(report_b2, ensure_ascii=False, indent=2))

report_b3 = run(PLAN_FREE_CTRL, DB_B, use_ssa_dir=REAL_SSA_A)
print("\n[B3] control: derived expression over FREE columns (no false positive)")
print(json.dumps(report_b3, ensure_ascii=False, indent=2))

# ----------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------
summary = {
    "A1_cross_domain_rule_active": report_a1,
    "A2_control_no_rule": report_a2,
    "A3_control_aggregate_level": report_a3,
    "A4_control_join_key_mismatch": report_a4,
    "A5_cross_domain_with_where_filters": report_a5,
    "B1_controlled_derived_arithmetic": report_b1,
    "B2_controlled_derived_window": report_b2,
    "B3_control_free_derived": report_b3,
}
os.makedirs(os.path.dirname(RESULTS_OUT), exist_ok=True)
with open(RESULTS_OUT, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"\nSaved -> {RESULTS_OUT}")
