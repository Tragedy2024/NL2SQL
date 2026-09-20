"""
RQ2 — 6-Baseline Comparison across datasets × modes.

B0 (Raw), B1 (+Audit), B2 (+Audit+Rewrite, OURS), B3 (Post-hoc), B4 (+Prompt),
B1-Q (QSG Audit-only), B2-Q (QSG Full).

Output: results/rq2/rq2_{dataset}_{mode}_results.jsonl + summary.json
"""
import json, os, sys, time, sqlite3, argparse
from collections import Counter, defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_src = os.path.join(_BASE, 'src')
_vendor = os.path.join(_BASE, 'vendor', 'MAC-SQL')
for _p in [_BASE, _src, _vendor]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from experiments.common import (
    QuerysetLoader, BaselineResult, SSA_DIR,
    get_dataset_config, run_audit_pipeline, run_ours_forward, ours_divergent,
    save_results, evaluate_ex,
)
from baselines.mac_sql import MACSQLVanilla
from baselines.mac_sql_safe_prompt import MACSQLSafePrompt
from baselines.post_hoc_filter import PostHocColumnFilter
from ssa.loader import load_ssa
from auditor.base import SecurityAuditor
from evaluation.metrics import compute_sar, compute_sscore
from evaluation.statistics import mcnemar_test, bootstrap_ci

ALL_METHODS = ["B0", "B1", "B2", "B3", "B4", "B1-Q", "B2-Q"]
SAMPLE_FRAC = 0.10  # v2: 10% sample for RQ2
N_REPETITIONS = 3
SEEDS = [42, 43, 44]
DATASETS = ['bird', 'spider']
MODES = ['fewshot', 'zeroshot']

# Paper naming ↔ code naming: B0-B6 now match the paper exactly.
METHOD_CONFIGS = {
    # B0: MAC-SQL raw — no security component (measurement only, violations silent)
    "B0": {"type": "mac_sql", "safe_prompt": False, "post_hoc": False,
           "enable_audit": False, "enable_rewrite": False},
    # B1: MAC-SQL + audit only — detects violations but cannot fix → degradation
    "B1": {"type": "mac_sql", "safe_prompt": False, "post_hoc": False,
           "enable_audit": True, "enable_rewrite": False},
    # B2: MAC-SQL + full pipeline — audit + rewrite + degradation (★ OURS)
    "B2": {"type": "mac_sql", "safe_prompt": False, "post_hoc": False,
           "enable_audit": True, "enable_rewrite": True},
    # B3: MAC-SQL + post-hoc filter — reactive masking baseline
    "B3": {"type": "mac_sql", "safe_prompt": False, "post_hoc": True,
           "enable_audit": False, "enable_rewrite": False},
    # B4: MAC-SQL + safe prompt — prompt-injection baseline (full pipeline to measure)
    "B4": {"type": "mac_sql", "safe_prompt": True, "post_hoc": False,
           "enable_audit": True, "enable_rewrite": True},
    # B5: QSG + audit only — generalization appendix
    "B1-Q": {"type": "ours", "enable_audit": True, "enable_rewrite": False},
    # B6: QSG + full pipeline — generalization appendix
    "B2-Q": {"type": "ours", "enable_audit": True, "enable_rewrite": True},
}


