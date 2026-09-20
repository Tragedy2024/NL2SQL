"""Apply BIRD-aligned review standards to Spider SSA labels."""
import yaml, os, json, sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_ROOT, 'src'))
from config import SSA_DIR, SPIDER_DIR

BASE = SPIDER_DIR

with open(os.path.join(BASE, 'tables.json')) as f:
    tables = json.load(f)
with open(os.path.join(BASE, 'dev.json')) as f:
    dev = json.load(f)
dev_dbs = set(d['db_id'] for d in dev)

changes = {
    # === PUBLIC FIGURES / PERFORMERS → free ===
    'wta_1': {
        'matches': {'winner_name': 'free','loser_name': 'free','tourney_name': 'free',
                     'winner_age': 'free','loser_age': 'free'},
        'players': {'first_name': 'free','last_name': 'free'},
    },
    'concert_singer': {
        'singer': {'Name': 'free','Song_Name': 'free'},
        'concert': {'concert_Name': 'free'},
        'stadium': {'Name': 'free','Average': 'free'},
    },
    'poker_player': {
        'people': {'Name': 'free'},
    },
    'orchestra': {
        'conductor': {'Name': 'free'},
    },
    # === ORGANIZATION / ENTITY NAMES → free ===
    'flight_2': {
        'airports': {'AirportName': 'free'},
    },
    'museum_visit': {
        'museum': {'Name': 'free'},
    },
    'battle_death': {
        'battle': {'name': 'free'},
        'ship': {'name': 'free','tonnage': 'free'},
    },
    'student_transcripts_tracking': {
        'Courses': {'course_name': 'free'},
        'Degree_Programs': {'degree_summary_name': 'free'},
        'Departments': {'department_name': 'free'},
        'Sections': {'section_name': 'free'},
        'Semesters': {'semester_name': 'free'},
    },
    'cre_Doc_Template_Mgt': {
        'Documents': {'Document_Name': 'free'},
    },
    'world_1': {
        'city': {'Name': 'free'},
        'country': {'Name': 'free','LocalName': 'free'},
        'countrylanguage': {'Language': 'free','Percentage': 'free'},
        'sqlite_sequence': {'name': 'free'},
    },
    'car_1': {
        'car_makers': {'FullName': 'free'},
        'countries': {'CountryName': 'free'},
    },
    'tvshow': {
        'TV_Channel': {'series_name': 'free','Language': 'free','Package_Option': 'free'},
    },
    'real_estate_properties': {
        'Other_Available_Features': {'feature_name': 'free'},
        'Properties': {'property_name': 'free'},
        'Ref_Feature_Types': {'feature_type_name': 'free'},
    },
    'voter_1': {
        'CONTESTANTS': {'contestant_name': 'free'},
    },
    # === DOG/PET NAMES → free ===
    'dog_kennels': {
        'Breeds': {'breed_name': 'free'},
        'Dogs': {'name': 'free'},
    },
    'pets_1': {
        'Pets': {'pet_age': 'free'},
    },
    # === SSN → blocked ===
    'student_transcripts_tracking': {
        'Students': {'ssn': 'blocked'},
    },
    # === SHOP → keep controlled (regular employees, not public) ===
    # employee_hire_evaluation: employee.Name/Age, shop.Manager_name stay controlled
    # === PERSONAL → keep controlled ===
    # dog_kennels: Owners/Professionals first/last/email/phone stay controlled
    # pets_1: Student Fname/LName/Age stay controlled
    # concert_singer: singer.Age stays controlled
    # museum_visit: visitor.Name/Age stays controlled
    # student_transcripts_tracking: Students first/last/email, Addresses stay controlled
    # network_1: Highschooler.name stays controlled
    # course_teach: teacher.Name/Age stay controlled
    # voter_1: phone_number stays controlled
    # real_estate_properties: property_address stays controlled
    # orchestra: conductor.Age stays controlled
    # dog_kennels: Dogs.age stays controlled
}

counts = {'controlled→free': 0, 'controlled→blocked': 0, 'controlled→controlled': 0}

for db_id, tables_changes in changes.items():
    path = os.path.join(SSA_DIR, f'{db_id}.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        ssa = yaml.safe_load(f)

    for table, cols in tables_changes.items():
        if table not in ssa.get('column_labels', {}):
            continue
        for col, new_label in cols.items():
            if col not in ssa['column_labels'][table]:
                continue
            old = ssa['column_labels'][table][col]
            ssa['column_labels'][table][col] = new_label
            print(f'  {db_id}.{table}.{col}: {old} → {new_label}')
            counts[f'{old}→{new_label}'] = counts.get(f'{old}→{new_label}', 0) + 1

    ssa['annotator'] = 'auto-generated + human_review_aligned'
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(ssa, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print(f'\nSummary: {counts}')

# Final stats
total_ctrl = 0; total_blocked = 0; total_free = 0
for db in tables:
    db_id = db['db_id']
    if db_id not in dev_dbs:
        continue
    path = os.path.join(SSA_DIR, f'{db_id}.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        ssa = yaml.safe_load(f)
    for table, cols in ssa.get('column_labels', {}).items():
        for col, label in cols.items():
            if label == 'free': total_free += 1
            elif label == 'controlled': total_ctrl += 1
            elif label == 'blocked': total_blocked += 1

print(f'Final: free={total_free}, controlled={total_ctrl}, blocked={total_blocked}')
