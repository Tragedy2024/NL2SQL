"""
Offline correction for the spider B4 ex_match values.

Background: ``evaluate_ex`` defaulted to ``dataset="bird"`` and the current
pipeline never passed the dataset, so every spider record evaluated by the
CURRENT code looked up the database under the BIRD path (missing file) and
got ex_match=False.  The new B4 spider lines are affected; old B0-B3/B5/B6
lines carry ex_match computed by earlier code and are untouched.

The Decomposer replies for the B4 run are still available in
``results/api_trace.json`` (chronologically appended).  This script:

1. For each spider B4 record (question_id, db_id, query), finds the LAST
   three Decomposer trace rows with the same (db_id, query) — these are the
   B4 re-run's three seeds, in seed order (42, 43, 44), because the run
   processed seeds sequentially per query and appended after all earlier
   runs' rows.
2. Re-derives final SQL with ``parse_sql_from_string`` and recomputes
   ex_match with the CORRECT dataset path.
3. Rewrites the two spider result files and recomputes their summaries.

Zero LLM calls.  Idempotent guard: refuses to run twice unless --force.
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments"),
           os.path.join(_BASE, "vendor", "MAC-SQL")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from core.utils import parse_sql_from_string  # noqa: E402
from evaluation.metrics import compute_sar, compute_sscore  # noqa: E402
from common import evaluate_ex  # noqa: E402

R_DIR = os.path.join(_BASE, "results", "rq2")
TRACE = os.path.join(_BASE, "results", "api_trace.json")
GROUPS = ["spider_fewshot", "spider_zeroshot"]
METHOD_ORDER = ["B0", "B1", "B2", "B3", "B4", "B5", "B6"]


def load_jsonl(path):
    """Parse a JSONL file that may contain several JSON objects per line."""
    rows = []
    decoder = json.JSONDecoder()
    with open(path, encoding="utf-8") as f:
        for line in f:
            pos = 0
            line = line.strip()
            while pos < len(line):
                while pos < len(line) and line[pos] in " \t":
                    pos += 1
                if pos >= len(line):
                    break
                try:
                    obj, end = decoder.raw_decode(line, pos)
                except json.JSONDecodeError:
                    break
                rows.append(obj)
                pos = end
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="Re-run even if records already carry a marker")
    args = ap.parse_args()

    trace_rows = load_jsonl(TRACE)
    decomp_by_key = defaultdict(list)
    for r in trace_rows:
        if r.get("send_to") != "Decomposer":
            continue
        key = (r.get("db_id"), r.get("query", "").strip())
        decomp_by_key[key].append(r)

    for g in GROUPS:
        path = os.path.join(R_DIR, f"rq2_{g}_results.jsonl")
        rows = load_jsonl(path)
        b4_rows = [(i, r) for i, r in enumerate(rows) if r.get("method") == "B4"]

        if b4_rows and b4_rows[0][1].get("_b4_ex_fixed") and not args.force:
            print(f"[{g}] already fixed (marker present), skip (--force to redo)")
            continue

        # Group B4 records by question_id; file order within a qid == seed order.
        by_qid = defaultdict(list)
        for i, r in b4_rows:
            by_qid[r.get("question_id")].append((i, r))

        fixed = 0
        mismatched = 0
        for qid, entries in by_qid.items():
            if len(entries) != 3:
                mismatched += 1
                print(f"[{g}] qid={qid}: expected 3 records, got {len(entries)}")
                continue
            r0 = entries[0][1]
            key = (r0.get("db_id"), (r0.get("query") or "").strip())
            trace = decomp_by_key.get(key, [])
            if len(trace) < 3:
                mismatched += 1
                print(f"[{g}] qid={qid}: only {len(trace)} trace rows for {key}")
                continue
            for (i, r), tr in zip(entries, trace[-3:]):
                final_sql = parse_sql_from_string(tr.get("response", ""))
                ex = evaluate_ex(final_sql, r.get("gold_sql") or "",
                                 r.get("db_id") or "", dataset="spider")
                rows[i]["ex_match"] = ex
                rows[i]["_b4_ex_fixed"] = True
                fixed += 1

        print(f"[{g}] fixed={fixed} records, mismatched_qids={mismatched}")
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        # Recompute summary.
        by_method = defaultdict(list)
        for r in rows:
            if not r.get("error"):
                by_method[r["method"]].append(r)
        summary = {}
        for method in METHOD_ORDER:
            rs = by_method[method]
            if not rs:
                continue
            ex_vals = [r for r in rs if r.get("ex_match") is not None]
            ex = sum(1 for r in ex_vals if r["ex_match"]) / max(len(ex_vals), 1)
            all_v = [r.get("n_violations_before") or 0 for r in rs]
            all_s = [r.get("n_subqueries") or 0 for r in rs]
            svr = sum(all_v) / max(sum(all_s), 1)
            sar = compute_sar(sum(all_v), sum(r.get("n_violations_after") or 0 for r in rs))
            sscore = compute_sscore(ex, svr)
            deg = Counter(r.get("degradation_level") for r in rs)
            summary[method] = {
                "n": len(rs), "EX": round(ex, 4), "S_VR": round(svr, 4),
                "S_AR": round(sar, 4), "S_Score": round(sscore, 4),
                "degradation": dict(deg),
            }
        with open(os.path.join(R_DIR, f"rq2_{g}_summary.json"), "w",
                  encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"[{g}] summary recomputed:")
        for m in METHOD_ORDER:
            if m in summary:
                s = summary[m]
                print(f"    {m}: n={s['n']} EX={s['EX']:.4f} S_VR={s['S_VR']:.4f} "
                      f"S_AR={s['S_AR']:.4f} deg={s['degradation']}")

    print("DONE")


if __name__ == "__main__":
    main()