def run_method(method, item, mac_sql_vanilla, mac_sql_safe_prompt,
               desc_str, fk_str, dataset, mode, seeds, cfg,
               ours_shared=None):
    """Run one method on one query, return list of BaselineResult per seed."""
    config = METHOD_CONFIGS[method]
    results = []

    for seed in seeds:
        t0 = time.time()
        r = BaselineResult(
            method=method, question_id=item['question_id'],
            db_id=item['db_id'], difficulty=item.get('difficulty', 'unknown'),
            query=item.get('question', ''), gold_sql=item.get('SQL', ''),
        )

        if config["type"] == "mac_sql":
            bl = mac_sql_safe_prompt if config["safe_prompt"] else mac_sql_vanilla
            if config["safe_prompt"]:
                # B4: activate the security prompt only for this decompose call,
                # then restore immediately so B0-B3 stay clean.
                mac_sql_safe_prompt._inject_security_prompt()
                try:
                    output = bl.decompose(item, skip_refiner=True, mode=mode)
                finally:
                    mac_sql_safe_prompt._restore_security_prompt()
            else:
                # Non-B4 methods: make sure no residual patch is active.
                mac_sql_safe_prompt._restore_security_prompt()
                output = bl.decompose(item, skip_refiner=True, mode=mode)
            r.elapsed_seconds = time.time() - t0

            if output.get('error'):
                r.error = output['error']
                results.append(r)
                continue

            r.sub_queries = output['sub_queries']
            r.n_subqueries = len(output['sub_queries'])
            r.pred_sql = output['pred_sql']

            if config["post_hoc"]:
                # B3: execute SQL then filter results
                try:
                    ssa = load_ssa(item['db_id'], SSA_DIR)
                except FileNotFoundError:
                    r.error = f"SSA missing for {item['db_id']}"
                    results.append(r)
                    continue

                phf = PostHocColumnFilter(ssa)
                auditor = SecurityAuditor(ssa)
                sqs = [{'id': sq['id'], 'sql': sq['sql']}
                       for sq in output['sub_queries']]
                db_path = os.path.join(cfg["db_path"], item['db_id'],
                                       f"{item['db_id']}.sqlite")
                total_v_before = 0
                total_v_after = 0

                try:
                    conn = sqlite3.connect(db_path)
                    conn.text_factory = lambda b: b.decode(errors="ignore")
                    cursor = conn.cursor()
                    for i, sq in enumerate(sqs):
                        exposed = phf._count_exposed_columns(sq['sql'])
                        if exposed < 0:
                            exposed = 0
                        total_v_before += exposed
                        down_needs = auditor._compute_downstream_needs(i, sqs)
                        try:
                            cursor.execute(sq['sql'])
                            rows = cursor.fetchall()
                            cols = [d[0] for d in cursor.description] if cursor.description else []
                            rs = [dict(zip(cols, row)) for row in rows]
                        except Exception:
                            rs = []
                        filtered, fr = phf.filter_intermediate_result(i, sq['sql'], rs, down_needs)
                        total_v_after += max(0, exposed - len(fr.removed_columns))
                    cursor.close()
                    conn.close()
                except Exception:
                    pass

                r.n_violations_before = total_v_before
                r.n_violations_after = total_v_after
            else:
                # B0/B1/B2/B4: MAC-SQL with configurable security pipeline
                sqs = [{'id': sq['id'], 'sql': sq['sql']}
                       for sq in output['sub_queries']]
                if sqs:
                    enable_audit = config.get("enable_audit", True)
                    enable_rewrite = config.get("enable_rewrite", True)

                    if not enable_audit:
                        # B0: no security component — measure violations silently
                        # (measurement-only audit: count violations but apply
                        #  no rewrite and no degradation)
                        v_b, v_a, n_rw, lev, msg, ex, sr = run_audit_pipeline(
                            sqs, item['db_id'], output['pred_sql'],
                            item.get('SQL', ''),
                            rewrite=False, degradation=False,
                            dataset=dataset,
                        )
                    else:
                        # B1 (no rewrite) or B2/B4 (full pipeline)
                        v_b, v_a, n_rw, lev, msg, ex, sr = run_audit_pipeline(
                            sqs, item['db_id'], output['pred_sql'],
                            item.get('SQL', ''),
                            rewrite=enable_rewrite, degradation=True,
                            dataset=dataset,
                        )

                    r.n_violations_before = v_b
                    r.n_violations_after = v_a
                    r.n_rewrites = n_rw
                    r.degradation_level = lev
                    r.degradation_message = msg
                    r.ex_match = ex
                    r.sub_results = sr

        elif config["type"] == "ours":
            if ours_shared.get('error'):
                r.error = ours_shared['error']
            else:
                r = ours_divergent(
                    item, ours_shared,
                    enable_audit=config["enable_audit"],
                    enable_rewrite=config["enable_rewrite"],
                    dataset=dataset,
                )
                r.method = method
            r.elapsed_seconds = time.time() - t0

        results.append(r)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=None, help='Override sample size')
    parser.add_argument('--methods', type=str, default=None)
    parser.add_argument('--reps', type=int, default=N_REPETITIONS)
    parser.add_argument('--smoke-test', action='store_true')
    parser.add_argument('--fresh', action='store_true')
    parser.add_argument('--fresh-ours', action='store_true',
                        help='Only clear B1-Q/B2-Q results, keep B0/B1/B2/B3/B4')
    parser.add_argument('--dataset', type=str, default=None,
                        help='Run only this dataset (bird or spider)')
    parser.add_argument('--mode', type=str, default=None,
                        help='Run only this mode (fewshot or zeroshot)')
    args = parser.parse_args()

    methods = [m.strip() for m in args.methods.split(',')] if args.methods else ALL_METHODS
    if args.smoke_test:
        methods = ["B0", "B2", "B2-Q"]

    datasets = [args.dataset] if args.dataset else DATASETS
    modes = [args.mode] if args.mode else MODES

    for dataset in datasets:
        for mode in modes:
            _run_rq2(dataset, mode, methods, args)


