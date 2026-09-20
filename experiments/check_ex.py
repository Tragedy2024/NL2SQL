import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RESULTS_DIR

files = [
    ('rq1_bird_fewshot', 'bird'), ('rq1_bird_zeroshot', 'bird'),
    ('rq1_spider_fewshot', 'spider'), ('rq1_spider_zeroshot', 'spider'),
    ('rq2_bird_fewshot', 'bird'), ('rq2_bird_zeroshot', 'bird'),
    ('rq2_spider_fewshot', 'spider'), ('rq2_spider_zeroshot', 'spider'),
]
for fname, ds in files:
    path = os.path.join(RESULTS_DIR, fname[:3], fname + '_results.jsonl')
    by_m = defaultdict(lambda: {'ok':0, 'total':0, 'none':0})
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            m = r.get('method', '?')
            ex = r.get('ex_match')
            if ex is True: by_m[m]['ok'] += 1
            elif ex is None: by_m[m]['none'] += 1
            by_m[m]['total'] += 1

    parts = []
    ok_flag = True
    for m in sorted(by_m.keys()):
        d = by_m[m]
        valid = d['total'] - d['none']
        ex = d['ok'] / max(valid, 1) * 100 if valid > 0 else 0
        if d['none'] > d['total'] * 0.5:
            ok_flag = False
        extra = ' (None:' + str(d['none']) + ')' if d['none'] > 0 else ''
        parts.append(m + '=' + str(int(ex)) + '%' + extra)
    flag = 'OK' if ok_flag else 'FIX'
    print('%-35s %s  %s' % (fname, flag, ' | '.join(parts[:6])))
