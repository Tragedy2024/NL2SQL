"""Generate SSA review markdown files for all 11 databases."""
import os, csv, yaml

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.insert(0, os.path.join(_ROOT, 'src'))
from config import BIRD_DIR, BIRD_DB_PATH, SSA_DIR

BASE = BIRD_DIR
DB_DIR = BIRD_DB_PATH
REVIEW_DIR = os.path.join(SSA_DIR, 'review')
os.makedirs(REVIEW_DIR, exist_ok=True)

def classify_reason(table, col, label, csv_info):
    desc = csv_info.get('desc', '')
    dtype = csv_info.get('type', '')
    if not desc:
        desc_lower = col.lower()
        if any(kw in desc_lower for kw in ['id', '_id', 'code', '_cd']):
            desc = 'identifier/code'
        elif any(kw in desc_lower for kw in ['name', 'title']):
            desc = 'name'
        elif any(kw in desc_lower for kw in ['date', 'year', 'month']):
            desc = 'date/time'
        elif any(kw in desc_lower for kw in ['type', 'status', 'category']):
            desc = 'type/status'
        elif any(kw in desc_lower for kw in ['count', 'number', 'amount', 'price']):
            desc = 'numeric value'
        elif any(kw in desc_lower for kw in ['email', 'phone', 'address']):
            desc = 'contact info'
        elif any(kw in desc_lower for kw in ['first', 'last']):
            desc = 'person name'
        else:
            desc = '(no description)'

    col_lower = col.lower()
    desc_lower = desc.lower()

    if label == 'free':
        if any(kw in col_lower for kw in ['id', '_id', 'code', '_cd']):
            return 'identifier, no personal semantics'
        if any(kw in col_lower for kw in ['date', 'year', 'month', 'day']):
            return 'date field, not linked to specific individual'
        if any(kw in col_lower for kw in ['type', 'status', 'category', 'kind', 'format', 'layout', 'rarity', 'color', 'border']):
            return 'category/label, public attribute'
        if any(kw in col_lower for kw in ['name']):
            if any(kw in desc_lower for kw in ['school', 'district', 'county', 'organization', 'league', 'team', 'country']):
                return 'organization/entity name, public information'
            if any(kw in desc_lower for kw in ['card', 'artist', 'set']):
                return 'entity name, public information'
            return 'entity name, public information'
        if any(kw in col_lower for kw in ['count', 'number', 'total', 'avg', 'percent', 'rate', 'enroll']):
            return 'aggregate statistic or count, not individual-level'
        if any(kw in col_lower for kw in ['latitude', 'longitude', 'location']):
            return 'geographic coordinates, public data'
        if any(kw in col_lower for kw in ['website', 'url']):
            return 'public website address'
        if any(kw in desc_lower for kw in ['identifier', 'code', 'number', 'reference']):
            return 'identifier or code'
        if any(kw in desc_lower for kw in ['statistics', 'aggregate', 'count', 'total', 'average', 'percentage']):
            return 'aggregate/statistical data'
        if any(kw in desc_lower for kw in ['name', 'school', 'district', 'county', 'organization', 'public']):
            return 'organization/entity public information'
        return 'public/non-personal data'

    elif label == 'controlled':
        if any(kw in col_lower for kw in ['email', 'mail']):
            return 'personal contact (email), traceable to individual'
        if any(kw in col_lower for kw in ['phone', 'tel']):
            return 'personal contact (phone), traceable to individual'
        if any(kw in col_lower for kw in ['address', 'street']):
            return 'personal/institutional address'
        if any(kw in col_lower for kw in ['city', 'zip']):
            return 'location detail, may locate individual/institution'
        if any(kw in col_lower for kw in ['salary', 'income', 'revenue', 'bonus']):
            return 'personal financial data, aggregatable'
        if any(kw in col_lower for kw in ['amount', 'balance', 'payment', 'fee', 'price']):
            return 'financial amount, may link to personal transactions'
        if any(kw in col_lower for kw in ['adm', 'admin']):
            if any(kw in col_lower for kw in ['fname', 'lname', 'name']):
                return 'administrator name, personal identifier'
            if any(kw in col_lower for kw in ['email']):
                return 'administrator email, personal contact'
            return 'administrative personal data'
        if any(kw in col_lower for kw in ['first', 'last', 'full']):
            if any(kw in col_lower for kw in ['name']):
                return 'personal name, traceable to individual'
        if any(kw in col_lower for kw in ['score', 'grade', 'rating']):
            return 'personal score/rating, reflects individual performance'
        if any(kw in col_lower for kw in ['hours', 'worked', 'attendance']):
            return 'personal activity record'
        if any(kw in col_lower for kw in ['account_to']):
            return 'financial account identifier'
        if any(kw in col_lower for kw in ['birth', 'age', 'gender', 'race', 'ethnicity']):
            return 'personal identity attribute'
        if any(kw in col_lower for kw in ['a11']):
            return 'BIRD anonymous column; CSV description may reference personal/financial data'
        if any(kw in desc_lower for kw in ['salary', 'income', 'financial', 'amount']):
            return 'financial data, aggregatable'
        if any(kw in desc_lower for kw in ['personal', 'individual', 'person']):
            return 'individual-level information'
        if any(kw in desc_lower for kw in ['email', 'phone', 'contact']):
            return 'personal contact information'
        if any(kw in desc_lower for kw in ['name', 'first name', 'last name']):
            return 'personal name'
        if any(kw in desc_lower for kw in ['administrator']):
            return 'administrator personal information'
        return 'personal or financial data, requires controlled exposure'

    elif label == 'blocked':
        if any(kw in col_lower for kw in ['hiv', 'genetic', 'dna', 'ssn', 'passport']):
            return 'legally protected data, cannot be exposed in any form'
        if any(kw in col_lower for kw in ['diagnosis', 'medical', 'patient', 'disease']):
            return 'medical data, strictly legally protected'
        if any(kw in desc_lower for kw in ['medical', 'diagnosis', 'hiv', 'disease', 'cancer']):
            return 'medical diagnostic data, strictly legally protected'
        if any(kw in desc_lower for kw in ['laboratory', 'blood', 'platelet', 'uric', 'glucose']):
            return 'laboratory test result, legally protected'
        if any(kw in desc_lower for kw in ['examination', 'patient', 'diagnosis']):
            return 'medical examination data, legally protected'
        return 'legally protected sensitive data'
    return ''


