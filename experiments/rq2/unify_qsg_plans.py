"""
Unify B1-Q / B2-Q records onto the frozen QSG cache plans.

Historical B1-Q/B2-Q records store plans from the original 8/20-era live
runs; 78 of them (bird/fewshot) diverge semantically from the final
ours_cache.  This script replaces each record's sub_queries/pred_sql with
the cache entry and re-runs the frozen audit pipeline (current code +
current SSA), so B0-Q / B1-Q / B2-Q share identical plans and identical
initial-audit counts.

Zero LLM calls.  Idempotent (safe to re-run).
"""
import json
import os
import sys

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from common import run_audit_pipeline  # noqa: E402

GROUPS = ["bird_fewshot", "bird_zeroshot", "spider_fewshot", "spider_zeroshot"]
METHODS = {"B1-Q": dict(rewrite=False, degradation=True),
           "B2-Q": dict(rewrite=True, degradation=True)}


def main():
    for g in GROUPS:
        cache = {}
        for line in open(os.path.join(
                _BASE, "results", "rq2",
                f"rq2_{g}_ours_cache.jsonl"), encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                cache[r["question_id"]] = r

        path = os.path.join(_BASE, "results", "rq2",
                            f"rq2_{g}_results.jsonl")
        rows = [json.loads(l) for l in open(path, encoding="utf-8")
                if l.strip()]
        n_replaced = 0
        for r in rows:
            if r.get("method") not in METHODS:
                continue
            e = cache.get(r["question_id"])
            if not e or not e.get("sub_queries"):
                print(f"[{g}] qid={r['question_id']} cache missing — skip")
                continue
            r["sub_queries"] = e["sub_queries"]
            r["n_subqueries"] = len(e["sub_queries"])
            if e.get("pred_sql"):
                r["pred_sql"] = e["pred_sql"]
            cfg = METHODS[r["method"]]
            sqs = [{"id": s.get("id", i), "sql": s["sql"]}
                   for i, s in enumerate(e["sub_queries"])]
            v_b, v_a, n_rw, lev, msg, _, sub_res = run_audit_pipeline(
                sqs, r["db_id"],
                e.get("pred_sql", ""), r.get("gold_sql", ""),
                rewrite=cfg["rewrite"], degradation=cfg["degradation"],
                dataset=g.split("_")[0],
            )
            r["n_violations_before"] = v_b
            r["n_violations_after"] = v_a
            r["n_rewrites"] = n_rw
            r["degradation_level"] = lev
            r["degradation_message"] = msg
            r["sub_results"] = sub_res
            n_replaced += 1

        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        # Report per-method aggregated counts.
        agg = {}
        for r in rows:
            m = r.get("method")
            if m not in METHODS:
                continue
            a = agg.setdefault(m, [0, 0, 0])
            a[0] += r.get("n_violations_before") or 0
            a[1] += r.get("n_violations_after") or 0
            a[2] += r.get("n_subqueries") or 0
        print(f"[{g}] replaced {n_replaced} records")
        for m, (vb, va, ns) in sorted(agg.items()):
            print(f"    {m}: V_before={vb} V_after={va} subq={ns} "
                  f"S_VR_pre={vb/ns:.4f} S_AR={1-va/max(vb,1):.4f}")


if __name__ == "__main__":
    main()
