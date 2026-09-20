"""
Recompute per-group summaries from the merged result files,
including the QSG parallel cells (B0-Q / B3-Q / B4-Q).

Same口径 as run_rq2's summary block + merge_b4_rerun.py.

Usage:
  python experiments/rq2/recompute_summaries.py [group ...]
  # groups: bird_fewshot bird_zeroshot spider_fewshot spider_zeroshot
"""
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


def main():
    groups = sys.argv[1:] or GROUPS
    for g in groups:
        path = os.path.join(_BASE, "results", "rq2", f"rq2_{g}_results.jsonl")
        rows = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
        by_m = defaultdict(list)
        for r in rows:
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
                "S_AR": round(sar, 4), "S_Score": round(compute_sscore(ex, svr), 4),
                "degradation": dict(deg),
            }
        with open(os.path.join(_BASE, "results", "rq2", f"rq2_{g}_summary.json"),
                  "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"== {g} ==")
        for m in METHOD_ORDER:
            if m in summary:
                s = summary[m]
                print(f"  {m}: n={s['n']} EX={s['EX']:.4f} S_VR={s['S_VR']:.4f} "
                      f"S_AR={s['S_AR']:.4f} deg={s['degradation']}")


if __name__ == "__main__":
    main()
