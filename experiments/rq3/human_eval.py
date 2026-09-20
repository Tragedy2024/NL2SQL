"""
RQ3 — Human Evaluation of Degradation Outputs.

Per v1.md §9.3 and v1-implementation-report §9.3:
  - Select 50 L1/L2 outputs from RQ2 results (20 L1, 20 L2, 10 mixed)
  - 2-3 raters independently score on 1-5 Likert:
    Q1 (Utility): How well does the degraded output satisfy the original query intent?
    Q2 (Transparency): Does the degradation message help you understand what changed and why?
    Q3 (Preference): Would you prefer this protected result over an unsafe result?
  - Report: mean ± std per question, inter-rater agreement (Cohen's κ)

Usage (run from the project root):
    PYTHONPATH="src;vendor/MAC-SQL" \
      python experiments/rq3/human_eval.py --prepare   # Generate evaluation template
    PYTHONPATH="..." python experiments/rq3/human_eval.py --analyze ratings.csv
"""
import json
import os
import sys
import argparse
import random
from collections import Counter, defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_src = os.path.join(_BASE, 'src')
for _p in [_src]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from evaluation.statistics import cohens_kappa

RATINGS_TEMPLATE = os.path.join(_BASE, 'results', 'rq3', 'rq3_evaluation_template.csv')
RATINGS_OUTPUT = os.path.join(_BASE, 'results', 'rq3', 'rq3_ratings.json')


def prepare_evaluation_template(rq2_results_file: str, n_samples: int = 50):
    """
    Load RQ2 results, filter for L1/L2 degradations, and produce
    a CSV template for human raters.
    """
    # Read RQ2 results
    with open(rq2_results_file, 'r', encoding='utf-8') as f:
        rq2_results = [json.loads(line) for line in f if line.strip()]

    # Filter: L1/L2/L3 degradations from B6 (ours full) or B6-constructed
    # (P1-1 blocked injections).  Under the current code the natural pool is
    # L3-only (malformed QSG SQL rejections); L1/L2 cases come from the
    # constructed blocked-injection set.
    degraded = [
        r for r in rq2_results
        if r.get('degradation_level') in ('L1', 'L2', 'L3')
        and str(r.get('method', '')).startswith('B6')
        and not r.get('error')
    ]

    print(f"RQ2 degraded outputs: {len(degraded)} total (L1/L2/L3, B6*)")

    # Stratified sampling: up to 15 L1, 15 L2, 20 L3
    l1_pool = [r for r in degraded if r['degradation_level'] == 'L1']
    l2_pool = [r for r in degraded if r['degradation_level'] == 'L2']
    l3_pool = [r for r in degraded if r['degradation_level'] == 'L3']

    rng = random.Random(42)
    selected_l1 = rng.sample(l1_pool, min(15, len(l1_pool)))
    selected_l2 = rng.sample(l2_pool, min(15, len(l2_pool)))
    selected_l3 = rng.sample(l3_pool, min(20, len(l3_pool)))

    selected = selected_l1 + selected_l2 + selected_l3
    rng.shuffle(selected)

    # Build CSV
    import csv
    os.makedirs(os.path.dirname(RATINGS_TEMPLATE), exist_ok=True)

    with open(RATINGS_TEMPLATE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'sample_id', 'question_id', 'db_id', 'query',
            'degradation_level', 'degradation_message',
            'sub_queries_summary',
            'Q1_utility', 'Q2_transparency', 'Q3_preference',
            'rater_id', 'notes'
        ])
        for i, r in enumerate(selected):
            writer.writerow([
                i + 1,
                r.get('question_id', ''),
                r.get('db_id', ''),
                (r.get('query', '') or '')[:200],
                r.get('degradation_level', ''),
                r.get('degradation_message', '')[:300],
                f"{r.get('n_subqueries', 0)} sub-queries",
                '', '', '', '', ''
            ])

    print(f"Template: {RATINGS_TEMPLATE}")
    print(f"  {len(selected_l1)} L1 + {len(selected_l2)} L2 + {len(selected_l3)} L3")
    print(f"\n  Send this CSV to raters. Each rater fills in Q1-Q3 (1-5) and rater_id.")
    print(f"  Note: L3 rows are rejections — rate Q1 as whether refusal was appropriate.")

    return selected


