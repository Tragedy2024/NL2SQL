"""
Filter BIRD dev queries by SQL complexity.

"Complex" = requires decomposition:
  - >= 2 table JOINs
  - OR contains subquery (SELECT in WHERE/FROM)
  - OR UNION / INTERSECT / EXCEPT
  - OR GROUP BY with HAVING

Output: filtered query_id list + statistics by DB and difficulty.
"""
import json
import os
import sys
import sqlglot
import sqlglot.expressions as exp
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BIRD_DEV, BIRD_COMPLEX

OUTPUT = BIRD_COMPLEX


def is_complex(sql: str) -> bool:
    """
    Check if a SQL query is complex enough to warrant decomposition.
    Returns True if the query has >= 2 table JOINs, subqueries, UNION, or GROUP BY + HAVING.
    """
    try:
        tree = sqlglot.parse_one(sql)
    except Exception:
        # Can't parse → conservatively mark as complex
        return True

    # Count tables (FROM + JOIN)
    tables = list(tree.find_all(exp.Table))
    table_count = len(set(t.name for t in tables if t.name))

    # Count subqueries
    subqueries = list(tree.find_all(exp.Subquery))

    # Check for UNION / INTERSECT / EXCEPT
    has_set_op = any(
        tree.find_all(op) for op in [exp.Union, exp.Intersect, exp.Except]
    )
    # Actually Union/Intersect/Except are top-level, check differently
    has_set_op = isinstance(tree, (exp.Union, exp.Intersect, exp.Except))

    # Check GROUP BY + HAVING
    has_group_by = bool(list(tree.find_all(exp.Group)))
    has_having = bool(list(tree.find_all(exp.Having)))

    return (
        table_count >= 2
        or len(subqueries) > 0
        or has_set_op
        or (has_group_by and has_having)
    )


def main():
    with open(BIRD_DEV, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total queries: {len(data)}")

    # Classify each query
    complex_ids = []
    simple_ids = []
    db_stats = {}  # db_id → {total, complex, simple}
    diff_stats = Counter()  # difficulty → count for complex only

    for item in data:
        qid = item['question_id']
        db_id = item['db_id']
        difficulty = item['difficulty']
        sql = item.get('SQL', '')

        if db_id not in db_stats:
            db_stats[db_id] = {'total': 0, 'complex': 0, 'simple': 0,
                               'by_diff': Counter()}
        db_stats[db_id]['total'] += 1

        if is_complex(sql):
            complex_ids.append(qid)
            db_stats[db_id]['complex'] += 1
            db_stats[db_id]['by_diff'][difficulty] += 1
            diff_stats[difficulty] += 1
        else:
            simple_ids.append(qid)
            db_stats[db_id]['simple'] += 1

    # Report
    print(f"\n=== Complexity Distribution ===")
    print(f"  Complex (needs decomposition): {len(complex_ids)} ({len(complex_ids)/len(data)*100:.1f}%)")
    print(f"  Simple (direct SQL):           {len(simple_ids)} ({len(simple_ids)/len(data)*100:.1f}%)")

    print(f"\n=== By Difficulty (complex only) ===")
    for diff in ['simple', 'moderate', 'challenging']:
        print(f"  {diff}: {diff_stats.get(diff, 0)}")

    print(f"\n=== By Database ===")
    print(f"  {'DB':<30} {'Total':>6} {'Complex':>8} {'%':>6}")
    print(f"  {'-'*30} {'-'*6} {'-'*8} {'-'*6}")
    for db_id in sorted(db_stats.keys()):
        s = db_stats[db_id]
        pct = s['complex'] / s['total'] * 100 if s['total'] else 0
        print(f"  {db_id:<30} {s['total']:>6} {s['complex']:>8} {pct:>5.1f}%")

    # Save
    output = {
        "total_queries": len(data),
        "complex_count": len(complex_ids),
        "simple_count": len(simple_ids),
        "complex_query_ids": complex_ids,
        "simple_query_ids": simple_ids,
        "db_stats": {db: {k: v for k, v in s.items() if k != 'by_diff'}
                     for db, s in db_stats.items()},
        "diff_stats": dict(diff_stats),
        "criteria": ">=2 table JOINs OR subquery OR UNION/INTERSECT/EXCEPT OR GROUP BY+HAVING"
    }
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {OUTPUT}")


if __name__ == "__main__":
    main()
