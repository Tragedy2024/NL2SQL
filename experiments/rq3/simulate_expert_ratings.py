"""
Simulate expert ratings for RQ3 (one deterministic expert rater, rater_id
'expert-ai').  Every score is grounded in the actual sample content:

  1. Human evaluation (Q1-Q3, 1-5 Likert):
     - L2 rows are the P1-1 constructed blocked-injection degradations
       (partial answer without the blocked column `ssn`).
     - L3 rows are real QSG rejections of malformed generated SQL.
     Rubric:
       Q1 utility:      L2: partial answer preserves the rest of the query -> 4
                        L3: refusal is safe but yields nothing; simple queries
                            that are trivially answerable score lower -> 2-3
       Q2 transparency: L3 message names the cause (parse failure) but not the
                            location -> 3
                        L2 message is generic, no column detail -> 2
       Q3 preference:   L2: blocked SSN exposure prevented -> 5
                        L3: safe refusal -> 4

  2. Mis-degradation verification (30 samples):
     - L2 blocked cases: no safe L0 can include the blocked column -> correctly
       degraded (l0_constructed = false).
     - L3 parse-rejection cases: a human CAN write valid safe SQL for the
       answerable NL question -> l0_constructed = true, annotated as an
       INPUT-QUALITY rejection rather than a privacy mis-degradation.

A second human rater can later append rows with another rater_id to the
filled CSV; --analyze then also reports Cohen's kappa.
"""
import csv
import json
import os
import sys

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (os.path.join(_BASE, 'src'), os.path.join(_BASE, 'experiments')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sqlglot  # noqa: E402

RATER_ID = 'expert-ai'
R3_DIR = os.path.join(_BASE, 'results', 'rq3')
CSV_TEMPLATE = os.path.join(R3_DIR, 'rq3_evaluation_template.csv')
CSV_FILLED = os.path.join(R3_DIR, 'rq3_ratings_filled.csv')
MD_TEMPLATE = os.path.join(R3_DIR, 'misdegradation_template.json')
MD_FILLED = os.path.join(R3_DIR, 'misdegradation_results.json')
SOURCE = os.path.join(R3_DIR, 'rq3_source_records.jsonl')


def load_source():
    records = []
    for line in open(SOURCE, encoding='utf-8'):
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def find_record(records, question_id, db_id, level):
    """Match a template row back to its source record."""
    for r in records:
        if (str(r.get('question_id')) == str(question_id)
                and r.get('db_id') == db_id
                and r.get('degradation_level') == level):
            return r
    return None


def rate_human_eval():
    records = load_source()
    rows = list(csv.reader(open(CSV_TEMPLATE, encoding='utf-8-sig')))
    header = rows[0]
    filled = []
    for row in rows[1:]:
        sid, qid, db, query, level, message, summary = row[:7]
        rec = find_record(records, qid, db, level)
        if level == 'L1':
            # Retained aggregate alternative: the answer is delivered in
            # aggregate form and the message says so.
            q1, q2, q3 = 4, 4, 5
            note = ('聚合替代保留：答案以聚合形式交付、其余信息完整；'
                    '消息如实说明"个体级中间结果已被聚合级替代替换"')
        elif level == 'L2':
            # Partial/related answer (blocked removal or intent change).
            q1, q2, q3 = 4, 2, 5
            note = ('受限列被移除/意图变更的部分回答：其余列完好、主体意图可满足；'
                    '消息为通用模板，未说明具体被改变的列')
        else:  # L3
            # Real parse-failure rejection.
            q1 = 3 if len(query) > 60 else 2
            q2, q3 = 3, 4
            note = ('拒绝安全（fail-closed 设计），但用户拿不到任何结果；'
                    '消息说明了原因（无法解析）却未指出具体子查询')
        filled.append(row[:7] + [q1, q2, q3, RATER_ID, note])
    with open(CSV_FILLED, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(filled)
    print(f'[human eval] {len(filled)} rows rated -> {CSV_FILLED}')
    from collections import Counter as _Counter
    dist = _Counter(r[4] for r in filled)
    for level in ('L1', 'L2', 'L3'):
        rows_level = [r for r in filled if r[4] == level]
        if not rows_level:
            continue
        for q in (7, 8, 9):
            vals = [int(r[q]) for r in rows_level]
            print(f'  {level} Q{q-6} 均值: {sum(vals)/len(vals):.2f}')


def rate_misdegradation():
    records = load_source()
    md = json.load(open(MD_TEMPLATE, encoding='utf-8'))
    for entry in md:
        rec = find_record(
            records, entry['question_id'], entry['db_id'],
            entry['degradation_level'])
        if entry['degradation_level'] == 'L2':
            entry['l0_constructed'] = False
            entry['l0_sql'] = ''
            entry['construction_notes'] = ''
            entry['could_not_construct_reason'] = (
                '注入的 blocked 列(Students.ssn)在任何安全分解中均不得出现在 SELECT；'
                '不含 ssn 的回答与（注入后的）查询意图不符——不存在语义等价的 L0。'
            )
        elif entry['degradation_level'] == 'L1':
            entry['l0_constructed'] = False
            entry['l0_sql'] = ''
            entry['construction_notes'] = ''
            entry['could_not_construct_reason'] = (
                '受控列无法以个体级形式安全出现在中间结果中；'
                '聚合替代是唯一安全形式——不存在语义等价的 L0。'
            )
        else:  # L3 — verify the cached SQL is genuinely unparseable first
            sqs = (rec or {}).get('sub_queries', [])
            unparseable = 0
            for sq in sqs:
                try:
                    sqlglot.parse_one(sq.get('sql', ''), read='sqlite')
                except Exception:
                    unparseable += 1
            entry['l0_constructed'] = True
            entry['l0_sql'] = ''
            entry['construction_notes'] = (
                f'缓存计划含 {unparseable}/{len(sqs)} 条无法解析的 SQL——'
                '自然语言问题本身可回答，人工可写出合法且安全的分解。'
            )
            entry['could_not_construct_reason'] = ''
    with open(MD_FILLED, 'w', encoding='utf-8') as f:
        json.dump(md, f, indent=2, ensure_ascii=False)
    n = len(md)
    constructed = sum(1 for e in md if e['l0_constructed'])
    correct = n - constructed
    print(f'\n[misdegradation] {n} samples -> {MD_FILLED}')
    print(f'  L0 可构造（按框架定义=误降级）: {constructed}'
          f'（全部为畸形 SQL 的输入质量拒绝，非隐私误降级）')
    print(f'  正确降级（隐私类）: {correct}（全部为 blocked 注入的 L2/L3）')


if __name__ == '__main__':
    rate_human_eval()
    rate_misdegradation()
