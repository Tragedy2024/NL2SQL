"""Recover EX from existing JSONL — no LLM calls, just SQLite execution."""
import json, os, sys, sqlite3
from collections import defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_BASE, 'src')
if _src not in sys.path:
    sys.path.insert(0, _src)

from experiments.common import SPIDER_DB_PATH, BIRD_DB_PATH, RESULTS_DIR


def recover_file(filepath, dataset):
    db_base = SPIDER_DB_PATH if dataset == 'spider' else BIRD_DB_PATH

    results = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))

    updated = 0
    for r in results:
        if r.get('ex_match') is not None and r.get('pred_sql', '').strip():
            continue

        sqs = r.get('sub_queries', [])
        if sqs:
            r['pred_sql'] = sqs[-1].get('sql', '')

        gold = r.get('gold_sql', '')
        pred = r.get('pred_sql', '')
        db_id = r.get('db_id', '')

        if pred and gold and db_id:
            db_path = os.path.join(db_base, db_id, f'{db_id}.sqlite')
            try:
                conn = sqlite3.connect(db_path)
                conn.text_factory = lambda b: b.decode(errors="ignore")
                c = conn.cursor()
                c.execute(pred)
                pr = c.fetchall()
                c.execute(gold)
                gr = c.fetchall()
                c.close()
                conn.close()
                r['ex_match'] = set(pr) == set(gr)
                updated += 1
            except Exception:
                r['ex_match'] = False
                updated += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    by_method = defaultdict(lambda: {'ok': 0, 'n': 0})
    for r in results:
        m = r.get('method', '?')
        by_method[m]['n'] += 1
        if r.get('ex_match'):
            by_method[m]['ok'] += 1

    print(f'\n{os.path.basename(filepath)}')
    print(f'  Updated: {updated}')
    print('  EX by method:')
    for m in sorted(by_method.keys()):
        d = by_method[m]
        ok = d['ok']
        n = d['n']
        print('    {}: {}/{} ({:.0f}%)'.format(m, ok, n, ok / max(n, 1) * 100))


if __name__ == '__main__':
    files = [
        # RQ1
        (os.path.join(RESULTS_DIR, 'rq1', 'rq1_bird_fewshot_results.jsonl'), 'bird'),
        (os.path.join(RESULTS_DIR, 'rq1', 'rq1_bird_zeroshot_results.jsonl'), 'bird'),
        (os.path.join(RESULTS_DIR, 'rq1', 'rq1_spider_fewshot_results.jsonl'), 'spider'),
        (os.path.join(RESULTS_DIR, 'rq1', 'rq1_spider_zeroshot_results.jsonl'), 'spider'),
        # RQ2
        (os.path.join(RESULTS_DIR, 'rq2', 'rq2_bird_fewshot_results.jsonl'), 'bird'),
        (os.path.join(RESULTS_DIR, 'rq2', 'rq2_bird_zeroshot_results.jsonl'), 'bird'),
        (os.path.join(RESULTS_DIR, 'rq2', 'rq2_spider_fewshot_results.jsonl'), 'spider'),
        (os.path.join(RESULTS_DIR, 'rq2', 'rq2_spider_zeroshot_results.jsonl'), 'spider'),
    ]
    for fpath, ds in files:
        if os.path.exists(fpath):
            recover_file(fpath, ds)
