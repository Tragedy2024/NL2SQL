# employee_hire_evaluation — Spider SSA Review

> Database: 
> Tables: 4
> SSA: auto-generated (column-name heuristic, NO human review)

## employee — 2 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | age | **controlled** |  |
|  | name | **controlled** |  |

## employee — 2 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | city | free |
|  | employee id | free |

## evaluation — 3 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | bonus | free |
|  | employee id | free |
|  | year awarded | free |

## hiring — 4 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | employee id | free |
|  | is full time | free |
|  | shop id | free |
|  | start from | free |

## shop — 2 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | manager name | **controlled** |  |
|  | name | **controlled** |  |

## shop — 4 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | district | free |
|  | location | free |
|  | number products | free |
|  | shop id | free |

---
**Total**: 4 controlled, 13 free

## Generation Rules Used

