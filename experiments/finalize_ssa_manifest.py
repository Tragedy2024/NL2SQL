"""
Finalize MANIFEST.json for the SSA evidence package.

Fills the author-supplied provenance facts into the per-database template:
  - human reviewer: the author (single reviewer, per-column check)
  - BIRD 11 DBs: initial labels by deepseek-v4-pro (batch dated 2026-07-14
    per the YAML header comments in financial/toxicology), human review
    finalized 2026-07-20
  - Spider 20 DBs: initial labels by heuristic rules (batch date unknown),
    human review finalized 2026-08-04
Frozen YAML files are NOT modified.
"""
import json
import os

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.environ.get("SSA_EVIDENCE_OUT", os.path.join(_BASE, "outputs", "ssa_evidence"))

BIRD_DBS = {
    "california_schools", "card_games", "codebase_community",
    "debit_card_specializing", "european_football_2", "financial",
    "formula_1", "student_club", "superhero", "thrombosis_prediction",
    "toxicology",
}


def main():
    tpl = json.load(open(os.path.join(SUB, "MANIFEST.template.json"),
                         encoding="utf-8"))
    out = {}
    for db, meta in tpl.items():
        if db in BIRD_DBS:
            meta["initial_annotator"] = "deepseek-v4-pro (one call per DB)"
            meta["generation_batch_date"] = (
                "2026-07-14 (per YAML header comment; documented on "
                "financial/toxicology, same batch inferred for the rest)"
            )
            meta["review_date_field"] = meta.get("review_date_field") or \
                "2026-07-20 (same batch)"
        else:
            meta["initial_annotator"] = "heuristic rules"
            meta["generation_batch_date"] = "unknown (not recorded)"
        meta["human_reviewer"] = "author (single reviewer, per-column check)"
        meta["review_mode"] = "per-column check; disputed columns adjusted to controlled/blocked"
        out[db] = meta

    manifest = {
        "schema": "SSA provenance manifest v1",
        "generated_by": "experiments/finalize_ssa_manifest.py",
        "note": (
            "Frozen config/ssa/*.yaml files are NOT modified. The YAML "
            "annotator header field (GPT-4o + human_review) is a historical "
            "leftover; the true provenance is recorded here. For 20 Spider "
            "files the review_date field (2026-08-04) is one day later than "
            "the file-system mtime (2026-08-03 10:52); both are recorded and "
            "the freeze date is taken as 2026-08-04."
        ),
        "freeze_date": "2026-08-04",
        "databases": out,
    }
    dst = os.path.join(SUB, "MANIFEST.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"MANIFEST.json -> {dst} ({len(out)} databases)")


if __name__ == "__main__":
    main()
