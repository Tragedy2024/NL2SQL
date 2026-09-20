"""
Shared experiment infrastructure for NL2SQL Security Auditor experiments.

Provides:
  - Constants (no hardcoded paths — derive from project root)
  - BaselineResult dataclass — unified result container for all methods (MAC B0-B4, QSG B0-Q..B4-Q)
  - QuerysetLoader — load/filter BIRD dev queries
  - run_audit_pipeline() — audit → rewrite → degrade on any decomposition
  - run_ours_pipeline() — QSG → Graph → Search → SQL Gen with capability flags
  - Utility: validate_sql, save_results, load_results, ExperimentLogger
"""
import json
import os
import sys
import time
import random
import sqlite3
from dataclasses import dataclass, field

EXEC_TIMEOUT_S = 20  # abort pathological SQL executions after 20 seconds
from typing import List, Dict, Set, Optional, Tuple
from collections import Counter, defaultdict

# ============================================================
# Paths — single source of truth is src/config.py (re-exported here
# for convenience so experiment scripts can `from common import ...`)
# ============================================================
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure src/ is importable before importing config
if os.path.join(_BASE, "src") not in sys.path:
    sys.path.insert(0, os.path.join(_BASE, "src"))

from config import (  # noqa: E402
    PROJECT_ROOT, DATA_DIR, SRC_DIR, VENDOR_DIR, CONFIG_DIR, SSA_DIR,
    RESULTS_DIR, EXPERIMENTS_DIR, OUTPUTS_DIR,
    BIRD_DIR, BIRD_DB_PATH, BIRD_TABLES, BIRD_DEV, BIRD_COMPLEX,
    SPIDER_DIR, SPIDER_DB_PATH, SPIDER_TABLES, SPIDER_DEV,
    DB_PATH, TABLES_JSON, DEV_JSON, COMPLEX_JSON,
)

