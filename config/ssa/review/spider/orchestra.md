# orchestra — Spider SSA Review

> Database: 
> Tables: 4
> SSA: auto-generated (column-name heuristic, NO human review)

## conductor — 2 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | age | **controlled** |  |
|  | name | **controlled** |  |

## conductor — 3 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | conductor id | free |
|  | nationality | free |
|  | year of work | free |

## orchestra — 6 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | conductor id | free |
|  | major record format | free |
|  | orchestra | free |
|  | orchestra id | free |
|  | record company | free |
|  | year of founded | free |

## performance — 7 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | date | free |
|  | official ratings (millions) | free |
|  | orchestra id | free |
|  | performance id | free |
|  | share | free |
|  | type | free |
|  | weekly rank | free |

## show — 5 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | attendance | free |
|  | if first show | free |
|  | performance id | free |
|  | result | free |
|  | show id | free |

---
**Total**: 2 controlled, 21 free

## Generation Rules Used

