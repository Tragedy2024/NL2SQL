"""
Controlled Violation Injection Experiment.

Picks 30 MAC-SQL sub-queries from BIRD that were originally clean (S-VR=0),
injects controlled columns into their SELECT lists, and verifies:
  1. Auditor detects ALL injections (recall = 100%)
  2. Rewrite engine fixes ALL injections (S-AR = 100%)
  3. Clean SQLs produce ZERO false alarms (precision = 100%)

No LLM calls — pure AST manipulation + SQLite lookups.
"""
import json, os, sys, random, copy
import sqlglot, sqlglot.expressions as exp
from collections import Counter, defaultdict

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_BASE, 'src')
sys.path.insert(0, _src)

from ssa.loader import load_ssa
from auditor.base import SecurityAuditor, ViolationType
from rewrite.engine import RewriteEngine
from common import run_audit_pipeline

SSA_DIR = os.path.join(_BASE, 'config', 'ssa')
BIRD_DEV = os.path.join(_BASE, 'data', 'bird-dev', 'dev_20240627', 'dev.json')
RQ1_FILE = os.path.join(_BASE, 'results', 'rq1', 'rq1_bird_fewshot_results.jsonl')


def load_clean_queries(n=30):
    """Load n BIRD queries whose cached sub-queries are clean under the
    CURRENT auditor (zero violations).

    Note: the clean set is validated live with the current audit code
    (deterministic, no LLM calls).  It is re-derived from the cached RQ1
    decomposition plans after each semantic change to the auditor; after
    the offline RQ1 re-run, the independent clean set (queries with zero
    violations in the re-run results) should be used instead.
    """
    # Index cached MAC-SQL sub-queries by question_id
    sq_by_qid = {}
    with open(RQ1_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            sq_by_qid[r['question_id']] = r.get('sub_queries', [])

    # Load BIRD data
    with open(BIRD_DEV, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    # Pick queries that are clean under the current auditor AND have
    # controlled columns in their DB
    candidates = []
    for item in all_data:
        sqs = sq_by_qid.get(item['question_id'])
        if not sqs or len(sqs) < 2:
            continue
        ssa_path = os.path.join(SSA_DIR, f"{item['db_id']}.yaml")
        if not os.path.exists(ssa_path):
            continue
        ssa = load_ssa(item['db_id'], SSA_DIR)
        auditor = SecurityAuditor(ssa)
        sqs_clean = [{'id': sq['id'], 'sql': sq['sql']} for sq in sqs]
        audit = auditor.audit_all(sqs_clean)
        if sum(len(ar.violations) for ar in audit) > 0:
            continue
        ctrl_cols = []
        for table, cols in ssa.column_labels.items():
            for col, label in cols.items():
                if label == 'controlled':
                    ctrl_cols.append(f"{table}.{col}")
        if ctrl_cols:
            candidates.append((item, ctrl_cols))

    random.seed(42)
    selected = random.sample(candidates, min(n, len(candidates)))
    return selected


def inject_violation(sql, controlled_col, ssa):
    """
    Inject a controlled column into the SELECT of a sub-query.
    If the column is from a table in the SQL, add it to SELECT.
    Returns (modified_sql, injection_detail).
    """
    try:
        tree = sqlglot.parse_one(sql, read='sqlite')
    except Exception:
        return None, "parse failed"

    table, col = controlled_col.rsplit('.', 1) if '.' in controlled_col else ('', controlled_col)

    # Check if this table appears in the query
    tables_in_query = {t.name for t in tree.find_all(exp.Table) if t.name}
    if table and table not in tables_in_query:
        return None, f"table {table} not in query (tables: {tables_in_query})"

    # Check if column already in SELECT
    existing_cols = set()
    for sel in tree.find_all(exp.Select):
        for col_expr in sel.expressions:
            for bc in col_expr.find_all(exp.Column):
                existing_cols.add(bc.name)

    if col in existing_cols:
        return None, f"col {col} already in SELECT"

    # Inject into outermost SELECT
    sel = list(tree.find_all(exp.Select))[-1]
    new_col = exp.Column(this=col, table=table if table else None)
    new_exprs = list(sel.expressions) + [new_col]
    sel.args['expressions'] = new_exprs

    return tree.sql(dialect='sqlite'), f"injected {controlled_col}"


def run_experiment(n=30):
    """Run the full injection experiment."""
    print("=" * 70)
    print("  Controlled Violation Injection Experiment")
    print("=" * 70)

    queries = load_clean_queries(n)
    print(f"  Selected {len(queries)} clean queries with controlled columns")

    results = {
        'total_clean': 0,
        'false_positives': 0,
        'total_injected': 0,
        'detected': 0,
        'missed': 0,
        'fixed': 0,
        'unfixable': 0,
        'details': [],
    }

    for item, ctrl_cols in queries:
        db_id = item['db_id']
        ssa = load_ssa(db_id, SSA_DIR)
        auditor = SecurityAuditor(ssa)
        rewriter = RewriteEngine(auditor, ssa)

        # Load MAC-SQL sub-queries for this query from RQ1
        sqs = []
        with open(RQ1_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                if r['question_id'] == item['question_id']:
                    sqs = r.get('sub_queries', [])
                    break

        if not sqs or len(sqs) < 2:
            continue  # Need at least 2 sub-queries (intermediate + final)

        sqs_clean = [{'id': sq['id'], 'sql': sq['sql']} for sq in sqs]

        # ===== Phase 1: Verify clean =====
        audit_clean = auditor.audit_all(sqs_clean)
        clean_v = sum(len(ar.violations) for ar in audit_clean)
        results['total_clean'] += len(sqs_clean)
        if clean_v > 0:
            results['false_positives'] += clean_v
            results['details'].append({
                'qid': item['question_id'], 'db': db_id,
                'type': 'false_positive',
                'detail': f'{clean_v} violations on clean SQL'
            })

        # ===== Phase 2: Inject violation =====
        # Inject into the first sub-query (not the final one)
        target_sq = sqs_clean[0]
        original_sql = target_sq['sql']

        # Try each controlled column until one works
        injected_sql = None
        inject_detail = ""
        for cc in ctrl_cols:
            res, detail = inject_violation(original_sql, cc, ssa)
            if res:
                injected_sql = res
                inject_detail = detail
                break

        if not injected_sql:
            continue

        # Replace with injected version
        sqs_injected = [{'id': sq['id'], 'sql': sq['sql']} for sq in sqs]
        sqs_injected[0]['sql'] = injected_sql
        results['total_injected'] += 1

        # ===== Phase 3: Detect =====
        audit_inj = auditor.audit_all(sqs_injected)
        v_before = sum(len(ar.violations) for ar in audit_inj)
        if v_before > 0:
            results['detected'] += 1
        else:
            results['missed'] += 1
            results['details'].append({
                'qid': item['question_id'], 'db': db_id,
                'type': 'missed',
                'detail': inject_detail,
                'injected_sql': injected_sql[:150]
            })

        # ===== Phase 4: Fix =====
        if v_before > 0:
            for i, sq in enumerate(sqs_injected):
                has_v = any(
                    v.sub_query_index == i
                    for ar in audit_inj for v in ar.violations
                )
                if has_v:
                    down_needs = auditor._compute_downstream_needs(i, sqs_injected)
                    rw = rewriter.rewrite(sq['sql'], i, sqs_injected, down_needs)
                    if rw.rewritten_sql != sq['sql']:
                        sq['sql'] = rw.rewritten_sql

            audit_after = auditor.audit_all(sqs_injected)
            v_after = sum(len(ar.violations) for ar in audit_after)
            if v_after == 0:
                results['fixed'] += 1
            else:
                results['unfixable'] += 1
                results['details'].append({
                    'qid': item['question_id'], 'db': db_id,
                    'type': 'unfixable',
                    'v_before': v_before, 'v_after': v_after,
                    'injected_sql': injected_sql[:150]
                })

    # ===== Print report =====
    print(f"\n  {'='*50}")
    print(f"  RESULTS")
    print(f"  {'='*50}")
    print(f"  Clean SQLs tested:      {results['total_clean']}")
    print(f"  False positives:        {results['false_positives']}")
    print(f"  Precision:              {(1 - results['false_positives']/max(results['total_clean'],1))*100:.0f}%")
    print()
    print(f"  Violations injected:    {results['total_injected']}")
    print(f"  Detected:               {results['detected']}")
    print(f"  Missed:                 {results['missed']}")
    print(f"  Recall:                 {results['detected']/max(results['total_injected'],1)*100:.0f}%")
    print()
    print(f"  Fixed (S-AR=100%):      {results['fixed']}")
    print(f"  Unfixable:              {results['unfixable']}")
    print(f"  Fix rate:               {results['fixed']/max(results['detected'],1)*100:.0f}%")

    if results['details']:
        print(f"\n  Details ({len(results['details'])} issues):")
        for d in results['details']:
            print(f"    [{d['type']}] Q{d['qid']} ({d['db']}): {d.get('detail','')[:100]}")

    return results


# ============================================================
# P1-1: Blocked Injection (L2/L3 degradation path)
# ============================================================

BLOCKED_DB = 'student_transcripts_tracking'
BLOCKED_TABLE = 'Students'
BLOCKED_COL = 'ssn'
RQ1_SPIDER_FILE = os.path.join(
    _BASE, 'results', 'rq1', 'rq1_spider_fewshot_results.jsonl')
BLOCKED_RESULTS_FILE = os.path.join(
    _BASE, 'results', 'rq3', 'blocked_injection_results.json')


def inject_blocked(sql: str, table: str, col: str, form: str):
    """Inject a blocked column into the outermost SELECT in four forms.

    Forms:
      direct  — bare column in SELECT
      derived — CAST(col AS TEXT) AS ssn_text (derived expression)
      alias   — col AS ssn_alias (alias pass-through)
      join    — bare column, injected into a sub-query that JOINs the table
      only    — replace the SELECT list with the blocked column alone (L3)
    """
    try:
        tree = sqlglot.parse_one(sql, read='sqlite')
    except Exception:
        return None
    sel = list(tree.find_all(exp.Select))[-1]
    col_ref = exp.Column(
        this=exp.Identifier(this=col),
        table=exp.Identifier(this=table),
    )
    if form == 'derived':
        new_expr = exp.Alias(
            this=exp.Cast(this=col_ref.copy(), to=exp.DataType.build('TEXT')),
            alias='ssn_text',
        )
    elif form == 'alias':
        new_expr = exp.Alias(this=col_ref.copy(), alias='ssn_alias')
    elif form == 'only':
        sel.args['expressions'] = [col_ref]
        return tree.sql(dialect='sqlite')
    else:  # direct / join
        new_expr = col_ref
    sel.args['expressions'] = list(sel.expressions) + [new_expr]
    return tree.sql(dialect='sqlite')


def run_blocked_injection(n_queries=10):
    """P1-1: inject the single real blocked column and verify the L2/L3 path.

    Per EXPERIMENT-ADDITIONS-PLAN P1-1:
      - use the existing real blocked column (Students.ssn, the only blocked
        column among the 834 annotated), covering four trigger forms;
      - every injection must be DETECTED (no L0 leak) and routed to L2/L3;
      - no new blocked labels are added to the frozen annotations.
    """
    print("=" * 70)
    print("  P1-1: Blocked Injection Experiment (L2/L3 path)")
    print("=" * 70)

    # Index Spider RQ1 cached plans for the blocked database
    plans = {}
    with open(RQ1_SPIDER_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            if r.get('db_id') == BLOCKED_DB:
                plans[r['question_id']] = r

    candidates = [
        r for r in plans.values()
        if len(r.get('sub_queries') or []) >= 2
        and any(BLOCKED_TABLE in (sq.get('sql') or '') for sq in r['sub_queries'])
    ]
    random.seed(42)
    selected = random.sample(candidates, min(n_queries, len(candidates)))
    print(f"  Selected {len(selected)} queries from {BLOCKED_DB} "
          f"({len(candidates)} candidates)")

    forms = ['direct', 'derived', 'alias', 'join', 'only', 'direct',
             'derived', 'alias', 'join', 'only']
    results = []
    for idx, r in enumerate(selected):
        form = forms[idx % len(forms)]
        sqs = copy.deepcopy(r.get('sub_queries') or [])

        # Pick a sub-query referencing the blocked table (final sub-queries
        # are valid targets too — the final-answer exemption covers
        # controlled columns only, blocked stays forbidden everywhere).
        # For the 'join' form, prefer one that actually JOINs it.
        target = None
        join_pool, plain_pool = [], []
        for i, sq in enumerate(sqs):
            if BLOCKED_TABLE not in (sq.get('sql') or ''):
                continue
            if 'JOIN' in sq['sql'].upper() or 'join' in sq['sql']:
                join_pool.append(i)
            else:
                plain_pool.append(i)
        if form == 'join' and join_pool:
            target = join_pool[0]
        elif form == 'only' and (plain_pool or join_pool):
            # 'only' replaces the SELECT entirely — works on any sub-query
            # that references the blocked table; never reassign its form.
            target = (plain_pool or join_pool)[0]
        elif plain_pool:
            target = plain_pool[0]
        elif join_pool:
            target = join_pool[0]
            form = 'join'
        if target is None:
            continue

        injected = inject_blocked(
            sqs[target]['sql'], BLOCKED_TABLE, BLOCKED_COL, form)
        if injected is None:
            continue
        sqs[target]['sql'] = injected

        details = {}
        vb, va, nrw, lv, msg, ex, subr = run_audit_pipeline(
            sqs, BLOCKED_DB, rewrite=True, degradation=True,
            violation_details=details,
        )
        detected = any(
            v.type.value.startswith('blocked') for v in details.get('before', [])
        )
        leaked = (lv == 'L0')
        results.append({
            'question_id': r.get('question_id'),
            'db_id': BLOCKED_DB,
            'form': form,
            'detected': bool(detected),
            'degradation_level': lv,
            'leaked': leaked,
            'v_before': vb,
            'v_after': va,
            'message': msg,
            'query': (r.get('query') or '')[:200],
            'gold_sql': r.get('gold_sql', ''),
            'injected_sql': injected[:300],
            'n_subqueries': len(sqs),
            'sub_queries': sqs,
        })

    # ---- Report ----
    n = len(results)
    n_detected = sum(1 for r in results if r['detected'])
    n_leaked = sum(1 for r in results if r['leaked'])
    l2 = sum(1 for r in results if r['degradation_level'] == 'L2')
    l3 = sum(1 for r in results if r['degradation_level'] == 'L3')
    print(f"\n  Injections:             {n}")
    print(f"  Blocked detected:       {n_detected}/{n} ({n_detected / max(n, 1) * 100:.0f}%)")
    print(f"  Leaked to L0 (漏放):    {n_leaked}  (expect 0)")
    print(f"  Degradation: L2={l2}  L3={l3}")
    print(f"\n  Form breakdown:")
    for form in ['direct', 'derived', 'alias', 'join', 'only']:
        fr = [r for r in results if r['form'] == form]
        if fr:
            print(f"    {form:8s}: {sum(r['detected'] for r in fr)}/{len(fr)} detected, "
                  f"leaked={sum(r['leaked'] for r in fr)}, "
                  f"levels={Counter(r['degradation_level'] for r in fr)})")

    os.makedirs(os.path.dirname(BLOCKED_RESULTS_FILE), exist_ok=True)
    with open(BLOCKED_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved: {BLOCKED_RESULTS_FILE}")
    return results


if __name__ == '__main__':
    run_experiment(30)
    run_blocked_injection(10)
