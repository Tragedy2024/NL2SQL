"""
Offline re-run of the security audit component on cached decomposition plans.

Re-executes audit → rewrite → degradation (plus EX reuse and the B3
post-hoc baseline) with the CURRENT code on the decomposition plans
cached during the original LLM runs.  Zero LLM calls — the plans in
results/rq1 and results/rq2 are reused as-is.

Why this is valid: the audit/rewrite/degradation component is purely
algorithmic (sqlglot AST, no API calls), so re-running it on the same
plans reproduces exactly what the live pipeline would have produced.
It also removes LLM variance across configurations, which makes the
B0-B4 and QSG-matrix comparison, a same-plan controlled comparison.

Usage:
  python experiments/offline_rerun.py --rq1               # RQ1 re-run
  python experiments/offline_rerun.py --rq2               # RQ2 B0-B6 re-run
  python experiments/offline_rerun.py --all               # both
  python experiments/offline_rerun.py --rq2 --limit 20    # smoke slice
  python experiments/offline_rerun.py --rq1 --groups bird_fewshot
"""
import argparse
import copy
import json
import os
import sqlite3
import sys
from collections import Counter, defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from common import (  # noqa: E402
    BIRD_DB_PATH, RESULTS_DIR, SPIDER_DB_PATH, SSA_DIR, run_audit_pipeline,
)
from evaluation.statistics import bootstrap_ci, mcnemar_test  # noqa: E402

OUT_DIR = os.path.join(RESULTS_DIR, "offline_rerun")

RQ1_GROUPS = {
    "bird_fewshot": "rq1_bird_fewshot_results.jsonl",
    "bird_zeroshot": "rq1_bird_zeroshot_results.jsonl",
    "spider_fewshot": "rq1_spider_fewshot_results.jsonl",
    "spider_zeroshot": "rq1_spider_zeroshot_results.jsonl",
}
RQ2_GROUPS = {
    "bird_fewshot": "rq2_bird_fewshot_results.jsonl",
    "bird_zeroshot": "rq2_bird_zeroshot_results.jsonl",
    "spider_fewshot": "rq2_spider_fewshot_results.jsonl",
    "spider_zeroshot": "rq2_spider_zeroshot_results.jsonl",
}

# B0/B1/B2/B4/B5/B6 use the same algorithmic pipeline with different
# switches, on each record's OWN cached plans.  B3 is the post-hoc
# column filter (executes SQL against the local database — still no LLM).
METHOD_CONFIGS = {
    "B0": dict(rewrite=False, degradation=False),
    "B1": dict(rewrite=False, degradation=True),
    "B2": dict(rewrite=True, degradation=True),
    "B4": dict(rewrite=True, degradation=True),
    "B1-Q": dict(rewrite=False, degradation=True),
    "B2-Q": dict(rewrite=True, degradation=True),
    "B0-Q": dict(rewrite=False, degradation=False),
    "B4-Q": dict(rewrite=True, degradation=True),
}
METHOD_ORDER = ["B0", "B1", "B2", "B3", "B4",
                "B0-Q", "B1-Q", "B2-Q", "B3-Q", "B4-Q"]


# ============================================================
# Helpers
# ============================================================

