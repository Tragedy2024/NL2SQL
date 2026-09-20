"""
Fold B4-Q shard records into the main result files.

The parallel B4-Q run writes each (dataset, mode, offset) shard to its own
file rq2_{dataset}_{mode}_b4q_{offset}.jsonl.  This script appends those
records to rq2_{dataset}_{mode}_results.jsonl (preserving the smoke-test
B4-Q records already there), with a qid-overlap guard, and recomputes the
group summaries.

Usage: python experiments/rq2/merge_b4q_shards.py [group ...]
"""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (os.path.join(_BASE, "src"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from evaluation.metrics import compute_sar, compute_sscore  # noqa: E402

GROUPS = ["bird_fewshot", "bird_zeroshot", "spider_fewshot", "spider_zeroshot"]
METHOD_ORDER = ["B0", "B1", "B2", "B3", "B4", "B0-Q", "B1-Q", "B2-Q", "B3-Q", "B4-Q"]


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main():
    groups = sys.argv[1:] or GROUPS
    for g in groups:
        main_path = os.path.join(
            _BASE, "results", "rq2", f"rq2_{g}_results.jsonl")
        main_rows = load_jsonl(main_path)
        existing_qids = {r["question_id"] for r in main_rows
                         if r.get("method") == "B4-Q"}

        shard_pattern = os.path.join(
            _BASE, "results", "rq2", f"rq2_{g}_b4q_*.jsonl")

        # Collect all B4-Q records (main + shards) and dedupe: keep the LAST
        # 3 records per question_id (historical restarts wrote duplicate
        # full runs into some shard files).
        b4q_main = [r for r in main_rows if r.get("method") == "B4-Q"]
        by_qid = defaultdict(list)
        for r in b4q_main:
            by_qid[r["question_id"]].append(r)
        for shard in sorted(glob.glob(shard_pattern)):
            rows = load_jsonl(shard)
            for r in rows:
                if r.get("method") != "B4-Q":
                    continue
                by_qid[r["question_id"]].append(r)
            print(f"[{g}] read {len(rows)} from {os.path.basename(shard)}")

        deduped = []
        short = []
        for qid, rs in sorted(by_qid.items()):
            keep = rs[-3:]  # last 3 (seed order within a single run)
            if len(keep) < 3:
                short.append((qid, len(keep)))
            deduped.extend(keep)
        print(f"[{g}] unique qids={len(by_qid)}, records={len(deduped)}, "
              f"qids with <3 records={short if short else 'none'}")

        non_b4q = [r for r in main_rows if r.get("method") != "B4-Q"]
        merged = non_b4q + deduped
        with open(main_path, "w", encoding="utf-8") as f:
            for r in merged:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        main_rows = merged
        print(f"[{g}] merged: {len(merged)} lines "
              f"({len(non_b4q)} non-B4-Q + {len(deduped)} B4-Q)")

        # Recompute summary (same口径 as recompute_summaries.py).
        by_m = defaultdict(list)
        for r in main_rows:
            if not r.get("error"):
                by_m[r["method"]].append(r)
        summary = {}
        for m in METHOD_ORDER:
            rs = by_m[m]
            if not rs:
                continue
            ex_vals = [r for r in rs if r.get("ex_match") is not None]
            ex = sum(1 for r in ex_vals if r["ex_match"]) / max(len(ex_vals), 1)
            all_v = [r.get("n_violations_before") or 0 for r in rs]
            all_s = [r.get("n_subqueries") or 0 for r in rs]
            svr = sum(all_v) / max(sum(all_s), 1)
            sar = compute_sar(
                sum(all_v), sum(r.get("n_violations_after") or 0 for r in rs))
            deg = Counter(r.get("degradation_level") for r in rs)
            summary[m] = {
                "n": len(rs), "EX": round(ex, 4), "S_VR": round(svr, 4),
                "S_AR": round(sar, 4),
                "S_Score": round(compute_sscore(ex, svr), 4),
                "degradation": dict(deg),
            }
        with open(os.path.join(_BASE, "results", "rq2", f"rq2_{g}_summary.json"),
                  "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"[{g}] summary recomputed")
        for m in METHOD_ORDER:
            if m in summary:
                s = summary[m]
                print(f"    {m}: n={s['n']} EX={s['EX']:.4f} "
                      f"S_VR={s['S_VR']:.4f} S_AR={s['S_AR']:.4f}")

    print("MERGE DONE")


if __name__ == "__main__":
    main()