db_ids = sorted([d for d in os.listdir(DB_DIR) if os.path.isdir(os.path.join(DB_DIR, d)) and not d.startswith('.')])

for db_id in db_ids:
    ssa_path = os.path.join(SSA_DIR, f'{db_id}.yaml')
    ssa = {}
    if os.path.exists(ssa_path):
        with open(ssa_path, 'r', encoding='utf-8') as f:
            ssa = yaml.safe_load(f) or {}
    col_labels = ssa.get('column_labels', {})

    desc_dir = os.path.join(DB_DIR, db_id, 'database_description')
    csv_descs = {}
    if os.path.isdir(desc_dir):
        for csv_file in os.listdir(desc_dir):
            if not csv_file.endswith('.csv'):
                continue
            table = csv_file.replace('.csv', '')
            csv_path = os.path.join(desc_dir, csv_file)
            try:
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        orig = (row.get('original_column_name', '') or '').strip()
                        desc = (row.get('column_description', '') or '').strip()
                        if orig:
                            csv_descs[f'{table}.{orig}'] = {'desc': desc}
            except Exception as e:
                print(f'  WARN: {db_id}/{csv_file}: {e}')

    lines = []
    lines.append(f'# {db_id} — SSA label review')
    lines.append('')
    lines.append(f'> **Database**: `{db_id}`')
    lines.append(f'> **Tables**: {len(col_labels)}')

    total_cols = sum(len(cols) for cols in col_labels.values())
    ctrl = sum(1 for cols in col_labels.values() for l in cols.values() if l == 'controlled')
    blk = sum(1 for cols in col_labels.values() for l in cols.values() if l == 'blocked')
    free_n = sum(1 for cols in col_labels.values() for l in cols.values() if l == 'free')
    lines.append(f'> **Columns**: {total_cols} total (free={free_n}, controlled={ctrl}, blocked={blk})')
    lines.append(f'> **Status**: AUTO-GENERATED — requires human review')
    lines.append('')
    lines.append('---')
    lines.append('')

    for table in sorted(col_labels.keys()):
        cols = col_labels[table]
        lines.append(f'## `{table}`')
        lines.append('')
        lines.append('| Column | Description | ECL | Reason | Review |')
        lines.append('|--------|-------------|-----|--------|--------|')
        for col in sorted(cols.keys()):
            label = cols[col]
            key = f'{table}.{col}'
            csv_info = csv_descs.get(key, {})
            desc = csv_info.get('desc', '')
            if desc:
                desc = desc[:100].replace('|', '/').replace('\n', ' ').replace('\r', '')
            reason = classify_reason(table, col, label, csv_info)
            lines.append(f'| `{col}` | {desc} | **{label}** | {reason} |  |')
        lines.append('')

    cross_rules = ssa.get('cross_domain_rules', [])
    if cross_rules:
        lines.append('## Cross-Domain Rules')
        lines.append('')
        for rule in cross_rules:
            tp = rule.get('table_pair', [])
            lines.append(f'- **{tp[0]} <-> {tp[1]}** (JOIN key: `{rule.get("join_key", "")}`)')
            lines.append(f'  - Forbid personal-level: {rule.get("forbid_personal_level", False)}')
            lines.append(f'  - Allow aggregate-level: {rule.get("allow_aggregate_level", True)}')
            lines.append(f'  - Reason: {rule.get("reason", "")}')
        lines.append('')
    else:
        lines.append('## Cross-Domain Rules')
        lines.append('')
        lines.append('(none defined yet)')
        lines.append('')

    lines.append('---')
    lines.append(f'*Edit `config/ssa/{db_id}.yaml` after review. Then re-run pilot/RQ1 for updated results.*')

    review_path = os.path.join(REVIEW_DIR, f'{db_id}.md')
    with open(review_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'  {db_id}: {total_cols} cols (free={free_n} ctrl={ctrl} blk={blk})')

print(f'\nDone. {len(db_ids)} files in {REVIEW_DIR}')
