# dog_kennels — Spider SSA Review

> Database: 
> Tables: 8
> SSA: auto-generated (column-name heuristic, NO human review)

## Breeds — 1 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | breed name | **controlled** |  |

## Breeds — 1 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | breed code | free |

## Charges — 3 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | charge amount | free |
|  | charge id | free |
|  | charge type | free |

## Dogs — 2 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | age | **controlled** |  |
|  | name | **controlled** |  |

## Dogs — 11 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | abandoned yes or no | free |
|  | breed code | free |
|  | date adopted | free |
|  | date arrived | free |
|  | date departed | free |
|  | date of birth | free |
|  | dog id | free |
|  | gender | free |
|  | owner id | free |
|  | size code | free |
|  | weight | free |

## Owners — 4 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | email address | **controlled** |  |
|  | first name | **controlled** |  |
|  | home phone | **controlled** |  |
|  | last name | **controlled** |  |

## Owners — 6 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | cell number | free |
|  | city | free |
|  | owner id | free |
|  | state | free |
|  | street | free |
|  | zip code | free |

## Professionals — 4 controlled columns

| Column | Description | Current | Review |
|--------|-------------|---------|--------|
|  | email address | **controlled** |  |
|  | first name | **controlled** |  |
|  | home phone | **controlled** |  |
|  | last name | **controlled** |  |

## Professionals — 7 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | cell number | free |
|  | city | free |
|  | professional id | free |
|  | role code | free |
|  | state | free |
|  | street | free |
|  | zip code | free |

## Sizes — 2 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | size code | free |
|  | size description | free |

## Treatment_Types — 2 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | treatment type code | free |
|  | treatment type description | free |

## Treatments — 6 free columns (for context)

| Column | Description | Current |
|--------|-------------|---------|
|  | cost of treatment | free |
|  | date of treatment | free |
|  | dog id | free |
|  | professional id | free |
|  | treatment id | free |
|  | treatment type code | free |

---
**Total**: 11 controlled, 38 free

## Generation Rules Used

