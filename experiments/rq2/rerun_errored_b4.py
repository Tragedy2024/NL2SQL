"""
Re-run B4 for queries whose B4 records carry an error.

The earlier failure-loop phase (before the log-contention fix) wrote
error records into the checkpoints, and the resume logic treated them as
done.  This script finds errored B4 records in a merged result file and
re-generates exactly those queries (3 seeds each) with the fixed code,
then patches the records back in place.

Usage:
  python experiments/rq2/rerun_errored_b4.py --dataset bird --mode zeroshot
  python experiments/rq2/rerun_errored_b4.py --dataset spider --mode zeroshot

Resumable: completed query ids are stored in
results/rq2/repair_{dataset}_{mode}.checkpoint.
"""
import argparse
import json
import os
import sys

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (_BASE, os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments"),
           os.path.join(_BASE, "vendor", "MAC-SQL")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from experiments.common import (  # noqa: E402
    BaselineResult, QuerysetLoader, get_dataset_config, run_audit_pipeline,
)
from baselines.mac_sql_safe_prompt import MACSQLSafePrompt  # noqa: E402

SEEDS = [42, 43, 44]


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, choices=["bird", "spider"])
    ap.add_argument("--mode", required=True, choices=["fewshot", "zeroshot"])
    args = ap.parse_args()

    results_file = os.path.join(
        _BASE, "results", "rq2", f"rq2_{args.dataset}_{args.mode}_results.jsonl")
    ckpt_file = os.path.join(
        _BASE, "results", "rq2", f"repair_{args.dataset}_{args.mode}.checkpoint")

    rows = load_jsonl(results_file)

    # Errored B4 records, grouped by question_id (file order == seed order).
    errored = {}
    for i, r in enumerate(rows):
        if r.get("method") == "B4" and r.get("error"):
            errored.setdefault(r.get("question_id"), []).append(i)
    qids = list(errored.keys())
    if not qids:
        print("no errored B4 records — nothing to do")
        return

    done = set()
    if os.path.exists(ckpt_file):
        with open(ckpt_file, encoding="utf-8") as f:
            done = {json.loads(l).get("qid") for l in f if l.strip()}

    loader = QuerysetLoader(dataset=args.dataset)
    all_q = loader.get_queries(n=None, complex_only=False, seed=42,
                               difficulty_balance=False)
    n_q = max(30, int(len(all_q) * 0.10))
    queries = loader.get_queries(n=n_q, complex_only=False, seed=42,
                                 difficulty_balance=True)
    by_qid = {q["question_id"]: q for q in queries}

    cfg = get_dataset_config(args.dataset)
    bl = MACSQLSafePrompt(
        data_path=cfg["db_path"], tables_json_path=cfg["tables_json"],
        model_name="gpt-4o", dataset_name=args.dataset, lazy=True,
    )

    print(f"[{args.dataset}/{args.mode}] {len(qids)} queries to repair "
          f"({len(done)} already done)")

    for n, qid in enumerate(qids, 1):
        if qid in done:
            continue
        item = by_qid.get(qid)
        if item is None:
            print(f"qid {qid}: not found in query set, skip")
            continue
        indices = errored[qid]
        print(f"[{n}/{len(qids)}] qid={qid} ({len(indices)} seeds)")

        new_records = []
        for seed in SEEDS:
            r = BaselineResult(
                method="B4",
                question_id=item["question_id"],
                db_id=item["db_id"],
                difficulty=item.get("difficulty", "unknown"),
                query=item.get("question", ""),
                gold_sql=item.get("SQL", ""),
            )
            bl._inject_security_prompt()
            try:
                output = bl.decompose(item, skip_refiner=True, mode=args.mode)
            finally:
                bl._restore_security_prompt()

            if output.get("error"):
                r.error = output["error"]
                new_records.append(r)
                continue

            r.sub_queries = output["sub_queries"]
            r.n_subqueries = len(output["sub_queries"])
            r.pred_sql = output["pred_sql"]
            sqs = [{"id": sq["id"], "sql": sq["sql"]}
                   for sq in output["sub_queries"]]
            if sqs:
                v_b, v_a, n_rw, lev, msg, ex, sr = run_audit_pipeline(
                    sqs, item["db_id"], output["pred_sql"], item.get("SQL", ""),
                    rewrite=True, degradation=True, dataset=args.dataset,
                )
                r.n_violations_before = v_b
                r.n_violations_after = v_a
                r.n_rewrites = n_rw
                r.degradation_level = lev
                r.degradation_message = msg
                r.ex_match = ex
                r.sub_results = sr
            new_records.append(r)

        # Replace the errored records in place (same count).
        if len(new_records) != len(indices):
            print(f"  WARNING: {len(new_records)} new vs {len(indices)} old — skip")
            continue
        for i, rec in zip(indices, new_records):
            rows[i] = rec.to_dict()

        with open(results_file, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(ckpt_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"qid": qid}) + "\n")
        done.add(qid)

    remaining = [q for q in qids if q not in done]
    print(f"done: {len(done)}/{len(qids)}"
          + (f", still errored: {remaining}" if remaining else " — all repaired"))


if __name__ == "__main__":
    main()