def analyze_ratings(ratings_csv: str):
    """Analyze collected ratings, compute means and inter-rater agreement."""
    import csv

    rater_scores = defaultdict(lambda: defaultdict(list))
    # rater_scores[question][rater_id] = [Q1, Q2, Q3]

    with open(ratings_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row['sample_id']
            rid = row.get('rater_id', 'unknown')
            try:
                q1 = int(row.get('Q1_utility', 0))
                q2 = int(row.get('Q2_transparency', 0))
                q3 = int(row.get('Q3_preference', 0))
                if q1 > 0 and q2 > 0 and q3 > 0:
                    rater_scores[sid][rid] = [q1, q2, q3]
            except (ValueError, KeyError):
                continue

    if not rater_scores:
        print("No valid ratings found.")
        return

    # Aggregate per question
    q1_all, q2_all, q3_all = [], [], []
    for sid, raters in rater_scores.items():
        for rid, scores in raters.items():
            q1_all.append(scores[0])
            q2_all.append(scores[1])
            q3_all.append(scores[2])

    print(f"\nRQ3 Human Evaluation Results:")
    print(f"  Samples rated: {len(rater_scores)}")
    print(f"  Total ratings: {len(q1_all)}")
    print(f"  Q1 (Utility):       mean={sum(q1_all)/len(q1_all):.2f} ± "
          f"{(sum((x-sum(q1_all)/len(q1_all))**2 for x in q1_all)/len(q1_all))**0.5:.2f}")
    print(f"  Q2 (Transparency):  mean={sum(q2_all)/len(q2_all):.2f} ± "
          f"{(sum((x-sum(q2_all)/len(q2_all))**2 for x in q2_all)/len(q2_all))**0.5:.2f}")
    print(f"  Q3 (Preference):    mean={sum(q3_all)/len(q3_all):.2f} ± "
          f"{(sum((x-sum(q3_all)/len(q3_all))**2 for x in q3_all)/len(q3_all))**0.5:.2f}")

    # Inter-rater agreement (if ≥2 raters)
    all_raters = set()
    for sid, raters in rater_scores.items():
        all_raters.update(raters.keys())
    rater_list = sorted(all_raters)

    if len(rater_list) >= 2:
        for qi, qname in enumerate(['Q1_utility', 'Q2_transparency', 'Q3_preference']):
            r1_scores, r2_scores = [], []
            for sid in rater_scores:
                if rater_list[0] in rater_scores[sid] and rater_list[1] in rater_scores[sid]:
                    r1_scores.append(rater_scores[sid][rater_list[0]][qi])
                    r2_scores.append(rater_scores[sid][rater_list[1]][qi])
            if r1_scores:
                ck = cohens_kappa(r1_scores, r2_scores)
                print(f"\n  {qname} — {rater_list[0]} vs {rater_list[1]}:")
                print(f"    κ = {ck['kappa']} ({ck['interpretation']}), "
                      f"agreement = {ck['agreement_pct']}%")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true',
                        help='Generate evaluation template from RQ2 results')
    parser.add_argument('--analyze', type=str, default=None,
                        help='Analyze ratings CSV file')
    parser.add_argument('--rq2-results', type=str,
                        default=os.path.join(_BASE, 'results', 'rq2', 'rq2_results.jsonl'),
                        help='Path to RQ2 results JSONL')
    args = parser.parse_args()

    if args.prepare:
        prepare_evaluation_template(args.rq2_results)
    elif args.analyze:
        analyze_ratings(args.analyze)
    else:
        print("Usage: python human_eval.py --prepare | --analyze <ratings.csv>")
        print("  --prepare: Generate CSV template from RQ2 results for human raters")
        print("  --analyze: Compute means and inter-rater agreement from collected ratings")


if __name__ == "__main__":
    main()