def _run_rq2(dataset, mode, methods, args):
    output_file = os.path.join(_BASE, 'results', 'rq2',
                               f'rq2_{dataset}_{mode}_results.jsonl')
    summary_file = os.path.join(_BASE, 'results', 'rq2',
                                f'rq2_{dataset}_{mode}_summary.json')

    if args.fresh and os.path.exists(output_file):
        os.remove(output_file)

    checkpoint_file = output_file + ".b4_checkpoint"
    if args.fresh and os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)

    # --- resume support: queries already checkpointed are skipped on restart ---
    done_qids = set()
    checkpoint_rows = []
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    checkpoint_rows.append(row)
                    done_qids.add(row.get('question_id'))
                except json.JSONDecodeError:
                    continue
        if checkpoint_rows:
            print(f"  [resume] {len(checkpoint_rows)} checkpointed results "
                  f"({len(done_qids)} queries) loaded from {checkpoint_file}")

    # Load existing MAC-SQL baselines when doing fresh-ours (preserve their data)
    all_results = []
    if args.fresh_ours and os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get('method', '') in ('B0', 'B1', 'B2', 'B3', 'B4'):
                    all_results.append(BaselineResult.from_dict(r))

    loader = QuerysetLoader(dataset=dataset)
    cfg = get_dataset_config(dataset)

    if args.smoke_test:
        n_q = 3
    elif args.n:
        n_q = args.n
    else:
        all_q = loader.get_queries(n=None, complex_only=False, seed=42, difficulty_balance=False)
        n_q = max(30, int(len(all_q) * SAMPLE_FRAC))

    queries = loader.get_queries(
        n=n_q, complex_only=False, seed=42, difficulty_balance=True,
    )

    print(f"\n{'='*60}")
    print(f"  RQ2 [{dataset}/{mode}]")
    print(f"  {len(queries)} queries × {len(methods)} methods × {args.reps} reps")
    print(f"{'='*60}")

    seeds = SEEDS[:args.reps]
    mac_sql_vanilla = MACSQLVanilla(
        data_path=cfg["db_path"], tables_json_path=cfg["tables_json"],
        model_name="gpt-4o", dataset_name=dataset, lazy=True,
    )
    mac_sql_safe_prompt = MACSQLSafePrompt(
        data_path=cfg["db_path"], tables_json_path=cfg["tables_json"],
        model_name="gpt-4o", dataset_name=dataset, lazy=True,
    )

    has_ours = any(METHOD_CONFIGS[m]["type"] == "ours" for m in methods)

    # QSG+SQLGen cache: avoids re-running LLM for B5/B6 recomputation
    cache_file = os.path.join(_BASE, 'results', 'rq2',
                              f'rq2_{dataset}_{mode}_ours_cache.jsonl')
    qsg_cache = {}
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    qsg_cache[entry['question_id']] = entry
                except (json.JSONDecodeError, KeyError):
                    continue

    for qi, item in enumerate(queries):
        qid = item['question_id']
        db = item['db_id']
        if qid in done_qids:
            print(f"\n[{qi+1}/{len(queries)}] [{qid}] {db} — SKIP (checkpointed)")
            continue
        print(f"\n[{qi+1}/{len(queries)}] [{qid}] {db}")

        # Get schema for Ours methods + shared decomposition (once for B5/B6)
        desc_str = ""
        fk_str = ""
        ours_shared = None
        if has_ours:
            if qid in qsg_cache:
                cached = qsg_cache[qid]
                ours_shared = {
                    'sub_queries': cached['sub_queries'],
                    'pred_sql': cached['pred_sql'],
                    'ssa': None,  # will be reloaded by ours_divergent
                    'I_score': cached.get('I_score'),
                }
            else:
                b1_out = mac_sql_vanilla.decompose(item, skip_refiner=True, mode=mode)
                desc_str = b1_out.get('desc_str', '')
                fk_str = b1_out.get('fk_str', '')
                try:
                    ours_shared = run_ours_forward(item, desc_str, fk_str)
                except Exception as e:
                    ours_shared = {'error': str(e)}
                if not ours_shared.get('error'):
                    cache_entry = {
                        'question_id': qid,
                        'sub_queries': ours_shared['sub_queries'],
                        'pred_sql': ours_shared['pred_sql'],
                        'I_score': ours_shared.get('I_score'),
                    }
                    with open(cache_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(cache_entry, ensure_ascii=False) + '\n')
                    qsg_cache[qid] = cache_entry

        for method in methods:
            reps = run_method(method, item, mac_sql_vanilla, mac_sql_safe_prompt,
                            desc_str, fk_str,
                            dataset, mode, seeds, cfg, ours_shared=ours_shared)
            for r in reps:
                st = f"V:{r.n_violations_before}→{r.n_violations_after}" if not r.error else "ERR"
                print(f"  {r.method}: {st} RW:{r.n_rewrites} {r.degradation_level}")
                all_results.append(r)

            # Checkpoint this query so a later restart can resume from here.
            with open(checkpoint_file, 'a', encoding='utf-8') as f:
                for r in reps:
                    f.write(json.dumps(r.to_dict(), ensure_ascii=False) + '\n')

    # Fold checkpointed rows back in so the final file contains the whole block.
    if checkpoint_rows:
        all_results = [BaselineResult.from_dict(r) for r in checkpoint_rows] + all_results

    save_results(all_results, output_file)
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)

    # Summary
    by_method = defaultdict(list)
    for r in all_results:
        if not r.error:
            by_method[r.method].append(r)

    summary = {}
    for method in methods:
        rs = by_method[method]
        if not rs:
            continue
        ex_vals = [r for r in rs if r.ex_match is not None]
        ex = sum(1 for r in ex_vals if r.ex_match) / max(len(ex_vals), 1)
        all_v = [r.n_violations_before for r in rs]
        all_s = [r.n_subqueries for r in rs]
        svr = sum(all_v) / max(sum(all_s), 1)
        sar = compute_sar(sum(r.n_violations_before for r in rs),
                          sum(r.n_violations_after for r in rs))
        sscore = compute_sscore(ex, svr)
        deg = Counter(r.degradation_level for r in rs)
        summary[method] = {
            'n': len(rs), 'EX': round(ex, 4), 'S_VR': round(svr, 4),
            'S_AR': round(sar, 4), 'S_Score': round(sscore, 4),
            'degradation': dict(deg),
        }

    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n  [{dataset}/{mode}]")
    print(f"  {'M':>6} {'EX':>8} {'S-VR':>8} {'S-AR':>8} {'S-Score':>8}")
    for method in sorted(summary.keys()):
        s = summary[method]
        print(f"  {method:>6} {s['EX']:>8.3f} {s['S_VR']:>8.3f} "
              f"{s['S_AR']:>8.3f} {s['S_Score']:>8.3f}")

    # McNemar B2 (MAC-SQL full) vs B6 (QSG full) — SQL generation quality comparison
    b2_rs = by_method.get("B2", [])
    b6_rs = by_method.get("B2-Q", [])
    common_qids = {r.question_id for r in b2_rs if r.ex_match is not None} & \
                  {r.question_id for r in b6_rs if r.ex_match is not None}
    if common_qids:
        b2_ex = [next(r for r in b2_rs if r.question_id == qid).ex_match
                 for qid in sorted(common_qids)]
        b6_ex = [next(r for r in b6_rs if r.question_id == qid).ex_match
                 for qid in sorted(common_qids)]
        if len(b2_ex) == len(b6_ex) and b2_ex:
            mc = mcnemar_test(b2_ex, b6_ex)
            print(f"  B2 vs B2-Q McNemar (n={len(b2_ex)}): p={mc['p_value']}")

    # Ablation: B0 vs B2 (does the security component change anything?)
    b0_rs = by_method.get("B0", [])
    if b0_rs and b2_rs:
        b0_v = sum(r.n_violations_before for r in b0_rs)
        b2_va = sum(r.n_violations_after for r in b2_rs)
        print(f"  Ablation: B0 silent violations={b0_v} → B2 residual={b2_va} "
              f"(S-AR={(b0_v-b2_va)/max(b0_v,1)*100:.0f}%)")

    print(f"  Results: {output_file}")


if __name__ == "__main__":
    main()