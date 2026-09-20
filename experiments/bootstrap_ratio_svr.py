"""
Query-level Bootstrap for RQ1 S-VR — reproduces the frozen-report CIs
and adds the missing inference for the headline "Spider ~= 2x BIRD" claim:

  1. Reproduce the paper's per-group 95% CIs (resample query records,
     recompute sum(violations)/sum(subqueries), 10,000 resamples, seed 42)
     as a sanity check that the resampling口径 matches the frozen report.
  2. Bootstrap 95% CI for the RATIO  SVR(Spider,few) / SVR(BIRD,few).
  3. Bootstrap 95% CI for the DIFFERENCE  SVR(Spider,few) - SVR(BIRD,few),
     plus a two-sided bootstrap p-value.

Per-record (v_i, n_i) comes from re-running the FROZEN audit pipeline in
measurement mode (rewrite=False, degradation=False) on the cached RQ1
plans — the identical code path used by experiments/offline_rerun.py.
No LLM calls.
"""
import copy
import json
import os
import sys
from collections import defaultdict

import numpy as np

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from offline_rerun import iter_jsonl, rerun_security  # noqa: E402
from common import RESULTS_DIR  # noqa: E402

RQ1_FILES = {
    "bird_fewshot": "rq1_bird_fewshot_results.jsonl",
    "bird_zeroshot": "rq1_bird_zeroshot_results.jsonl",
    "spider_fewshot": "rq1_spider_fewshot_results.jsonl",
    "spider_zeroshot": "rq1_spider_zeroshot_results.jsonl",
}
RQ1_DIR = os.path.join(RESULTS_DIR, "rq1")

N_RESAMPLES = 10000
SEED = 42


def load_pairs(group):
    """Return per-query (v, n) pairs via the frozen measurement pipeline.

    Resampling unit is the query (first record kept for queries that
    carry multiple run records), matching the paper's query-level口径.
    """
    path = os.path.join(RQ1_DIR, RQ1_FILES[group])
    by_qid = {}
    for rec in iter_jsonl(path):
        qid = rec.get("question_id")
        if qid is None:
            continue
        if qid in by_qid:
            continue  # keep first record per query (s42)
        r = rerun_security(rec, rewrite=False, degradation=False)
        by_qid[qid] = (r["v_before"], r["n_subqueries"])
    return list(by_qid.values())


def bootstrap_svr(pairs, rng):
    """Resample query records; return array of SVR* = sum(v*)/sum(n*)."""
    pairs = np.asarray(pairs, dtype=float)
    idx = rng.randint(0, len(pairs), size=(N_RESAMPLES, len(pairs)))
    v = pairs[:, 0][idx]
    n = pairs[:, 1][idx]
    return v.sum(axis=1) / n.sum(axis=1)


def ci(x, level=0.95):
    lo, hi = np.percentile(x, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return lo, hi


def main():
    print("Loading per-query (v, n) via frozen measurement pipeline ...")
    pairs = {g: load_pairs(g) for g in RQ1_FILES}
    for g, p in pairs.items():
        tot_v = sum(v for v, _ in p)
        tot_n = sum(n for _, n in p)
        print(f"  {g:15s} queries={len(p):5d}  sum_v={tot_v:4d}  "
              f"sum_n={tot_n:5d}  SVR={100*tot_v/tot_n if tot_n else 0:.4f}%")

    svr_boot = {}
    cirep = {}
    for g in pairs:
        # Fresh RandomState per group so each group's CI uses the same
        # seed-42 stream (matches the frozen report's per-group intervals).
        rng = np.random.RandomState(SEED)
        svr_boot[g] = bootstrap_svr(pairs[g], rng)
        lo, hi = ci(svr_boot[g])
        cirep[g] = (100 * lo, 100 * hi)
        print(f"  {g:15s} reproduced 95% CI: "
              f"[{100*lo:.4f}%, {100*hi:.4f}%]")

    # Difference / ratio: independent resamples for the two groups.
    rng_ratio = np.random.RandomState(SEED)
    svr_boot["bird_fewshot"] = bootstrap_svr(pairs["bird_fewshot"], rng_ratio)
    svr_boot["spider_fewshot"] = bootstrap_svr(pairs["spider_fewshot"], rng_ratio)

    # ---- difference and ratio: Spider/few vs BIRD/few ----
    b = svr_boot["bird_fewshot"]
    s = svr_boot["spider_fewshot"]

    point_b = sum(v for v, _ in pairs["bird_fewshot"]) / sum(
        n for _, n in pairs["bird_fewshot"])
    point_s = sum(v for v, _ in pairs["spider_fewshot"]) / sum(
        n for _, n in pairs["spider_fewshot"])

    diff = s - b
    ratio = np.divide(s, b, out=np.full_like(s, np.nan), where=b > 0)

    lo_d, hi_d = ci(diff)
    lo_r, hi_r = ci(ratio)

    # two-sided bootstrap p-value for H0: SVR_bird = SVR_spider
    p_diff = 2.0 * min(float(np.mean(diff <= 0)), float(np.mean(diff >= 0)))
    p_diff = min(1.0, p_diff)
    # bootstrap p-value for H0: ratio = 1
    p_ratio = 2.0 * min(float(np.mean(ratio <= 1)), float(np.mean(ratio >= 1)))
    p_ratio = min(1.0, p_ratio)

    report = {
        "point_SVR_bird_few_pct": 100 * point_b,
        "point_SVR_spider_few_pct": 100 * point_s,
        "point_ratio_spider_over_bird": point_s / point_b if point_b else None,
        "reproduced_CI_pct": cirep,
        "diff_CI_pct": [100 * lo_d, 100 * hi_d],
        "ratio_CI": [float(lo_r), float(hi_r)],
        "bootstrap_p_diff": float(p_diff),
        "bootstrap_p_ratio_eq1": float(p_ratio),
        "n_resamples": N_RESAMPLES,
        "seed": SEED,
        "fraction_diff_le_0": float(np.mean(diff <= 0)),
        "fraction_ratio_le_1": float(np.mean(ratio <= 1)),
        "fraction_ratio_ge_2": float(np.mean(ratio >= 2)),
    }
    out_path = os.path.join(RESULTS_DIR, "bootstrap_ratio_svr.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n--- Spider/few vs BIRD/few inference ---")
    print(f"point S-VR:   BIRD {100*point_b:.4f}%   "
          f"Spider {100*point_s:.4f}%")
    print(f"point ratio:  {report['point_ratio_spider_over_bird']:.3f}")
    print(f"difference 95% CI (pp): "
          f"[{100*lo_d:.4f}, {100*hi_d:.4f}]   (two-sided bootstrap "
          f"p = {p_diff:.4f})")
    print(f"ratio 95% CI: [{lo_r:.4f}, {hi_r:.4f}]   "
          f"(bootstrap p for ratio=1: {p_ratio:.4f})")
    print(f"P(ratio >= 2) = {report['fraction_ratio_ge_2']:.3f}")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()
