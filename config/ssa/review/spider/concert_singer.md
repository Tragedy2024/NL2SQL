# concert_singer — Spider SSA Review

> Database: 
> Tables: 4
> SSA: auto-generated (column-name heuristic, NO human review)

## concert — 1 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | concert name | **controlled** |  |

## concert — 4 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | stadium id | free |
|  | theme | free |
|  | year | free |
|  | concert id | free |

## singer — 3 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | age | **controlled** |  |
|  | name | **controlled** |  |
|  | song name | **controlled** |  |

## singer — 4 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | country | free |
|  | is male | free |
|  | singer id | free |
|  | song release year | free |

## singer_in_concert — 2 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | singer id | free |
|  | concert id | free |

## stadium — 2 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | average | **controlled** |  |
|  | name | **controlled** |  |

## stadium — 5 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | capacity | free |
|  | highest | free |
|  | location | free |
|  | lowest | free |
|  | stadium id | free |

---
**Total**: 6 controlled, 15 free

## Generation Rules Used

