"""
SQLite execution tester — standalone script to verify SQL generation accuracy.

Reads any RQ1/RQ2 JSONL file, extracts pred_sql and gold_sql, tests against SQLite.
No LLM calls, pure database execution. Useful for debugging EX=0% issues.

Usage:
    python experiments/test_sqlite.py results/rq1/rq1_bird_fewshot_results.jsonl bird
    python experiments/test_sqlite.py results/rq2/rq2_spider_fewshot_results.jsonl spider
"""
import json, os, sys, sqlite3, argparse
from collections import Counter, defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_BASE, 'src')
if _src not in sys.path:
    sys.path.insert(0, _src)

BIRD_DB = os.path.join(_BASE, 'data', 'bird-dev', 'dev_20240627', 'dev_databases')
SPIDER_DB = os.path.join(_BASE, 'data', 'spider1.0', 'database')


def test_file(filepath, dataset):
    db_base = SPIDER_DB if dataset == 'spider' else BIRD_DB

    results = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))

    stats = defaultdict(lambda: {'total': 0, 'ok': 0, 'fail': 0, 'error': 0,
                                  'no_pred': 0, 'no_gold': 0, 'no_db': 0,
                                  'errors_detail': []})

    for r in results:
        m = r.get('method', '?')
        db_id = r.get('db_id', '')
        gold = r.get('gold_sql', '')
        pred = r.get('pred_sql', '')

        # Recover pred from sub_queries if empty
        if not pred.strip():
            sqs = r.get('sub_queries', [])
            if sqs:
                pred = sqs[-1].get('sql', '')
                r['pred_sql'] = pred

        stats[m]['total'] += 1

        if not pred.strip():
            stats[m]['no_pred'] += 1
            continue
        if not gold.strip():
            stats[m]['no_gold'] += 1
            continue

        db_path = os.path.join(db_base, db_id, f'{db_id}.sqlite')
        if not os.path.exists(db_path):
            stats[m]['no_db'] += 1
            continue

        try:
            conn = sqlite3.connect(db_path)
            conn.text_factory = lambda b: b.decode(errors='ignore')
            c = conn.cursor()
            c.execute(pred)
            pr = c.fetchall()
            c.execute(gold)
            gr = c.fetchall()
            c.close()
            conn.close()
            if set(pr) == set(gr):
                stats[m]['ok'] += 1
            else:
                stats[m]['fail'] += 1
                if len(stats[m]['errors_detail']) < 3:
                    stats[m]['errors_detail'].append({
                        'qid': r.get('question_id'),
                        'db': db_id,
                        'pred': pred[:100],
                        'gold': gold[:100],
                        'pred_rows': len(pr),
                        'gold_rows': len(gr),
                    })
        except Exception as e:
            stats[m]['error'] += 1
            if len(stats[m]['errors_detail']) < 3:
                stats[m]['errors_detail'].append({
                    'qid': r.get('question_id'),
                    'db': db_id,
                    'pred': pred[:100],
                    'error': str(e)[:100],
                })

    # Print report
    print(f'\n{"="*70}')
    print(f'  SQLite Test: {os.path.basename(filepath)}')
    print(f'  Dataset: {dataset}')
    print(f'  Total results: {len(results)}')
    print(f'{"="*70}')
    print(f'  {"Method":<8} {"Total":>6} {"OK":>6} {"Fail":>6} {"Error":>6} {"NoPred":>7} {"EX%":>7}')
    print(f'  {"-"*8} {"-"*6} {"-"*6} {"-"*6} {"-"*6} {"-"*7} {"-"*7}')

    for m in sorted(stats.keys()):
        d = stats[m]
        total = d['total']
        ex = d['ok'] / max(total - d['no_pred'] - d['no_gold'] - d['no_db'], 1) * 100
        print(f'  {m:<8} {total:>6} {d["ok"]:>6} {d["fail"]:>6} {d["error"]:>6} {d["no_pred"]:>7} {ex:>6.0f}%')

    # Show error details
    for m in sorted(stats.keys()):
        if stats[m]['errors_detail']:
            print(f'\n  [{m}] Sample failures:')
            for e in stats[m]['errors_detail']:
                qid = e.get('qid', '?')
                if 'error' in e:
                    print(f'    Q{qid} [{e["db"]}]: ERROR — {e["error"]}')
                else:
                    print(f'    Q{qid} [{e["db"]}]: pred={e["pred_rows"]}r, gold={e["gold_rows"]}r')
                    print(f'      pred: {e["pred"]}')
                    print(f'      gold: {e["gold"]}')

    # Also write back corrected EX values
    print(f'\n  Writing corrected EX values back to file...')
    with open(filepath, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'  Done.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='JSONL file to test')
    parser.add_argument('dataset', choices=['bird', 'spider'], help='Dataset name')
    args = parser.parse_args()
    test_file(args.file, args.dataset)
