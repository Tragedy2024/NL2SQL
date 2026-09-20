# flight_2 — Spider SSA Review

> Database: 
> Tables: 3
> SSA: auto-generated (column-name heuristic, NO human review)

## airlines — 4 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | abbreviation | free |
|  | airline name | free |
|  | country | free |
|  | airline id | free |

## airports — 1 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | airport name | **controlled** |  |

## airports — 4 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | airport code | free |
|  | city | free |
|  | country | free |
|  | country abbrev | free |

## flights — 4 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | airline | free |
|  | destination airport | free |
|  | flight number | free |
|  | source airport | free |

---
**Total**: 1 controlled, 12 free

## Generation Rules Used