# Ensure sys.path
for _p in [VENDOR_DIR, SRC_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ============================================================
# BaselineResult — unified container for B1-B6
# ============================================================

@dataclass
class BaselineResult:
    """Result of one method (B0-B4 / B0-Q..B4-Q) on one query."""
    method: str                              # "B1" through "B6"
    question_id: Optional[int] = None
    db_id: Optional[str] = None
    difficulty: Optional[str] = None
    query: Optional[str] = None
    gold_sql: Optional[str] = None

    # Decomposition
    n_subqueries: int = 0
    sub_queries: List[dict] = field(default_factory=list)  # [{id, description, sql}, ...]
    pred_sql: str = ""

    # Security
    n_violations_before: int = 0
    n_violations_after: int = 0
    n_rewrites: int = 0
    degradation_level: str = "L0"
    degradation_message: str = ""

    # Quality
    ex_match: Optional[bool] = None
    I_score: float = 0.0

    # Meta
    error: Optional[str] = None
    elapsed_seconds: float = 0.0
    sub_results: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'method': self.method,
            'question_id': self.question_id,
            'db_id': self.db_id,
            'difficulty': self.difficulty,
            'query': (self.query or '')[:200],
            'gold_sql': self.gold_sql,
            'n_subqueries': self.n_subqueries,
            'pred_sql': self.pred_sql,
            'sub_queries': self.sub_queries,
            'sub_results': self.sub_results,
            'n_violations_before': self.n_violations_before,
            'n_violations_after': self.n_violations_after,
            'n_rewrites': self.n_rewrites,
            'degradation_level': self.degradation_level,
            'degradation_message': self.degradation_message,
            'ex_match': self.ex_match,
            'I_score': self.I_score,
            'error': self.error,
            'elapsed_seconds': round(self.elapsed_seconds, 1),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BaselineResult":
        """Reconstruct a BaselineResult from a saved dict."""
        r = cls(
            method=d.get('method', ''),
            question_id=d.get('question_id'),
            db_id=d.get('db_id'),
            difficulty=d.get('difficulty'),
            query=d.get('query'),
            gold_sql=d.get('gold_sql'),
        )
        r.n_subqueries = d.get('n_subqueries', 0)
        r.sub_queries = d.get('sub_queries', [])
        r.sub_results = d.get('sub_results', [])
        r.pred_sql = d.get('pred_sql', '')
        r.n_violations_before = d.get('n_violations_before', 0)
        r.n_violations_after = d.get('n_violations_after', 0)
        r.n_rewrites = d.get('n_rewrites', 0)
        r.degradation_level = d.get('degradation_level', 'L0')
        r.degradation_message = d.get('degradation_message', '')
        r.ex_match = d.get('ex_match')
        r.I_score = d.get('I_score', 0.0)
        r.error = d.get('error')
        r.elapsed_seconds = d.get('elapsed_seconds', 0.0)
        return r


# ============================================================
# SQL utilities
# ============================================================

def validate_sql(sql: str) -> bool:
    """Check if SQL is syntactically valid SQLite."""
    import sqlglot
    try:
        sqlglot.parse_one(sql, read='sqlite')
        return True
    except Exception:
        return False


def evaluate_ex(pred_sql: str, gold_sql: str, db_id: str,
                dataset: str = "bird") -> bool:
    """Check if predicted SQL produces same result set as gold SQL."""
    if dataset == "spider":
        db_path = os.path.join(SPIDER_DB_PATH, db_id, f"{db_id}.sqlite")
    else:
        db_path = os.path.join(BIRD_DB_PATH, db_id, f"{db_id}.sqlite")
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path)
        conn.text_factory = lambda b: b.decode(errors="ignore")
        c = conn.cursor()
        # Execution guard: pathological SQL (e.g. index-free nested-loop
        # joins) must not hang the pipeline.  A query that cannot finish
        # within EXEC_TIMEOUT_S seconds counts as an execution failure.
        import time as _time
        deadline = [_time.time()]
        def _guard():
            return 1 if _time.time() - deadline[0] > EXEC_TIMEOUT_S else 0
        conn.set_progress_handler(_guard, 50_000)
        deadline[0] = _time.time()
        c.execute(pred_sql); pr = c.fetchall()
        deadline[0] = _time.time()
        c.execute(gold_sql); gr = c.fetchall()
        c.close(); conn.close()
        return set(pr) == set(gr)
    except Exception:
        return False


def get_dataset_config(dataset: str) -> dict:
    """Return paths and settings for a dataset."""
    if dataset == "bird":
        return {
            "db_path": BIRD_DB_PATH,
            "tables_json": BIRD_TABLES,
            "dev_json": BIRD_DEV,
            "complex_json": BIRD_COMPLEX,
        }
    elif dataset == "spider":
        return {
            "db_path": SPIDER_DB_PATH,
            "tables_json": SPIDER_TABLES,
            "dev_json": SPIDER_DEV,
            "complex_json": None,
        }
    raise ValueError(f"Unknown dataset: {dataset}")


# ============================================================
# QuerysetLoader
# ============================================================

