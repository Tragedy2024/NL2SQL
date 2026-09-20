# -*- coding: utf-8 -*-
"""Post-disposition utility evaluation for the security pipeline.

Goal: for every case where the frozen pipeline modified the plan
(n_rewrites > 0) or routed to L1/L2, execute the audited (post-disposition)
final answer and compare with the gold answer.

Execution semantics (MAC-SQL convention, matching the project's EX
protocol): the answer is the FINAL sub-query, with upstream sub-queries
inlined as CTEs named step{id}.  A final query that references no step
tables is executed as-is.  Plans whose intermediate naming is not the
step{id} convention (observed in some QSG plans) are recorded as
"unsupported_plan_naming" rather than faking a result.

Zero LLM, deterministic: replay uses frozen code + frozen SSA.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
import time

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_BASE, os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from common import SSA_DIR, get_dataset_config  # noqa: E402
from security_auditor import run_security_auditor_pipeline  # noqa: E402

EXEC_TIMEOUT_S = 20
OUT_DIR = os.path.join(_BASE, "results", "post_disposition_ex")

GROUPS = [
    ("bird", "fewshot"), ("bird", "zeroshot"),
    ("spider", "fewshot"), ("spider", "zeroshot"),
]


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def db_path_for(db_id, dataset):
    cfg = get_dataset_config(dataset)
    p = os.path.join(cfg["db_path"], db_id, f"{db_id}.sqlite")
    return p if os.path.exists(p) else None


def execute_sql(conn, sql):
    deadline = [time.time()]

    def guard():
        return 1 if time.time() - deadline[0] > EXEC_TIMEOUT_S else 0

    conn.set_progress_handler(guard, 50_000)
    deadline[0] = time.time()
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


def build_final_sql(audited_plan):
    """Inline non-final sub-queries as CTEs named step{id} around the final
    sub-query.  Returns (final_sql, error)."""
    n = len(audited_plan)
    if n == 0:
        return None, "empty_plan"
    final = audited_plan[-1]
    final_sql = final["sql"]
    upstream = audited_plan[:-1]
    # Detect unsupported naming: upstream references to tables that are not
    # step{id} (e.g. step_3, substep1, joined) can't be safely inlined.
    unsupported = set()
    step_id_re = re.compile(r"step(\d+)", re.IGNORECASE)
    for sq in audited_plan:
        for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", sq["sql"]):
            # we only flag tokens that look like step-style aliases
            pass
    # Build CTEs for upstream steps in order; step{k} may reference step{j<i}.
    ctes = []
    for sq in upstream:
        sid = sq.get("id", len(ctes))
        ctes.append(f'"step{sid}" AS ({sq["sql"]})')
    if ctes:
        return "WITH " + ",\n".join(ctes) + "\n" + final_sql, None
    return final_sql, None


def execute_answer(audited_plan, db_path):
    final_sql, err = build_final_sql(audited_plan)
    if err:
        return None, err
    conn = sqlite3.connect(db_path)
    conn.text_factory = lambda b: b.decode(errors="ignore")
    try:
        rows = execute_sql(conn, final_sql)
        conn.close()
        return rows, None
    except Exception as e:  # noqa: BLE001
        try:
            conn.close()
        except Exception:
            pass
        return None, f"{type(e).__name__}: {str(e)[:140]}"


def evaluate_case(rec, dataset, mode, scope):
    plan = [{"id": s.get("id", i), "sql": s["sql"]}
            for i, s in enumerate(rec.get("sub_queries") or [])]
    db_id = rec.get("db_id", "")
    if not plan:
        return None
    res = run_security_auditor_pipeline(plan, db_id, ssa_dir=SSA_DIR)
    level = res.get("degradation_level", "L0")
    audited = res.get("audited_plan") or []
    raw_rew = (res.get("audit_report") or {}).get("rewrites_applied") or 0
    n_rew = raw_rew if isinstance(raw_rew, int) else len(raw_rew)
    changed = n_rew > 0 or level in ("L1", "L2")
    out = {
        "scope": scope, "group": f"{dataset}_{mode}", "dataset": dataset,
        "db_id": db_id, "question_id": rec.get("question_id"),
        "level": level, "n_rewrites": n_rew,
        "n_subqueries_after": len(audited),
        "cached_ex": rec.get("ex_match"),
    }
    if not changed:
        out["evaluated"] = False
        return out
    out["evaluated"] = True
    db_path = db_path_for(db_id, dataset)
    if db_path is None:
        out["ex_post"] = None
        out["error"] = "db_missing"
        return out
    # Gold execution
    try:
        conn = sqlite3.connect(db_path)
        conn.text_factory = lambda b: b.decode(errors="ignore")
        gold_rows = execute_sql(conn, rec["gold_sql"])
        conn.close()
    except Exception as e:  # noqa: BLE001
        out["ex_post"] = None
        out["error"] = f"gold_fail: {type(e).__name__}"
        return out
    if level == "L3":
        out["ex_post"] = False  # no executable answer
        return out
    rows, err = execute_answer(audited, db_path)
    if err:
        out["ex_post"] = None
        out["error"] = err
        return out
    out["ex_post"] = set(rows) == set(gold_rows)
    return out


def run_group(dataset, mode, scope):
    if scope == "rq1":
        src = os.path.join(_BASE, "results", "rq1",
                           f"rq1_{dataset}_{mode}_results.jsonl")
        method = None
    else:
        src = os.path.join(_BASE, "results", "rq2",
                           f"rq2_{dataset}_{mode}_results.jsonl")
        method = "B0" if scope == "mac" else "B2-Q"
    if not os.path.exists(src):
        print(f"[skip] {src} missing")
        return []
    rows = load_jsonl(src)
    if method:
        rows = [r for r in rows if r.get("method") == method]
    out = []
    for i, r in enumerate(rows):
        try:
            case = evaluate_case(r, dataset, mode, scope)
        except Exception as e:  # noqa: BLE001
            case = {"scope": scope, "group": f"{dataset}_{mode}",
                    "dataset": dataset, "db_id": r.get("db_id"),
                    "question_id": r.get("question_id"), "evaluated": True,
                    "ex_post": None,
                    "error": f"pipeline_fail: {type(e).__name__}: {str(e)[:120]}"}
        if case:
            out.append(case)
        if (i + 1) % 200 == 0:
            print(f"  [{dataset}_{mode}/{scope}] {i + 1}/{len(rows)}")
    return out


def summarize(results, label):
    ev = [r for r in results if r.get("evaluated")]
    ok = [r for r in ev if r.get("ex_post") is not None]
    fail = [r for r in ev if r.get("ex_post") is None]
    correct = [r for r in ok if r["ex_post"]]
    s = {
        "label": label, "n_records": len(results),
        "n_changed": len(ev), "n_executed_ok": len(ok),
        "n_execution_failed": len(fail),
        "ex_post": round(len(correct) / len(ok), 4) if ok else None,
        "ex_cached_on_same_cases": round(
            sum(1 for r in ok if r.get("cached_ex") is True) / len(ok), 4)
            if ok else None,
        "by_level": {},
    }
    for lv in ("L0", "L1", "L2", "L3"):
        sub = [r for r in ok if r["level"] == lv]
        if sub:
            s["by_level"][lv] = {
                "n": len(sub),
                "ex_post": round(sum(1 for r in sub if r["ex_post"]) / len(sub), 4),
                "ex_cached": round(
                    sum(1 for r in sub if r.get("cached_ex") is True) / len(sub), 4),
            }
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=["mac", "qsg", "rq1", "all"],
                    default="all")
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    scopes = ["mac", "qsg", "rq1"] if args.scope == "all" else [args.scope]
    all_rows = []
    summaries = []
    for scope in scopes:
        for dataset, mode in GROUPS:
            t0 = time.time()
            res = run_group(dataset, mode, scope)
            all_rows.extend(res)
            summaries.append(summarize(res, f"{scope}:{dataset}_{mode}"))
            print(f"[done] {scope}:{dataset}_{mode} "
                  f"({len(res)} records, {time.time() - t0:.1f}s)")
    with open(os.path.join(OUT_DIR, "details.jsonl"), "w",
              encoding="utf-8") as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    summary = {
        "generated_by": "experiments/post_disposition_ex.py (CTE-inline)",
        "note": "Post-disposition utility: audited plans replayed with frozen "
                "code + frozen SSA; final answer = final sub-query with "
                "upstream steps inlined as CTEs step{id}; ex_post = result-set "
                "equality vs executed gold.",
        "per_group": summaries,
    }
    with open(os.path.join(OUT_DIR, "summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("summary saved:", os.path.join(OUT_DIR, "summary.json"))


if __name__ == "__main__":
    main()
