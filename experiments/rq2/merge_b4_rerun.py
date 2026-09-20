"""
Merge re-run B4 results back into the RQ2 result files.

The B4 re-run (after fixing the MACSQLSafePrompt injection no-op bug) writes
B4-ONLY lines into the standard result files.  This script:

1. Takes the pre-fix backup (results/rq2/backup_pre_b4_fix/) as the source of
   B0/B1/B2/B3/B1-Q/B2-Q lines.
2. DROPS all old B4 lines from the backup (those were produced while the
   security-prompt injection was a no-op and must never be re-reported).
3. Takes the new B4 lines from the freshly written result files.
4. Writes the merged file back and recomputes the summary JSON.

Safety: refuses to run if the backup directory is missing, if the new files
contain any non-B4 lines, or if qid coverage differs between old and new.
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from evaluation.metrics import compute_sar, compute_sscore  # noqa: E402

R_DIR = os.path.join(_BASE, "results", "rq2")
BK_DIR = os.path.join(R_DIR, "backup_pre_b4_fix")
GROUPS = ["bird_fewshot", "bird_zeroshot", "spider_fewshot", "spider_zeroshot"]
METHOD_ORDER = ["B0", "B1", "B2", "B3", "B4", "B1-Q", "B2-Q"]


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def save_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def qid_seed_keys(rows):
    return {(r["question_id"], r.get("seed")) for r in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", type=str, default=None,
                    help="Comma-separated subset of groups to merge, "
                         "e.g. 'bird_zeroshot,spider_zeroshot'")
    args = ap.parse_args()
    selected = set(GROUPS)
    if args.groups:
        selected = {g.strip() for g in args.groups.split(",") if g.strip()}
        unknown = selected - set(GROUPS)
        if unknown:
            raise SystemExit(f"unknown groups: {unknown}")

    if not os.path.isdir(BK_DIR):
        raise SystemExit(f"backup dir missing: {BK_DIR}")

    for g in GROUPS:
        if g not in selected:
            continue
        res_name = f"rq2_{g}_results.jsonl"
        sum_name = f"rq2_{g}_summary.json"
        bk_path = os.path.join(BK_DIR, res_name)
        new_path = os.path.join(R_DIR, res_name)

        if not os.path.exists(new_path):
            print(f"[{g}] new file not ready yet, skip")
            continue

        old = load_jsonl(bk_path)
        new = load_jsonl(new_path)

        new_methods = {r.get("method") for r in new}
        if new_methods != {"B4"}:
            raise SystemExit(
                f"[{g}] expected only B4 lines in new file, got {new_methods}; "
                f"the B4 re-run may have finished only partially — do not merge")

        old_non_b4 = [r for r in old if r.get("method") != "B4"]
        dropped = len(old) - len(old_non_b4)
        print(f"[{g}] backup lines={len(old)} (drop old B4={dropped}), new B4 lines={len(new)}")

        # Coverage check: old non-B4 vs new B4 must cover the same qid x seed set.
        old_keys = qid_seed_keys(old_non_b4)
        new_keys = qid_seed_keys(new)
        if old_keys and new_keys and old_keys != new_keys:
            only_old = sorted(old_keys - new_keys)[:5]
            only_new = sorted(new_keys - old_keys)[:5]
            raise SystemExit(
                f"[{g}] qid/seed coverage mismatch. only in old: {only_old} "
                f"only in new: {only_new} — merge aborted")

        merged = old_non_b4 + new
        save_jsonl(new_path, merged)
        print(f"[{g}] merged file written: {len(merged)} lines")

        # Recompute summary from the merged file.
        by_method = defaultdict(list)
        for r in merged:
            if not r.get("error"):
                by_method[r["method"]].append(r)
        summary = {}
        for method in METHOD_ORDER:
            rs = by_method[method]
            if not rs:
                continue
            ex_vals = [r for r in rs if r.get("ex_match") is not None]
            ex = sum(1 for r in ex_vals if r["ex_match"]) / max(len(ex_vals), 1)
            all_v = [r.get("n_violations_before") or 0 for r in rs]
            all_s = [r.get("n_subqueries") or 0 for r in rs]
            svr = sum(all_v) / max(sum(all_s), 1)
            sar = compute_sar(sum(all_v), sum(r.get("n_violations_after") or 0 for r in rs))
            sscore = compute_sscore(ex, svr)
            deg = Counter(r.get("degradation_level") for r in rs)
            summary[method] = {
                "n": len(rs), "EX": round(ex, 4), "S_VR": round(svr, 4),
                "S_AR": round(sar, 4), "S_Score": round(sscore, 4),
                "degradation": dict(deg),
            }
        with open(os.path.join(R_DIR, sum_name), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"[{g}] summary recomputed: {sum_name}")
        for m in METHOD_ORDER:
            if m in summary:
                s = summary[m]
                print(f"    {m}: n={s['n']} EX={s['EX']:.4f} S_VR={s['S_VR']:.4f} "
                      f"S_AR={s['S_AR']:.4f} deg={s['degradation']}")

    print("\nMERGE DONE")


if __name__ == "__main__":
    main()
