# pets_1 — Spider SSA Review

> Database: 
> Tables: 3
> SSA: auto-generated (column-name heuristic, NO human review)

## Has_Pet — 2 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | pet id | free |
|  | student id | free |

## Pets — 1 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | pet age | **controlled** |  |

## Pets — 3 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | pet id | free |
|  | pet type | free |
|  | weight | free |

## Student — 3 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | age | **controlled** |  |
|  | first name | **controlled** |  |
|  | last name | **controlled** |  |

## Student — 5 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | advisor | free |
|  | major | free |
|  | sex | free |
|  | student id | free |
|  | city code | free |

---
**Total**: 4 controlled, 10 free

## Generation Rules Used

