# formula_1 — SSA 标签审查

> **数据库**: `formula_1`
> **表**: 13
> **列**: 94 总计 (free=89, controlled=5, blocked=0)
> **状态**: 自动生成 — 需要人工审查

---

## `circuits`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `alt` |  | **free** | 公开/非个人数据 |  |
| `circuitId` | unique identification number of the circuit | **free** | 标识符，无个人语义 |  |
| `circuitRef` | circuit reference name | **free** | 标识符或代码 |  |
| `country` | country of circuit | **free** | 聚合统计数据或计数，非个人级别 |  |
| `lat` | latitude of location of circuit | **free** | 公开/非个人数据 |  |
| `lng` | longitude of location of circuit | **free** | 公开/非个人数据 |  |
| `location` | location of circuit | **free** | 地理坐标，公开数据 |  |
| `name` | full name of circuit | **free** | 实体名称，公开信息 |  |
| `url` | url | **free** | 公开网站地址 |  |

## `constructorResults`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `constructorId` | constructor id | **free** | 标识符，无个人语义 |  |
| `constructorResultsId` | constructor Results Id | **free** | 标识符，无个人语义 |  |
| `points` | points | **free** | 公开/非个人数据 |  |
| `raceId` | race id | **free** | 标识符，无个人语义 |  |
| `status` | status | **free** | 类别/标签，公开属性 |  |

## `constructorStandings`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `constructorId` | id number identifying which id | **free** | 标识符，无个人语义 |  |
| `constructorStandingsId` | unique identification of the constructor standing records | **free** | 标识符，无个人语义 |  |
| `points` | how many points acquired in each race | **free** | 公开/非个人数据 |  |
| `position` | position or track of circuits | **free** | 公开/非个人数据 |  |
| `positionText` |  | **free** | 公开/非个人数据 |  |
| `raceId` | id number identifying which races | **free** | 标识符，无个人语义 |  |
| `wins` | wins | **free** | 公开/非个人数据 |  |

## `constructors`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `constructorId` | the unique identification number identifying constructors | **free** | 标识符，无个人语义 |  |
| `constructorRef` | Constructor Reference name | **free** | 标识符或代码 |  |
| `name` | full name of the constructor | **free** | 实体名称，公开信息 |  |
| `nationality` | nationality of the constructor | **free** | 公开/非个人数据 |  |
| `url` | the introduction website of the constructor | **free** | 公开网站地址 |  |

## `driverStandings`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `driverId` | id number identifying which drivers | **free** | 标识符，无个人语义 |  |
| `driverStandingsId` | the unique identification number identifying driver standing records | **free** | 标识符，无个人语义 |  |
| `points` | how many points acquired in each race | **free** | 公开/非个人数据 |  |
| `position` | position or track of circuits | **free** | 公开/非个人数据 |  |
| `positionText` |  | **free** | 公开/非个人数据 |  |
| `raceId` | id number identifying which races | **free** | 标识符，无个人语义 |  |
| `wins` | wins | **free** | 公开/非个人数据 |  |

## `drivers`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `code` | abbreviated code for drivers | **controlled** | 个人或财务数据，需要受控暴露 |  |
| `dob` | date of birth | **controlled** | 个人或财务数据，需要受控暴露 |  |
| `driverId` | the unique identification number identifying each driver | **free** | 标识符，无个人语义 |  |
| `driverRef` | driver reference name | **controlled** | 个人姓名 |  |
| `forename` | forename | **controlled** | 个人姓名 |  |
| `nationality` | nationality of drivers | **free** | 公开/非个人数据 |  |
| `number` | number | **free** | 聚合统计数据或计数，非个人级别 |  |
| `surname` | surname | **controlled** | 个人姓名 |  |
| `url` | the introduction website of the drivers | **free** | 公开网站地址 |  |

## `lapTimes`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `driverId` | the identification number identifying each driver | **free** | 标识符，无个人语义 |  |
| `lap` | lap number | **free** | 标识符或代码 |  |
| `milliseconds` | milliseconds | **free** | 公开/非个人数据 |  |
| `position` | position or track of circuits | **free** | 公开/非个人数据 |  |
| `raceId` | the identification number identifying race | **free** | 标识符，无个人语义 |  |
| `time` | lap time | **free** | 公开/非个人数据 |  |

