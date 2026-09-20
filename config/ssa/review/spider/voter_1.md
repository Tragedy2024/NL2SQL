# voter_1 — Spider SSA Review

> Database: 
> Tables: 3
> SSA: auto-generated (column-name heuristic, NO human review)

## AREA_CODE_STATE — 2 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | area code | free |
|  | state | free |

## CONTESTANTS — 1 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | contestant name | **controlled** |  |

## CONTESTANTS — 1 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | contestant number | free |

## VOTES — 1 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | phone number | **controlled** |  |

## VOTES — 4 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | contestant number | free |
|  | created | free |
|  | state | free |
|  | vote id | free |

---
**Total**: 2 controlled, 7 free

## Generation Rules Used

