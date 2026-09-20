"""
Standalone X/Y/Z classification — run on any JSONL results file.

Classifies each violation as:
  X = purely redundant: column not consumed downstream → mask不影响EX
  Y = downstream-needed but not in output: consumed by WHERE/JOIN → mask破坏功能
  Z = needed + in SELECT output + aggregatable

Usage (run from the project root):
    PYTHONPATH="src" python experiments/classify_xyz.py results/pilot/pilot_results.jsonl
    PYTHONPATH="src" python experiments/classify_xyz.py results/rq1/rq1_results.jsonl
"""
import json
import sys
import os
from collections import Counter, defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_BASE, 'src')
if _src not in sys.path:
    sys.path.insert(0, _src)

from experiments.common import classify_violations, SSA_DIR
from ssa.loader import load_ssa
from auditor.base import SecurityAuditor


def classify_file(filepath: str):
    """Run X/Y/Z classification on all results in a JSONL file."""
    results = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not results:
        print("No results found.")
        return

    print(f"Loaded {len(results)} results")

    all_xyz = {"X": 0, "Y": 0, "Z": 0, "total": 0}
    violation_types = Counter()
    violation_severities = Counter()
    per_db = defaultdict(lambda: {"n": 0, "v": 0, "xyz": {"X": 0, "Y": 0, "Z": 0, "total": 0}})
    queries_with_v = set()
    valid = 0
    skipped = 0

    for r in results:
        db_id = r.get("db_id", "")
        sub_queries = r.get("sub_queries", [])

        if not sub_queries or r.get("n_violations_before", 0) == 0:
            skipped += 1
            continue

        valid += 1
        qid = r.get("question_id")
        queries_with_v.add(qid)

        sqs = [{"id": sq["id"], "sql": sq["sql"]} for sq in sub_queries]

        # Classify X/Y/Z
        xyz = classify_violations(sqs, db_id)
        for k in ["X", "Y", "Z", "total"]:
            all_xyz[k] += xyz[k]

        per_db[db_id]["n"] += 1
        per_db[db_id]["v"] += r.get("n_violations_before", 0)
        per_db[db_id]["xyz"]["X"] += xyz["X"]
        per_db[db_id]["xyz"]["Y"] += xyz["Y"]
        per_db[db_id]["xyz"]["Z"] += xyz["Z"]
        per_db[db_id]["xyz"]["total"] += xyz["total"]

        # Violation type breakdown
        try:
            ssa = load_ssa(db_id, SSA_DIR)
            auditor = SecurityAuditor(ssa)
            audit_results = auditor.audit_all(sqs)
            for ar in audit_results:
                for v in ar.violations:
                    violation_types[v.type.value] += 1
                    violation_severities[v.severity.value] += 1
        except FileNotFoundError:
            pass

    # ============================================================
    # Output
    # ============================================================
    t = max(all_xyz["total"], 1)

    print(f"\n{'='*60}")
    print(f"  X/Y/Z Classification")
    print(f"{'='*60}")
    print(f"  Results with violations: {valid}/{len(results)}")
    print(f"  Unique queries:          {len(queries_with_v)}")
    print()
    print(f"  X (purely redundant):        {all_xyz['X']:>5} ({all_xyz['X']/t*100:.0f}%)")
    print(f"    → mask/post-hoc filter不影响EX")
    print(f"  Y (downstream-needed):       {all_xyz['Y']:>5} ({all_xyz['Y']/t*100:.0f}%)")
    print(f"    → mask破坏功能，需要事前改写")
    print(f"  Z (aggregatable):            {all_xyz['Z']:>5} ({all_xyz['Z']/t*100:.0f}%)")
    print(f"    → 下游需要且在SELECT中，可聚合")
    print(f"  ─────────────────────────")
    print(f"  Total:                       {all_xyz['total']:>5}")

    if all_xyz["Y"] / t > 0.30:
        print(f"\n  → 叙事: 功能优势 (Y>{30}%: Post-hoc Filter破坏功能)")
    elif all_xyz["X"] / t > 0.60:
        print(f"\n  → 叙事: GDPR合规 + 暴露面优势 (X>{60}%: 大部分纯粹冗余)")
    else:
        print(f"\n  → 混合分布")

    print(f"\n  Violation Types:")
    for typ, c in violation_types.most_common():
        print(f"    {typ}: {c}")

    print(f"\n  Violation Severities:")
    for sev, c in violation_severities.most_common():
        print(f"    {sev}: {c}")

    print(f"\n  Per Database:")
    for db in sorted(per_db.keys()):
        d = per_db[db]
        xyz = d["xyz"]
        tdb = max(xyz["total"], 1)
        print(f"    {db}: {d['n']} results, {d['v']} violations")
        print(f"      X={xyz['X']} ({xyz['X']/tdb*100:.0f}%)  "
              f"Y={xyz['Y']} ({xyz['Y']/tdb*100:.0f}%)  "
              f"Z={xyz['Z']} ({xyz['Z']/tdb*100:.0f}%)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python experiments/classify_xyz.py <results.jsonl>")
        sys.exit(1)

    classify_file(sys.argv[1])