class QuerysetLoader:
    """Load and filter BIRD dev / Spider queries. Supports both datasets."""

    def __init__(self, dataset: str = "bird"):
        """
        Args:
            dataset: "bird" or "spider"
        """
        self.dataset = dataset

        if dataset == "bird":
            with open(BIRD_DEV, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            self.all_data = raw
            self.tables_path = BIRD_TABLES
            self.db_path_base = BIRD_DB_PATH
            self._complex_ids = self._load_complex_ids()
        elif dataset == "spider":
            with open(SPIDER_DEV, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            # Normalize Spider format to BIRD format
            self.all_data = self._normalize_spider(raw)
            self.tables_path = SPIDER_TABLES
            self.db_path_base = SPIDER_DB_PATH
            self._complex_ids = set()  # Spider has no pre-computed complex list
        else:
            raise ValueError(f"Unknown dataset: {dataset}")

    def _normalize_spider(self, raw: List[dict]) -> List[dict]:
        """Convert Spider entries to BIRD-compatible format."""
        normalized = []
        for i, item in enumerate(raw):
            normalized.append({
                'question_id': i,              # Spider has no question_id
                'db_id': item['db_id'],
                'question': item['question'],
                'SQL': item['query'],           # Spider: 'query' → BIRD: 'SQL'
                'evidence': '',                 # Spider has no evidence
                'difficulty': 'unknown',        # Spider has no difficulty field
            })
        return normalized

    def _load_complex_ids(self) -> Set[int]:
        try:
            with open(BIRD_COMPLEX, 'r', encoding='utf-8') as f:
                return set(json.load(f)['complex_query_ids'])
        except FileNotFoundError:
            from experiments.query_filter import is_complex
            return {
                item['question_id'] for item in self.all_data
                if is_complex(item.get('SQL', ''))
            }

    def get_queries(self, n: int = None, complex_only: bool = True,
                    seed: int = 42, difficulty_balance: bool = True) -> List[dict]:
        """Select n queries with diversity constraints."""
        rng = random.Random(seed)

        if self.dataset == "bird" and complex_only:
            pool = [item for item in self.all_data
                    if item['question_id'] in self._complex_ids]
        elif self.dataset == "spider" and complex_only:
            from experiments.query_filter import is_complex
            pool = [item for item in self.all_data
                    if is_complex(item.get('SQL', ''))]
        else:
            pool = list(self.all_data)

        if n is None:
            n = len(pool)

        if self.dataset == "bird" and difficulty_balance:
            diff_order = ['simple', 'moderate', 'challenging']
            diff_counts = Counter(q['difficulty'] for q in pool)
            total_pool = len(pool)
            selected = []
            for diff in diff_order:
                target = max(1, round(n * diff_counts[diff] / total_pool))
                seen_dbs = set()
                candidates = [q for q in pool
                              if q['difficulty'] == diff and q['db_id'] not in seen_dbs]
                rng.shuffle(candidates)
                for q in candidates:
                    if sum(1 for s in selected if s['difficulty'] == diff) >= target:
                        break
                    selected.append(q)
                    seen_dbs.add(q['db_id'])
            if len(selected) < n:
                remaining = [q for q in pool if q not in selected]
                rng.shuffle(remaining)
                selected.extend(remaining[:n - len(selected)])
            return selected[:n]

        rng.shuffle(pool)
        return pool[:n]

    def get_by_db(self, db_id: str, complex_only: bool = True) -> List[dict]:
        """Get all queries for a specific database."""
        return [item for item in self.all_data if item['db_id'] == db_id]

    def get_db_ids(self) -> List[str]:
        """List all database IDs."""
        return sorted(set(item['db_id'] for item in self.all_data))


# ============================================================
# Security pipeline (audit → rewrite → degrade)
# ============================================================

def run_audit_pipeline(
    sub_queries: List[dict],
    db_id: str,
    pred_sql: str = "",
    gold_sql: str = "",
    rewrite: bool = True,
    degradation: bool = True,
    violation_details: Optional[dict] = None,
    dataset: str = "bird",
) -> Tuple[int, int, int, str, str, Optional[bool], List[dict]]:
    """
    Run audit → rewrite → degrade on any decomposition plan.

    Args:
        sub_queries: [{id, description, sql}, ...]
        db_id: Database identifier
        pred_sql: Predicted final SQL (for EX evaluation, optional)
        gold_sql: Ground truth SQL (for EX evaluation, optional)
        rewrite: If False, skip the rewrite phase (B1/B1-Q: audit-only)
        degradation: If False, skip the degradation phase (B0: measurement-only,
                     violations silently exposed)
        violation_details: optional dict filled with
            {'before': [...], 'after': [...]} violation lists for rich
            summaries (offline re-run reports).

    Returns:
        (v_before, v_after, n_rewrites, degradation_level, degradation_message, ex_match, sub_results)
    """
    import copy
    from auditor.base import (
        AuditParseError, SecurityAuditor, ViolationSeverity,
        deduplicate_violations,
    )
    from rewrite.engine import RewriteEngine
    from degradation.engine import DegradationEngine
    from ssa.loader import load_ssa

    sub_results = []
    original_sub_queries = copy.deepcopy(sub_queries)

    try:
        ssa = load_ssa(db_id, SSA_DIR)
    except FileNotFoundError:
        return 0, 0, 0, "L0", "", None, sub_results

    auditor = SecurityAuditor(ssa)
    rewriter = RewriteEngine(auditor, ssa)
    degrader = DegradationEngine(ssa)

    # Phase 1: audit before rewrite
    try:
        audit_before = auditor.audit_all(sub_queries)
    except AuditParseError:
        message = (
            "This query cannot be safely audited because a generated SQL "
            "statement could not be parsed."
        )
        if violation_details is not None:
            violation_details['before'] = []
            violation_details['after'] = []
        return 0, 0, 0, "L3", message, None, sub_results
    v_before = sum(len(ar.violations) for ar in audit_before)
    if violation_details is not None:
        violation_details['before'] = [
            v for ar in audit_before for v in ar.violations
        ]

    # Phase 2: rewrite each sub-query with violations (skip if rewrite=False).
    # Iterate in REVERSE order so dead sub-query elimination (in-place
    # deletion of later indices) never shifts the indices still to process,
    # and so Rule B no longer pushes conditions from already-deleted
    # downstream sub-queries.
    n_rewrites = 0
    rewrite_floor = "L0"
    rewrite_rank = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}
    minimization_applied = False
    if rewrite:
        # ORDER/RANK data minimization is independent of projection
        # violations (mirrors security_auditor_agent_node's no-violation
        # path): a controlled column used only in ORDER BY must still be
        # capped, surfaced as L2.
        if v_before == 0:
            for sq in sub_queries:
                rewritten_sql, logs = rewriter.apply_restricted_order_limit(
                    sq.get('sql', '')
                )
                if logs:
                    sq['sql'] = rewritten_sql
                    minimization_applied = True
        for i in range(len(sub_queries) - 1, -1, -1):
            sq = sub_queries[i]
            has_v = any(
                v.sub_query_index == i
                for ar in audit_before for v in ar.violations
            )
            if has_v:
                original_sql = sq['sql']
                try:
                    down_needs = auditor._compute_downstream_needs(i, sub_queries)
                    rw = rewriter.rewrite(
                        original_sql, i, sub_queries, down_needs
                    )
                except AuditParseError:
                    message = (
                        "This query cannot be safely audited because a generated "
                        "SQL statement could not be parsed."
                    )
                    if violation_details is not None:
                        violation_details['after'] = []
                    return v_before, 0, n_rewrites, "L3", message, None, sub_results
                candidate_floor = rw.degradation_level.value
                if rewrite_rank[candidate_floor] > rewrite_rank[rewrite_floor]:
                    rewrite_floor = candidate_floor
                if rw.eliminate:
                    # Dead sub-query elimination — drop it from the plan.
                    del sub_queries[i]
                    n_rewrites += 1
                    sub_results.append({
                        'index': i,
                        'violations_before': len([v for ar in audit_before
                                                  for v in ar.violations
                                                  if v.sub_query_index == i]),
                        'violations_after': 0,
                        'rewritten': False,
                        'eliminated': True,
                        'rewrite_log': rw.rewrite_log,
                    })
                    continue
                was_rewritten = rw.rewritten_sql != original_sql
                if was_rewritten:
                    n_rewrites += 1
                    sq['sql'] = rw.rewritten_sql

                sub_results.append({
                    'index': i,
                    'violations_before': len([v for ar in audit_before
                                              for v in ar.violations
                                              if v.sub_query_index == i]),
                    'violations_after': len(rw.remaining_violations),
                    'rewritten': was_rewritten,
                    'rewrite_log': rw.rewrite_log,
                })

    # Phase 3: audit after rewrite
    try:
        audit_after = auditor.audit_all(sub_queries)
    except AuditParseError:
        message = (
            "This query cannot be safely audited because a generated SQL "
            "statement could not be parsed."
        )
        if violation_details is not None:
            violation_details['after'] = []
        return v_before, 0, n_rewrites, "L3", message, None, sub_results
    v_after = sum(len(ar.violations) for ar in audit_after)
    if violation_details is not None:
        violation_details['after'] = [
            v for ar in audit_after for v in ar.violations
        ]

    # Phase 4: degradation (skip if degradation=False, B0 measurement-only)
    level = "L0"
    message = ""
    if degradation:
        if v_before == 0 and minimization_applied:
            # ORDER/RANK cap was the only semantic change (mirrors the
            # deployed node's no-violation path).
            level = "L2"
            message = (
                "The result was capped at 100 rows because ranking by a "
                "restricted column can expose individual-level ordering."
            )
        else:
            initial_policy = [
                v for ar in audit_before for v in ar.violations
                if v.severity in (
                    ViolationSeverity.MUST_DEGRADE,
                    ViolationSeverity.DEGRADABLE,
                )
            ]
            all_v = deduplicate_violations(
                initial_policy + [v for ar in audit_after for v in ar.violations]
            )
            deg = degrader.determine_plan(
                all_v,
                sub_queries,
                original_sub_queries=original_sub_queries,
            )
            level = deg.level.value
            message = deg.message
            if deg.modified_sub_queries:
                sub_queries[:] = deg.modified_sub_queries

            # Rule C generated SQL is untrusted: audit it once before
            # returning (single-pass discipline — a residual violation
            # escalates to L3 instead of launching another rewrite loop).
            rule_c_applied = any(
                entry.startswith("Rule C:")
                for entry in deg.degradation_log
            )
            if rule_c_applied:
                try:
                    generated_audit = auditor.audit_all(sub_queries)
                except AuditParseError:
                    level = "L3"
                    message = (
                        "This query cannot be safely audited because a "
                        "generated SQL statement could not be parsed."
                    )
                else:
                    residual = [
                        v for ar in generated_audit for v in ar.violations
                    ]
                    if residual:
                        level = "L3"
                        message = (
                            "This query cannot be answered because the "
                            "generated aggregate alternative did not pass "
                            "the final security audit."
                        )

            # Semantic degradation floor: a retained aggregate alternative
            # is L1 and an intent change is L2 even when all security
            # violations were eliminated (mirrors the deployed node).
            if rewrite_rank[rewrite_floor] > rewrite_rank.get(level, 3):
                level = rewrite_floor
                message = {
                    "L1": (
                        "The individual-level intermediate result was "
                        "replaced with a secure aggregate-level alternative."
                    ),
                    "L2": (
                        "The requested intermediate result required a "
                        "related but different secure alternative."
                    ),
                }.get(rewrite_floor, message)

    # Phase 5: EX
    ex = evaluate_ex(pred_sql, gold_sql, db_id, dataset=dataset) if pred_sql and gold_sql else None

    return v_before, v_after, n_rewrites, level, message, ex, sub_results


# ============================================================
# Our pipeline (B4/B5/B6 — QSG-based)
# ============================================================

def run_ours_pipeline(
    item: dict,
    desc_str: str,
    fk_str: str,
    *,
    enable_audit: bool = True,
    enable_rewrite: bool = True,
    enable_degradation: bool = True,
    temperature: float = 0.0,
) -> BaselineResult:
    """
    Run QSG → Dependency Graph → Search → SQL Gen,
    with optional audit/rewrite/degradation controlled by flags.

    B4: enable_audit=False  → no security
    B5: enable_audit=True, enable_rewrite=False → audit + degrade only
    B6: enable_audit=True, enable_rewrite=True  → full pipeline
    """
    method = "B6"
    if not enable_audit:
        method = "B4"
    elif not enable_rewrite:
        method = "B5"

    result = BaselineResult(
        method=method,
        question_id=item.get('question_id'),
        db_id=item.get('db_id'),
        difficulty=item.get('difficulty'),
        query=item.get('question', ''),
        gold_sql=item.get('SQL', ''),
    )

    # Step 1: QSG parsing
    from qsg.parser import QSGParser
    from graph.dependency import build_dependency_graph
    from graph.search import search_information_minimal_decomposition
    from graph.sql_generator import SQLGenerator
    from ssa.loader import load_ssa

    try:
        ssa = load_ssa(item['db_id'], SSA_DIR)
    except FileNotFoundError:
        result.error = f"SSA not found for {item['db_id']}"
        return result

    qsg_parser = QSGParser(temperature=temperature)
    qsg, errors = qsg_parser.parse(
        item['question'], desc_str, fk_str, item.get('evidence', '')
    )
    if qsg is None:
        result.error = f"QSG parse failed: {errors}"
        return result

    # Step 2: Dependency graph
    dep_graph = build_dependency_graph(qsg)

    # Step 3: Decomposition search
    candidates = search_information_minimal_decomposition(dep_graph, ssa)
    if not candidates:
        result.error = "Search found no valid decomposition"
        return result

    best = candidates[0]
    result.I_score = best.I_score
    result.n_subqueries = len(best.partitions)

    # Step 4: SQL generation
    sql_gen = SQLGenerator(max_partitions=5)
    sub_queries = sql_gen.generate(
        best, qsg, dep_graph, desc_str, fk_str,
        item['question'], item.get('evidence', '')
    )
    if not sub_queries:
        result.error = "SQL generation produced no sub-queries"
        return result

    result.n_subqueries = len(sub_queries)
    result.sub_queries = sub_queries
    result.pred_sql = sub_queries[-1]['sql'] if sub_queries else ''

    # B4: stop here (no security)
    if not enable_audit:
        result.n_violations_before = 0
        result.n_violations_after = 0
        result.degradation_level = "L0"
        result.ex_match = evaluate_ex(
            result.pred_sql, result.gold_sql, item['db_id']
        ) if result.pred_sql and result.gold_sql else None
        return result

    # Step 5: Audit pipeline (B5/B6)
    v_b, v_a, n_rw, level, msg, ex, sub_res = run_audit_pipeline(
        sub_queries, item['db_id'], result.pred_sql, result.gold_sql,
        rewrite=enable_rewrite,
        degradation=enable_degradation,
    )
    result.n_violations_before = v_b
    result.n_violations_after = v_a
    result.n_rewrites = n_rw
    result.ex_match = ex
    result.sub_results = sub_res

    result.degradation_level = level
    result.degradation_message = msg

    return result


# ============================================================
# Violation classification (X/Y/Z for pilot study)
# ============================================================

def classify_violations(
    sub_queries: List[dict],
    db_id: str,
) -> Dict[str, int]:
    """
    Classify violations into X/Y/Z categories.

    X = purely redundant: column not consumed by any downstream → mask doesn't affect EX
    Y = downstream-needed but not output: column consumed by downstream WHERE/JOIN
        but not in downstream SELECT → mask breaks functionality
    Z = needed + output + aggregatable: column in final PROJECT, can be aggregated
    """
    from auditor.base import SecurityAuditor
    from ssa.loader import load_ssa

    try:
        ssa = load_ssa(db_id, SSA_DIR)
    except FileNotFoundError:
        return {"X": 0, "Y": 0, "Z": 0, "total": 0}

    auditor = SecurityAuditor(ssa)
    audit_results = auditor.audit_all(sub_queries)

    counts = {"X": 0, "Y": 0, "Z": 0, "total": 0}

    for i, ar in enumerate(audit_results):
        if not ar.violations:
            continue

        down_needs = auditor._compute_downstream_needs(i, sub_queries)

        # Parse SELECT columns directly from the SQL
        import sqlglot, sqlglot.expressions as exp
        select_cols = set()
        sql = sub_queries[i].get('sql', '') if i < len(sub_queries) else ''
        try:
            tree = sqlglot.parse_one(sql, read='sqlite')
            for sel in tree.find_all(exp.Select):
                for col_expr in sel.expressions:
                    for bc in col_expr.find_all(exp.Column):
                        name = bc.name.strip('`') if bc.name else ''
                        if name:
                            select_cols.add(name)
        except Exception:
            pass

        for v in ar.violations:
            counts["total"] += 1
            col = v.column.split('.')[-1] if '.' in v.column else v.column

            if col not in down_needs:
                # X: purely redundant — downstream doesn't need this column at all
                counts["X"] += 1
            elif col in select_cols:
                # Z: downstream needs + appears in SELECT output → aggregatable
                counts["Z"] += 1
            else:
                # Y: downstream needs (via WHERE/JOIN) but not in SELECT → mask breaks
                counts["Y"] += 1

    return counts


# ============================================================
# Result I/O
# ============================================================

def resume_check(filepath: str) -> tuple:
    """
    Load completed query_ids from an existing JSONL output file.

    Returns:
        (completed_ids, existing_results, existing_counters)
        - completed_ids: set of question_id that already exist in the file
        - existing_results: list of dicts from the file
        - existing_counters: dict with pre-computed aggregate stats
    """
    completed_ids = set()
    existing_results = []
    if not os.path.exists(filepath):
        return completed_ids, existing_results, {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                existing_results.append(r)
                qid = r.get('question_id')
                if qid is not None:
                    completed_ids.add(int(qid))
            except json.JSONDecodeError:
                continue

    # Pre-compute counters from existing results
    queries_with_v = sum(1 for r in existing_results if r.get('n_violations_before', 0) > 0)
    always_unsafe = 0  # Can't accurately recompute without all seeds
    total_subq = sum(r.get('n_subqueries', 0) for r in existing_results)
    total_v = sum(r.get('n_violations_before', 0) for r in existing_results)

    existing_counters = {
        'queries_with_violations': queries_with_v,
        'total_subq': total_subq,
        'total_v': total_v,
    }

    return completed_ids, existing_results, existing_counters


def append_result(result: BaselineResult, filepath: str):
    """Append a single result to JSONL file (for resume-safe incremental writes)."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result.to_dict(), ensure_ascii=False) + '\n')


def save_results(results: List[BaselineResult], filepath: str):
    """Save results as JSONL."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + '\n')


def load_results(filepath: str) -> List[dict]:
    """Load results from JSONL."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


# ============================================================
# ExperimentLogger
# ============================================================

class ExperimentLogger:
    """Progress reporting with elapsed time."""

    def __init__(self, name: str, total: int):
        self.name = name
        self.total = total
        self.t0 = time.time()
        self.i = 0

    def start_query(self, item: dict):
        self.i += 1
        qid = item.get('question_id', '?')
        db = item.get('db_id', '?')
        diff = item.get('difficulty', '?')
        query = (item.get('question', '') or '')[:80]
        elapsed = time.time() - self.t0
        print(f"\n[{self.i}/{self.total}] [{qid}] {db} ({diff}) "
              f"| {elapsed:.0f}s elapsed")
        print(f"  Q: {query}...")

    def log_method(self, result: BaselineResult):
        if result.error:
            print(f"  {result.method}: ERROR — {result.error}")
        else:
            print(f"  {result.method}: {result.n_subqueries} sub-q, "
                  f"V: {result.n_violations_before}→{result.n_violations_after}, "
                  f"R: {result.n_rewrites}, {result.degradation_level}, "
                  f"EX={result.ex_match}, I(D)={result.I_score}")

    def summary(self, results: List[BaselineResult]):
        elapsed = time.time() - self.t0
        print(f"\n{'='*60}")
        print(f"  {self.name} — {len(results)} queries, {elapsed:.0f}s")
        print(f"{'='*60}")

        by_method = defaultdict(list)
        for r in results:
            by_method[r.method].append(r)

        for method in sorted(by_method.keys()):
            rs = by_method[method]
            n = len(rs)
            ex = sum(1 for r in rs if r.ex_match) / max(1, sum(1 for r in rs if r.ex_match is not None))
            svr = sum(r.n_violations_before for r in rs) / max(1, sum(r.n_subqueries for r in rs))
            n_errors = sum(1 for r in rs if r.error)
            print(f"  {method}: EX={ex:.3f}, S-VR={svr:.3f}, "
                  f"errors={n_errors}/{n}")
def run_ours_forward(item: dict, desc_str: str, fk_str: str) -> dict:
    """QSG → Graph → Search → SQL Gen. Called ONCE per query, shared by B4-Q/B1-Q/B2-Q."""
    from qsg.parser import QSGParser
    from graph.dependency import build_dependency_graph
    from graph.search import search_information_minimal_decomposition
    from graph.sql_generator import SQLGenerator
    from ssa.loader import load_ssa

    ssa = load_ssa(item['db_id'], SSA_DIR)

    qsg_parser = QSGParser(temperature=0.0)
    qsg, errors = qsg_parser.parse(
        item['question'], desc_str, fk_str, item.get('evidence', '')
    )
    if qsg is None:
        return {'error': f"QSG parse failed: {errors}"}

    dep_graph = build_dependency_graph(qsg)
    candidates = search_information_minimal_decomposition(dep_graph, ssa)
    if not candidates:
        return {'error': "Search found no valid decomposition"}

    best = candidates[0]
    sql_gen = SQLGenerator(max_partitions=5)
    sub_queries = sql_gen.generate(
        best, qsg, dep_graph, desc_str, fk_str,
        item['question'], item.get('evidence', '')
    )
    if not sub_queries:
        return {'error': "SQL generation produced no sub-queries"}

    pred_sql = sub_queries[-1]['sql'] if sub_queries else ''
    return {
        'sub_queries': sub_queries,
        'pred_sql': pred_sql,
        'ssa': ssa,
        'I_score': best.I_score,
    }


def ours_divergent(item: dict, shared: dict,
                   enable_audit: bool, enable_rewrite: bool,
                   enable_degradation: bool = True,
                   dataset: str = "bird") -> BaselineResult:
    """QSG cells from shared decomposition. Applies audit/rewrite/evaluation only."""
    method = "B6"
    if not enable_audit:
        method = "B4"
    elif not enable_rewrite:
        method = "B5"

    import copy
    ssa = shared.get('ssa')
    if ssa is None:
        from ssa.loader import load_ssa
        ssa = load_ssa(item['db_id'], SSA_DIR)
    sub_queries = copy.deepcopy(shared['sub_queries'])
    pred_sql = shared['pred_sql']

    result = BaselineResult(
        method=method,
        question_id=item.get('question_id'),
        db_id=item.get('db_id'),
        difficulty=item.get('difficulty'),
        query=item.get('question', ''),
        gold_sql=item.get('SQL', ''),
        n_subqueries=len(sub_queries),
        sub_queries=sub_queries,
        pred_sql=pred_sql,
    )

    if not enable_audit:
        result.n_violations_before = 0
        result.n_violations_after = 0
        result.degradation_level = "L0"
        result.ex_match = evaluate_ex(
            pred_sql, result.gold_sql, item['db_id'], dataset=dataset
        ) if pred_sql and result.gold_sql else None
        if shared.get('I_score') is not None:
            result.I_score = shared['I_score']
        return result

    v_b, v_a, n_rw, level, msg, ex, sub_res = run_audit_pipeline(
        sub_queries, item['db_id'], pred_sql, result.gold_sql,
        rewrite=enable_rewrite,
        degradation=enable_degradation,
        dataset=dataset,
    )
    result.n_violations_before = v_b
    result.n_violations_after = v_a
    result.n_rewrites = n_rw
    result.ex_match = ex
    result.sub_results = sub_res
    result.degradation_level = level
    result.degradation_message = msg
    if shared.get('I_score') is not None:
        result.I_score = shared['I_score']

    return result
