"""
Offline B0-Q / B3-Q cells for the QSG generalization matrix (zero LLM).

B0-Q: measurement-only audit (rewrite=False, degradation=False) on the
      cached QSG decomposition plans — violations counted, no intervention.
B3-Q: post-hoc column filter on the cached QSG plans (executes SQL locally).

Cached plans come from results/rq2/rq2_{dataset}_{mode}_ours_cache.jsonl
(the same plans B5/B6 were built on).  Records are appended to the standard
result files with method names "B0-Q" / "B3-Q", one record per seed
(3 per query, mirroring the B5/B6 layout).

Usage:
  python experiments/rq2/run_qsg_offline_cells.py --dataset bird --mode fewshot
  python experiments/rq2/run_qsg_offline_cells.py --all
"""
import argparse
import json
import os
import sqlite3
import sys
import time

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (_BASE, os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from experiments.common import (  # noqa: E402
    BaselineResult, QuerysetLoader, get_dataset_config, run_audit_pipeline,
    append_result, SSA_DIR, evaluate_ex,
)
from baselines.post_hoc_filter import PostHocColumnFilter  # noqa: E402
from ssa.loader import load_ssa  # noqa: E402
from auditor.base import SecurityAuditor  # noqa: E402

SEEDS = [42, 43, 44]
EXEC_TIMEOUT_S = 20  # abort pathological sub-query executions after 20s


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def run_group(dataset: str, mode: str):
    cache_path = os.path.join(
        _BASE, "results", "rq2", f"rq2_{dataset}_{mode}_ours_cache.jsonl")
    results_path = os.path.join(
        _BASE, "results", "rq2", f"rq2_{dataset}_{mode}_results.jsonl")

    if not os.path.exists(cache_path):
        print(f"[{dataset}/{mode}] no cache file, skip")
        return

    cache = {e["question_id"]: e for e in load_jsonl(cache_path)}
    loader = QuerysetLoader(dataset=dataset)
    all_q = loader.get_queries(n=None, complex_only=False, seed=42,
                               difficulty_balance=False)
    n_q = max(30, int(len(all_q) * 0.10))
    queries = loader.get_queries(n=n_q, complex_only=False, seed=42,
                                 difficulty_balance=True)
    by_qid = {q["question_id"]: q for q in queries}
    cfg = get_dataset_config(dataset)
    db_root = cfg["db_path"]

    # Existing -Q records: skip queries already covered (resumable).
    existing = load_jsonl(results_path) if os.path.exists(results_path) else []
    done_b0 = {r["question_id"] for r in existing if r.get("method") == "B0-Q"}
    done_b3 = {r["question_id"] for r in existing if r.get("method") == "B3-Q"}
    print(f"[{dataset}/{mode}] cache={len(cache)} queries, "
          f"B0-Q done={len(done_b0)}, B3-Q done={len(done_b3)}")

    n_new = 0
    for item in queries:
        qid = item["question_id"]
        entry = cache.get(qid)
        if entry is None:
            continue
        if qid in done_b0 and qid in done_b3:
            continue
        print(f"[{dataset}/{mode}] qid={qid} db={item['db_id']} "
              f"(b0_done={qid in done_b0}, b3_done={qid in done_b3})",
              flush=True)

        sqs = [{"id": s.get("id", i), "description": s.get("description", ""),
                "sql": s.get("sql", "")}
               for i, s in enumerate(entry.get("sub_queries") or [])]
        pred_sql = entry.get("pred_sql") or ""
        gold_sql = item.get("SQL", "")
        db_id = item["db_id"]

        if qid not in done_b0:
            v_b, v_a, n_rw, lev, msg, ex, sr = run_audit_pipeline(
                sqs, db_id, pred_sql, gold_sql,
                rewrite=False, degradation=False, dataset=dataset,
            )
            for seed in SEEDS:
                r = BaselineResult(
                    method="B0-Q", question_id=qid, db_id=db_id,
                    difficulty=item.get("difficulty", "unknown"),
                    query=item.get("question", ""), gold_sql=gold_sql,
                )
                r.sub_queries = [dict(s) for s in sqs]
                r.n_subqueries = len(sqs)
                r.pred_sql = pred_sql
                r.n_violations_before = v_b
                r.n_violations_after = v_a
                r.n_rewrites = n_rw
                r.degradation_level = lev
                r.degradation_message = msg
                r.ex_match = ex
                r.sub_results = sr
                r.elapsed_seconds = 0.0
                append_result(r, results_path)
            done_b0.add(qid)
            n_new += 1

        if qid not in done_b3:
            try:
                ssa = load_ssa(db_id, SSA_DIR)
            except FileNotFoundError:
                ssa = None
            phf = PostHocColumnFilter(ssa) if ssa else None
            auditor = SecurityAuditor(ssa) if ssa else None
            db_path = os.path.join(db_root, db_id, f"{db_id}.sqlite")

            total_v_before = 0
            total_v_after = 0
            b3_error = None
            if phf is None or auditor is None:
                b3_error = f"SSA missing for {db_id}"
            else:
                try:
                    conn = sqlite3.connect(db_path)
                    conn.text_factory = lambda b: b.decode(errors="ignore")
                    cur = conn.cursor()
                    # Per-query execution guard: abort any sub-query that
                    # runs longer than EXEC_TIMEOUT_S seconds (pathological
                    # QSG SQL can otherwise spin for minutes/hours).
                    deadline = [time.time()]
                    def _guard():
                        return 1 if time.time() - deadline[0] > EXEC_TIMEOUT_S else 0
                    conn.set_progress_handler(_guard, 50_000)
                    for i, sq in enumerate(sqs):
                        deadline[0] = time.time()
                        # Malformed QSG SQL (empty / unparseable) cannot be
                        # measured or filtered — tolerate each step, never
                        # fail the whole record.
                        try:
                            exposed = phf._count_exposed_columns(sq["sql"])
                        except Exception:
                            continue
                        total_v_before += max(0, exposed)
                        try:
                            down_needs = auditor._compute_downstream_needs(
                                i, sqs)
                        except Exception:
                            down_needs = []
                        try:
                            # Memory guard: the filter's removed-columns
                            # decision only needs the column NAMES, so sample
                            # a handful of rows instead of fetchall-ing large
                            # tables (BIRD DBs can be huge).
                            cur.execute(sq["sql"])
                            sample = cur.fetchmany(5)
                            cols = [d[0] for d in cur.description] \
                                if cur.description else []
                            rs = [dict(zip(cols, row)) for row in sample]
                            filtered, fr = phf.filter_intermediate_result(
                                i, sq["sql"], rs, down_needs)
                        except Exception:
                            continue
                        total_v_after += max(
                            0, exposed - len(fr.removed_columns))
                    cur.close()
                    conn.close()
                except Exception as e:
                    b3_error = str(e)

            ex = evaluate_ex(pred_sql, gold_sql, db_id, dataset=dataset) \
                if pred_sql and gold_sql else None
            for seed in SEEDS:
                r = BaselineResult(
                    method="B3-Q", question_id=qid, db_id=db_id,
                    difficulty=item.get("difficulty", "unknown"),
                    query=item.get("question", ""), gold_sql=gold_sql,
                )
                r.sub_queries = [dict(s) for s in sqs]
                r.n_subqueries = len(sqs)
                r.pred_sql = pred_sql
                r.n_violations_before = total_v_before
                r.n_violations_after = total_v_after
                r.degradation_level = "L0"
                r.ex_match = ex
                if b3_error:
                    r.error = b3_error
                append_result(r, results_path)
            done_b3.add(qid)
            n_new += 1

    print(f"[{dataset}/{mode}] added {n_new} queries' records — DONE")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=None, choices=["bird", "spider"])
    ap.add_argument("--mode", default=None, choices=["fewshot", "zeroshot"])
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    combos = (["bird", "spider"], ["fewshot", "zeroshot"])
    import itertools
    if args.all:
        for ds, mo in itertools.product(*combos):
            run_group(ds, mo)
    elif args.dataset and args.mode:
        run_group(args.dataset, args.mode)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
