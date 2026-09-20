# world_1 — Spider SSA Review

> Database: 
> Tables: 4
> SSA: auto-generated (column-name heuristic, NO human review)

## city — 1 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | name | **controlled** |  |

## city — 4 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | country code | free |
|  | district | free |
|  | id | free |
|  | population | free |

## country — 2 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | local name | **controlled** |  |
|  | name | **controlled** |  |

## country — 13 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | capital | free |
|  | code | free |
|  | code2 | free |
|  | continent | free |
|  | gnp | free |
|  | gnp old | free |
|  | government form | free |
|  | head of state | free |
|  | indepdent year | free |
|  | life expectancy | free |
|  | population | free |
|  | region | free |
|  | surface area | free |

## countrylanguage — 2 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | language | **controlled** |  |
|  | percentage | **controlled** |  |

## countrylanguage — 2 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | countrycode | free |
|  | is official | free |

## sqlite_sequence — 1 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | name | **controlled** |  |

## sqlite_sequence — 1 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | seq | free |

---
**Total**: 6 controlled, 20 free

## Generation Rules Used