def iter_jsonl(path):
    """Yield parsed records, skipping blank/corrupt lines."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _details_dict():
    return {"before": [], "after": []}


def _resolve_group_file(root: str, subdir: str, filename: str) -> str:
    """Locate a group results file in nested (root/rqX/file) or flat layout."""
    nested = os.path.join(root, subdir, filename)
    if os.path.exists(nested):
        return nested
    flat = os.path.join(root, filename)
    if os.path.exists(flat):
        return flat
    return nested  # raise FileNotFoundError with the nested path


def rerun_security(record, rewrite, degradation):
    """Re-run the security pipeline on one cached record.  Zero LLM."""
    sqs = copy.deepcopy(record.get("sub_queries") or [])
    details = _details_dict()
    v_before, v_after, n_rewrites, level, message, _, sub_results = (
        run_audit_pipeline(
            sqs, record["db_id"],
            rewrite=rewrite, degradation=degradation,
            violation_details=details,
        )
    )
    n_subqueries = record.get("n_subqueries") or len(
        record.get("sub_queries") or []
    )
    return {
        "v_before": v_before,
        "v_after": v_after,
        "n_rewrites": n_rewrites,
        "level": level,
        "message": message,
        "sub_results": sub_results,
        "violations_before": details.get("before", []),
        "violations_after": details.get("after", []),
        "n_subqueries": n_subqueries,
    }


def rerun_b3(record, dataset):
    """Re-run the B3 post-hoc column filter on cached plans.  Zero LLM.

    Mirrors experiments/rq2/run_rq2.py's B3 block: execute each cached
    sub-query against the local SQLite database, count exposed columns
    via _count_exposed_columns, filter the result set, and re-count.
    Returns None when the local database is unavailable.
    """
    from auditor.base import SecurityAuditor
    from baselines.post_hoc_filter import PostHocColumnFilter
    from ssa.loader import load_ssa

    sqs = copy.deepcopy(record.get("sub_queries") or [])
    if not sqs:
        return None
    try:
        ssa = load_ssa(record["db_id"], SSA_DIR)
    except FileNotFoundError:
        return None
    db_base = BIRD_DB_PATH if dataset == "bird" else SPIDER_DB_PATH
    db_path = os.path.join(
        db_base, record["db_id"], f"{record['db_id']}.sqlite"
    )
    if not os.path.exists(db_path):
        return None

    phf = PostHocColumnFilter(ssa)
    auditor = SecurityAuditor(ssa)
    total_before = 0
    total_after = 0
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.text_factory = lambda b: b.decode(errors="ignore")
        cursor = conn.cursor()
        # Per-query execution guard against pathological SQL.
        import time as _time
        deadline = [_time.time()]
        def _guard():
            return 1 if _time.time() - deadline[0] > 20 else 0
        conn.set_progress_handler(_guard, 50_000)
        for i, sq in enumerate(sqs):
            deadline[0] = _time.time()
            exposed = phf._count_exposed_columns(sq["sql"])
            if exposed < 0:
                exposed = 0
            total_before += exposed
            down_needs = auditor._compute_downstream_needs(i, sqs)
            try:
                cursor.execute(sq["sql"])
                rows = cursor.fetchmany(5)  # sample: only column names matter
                cols = (
                    [d[0] for d in cursor.description]
                    if cursor.description else []
                )
                rs = [dict(zip(cols, row)) for row in rows]
            except Exception:
                rs = []
            _, fr = phf.filter_intermediate_result(
                i, sq["sql"], rs, down_needs
            )
            total_after += max(0, exposed - len(fr.removed_columns))
        cursor.close()
        conn.close()
        conn = None
    except Exception:
        if conn is not None:
            conn.close()
        return None

    return {
        "v_before": total_before,
        "v_after": total_after,
        "n_subqueries": record.get("n_subqueries") or len(sqs),
    }


# ============================================================
# RQ1
# ============================================================

def rerun_rq1(group: str, limit: int = None, results_root: str = None) -> dict:
    dataset, mode = group.split("_", 1)
    root = results_root or RESULTS_DIR
    path = _resolve_group_file(root, "rq1", RQ1_GROUPS[group])
    print(f"\n[RQ1 {group}] reading {path}")

    # Dedupe by question_id: some files contain a few re-run remnants.
    # Keep the record with the most sub-queries.
    records = {}
    raw_count = 0
    for rec in iter_jsonl(path):
        raw_count += 1
        qid = rec.get("question_id")
        if qid is None:
            continue
        if (
            qid not in records
            or len(rec.get("sub_queries") or [])
            > len(records[qid].get("sub_queries") or [])
        ):
            records[qid] = rec

    processed = 0
    skipped_empty = 0
    parse_failures = 0
    total_subqueries = 0
    v_before = 0
    v_after = 0
    n_rewrites = 0
    type_counter = Counter()
    severity_counter = Counter()
    degradation = Counter()
    ex_hits = 0
    ex_known = 0

    for qid, rec in records.items():
        if limit is not None and processed >= limit:
            break
        if not rec.get("sub_queries"):
            skipped_empty += 1
            continue
        r = rerun_security(rec, rewrite=True, degradation=True)
        processed += 1
        if r["message"] and "could not be parsed" in r["message"]:
            parse_failures += 1
        total_subqueries += r["n_subqueries"]
        v_before += r["v_before"]
        v_after += r["v_after"]
        n_rewrites += r["n_rewrites"]
        degradation[r["level"]] += 1
        for v in r["violations_before"]:
            type_counter[v.type.value] += 1
            severity_counter[v.severity.value] += 1
        if rec.get("ex_match") is not None:
            ex_known += 1
            ex_hits += int(bool(rec.get("ex_match")))

    summary = {
        "rq": "RQ1",
        "dataset": dataset,
        "mode": mode,
        "n_records_raw": raw_count,
        "n_queries": processed,
        "n_skipped_empty": skipped_empty,
        "parse_failures_L3": parse_failures,
        "total_sub_queries": total_subqueries,
        "total_violations_before": v_before,
        "S_VR": round(v_before / total_subqueries, 4) if total_subqueries else 0.0,
        "total_violations_after": v_after,
        "S_VR_after": round(v_after / total_subqueries, 4) if total_subqueries else 0.0,
        "S_AR": round((v_before - v_after) / v_before, 4) if v_before else None,
        "n_rewrites": n_rewrites,
        "EX": round(ex_hits / ex_known, 4) if ex_known else None,
        "degradation": dict(degradation),
        "violation_types": dict(type_counter),
        "violation_severities": dict(severity_counter),
    }
    return summary


# ============================================================
# RQ2
# ============================================================

def _aggregate_method(rows):
    """rows: list of rerun result dicts (with 'method' filled)."""
    agg = {
        "n": len(rows),
        "EX": None,
        "ex_known": 0,
        "S_VR_pre": None,
        "S_VR_post": None,
        "S_AR": None,
        "V": 0,
        "n_rewrites": 0,
        "degradation": {},
        "n_subqueries": 0,
    }
    ex_hits = 0
    for r in rows:
        agg["V"] += r["v_before"]
        agg["n_subqueries"] += r["n_subqueries"]
        agg["n_rewrites"] += r.get("n_rewrites", 0)
        if r.get("level"):
            agg["degradation"][r["level"]] = agg["degradation"].get(r["level"], 0) + 1
        if r.get("ex_match") is not None:
            agg["ex_known"] += 1
            ex_hits += int(bool(r["ex_match"]))
    if agg["ex_known"]:
        agg["EX"] = round(ex_hits / agg["ex_known"], 4)
    if agg["n_subqueries"]:
        agg["S_VR_pre"] = round(agg["V"] / agg["n_subqueries"], 4)
        v_after = sum(r["v_after"] for r in rows)
        agg["S_VR_post"] = round(v_after / agg["n_subqueries"], 4)
        if agg["V"]:
            agg["S_AR"] = round((agg["V"] - v_after) / agg["V"], 4)
    return agg


def rerun_rq2(group: str, limit: int = None, results_root: str = None) -> dict:
    dataset, mode = group.split("_", 1)
    root = results_root or RESULTS_DIR
    path = _resolve_group_file(root, "rq2", RQ2_GROUPS[group])
    print(f"\n[RQ2 {group}] reading {path}")

    per_method = {m: [] for m in METHOD_ORDER}
    skipped = Counter()
    processed_total = 0

    for rec in iter_jsonl(path):
        method = rec.get("method")
        if method not in per_method:
            skipped["unknown_method"] += 1
            continue
        if limit is not None and len(per_method[method]) >= limit:
            continue
        if not rec.get("sub_queries"):
            skipped["empty_plan"] += 1
            continue

        if method in ("B3", "B3-Q"):
            r = rerun_b3(rec, dataset)
            if r is None:
                skipped["b3_no_db"] += 1
                continue
            r.update({"level": None, "n_rewrites": 0, "ex_match": rec.get("ex_match")})
        else:
            cfg = METHOD_CONFIGS[method]
            r = rerun_security(rec, rewrite=cfg["rewrite"], degradation=cfg["degradation"])
            r["ex_match"] = rec.get("ex_match")
        r["qid"] = rec.get("question_id")
        per_method[method].append(r)
        processed_total += 1
        if processed_total % 500 == 0:
            print(f"  ... {processed_total} records processed")

    methods = {}
    for m in METHOD_ORDER:
        rows = per_method[m]
        if not rows:
            methods[m] = {"n": 0, "note": "no records"}
            continue
        methods[m] = _aggregate_method(rows)
    methods["_skipped"] = dict(skipped)

    # ---- Statistical tests ----
    stats = {}
    b1_ex = defaultdict(list)
    b6_ex = defaultdict(list)
    b6_svr = []
    for r in per_method["B1"]:
        b1_ex[r["qid"]].append(r["ex_match"])
    for r in per_method["B2-Q"]:
        b6_ex[r["qid"]].append(r["ex_match"])
        if r["n_subqueries"]:
            b6_svr.append(r["v_before"] / r["n_subqueries"])
    a, b = [], []
    for qid in b1_ex:
        for i, ex in enumerate(b1_ex[qid]):
            if qid in b6_ex and i < len(b6_ex[qid]):
                a.append(ex)
                b.append(b6_ex[qid][i])
    if a:
        stats["mcnemar_B1_vs_B2Q_EX"] = mcnemar_test(
            [bool(x) for x in a], [bool(y) for y in b]
        )
    if b6_svr:
        stats["bootstrap_B6_SVR"] = bootstrap_ci(b6_svr)

    return {
        "dataset": dataset,
        "mode": mode,
        "methods": methods,
        "stats": stats,
    }


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rq1", action="store_true", help="re-run RQ1 groups")
    parser.add_argument("--rq2", action="store_true", help="re-run RQ2 groups")
    parser.add_argument("--all", action="store_true", help="re-run RQ1 + RQ2")
    parser.add_argument("--groups", default=None,
                        help="comma-separated group names, e.g. bird_fewshot")
    parser.add_argument("--limit", type=int, default=None,
                        help="max records per method/group (smoke testing)")
    parser.add_argument("--results-root", default=RESULTS_DIR,
                        help="results root (e.g. results/backup_20260726)")
    parser.add_argument("--out-dir", default=None,
                        help="output directory (default: <results-root>/offline_rerun)")
    args = parser.parse_args()

    if not (args.rq1 or args.rq2 or args.all):
        parser.error("pass --rq1, --rq2, or --all")

    root = args.results_root
    out_dir = args.out_dir or (
        os.path.join(root, "offline_rerun")
        if os.path.abspath(root) != os.path.abspath(RESULTS_DIR)
        else OUT_DIR
    )
    os.makedirs(out_dir, exist_ok=True)
    report = {"generated_by": "experiments/offline_rerun.py",
              "results_root": root,
              "note": "Zero LLM calls — audit re-run on cached decomposition plans."}

    if args.rq1 or args.all:
        groups = RQ1_GROUPS
        if args.groups:
            groups = {g: RQ1_GROUPS[g] for g in args.groups.split(",") if g in RQ1_GROUPS}
        for group in groups:
            summary = rerun_rq1(group, args.limit, results_root=root)
            out = os.path.join(out_dir, f"rq1_{group}_summary.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            report[f"rq1_{group}"] = summary
            print(f"  -> {out}")
            print(f"     S-VR {summary['S_VR']} -> {summary['S_VR_after']} "
                  f"(S-AR {summary['S_AR']}), violations {summary['total_violations_before']}")

    if args.rq2 or args.all:
        groups = RQ2_GROUPS
        if args.groups:
            groups = {g: RQ2_GROUPS[g] for g in args.groups.split(",") if g in RQ2_GROUPS}
        for group in groups:
            summary = rerun_rq2(group, args.limit, results_root=root)
            out = os.path.join(out_dir, f"rq2_{group}_summary.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            report[f"rq2_{group}"] = summary
            print(f"  -> {out}")
            for m in METHOD_ORDER:
                agg = summary["methods"].get(m, {})
                if agg.get("n"):
                    print(f"     {m}: EX={agg['EX']} S-VR {agg['S_VR_pre']}->{agg['S_VR_post']} "
                          f"S-AR={agg['S_AR']} V={agg['V']} deg={agg['degradation']}")
            if summary["stats"]:
                print(f"     stats: {json.dumps(summary['stats'], ensure_ascii=False)[:200]}")

    report_out = os.path.join(out_dir, "rerun_report.json")
    with open(report_out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] full report: {report_out}")


if __name__ == "__main__":
    main()
