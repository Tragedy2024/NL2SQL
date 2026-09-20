"""
Generate SSA evidence-package artifacts (no LLM, no modification of frozen files):

  1. SSA_review_worksheet.csv      — 199 columns (99 restricted + 100 free
     sampled with seed 42), WITHOUT labels, shuffled: the second annotator's
     worksheet.
  2. SSA_review_worksheet_KEY.csv — same rows with current labels: only for
     the adjudicator (do not show to the second annotator).
  3. MANIFEST.template.json       — per-database provenance, prefilled from
     the frozen YAML files (annotator field, review_date, mtimes, label
     counts, md5); human-reviewer fields left blank for the authors to fill.
"""
import csv
import hashlib
import json
import os
import random

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSA_DIR = os.path.join(_BASE, "config", "ssa")
OUT_DIR = os.environ.get("SSA_EVIDENCE_OUT", os.path.join(_BASE, "outputs", "ssa_evidence"))

import sys
sys.path.insert(0, os.path.join(_BASE, "src"))
from ssa.loader import load_ssa


def main():
    # ---- collect columns ----
    rows = []  # (db, table, col, label)
    dbs = sorted(
        f[:-5] for f in os.listdir(SSA_DIR)
        if f.endswith(".yaml")
    )
    for db in dbs:
        ssa = load_ssa(db, SSA_DIR)
        for table, cols in ssa.column_labels.items():
            for col, label in cols.items():
                rows.append((db, table, col, label))
    print(f"total columns: {len(rows)}")

    restricted = [r for r in rows if r[3] in ("controlled", "blocked")]
    free = [r for r in rows if r[3] == "free"]
    print(f"restricted: {len(restricted)}, free: {len(free)}")

    rng = random.Random(42)
    free_sample = rng.sample(free, 100)
    pool = restricted + free_sample
    rng.shuffle(pool)

    # ---- worksheet (no labels) ----
    ws_path = os.path.join(OUT_DIR, "SSA_review_worksheet.csv")
    with open(ws_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["row_id", "database", "table", "column", "your_label"])
        for i, (db, table, col, _) in enumerate(pool, 1):
            w.writerow([i, db, table, col, ""])
    print(f"worksheet -> {ws_path} ({len(pool)} rows)")

    # ---- key ----
    key_path = os.path.join(OUT_DIR, "SSA_review_worksheet_KEY.csv")
    with open(key_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["row_id", "database", "table", "column", "current_label"])
        for i, (db, table, col, label) in enumerate(pool, 1):
            w.writerow([i, db, table, col, label])
    print(f"key -> {key_path}")

    # ---- manifest ----
    manifest = {}
    for db in dbs:
        ssa = load_ssa(db, SSA_DIR)
        path = os.path.join(SSA_DIR, db + ".yaml")
        raw = open(path, "rb").read()
        mtime = os.path.getmtime(path)
        import datetime
        n_f = n_c = n_b = 0
        for cols in ssa.column_labels.values():
            for label in cols.values():
                if label == "free":
                    n_f += 1
                elif label == "controlled":
                    n_c += 1
                elif label == "blocked":
                    n_b += 1
        manifest[db] = {
            "db_id": db,
            "initial_annotator": "TODO: deepseek-v4-pro (BIRD) / heuristic rules (Spider)",
            "generation_batch_date": "TODO",
            "human_reviewer": "TODO",
            "review_date_field": ssa_meta_review_date(path),
            "file_mtime": datetime.datetime.fromtimestamp(mtime).strftime(
                "%Y-%m-%d %H:%M:%S"),
            "yaml_md5": hashlib.md5(raw).hexdigest(),
            "n_free": n_f,
            "n_controlled": n_c,
            "n_blocked": n_b,
            "n_cross_domain_rules": len(ssa.cross_domain_rules),
        }
    man_path = os.path.join(OUT_DIR, "MANIFEST.template.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"manifest -> {man_path} ({len(dbs)} databases)")


def ssa_meta_review_date(path):
    import yaml
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return str(data.get("review_date", ""))


if __name__ == "__main__":
    main()
