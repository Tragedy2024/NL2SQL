"""
RQ3 — Mis-degradation Rate Verification.

Per v1-implementation-report §9.3:
  - Select 30 L1/L2 degraded outputs from RQ2
  - Human attempts to manually construct an L0 (safe) decomposition for each
  - If L0 can be constructed → system mis-degraded (false positive)
  - If L0 cannot be constructed → degradation was correct

This script prepares the verification dataset and provides a framework
for recording and analyzing manual construction attempts.

Usage (run from the project root):
    PYTHONPATH="src" \
      python experiments/rq3/misdegradation.py --prepare
    PYTHONPATH="..." python experiments/rq3/misdegradation.py --analyze results.json
"""
import json
import os
import sys
import argparse
import random
from collections import Counter

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEMPLATE_FILE = os.path.join(_BASE, 'results', 'rq3', 'misdegradation_template.json')
RESULTS_FILE = os.path.join(_BASE, 'results', 'rq3', 'misdegradation_results.json')


def prepare_template(rq2_results_file: str, n_samples: int = 30):
    """Select 30 degraded outputs for manual L0 construction attempt."""
    with open(rq2_results_file, 'r', encoding='utf-8') as f:
        rq2_results = [json.loads(line) for line in f if line.strip()]

    degraded = [
        r for r in rq2_results
        if r.get('degradation_level') in ('L1', 'L2', 'L3')
        and str(r.get('method', '')).startswith('B6')
        and not r.get('error')
    ]

    rng = random.Random(42)
    selected = rng.sample(degraded, min(n_samples, len(degraded)))

    template = []
    for i, r in enumerate(selected):
        template.append({
            'sample_id': i + 1,
            'question_id': r.get('question_id'),
            'db_id': r.get('db_id'),
            'query': (r.get('query', '') or '')[:300],
            'gold_sql': r.get('gold_sql', ''),
            'degradation_level': r.get('degradation_level'),
            'degradation_message': r.get('degradation_message', ''),
            'n_subqueries': r.get('n_subqueries', 0),
            'violations_count': r.get('n_violations_after', 0),
            # To be filled by human:
            'l0_constructed': None,        # true/false
            'l0_sql': '',                   # manually constructed safe SQL
            'construction_notes': '',       # how did you construct L0?
            'could_not_construct_reason': '', # if false, why not?
        })

    os.makedirs(os.path.dirname(TEMPLATE_FILE), exist_ok=True)
    with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print(f"Mis-degradation template: {TEMPLATE_FILE}")
    print(f"  {len(selected)} samples selected for manual L0 construction attempt")
    print(f"\n  For each sample, attempt to manually write an L0 (safe) decomposition.")
    print(f"  If you CAN write one → system mis-degraded.")
    print(f"  If you CANNOT → degradation was correct.")


def analyze_results(results_file: str):
    """Analyze mis-degradation verification results."""
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    evaluated = [r for r in data if r.get('l0_constructed') is not None]
    misdegraded = [r for r in evaluated if r['l0_constructed'] is True]
    correct = [r for r in evaluated if r['l0_constructed'] is False]

    print(f"\nMis-degradation Verification Results:")
    print(f"  Total samples: {total}")
    print(f"  Evaluated: {len(evaluated)}")
    print(f"  Mis-degraded (L0 could be constructed): {len(misdegraded)} "
          f"({len(misdegraded)/max(len(evaluated),1)*100:.0f}%)")
    print(f"  Correctly degraded (L0 impossible): {len(correct)} "
          f"({len(correct)/max(len(evaluated),1)*100:.0f}%)")

    if misdegraded:
        print(f"\n  Mis-degraded cases (review needed):")
        for r in misdegraded:
            print(f"    [{r['sample_id']}] {r['db_id']}: "
                  f"{r['query'][:80]}...")
            print(f"      Reason L0 was possible: {r.get('construction_notes', '')[:100]}")

    # Per-level breakdown
    by_level = Counter(r.get('degradation_level') for r in data)
    for level in sorted(by_level.keys()):
        level_cases = [r for r in evaluated if r.get('degradation_level') == level]
        level_mis = [r for r in misdegraded if r.get('degradation_level') == level]
        if level_cases:
            print(f"\n  {level}: {len(level_mis)}/{len(level_cases)} mis-degraded "
                  f"({len(level_mis)/len(level_cases)*100:.0f}%)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--analyze', type=str, default=None,
                        help='Path to filled misdegradation results JSON')
    parser.add_argument('--rq2-results', type=str,
                        default=os.path.join(_BASE, 'results', 'rq2', 'rq2_results.jsonl'))
    args = parser.parse_args()

    if args.prepare:
        prepare_template(args.rq2_results)
    elif args.analyze:
        analyze_results(args.analyze)
    else:
        print("Usage: python misdegradation.py --prepare | --analyze <results.json>")


if __name__ == "__main__":
    main()
