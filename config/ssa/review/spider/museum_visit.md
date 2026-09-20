# museum_visit — Spider SSA Review

> Database: 
> Tables: 3
> SSA: auto-generated (column-name heuristic, NO human review)

## museum — 1 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | name | **controlled** |  |

## museum — 3 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | museum id | free |
|  | num of staff | free |
|  | open year | free |

## visit — 4 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | museum id | free |
|  | num of ticket | free |
|  | total spent | free |
|  | customer id | free |

## visitor — 2 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | age | **controlled** |  |
|  | name | **controlled** |  |

## visitor — 2 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | customer id | free |
|  | level of membership | free |

---
**Total**: 3 controlled, 9 free

## Generation Rules Used

