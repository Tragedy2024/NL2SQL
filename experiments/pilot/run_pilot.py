"""
Pilot Study — 10% sample across BIRD + Spider × fewshot + zeroshot.

Runs MAC-SQL (B1) × 1 rep per query, skip-refiner.
Audits every decomposition across 3 dimensions.

Output:
  results/pilot/pilot_{dataset}_{mode}_results.jsonl  (4 files)
"""
import json, os, sys, time, argparse
from collections import Counter, defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_src = os.path.join(_BASE, 'src')
_vendor = os.path.join(_BASE, 'vendor', 'MAC-SQL')
for _p in [_src, _vendor]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from experiments.common import (
    QuerysetLoader, BaselineResult, get_dataset_config,
    run_audit_pipeline, save_results,
)
from baselines.mac_sql import MACSQLVanilla

SAMPLE_FRAC = 0.10
DATASETS = ['bird', 'spider']
MODES = ['fewshot', 'zeroshot']


def run_pilot(dataset: str, mode: str, fresh: bool = False):
    loader = QuerysetLoader(dataset=dataset)
    cfg = get_dataset_config(dataset)
    all_queries = loader.get_queries(n=None, complex_only=False, seed=42,
                                     difficulty_balance=False)
    n_sample = max(30, int(len(all_queries) * SAMPLE_FRAC))
    queries = loader.get_queries(n=n_sample, complex_only=False, seed=42,
                                 difficulty_balance=True)

    output_file = os.path.join(_BASE, 'results', 'pilot',
                               f'pilot_{dataset}_{mode}_results.jsonl')
    if fresh and os.path.exists(output_file):
        os.remove(output_file)

    dbs = sorted(set(q['db_id'] for q in queries))
    print(f"\n{'='*60}")
    print(f"  Pilot [{dataset}/{mode}]")
    print(f"  Sample: {len(queries)}/{len(all_queries)} queries × 1 rep")
    print(f"  Databases: {len(dbs)}")
    print(f"{'='*60}")

    baseline = MACSQLVanilla(
        data_path=cfg["db_path"], tables_json_path=cfg["tables_json"],
        model_name="gpt-4o", dataset_name=dataset, lazy=True,
    )

    results = []
    for qi, item in enumerate(queries):
        qid = item['question_id']
        db = item['db_id']
        qtext = (item.get('question', '') or '')[:80]
        t0 = time.time()
        output = baseline.decompose(item, skip_refiner=True, mode=mode)
        dt = time.time() - t0

        result = BaselineResult(
            method=f"pilot_{mode}",
            question_id=qid, db_id=db,
            difficulty=item.get('difficulty', 'unknown'),
            query=item.get('question', ''),
            gold_sql=item.get('SQL', ''),
            n_subqueries=len(output['sub_queries']),
            sub_queries=output['sub_queries'],
            pred_sql=output['pred_sql'],
            error=output.get('error'),
            elapsed_seconds=dt,
        )

        if output['sub_queries'] and not output.get('error'):
            sqs = [{'id': sq['id'], 'sql': sq['sql']}
                   for sq in output['sub_queries']]
            v_b, v_a, n_rw, lev, msg, ex, sub_res = run_audit_pipeline(
                sqs, item['db_id'], output['pred_sql'], item.get('SQL', '')
            )
            result.n_violations_before = v_b
            result.n_violations_after = v_a
            result.n_rewrites = n_rw
            result.degradation_level = lev
            result.degradation_message = msg
            result.ex_match = ex
            result.sub_results = sub_res
            print(f"  [{qi+1}/{len(queries)}] [{qid}] {db}: "
                  f"V:{v_b}→{v_a} RW:{n_rw} {lev} EX={ex} {dt:.0f}s")
        elif output.get('error'):
            print(f"  [{qi+1}/{len(queries)}] [{qid}] {db}: ERROR — {output['error'][:80]}")
        else:
            print(f"  [{qi+1}/{len(queries)}] [{qid}] {db}: no sub-q, {dt:.0f}s")

        results.append(result)

    save_results(results, output_file)
    return results, output_file


def summarize(results, dataset: str, mode: str, outfile: str):
    valid = [r for r in results if not r.error]
    n_q = len(set(r.question_id for r in results))
    total_subq = sum(r.n_subqueries for r in valid)
    total_v = sum(r.n_violations_before for r in valid)
    total_va = sum(r.n_violations_after for r in valid)
    svr = total_v / max(total_subq, 1) * 100

    print(f"\n  [{dataset}/{mode}]")
    print(f"    {n_q} queries, {total_subq} sub-q")
    print(f"    S-VR: {total_v}/{total_subq} ({svr:.1f}%)  →  {total_va} after rewrite")
    print(f"    Degradation: {dict(Counter(r.degradation_level for r in results))}")
    print(f"    Results: {outfile}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fresh', action='store_true')
    args = parser.parse_args()

    all_data = {}

    for dataset in DATASETS:
        for mode in MODES:
            results, outfile = run_pilot(dataset, mode, fresh=args.fresh)
            all_data[(dataset, mode)] = results
            summarize(results, dataset, mode, outfile)

    # Cross comparison
    print(f"\n{'='*60}")
    print(f"  COMPARISON")
    print(f"{'='*60}")
    print(f"  {'Dataset/Mode':<25} {'S-VR':>10} {'Sub-Q':>8}")
    print(f"  {'-'*25} {'-'*10} {'-'*8}")
    for (ds, mode), results in all_data.items():
        valid = [r for r in results if not r.error]
        total_subq = sum(r.n_subqueries for r in valid)
        total_v = sum(r.n_violations_before for r in valid)
        svr = total_v / max(total_subq, 1) * 100
        print(f"  {ds}/{mode:<25} {svr:>9.1f}% {total_subq:>8}")


if __name__ == "__main__":
    main()
