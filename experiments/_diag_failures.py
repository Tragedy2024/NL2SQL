# -*- coding: utf-8 -*-
"""Diagnose post-disposition execution failures: pre-existing plan breakage
vs rewrite-induced breakage."""
import json
import os
import sqlite3
import sys
import time
from collections import Counter

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_BASE, os.path.join(_BASE, "src"), os.path.join(_BASE, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from common import get_dataset_config  # noqa: E402

recs = [json.loads(l) for l in open(
    os.path.join(_BASE, "results", "post_disposition_ex", "details.jsonl"),
    encoding="utf-8") if l.strip()]
fail = [r for r in recs if r.get("evaluated") and r.get("ex_post") is None
        and r.get("error")]
print("fail cases:", len(fail))

def load_original(group, qid, method):
    ds, mode = group.split("_", 1)
    src = os.path.join(_BASE, "results", "rq2",
                       f"rq2_{ds}_{mode}_results.jsonl")
    if not os.path.exists(src):
        return None
    for l in open(src, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            if r.get("question_id") == qid and r.get("method") == method:
                return r
    return None

orig_ok = 0
orig_broken = 0
errs = Counter()
for r in fail:
    group = r["group"]
    ds = r["dataset"]
    qid = r["question_id"]
    db = r["db_id"]
    method = "B0" if group.startswith(("mac", "rq1")) else "B2-Q"
    rec = load_original(group, qid, method)
    if rec is None:
        errs["orig_record_missing"] += 1
        continue
    cfg = get_dataset_config(ds)
    db_path = os.path.join(cfg["db_path"], db, db + ".sqlite")
    conn = sqlite3.connect(db_path)
    conn.text_factory = lambda b: b.decode(errors="ignore")
    plan = rec["sub_queries"]
    n = len(plan)
    err = None
    try:
        deadline = [time.time()]
        def guard():
            return 1 if time.time() - deadline[0] > 20 else 0
        conn.set_progress_handler(guard, 50000)
        for i, sq in enumerate(plan):
            deadline[0] = time.time()
            cur = conn.cursor()
            cur.execute(sq["sql"])
            rows = cur.fetchall()
            if i < n - 1:
                deadline[0] = time.time()
                conn.execute("CREATE TEMP TABLE step%d AS %s"
                             % (sq.get("id", i), sq["sql"]))
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {str(e)[:60]}"
    conn.close()
    if err:
        orig_broken += 1
        errs[err] += 1
    else:
        orig_ok += 1

print("original plan executable:", orig_ok, "| already broken:", orig_broken)
for k, v in errs.most_common(10):
    print(" ", v, k)
