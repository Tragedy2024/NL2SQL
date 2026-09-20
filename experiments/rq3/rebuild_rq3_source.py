"""
Rebuild fresh per-record B6 results for RQ3 with the CURRENT code.

The results/rq2/*.jsonl degradation fields were written by the pre-fix
code; this script recomputes the B6 records (QSG full pipeline) on the
cached plans with the current auditor/rewrite/degradation implementation
(zero LLM calls) and appends the P1-1 blocked-injection degradation cases
as constructed samples for the human evaluation.

Usage:
    python experiments/rq3/rebuild_rq3_source.py
Output:
    results/rq3/rq3_source_records.jsonl
"""
import copy
import json
import os
import sys

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (os.path.join(_BASE, 'src'), os.path.join(_BASE, 'experiments')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from common import RESULTS_DIR, run_audit_pipeline  # noqa: E402

OUT_FILE = os.path.join(_BASE, 'results', 'rq3', 'rq3_source_records.jsonl')
BLOCKED_RESULTS = os.path.join(
    _BASE, 'results', 'rq3', 'blocked_injection_results.json')

GROUPS = [
    ('rq2_bird_fewshot_results.jsonl', 'B6'),
    ('rq2_bird_zeroshot_results.jsonl', 'B6'),
    ('rq2_spider_fewshot_results.jsonl', 'B6'),
    ('rq2_spider_zeroshot_results.jsonl', 'B6'),
]


def main():
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    total = 0
    with open(OUT_FILE, 'w', encoding='utf-8') as out:
        for filename, method in GROUPS:
            path = os.path.join(RESULTS_DIR, 'rq2', filename)
            print(f'[{filename}]')
            for line in open(path, encoding='utf-8'):
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get('method') != method:
                    continue
                sqs = copy.deepcopy(rec.get('sub_queries') or [])
                if not sqs:
                    continue
                vb, va, nrw, lv, msg, ex, subr = run_audit_pipeline(
                    sqs, rec['db_id'], rewrite=True, degradation=True)
                out.write(json.dumps({
                    'method': method,
                    'source': 'offline_rerun',
                    'question_id': rec.get('question_id'),
                    'db_id': rec.get('db_id'),
                    'query': (rec.get('query') or '')[:200],
                    'gold_sql': rec.get('gold_sql', ''),
                    'n_subqueries': len(sqs),
                    'sub_queries': sqs,
                    'n_violations_before': vb,
                    'n_violations_after': va,
                    'n_rewrites': nrw,
                    'degradation_level': lv,
                    'degradation_message': msg,
                    'error': None,
                }, ensure_ascii=False) + '\n')
                total += 1
        # P1-1 constructed blocked-injection degradation cases
        if os.path.exists(BLOCKED_RESULTS):
            constructed = json.load(open(BLOCKED_RESULTS, encoding='utf-8'))
            for c in constructed:
                out.write(json.dumps({
                    'method': 'B6-constructed',
                    'source': 'p1_1_blocked_injection',
                    'question_id': c.get('question_id'),
                    'db_id': c.get('db_id'),
                    'query': c.get('query', ''),
                    'gold_sql': c.get('gold_sql', ''),
                    'n_subqueries': c.get('n_subqueries', 0),
                    'sub_queries': c.get('sub_queries', []),
                    'n_violations_before': c.get('v_before', 0),
                    'n_violations_after': c.get('v_after', 0),
                    'degradation_level': c.get('degradation_level'),
                    'degradation_message': c.get('message', ''),
                    'error': None,
                    'injection_form': c.get('form'),
                }, ensure_ascii=False) + '\n')
                total += 1
            print(f'  + {len(constructed)} constructed blocked-injection cases')
    print(f'\n[OK] {total} records -> {OUT_FILE}')


if __name__ == '__main__':
    main()