## `pitStops`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `driverId` | the identification number identifying each driver | **free** | 标识符，无个人语义 |  |
| `duration` | duration time | **free** | 公开/非个人数据 |  |
| `lap` | lap number | **free** | 标识符或代码 |  |
| `milliseconds` | milliseconds | **free** | 公开/非个人数据 |  |
| `raceId` | the identification number identifying race | **free** | 标识符，无个人语义 |  |
| `stop` | stop number | **free** | 标识符或代码 |  |
| `time` | time | **free** | 公开/非个人数据 |  |

## `qualifying`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `constructorId` |  | **free** | 标识符，无个人语义 |  |
| `driverId` |  | **free** | 标识符，无个人语义 |  |
| `number` |  | **free** | 聚合统计数据或计数，非个人级别 |  |
| `position` |  | **free** | 公开/非个人数据 |  |
| `q1` |  | **free** | 公开/非个人数据 |  |
| `q2` |  | **free** | 公开/非个人数据 |  |
| `q3` |  | **free** | 公开/非个人数据 |  |
| `qualifyId` |  | **free** | 标识符，无个人语义 |  |
| `raceId` |  | **free** | 标识符，无个人语义 |  |

## `races`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `circuitId` | circuit Id | **free** | 标识符，无个人语义 |  |
| `date` | duration time | **free** | 日期字段，未关联到特定个人 |  |
| `name` | name of the race | **free** | 实体名称，公开信息 |  |
| `raceId` | the unique identification number identifying the race | **free** | 标识符，无个人语义 |  |
| `round` | round | **free** | 公开/非个人数据 |  |
| `time` | time of the location | **free** | 公开/非个人数据 |  |
| `url` | introduction of races | **free** | 公开网站地址 |  |
| `year` | year | **free** | 日期字段，未关联到特定个人 |  |

## `results`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `constructorId` | the identification number identifying which constructors | **free** | 标识符，无个人语义 |  |
| `driverId` | the identification number identifying the driver | **free** | 标识符，无个人语义 |  |
| `fastestLap` | fastest lap number | **free** | 标识符或代码 |  |
| `fastestLapSpeed` | fastest Lap Speed | **free** | 公开/非个人数据 |  |
| `fastestLapTime` | fastest Lap Time | **free** | 公开/非个人数据 |  |
| `grid` | the number identifying the area where cars are set into a grid formation in order to start the race. | **free** | 标识符，无个人语义 |  |
| `laps` | lap number | **free** | 标识符或代码 |  |
| `milliseconds` | the actual finishing time of drivers in milliseconds | **free** | 公开/非个人数据 |  |
| `number` | number | **free** | 聚合统计数据或计数，非个人级别 |  |
| `points` | points | **free** | 公开/非个人数据 |  |
| `position` | The finishing position or track of circuits | **free** | 公开/非个人数据 |  |
| `positionOrder` | the finishing order of positions | **free** | 公开/非个人数据 |  |
| `positionText` |  | **free** | 公开/非个人数据 |  |
| `raceId` | the identification number identifying the race | **free** | 标识符，无个人语义 |  |
| `rank` | starting rank positioned by fastest lap speed | **free** | 公开/非个人数据 |  |
| `resultId` | the unique identification number identifying race result | **free** | 标识符，无个人语义 |  |
| `statusId` | status ID | **free** | 标识符，无个人语义 |  |
| `time` | finish time | **free** | 公开/非个人数据 |  |

## `seasons`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `url` | website link of season race introduction | **free** | 公开网站地址 |  |
| `year` | the unique identification number identifying the race | **free** | 日期字段，未关联到特定个人 |  |

## `status`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `status` | full name of status | **free** | 类别/标签，公开属性 |  |
| `statusId` | the unique identification number identifying status | **free** | 标识符，无个人语义 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/formula_1.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
