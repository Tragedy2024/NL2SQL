"""
B4-Q cell: QSG + safety prompt + full security pipeline.

Parallel to MAC-SQL's B4 (safe prompt + full pipeline behind it), but the
prompt is injected into the QSG graph-generation and SQL-generation system
prompts (src/qsg/safe_prompt.py) and the QSG generation is re-run per seed
with the patched prompts.

Protocol (mirrors run_rq2's QSG path):
  - same 10% sampling (seed 42)
  - desc_str/fk_str obtained once per query from MAC-SQL vanilla decompose
    (same as the B5/B6 generation protocol)
  - per seed: inject → run_ours_forward (fresh QSG plans) → restore
    → run_audit_pipeline(rewrite=True, degradation=True)  [full pipeline]
  - records appended to rq2_{dataset}_{mode}_results.jsonl as method "B4-Q"

Resumable via results/rq2/b4q_{dataset}_{mode}_{offset}.checkpoint (one qid per
line).  Each (dataset, mode, offset) shard writes its OWN result file
(rq2_{dataset}_{mode}_b4q_{offset}.jsonl) so multiple shards of the same
group can run in parallel without file contention; a merge step at the end
folds them into the main result file.

Per-database desc/fk caching: the schema description is obtained once per
database (31 databases total) instead of once per query, and cached in
results/rq2/b4q_desc_fk_{dataset}_{offset}.json.

Usage:
  python experiments/rq2/run_b4q.py --dataset bird --mode zeroshot
  python experiments/rq2/run_b4q.py --dataset bird --mode zeroshot --limit 2
  python experiments/rq2/run_b4q.py --dataset bird --mode zeroshot --offset 77
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
    run_ours_forward, append_result,
)
from baselines.mac_sql import MACSQLVanilla  # noqa: E402
from qsg.safe_prompt import inject_qsg_safe_prompt, restore_qsg_safe_prompt  # noqa: E402

SEEDS = [42, 43, 44]


def load_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, choices=["bird", "spider"])
    ap.add_argument("--mode", required=True, choices=["fewshot", "zeroshot"])
    ap.add_argument("--limit", type=int, default=None,
                    help="Only process the first N queries (smoke test)")
    ap.add_argument("--offset", type=int, default=0,
                    help="Skip the first N queries (parallel sharding)")
    args = ap.parse_args()

    results_path = os.path.join(
        _BASE, "results", "rq2", f"rq2_{args.dataset}_{args.mode}_results.jsonl")
    shard_path = os.path.join(
        _BASE, "results", "rq2",
        f"rq2_{args.dataset}_{args.mode}_b4q_{args.offset}.jsonl")
    ckpt_path = os.path.join(
        _BASE, "results", "rq2",
        f"b4q_{args.dataset}_{args.mode}_{args.offset}.checkpoint")
    desc_cache_path = os.path.join(
        _BASE, "results", "rq2",
        f"b4q_desc_fk_{args.dataset}_{args.offset}.json")

    loader = QuerysetLoader(dataset=args.dataset)
    all_q = loader.get_queries(n=None, complex_only=False, seed=42,
                               difficulty_balance=False)
    n_q = max(30, int(len(all_q) * 0.10))
    queries = loader.get_queries(n=n_q, complex_only=False, seed=42,
                                 difficulty_balance=True)
    queries = queries[args.offset:]
    if args.limit:
        queries = queries[:args.limit]

    done = set()
    if os.path.exists(ckpt_path):
        done = {l["qid"] for l in load_jsonl(ckpt_path)}
    existing_b4q = {r["question_id"] for r in load_jsonl(results_path)
                    if r.get("method") == "B4-Q"}
    done |= existing_b4q
    done |= {r["question_id"] for r in load_jsonl(shard_path)
             if r.get("method") == "B4-Q"}

    # Per-database desc/fk cache (schema description is db-level).
    desc_cache = {}
    if os.path.exists(desc_cache_path):
        with open(desc_cache_path, encoding="utf-8") as f:
            try:
                desc_cache = json.load(f)
            except json.JSONDecodeError:
                desc_cache = {}

    cfg = get_dataset_config(args.dataset)
    vanilla = MACSQLVanilla(
        data_path=cfg["db_path"], tables_json_path=cfg["tables_json"],
        model_name="gpt-4o", dataset_name=args.dataset, lazy=True,
    )

    print(f"[{args.dataset}/{args.mode}@{args.offset}] {len(queries)} queries, "
          f"{len(done)} already done", flush=True)

    for n, item in enumerate(queries, 1):
        qid = item["question_id"]
        if qid in done:
            print(f"[{n}/{len(queries)}] qid={qid} — skip (done)")
            continue
        print(f"[{n}/{len(queries)}] qid={qid} db={item['db_id']}", flush=True)

        # desc/fk once per database (cached; 31 DBs total).
        if item["db_id"] not in desc_cache:
            out = vanilla.decompose(item, skip_refiner=True, mode=args.mode)
            if out.get("error"):
                print(f"  desc/fk decompose failed: {out['error']}")
                desc_str, fk_str = "", ""
            else:
                desc_str = out.get("desc_str", "")
                fk_str = out.get("fk_str", "")
            desc_cache[item["db_id"]] = {"desc_str": desc_str,
                                         "fk_str": fk_str}
            with open(desc_cache_path, "w", encoding="utf-8") as f:
                json.dump(desc_cache, f, ensure_ascii=False)
        else:
            entry = desc_cache[item["db_id"]]
            desc_str, fk_str = entry["desc_str"], entry["fk_str"]

        new_records = []
        for seed in SEEDS:
            inject_qsg_safe_prompt()
            try:
                shared = run_ours_forward(item, desc_str, fk_str)
            finally:
                restore_qsg_safe_prompt()

            r = BaselineResult(
                method="B4-Q", question_id=qid, db_id=item["db_id"],
                difficulty=item.get("difficulty", "unknown"),
                query=item.get("question", ""), gold_sql=item.get("SQL", ""),
            )
            if shared.get("error"):
                r.error = shared["error"]
                new_records.append(r)
                continue

            sqs = [{"id": s.get("id", i), "sql": s.get("sql", "")}
                   for i, s in enumerate(shared.get("sub_queries") or [])]
            r.sub_queries = [dict(s) for s in shared.get("sub_queries") or []]
            r.n_subqueries = len(sqs)
            r.pred_sql = shared.get("pred_sql", "")
            r.I_score = shared.get("I_score", 0.0)
            if sqs:
                v_b, v_a, n_rw, lev, msg, ex, sr = run_audit_pipeline(
                    sqs, item["db_id"], r.pred_sql, item.get("SQL", ""),
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

        for rec in new_records:
            append_result(rec, shard_path)
        with open(ckpt_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"qid": qid}) + "\n")
        done.add(qid)

    print(f"[{args.dataset}/{args.mode}] DONE: {len(done)}/{len(queries)} queries")


if __name__ == "__main__":
    main()
