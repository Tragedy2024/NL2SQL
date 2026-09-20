"""Apply all SSA review changes to YAML files."""
import yaml, os, sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_ROOT, 'src'))
from config import SSA_DIR

changes = {
    'california_schools': {
        'schools': {
            'AdmFName1': 'free', 'AdmFName2': 'free', 'AdmFName3': 'free',
            'AdmLName1': 'free', 'AdmLName2': 'free', 'AdmLName3': 'free',
            'AdmEmail1': 'free', 'AdmEmail2': 'free', 'AdmEmail3': 'free',
            'Phone': 'free', 'Ext': 'free',
        }
    },
    'thrombosis_prediction': {
        'Examination': {
            'ANA': 'controlled', 'ANA Pattern': 'controlled',
            'Diagnosis': 'controlled', 'KCT': 'controlled',
            'LAC': 'controlled', 'RVVT': 'controlled',
            'Symptoms': 'controlled', 'Thrombosis': 'controlled',
            'aCL IgA': 'controlled', 'aCL IgG': 'controlled', 'aCL IgM': 'controlled',
            'Age': 'controlled', 'Date': 'free', 'ID': 'free',
        },
        'Laboratory': {
            'ALB': 'controlled', 'ALP': 'controlled', 'APTT': 'controlled',
            'C3': 'controlled', 'C4': 'controlled', 'CENTROMEA': 'controlled',
            'CPK': 'controlled', 'CRE': 'controlled', 'CRP': 'controlled',
            'DNA': 'controlled', 'DNA-II': 'controlled',
            'FG': 'controlled', 'GLU': 'controlled', 'GOT': 'controlled',
            'GPT': 'controlled', 'HCT': 'controlled', 'HGB': 'controlled',
            'IGA': 'controlled', 'IGG': 'controlled', 'IGM': 'controlled',
            'LDH': 'controlled', 'PIC': 'controlled', 'PLT': 'controlled',
            'PT': 'controlled', 'RA': 'controlled', 'RBC': 'controlled',
            'RF': 'controlled', 'RNP': 'controlled', 'SC170': 'controlled',
            'SM': 'controlled', 'SSA': 'controlled', 'SSB': 'controlled',
            'T-BIL': 'controlled', 'T-CHO': 'controlled',
            'TAT': 'controlled', 'TAT2': 'controlled', 'TG': 'controlled',
            'TP': 'controlled', 'U-PRO': 'controlled', 'UA': 'controlled',
            'UN': 'controlled', 'WBC': 'controlled',
            'ID': 'free', 'Date': 'free',
        },
        'Patient': {
            'Diagnosis': 'controlled',
        }
    },
    'student_club': {
        'expense': {'expense_description': 'free'},
        'income': {'notes': 'free'},
    },
    'codebase_community': {
        'comments': {'UserDisplayName': 'free'},
        'postHistory': {'UserDisplayName': 'free'},
        'posts': {'OwnerDisplayName': 'free', 'LastEditorDisplayName': 'free'},
        'users': {'DisplayName': 'free', 'ProfileImageUrl': 'free',
                   'WebsiteUrl': 'free', 'AboutMe': 'free'},
    },
    'card_games': {
        'cards': {'artist': 'free'},
    },
    'debit_card_specializing': {
        'transactions_1k': {'CardID': 'free'},
        'yearmonth': {'Consumption': 'free'},
    },
    'european_football_2': {
        'Player': {'player_name': 'free', 'birthday': 'free',
                    'height': 'free', 'weight': 'free'},
    },
    'formula_1': {
        'drivers': {'forename': 'free', 'surname': 'free', 'dob': 'free',
                     'code': 'free', 'driverRef': 'free'},
    },
    'superhero': {
        'superhero': {'full_name': 'free', 'superhero_name': 'free'},
    },
    # financial: no changes (GPT-4o was correct)
    # toxicology: no changes (all free)
}

for db_id, tables in changes.items():
    path = os.path.join(SSA_DIR, f'{db_id}.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        ssa = yaml.safe_load(f)

    for table, cols in tables.items():
        if table not in ssa['column_labels']:
            print(f'  WARN: {db_id}.{table} not found')
            continue
        for col, new_label in cols.items():
            if col not in ssa['column_labels'][table]:
                print(f'  WARN: {db_id}.{table}.{col} not found')
                continue
            old_label = ssa['column_labels'][table][col]
            ssa['column_labels'][table][col] = new_label
            if old_label != new_label:
                print(f'  {db_id}.{table}.{col}: {old_label} → {new_label}')

    # Update metadata
    ssa['annotator'] = 'GPT-4o + human_review'
    ssa['review_date'] = '2026-07-20'

    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(ssa, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f'  Saved: {db_id}.yaml')

# Stats
total_ctrl = 0
total_blocked = 0
total_free = 0
for db_id in sorted(os.listdir(SSA_DIR)):
    path = os.path.join(SSA_DIR, db_id)
    if not db_id.endswith('.yaml'):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        ssa = yaml.safe_load(f)
    for table, cols in ssa.get('column_labels', {}).items():
        for col, label in cols.items():
            if label == 'free': total_free += 1
            elif label == 'controlled': total_ctrl += 1
            elif label == 'blocked': total_blocked += 1

print(f'\nFinal: free={total_free}, controlled={total_ctrl}, blocked={total_blocked}')
