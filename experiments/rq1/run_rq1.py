"""
RQ1 — MAC-SQL Security Audit across datasets × modes.

Runs MAC-SQL on all queries (or --n subset), audits every decomposition.
Supports resume via --fresh / auto-detect.

Output: results/rq1/rq1_{dataset}_{mode}_results.jsonl + summary.json
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
    QuerysetLoader, BaselineResult, SSA_DIR,
    get_dataset_config, run_audit_pipeline,
    append_result, resume_check,
)
from baselines.mac_sql import MACSQLVanilla
from auditor.base import SecurityAuditor, ViolationType, ViolationSeverity
from ssa.loader import load_ssa

N_QUERIES = None  # None = all
N_REPETITIONS = 1  # v2: 1 rep for full-dataset coverage
SEEDS = [42, 43, 44]
DATASETS = ['bird', 'spider']
MODES = ['fewshot', 'zeroshot']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=N_QUERIES)
    parser.add_argument('--reps', type=int, default=N_REPETITIONS)
    parser.add_argument('--db', type=str, default=None)
    parser.add_argument('--fresh', action='store_true')
    args = parser.parse_args()

    for dataset in DATASETS:
        for mode in MODES:
            _run_rq1(dataset, mode, args)


def _run_rq1(dataset: str, mode: str, args):
    output_file = os.path.join(_BASE, 'results', 'rq1',
                               f'rq1_{dataset}_{mode}_results.jsonl')
    summary_file = os.path.join(_BASE, 'results', 'rq1',
                                f'rq1_{dataset}_{mode}_summary.json')

    completed_ids, existing_results, saved = resume_check(output_file)
    if completed_ids and not args.fresh:
        print(f"Resume [{dataset}/{mode}]: {len(completed_ids)} done, skipping")
    elif args.fresh and os.path.exists(output_file):
        os.remove(output_file)
        completed_ids = set()
        existing_results = []

    loader = QuerysetLoader(dataset=dataset)
    cfg = get_dataset_config(dataset)

    if args.db:
        queries = loader.get_by_db(args.db)
    else:
        queries = loader.get_queries(n=args.n, complex_only=False, seed=42,
                                     difficulty_balance=True)

    pending = [q for q in queries if q['question_id'] not in completed_ids]
    skipped = len(queries) - len(pending)

    print(f"\n{'='*60}")
    print(f"  RQ1 [{dataset}/{mode}]")
    print(f"  {len(queries)} queries × {args.reps} reps")
    if skipped:
        print(f"  Skipping {skipped} done, {len(pending)} remaining")
    dbs = sorted(set(q['db_id'] for q in queries))
    print(f"  Databases: {len(dbs)}")
    print(f"{'='*60}")

    baseline = MACSQLVanilla(
        data_path=cfg["db_path"], tables_json_path=cfg["tables_json"],
        model_name="gpt-4o", dataset_name=dataset, lazy=True,
    )

    violation_types = Counter()
    violation_severities = Counter()
    all_results = list(existing_results)

    for qi, item in enumerate(pending):
        qid = item['question_id']
        db = item['db_id']
        print(f"\n[{qi+1}/{len(pending)}] [{qid}] {db}: "
              f"{(item.get('question','') or '')[:80]}...")

        for seed in SEEDS[:args.reps]:
            t0 = time.time()
            output = baseline.decompose(item, skip_refiner=True, mode=mode)
            dt = time.time() - t0

            result = BaselineResult(
                method=f"B1_{mode}_s{seed}",
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
                    sqs, item['db_id']
                )
                result.n_violations_before = v_b
                result.n_violations_after = v_a
                result.n_rewrites = n_rw
                result.degradation_level = lev
                result.sub_results = sub_res

                if v_b > 0:
                    try:
                        ssa = load_ssa(item['db_id'], SSA_DIR)
                        auditor = SecurityAuditor(ssa)
                        for ar in auditor.audit_all(sqs):
                            for v in ar.violations:
                                violation_types[v.type.value] += 1
                                violation_severities[v.severity.value] += 1
                    except FileNotFoundError:
                        pass

            action = f"V:{result.n_violations_before}→{result.n_violations_after}" \
                if output['sub_queries'] else "0 sub-q"
            print(f"  seed{seed}: {result.n_subqueries} sub-q, {action}, "
                  f"RW:{result.n_rewrites}, {result.degradation_level}, {dt:.0f}s")

            all_results.append(result)
            append_result(result, output_file)

    # Summary
    def _g(r, k):
        return r.get(k) if isinstance(r, dict) else getattr(r, k, 0)

    n_q = len(set(_g(r, 'question_id') for r in all_results if not _g(r, 'error')))
    total_subq = sum(_g(r, 'n_subqueries') for r in all_results if not _g(r, 'error'))
    total_v = sum(_g(r, 'n_violations_before') for r in all_results if not _g(r, 'error'))
    svr = total_v / max(total_subq, 1)

    summary = {
        'rq': 'RQ1', 'dataset': dataset, 'mode': mode,
        'n_queries': n_q, 'n_repetitions': args.reps,
        'total_sub_queries': total_subq, 'total_violations': total_v,
        'S_VR': round(svr, 4), 'S_VR_pct': round(svr * 100, 1),
        'violation_types': dict(violation_types),
        'violation_severities': dict(violation_severities),
    }
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n  [{dataset}/{mode}] S-VR: {svr*100:.1f}% ({total_v}/{total_subq})")
    print(f"  Types: {dict(violation_types)}")
    print(f"  Results: {output_file}")


if __name__ == "__main__":
    main()
