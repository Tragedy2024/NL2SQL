# -*- coding: utf-8 -*-
"""Overhead measurement for the security component.

Protocol: replay 200 BIRD cached plans from
results/rq1 sequentially in a single process; report the mean per-record
time of (a) audit-only and (b) the full audit+rewrite+degradation pipeline.
Zero LLM calls — rerun_security operates on the cached sub-query plans.

Run:  python experiments/measure_overhead.py
"""
import os
import sys
import time

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from offline_rerun import iter_jsonl, rerun_security  # noqa: E402
from common import RESULTS_DIR  # noqa: E402

N = 200
WARMUP = 10
SRC = os.path.join(RESULTS_DIR, "rq1", "rq1_bird_fewshot_results.jsonl")


def load_records(path, n):
    recs = []
    for rec in iter_jsonl(path):
        if rec.get("question_id") is not None and rec.get("sub_queries"):
            recs.append(rec)
        if len(recs) >= n + WARMUP:
            break
    return recs[:WARMUP], recs[WARMUP:WARMUP + n]


def measure(records, rewrite, degradation):
    t0 = time.perf_counter()
    for rec in records:
        rerun_security(rec, rewrite=rewrite, degradation=degradation)
    return (time.perf_counter() - t0) / len(records) * 1000


def main():
    warm, recs = load_records(SRC, N)
    # warmup (both configs)
    for rec in warm:
        rerun_security(rec, rewrite=False, degradation=False)
        rerun_security(rec, rewrite=True, degradation=True)
    audit_ms = measure(recs, rewrite=False, degradation=False)
    full_ms = measure(recs, rewrite=True, degradation=True)
    print(f"records: {len(recs)} (warmup {len(warm)})")
    print(f"audit-only: {audit_ms:.1f} ms/record")
    print(f"full pipeline: {full_ms:.1f} ms/record")
    print(f"<20ms claim: {'holds' if max(audit_ms, full_ms) < 20 else 'VIOLATED'}")


if __name__ == "__main__":
    main()
