# european_football_2 — SSA 标签审查

> **数据库**: `european_football_2`
> **表**: 7
> **列**: 199 总计 (free=195, controlled=4, blocked=0)
> **状态**: 自动生成 — 需要人工审查

---

## `Country`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `id` | the unique id for countries | **free** | 标识符，无个人语义 |  |
| `name` | country name | **free** | 组织/实体名称，公开信息 |  |

## `League`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `country_id` | the unique id for countries | **free** | 标识符，无个人语义 |  |
| `id` | the unique id for leagues | **free** | 标识符，无个人语义 |  |
| `name` | league name | **free** | 组织/实体名称，公开信息 |  |

## `Match`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `B365A` |  | **free** | 公开/非个人数据 |  |
| `B365D` |  | **free** | 公开/非个人数据 |  |
| `B365H` |  | **free** | 公开/非个人数据 |  |
| `BSA` |  | **free** | 公开/非个人数据 |  |
| `BSD` |  | **free** | 公开/非个人数据 |  |
| `BSH` |  | **free** | 公开/非个人数据 |  |
| `BWA` |  | **free** | 公开/非个人数据 |  |
| `BWD` |  | **free** | 公开/非个人数据 |  |
| `BWH` |  | **free** | 公开/非个人数据 |  |
| `GBA` |  | **free** | 公开/非个人数据 |  |
| `GBD` |  | **free** | 公开/非个人数据 |  |
| `GBH` |  | **free** | 公开/非个人数据 |  |
| `IWA` |  | **free** | 公开/非个人数据 |  |
| `IWD` |  | **free** | 公开/非个人数据 |  |
| `IWH` |  | **free** | 公开/非个人数据 |  |
| `LBA` |  | **free** | 公开/非个人数据 |  |
| `LBD` |  | **free** | 公开/非个人数据 |  |
| `LBH` |  | **free** | 公开/非个人数据 |  |
| `PSA` |  | **free** | 公开/非个人数据 |  |
| `PSD` |  | **free** | 公开/非个人数据 |  |
| `PSH` |  | **free** | 公开/非个人数据 |  |
| `SJA` |  | **free** | 公开/非个人数据 |  |
| `SJD` |  | **free** | 公开/非个人数据 |  |
| `SJH` |  | **free** | 公开/非个人数据 |  |
| `VCA` |  | **free** | 公开/非个人数据 |  |
| `VCD` |  | **free** | 公开/非个人数据 |  |
| `VCH` |  | **free** | 公开/非个人数据 |  |
| `WHA` |  | **free** | 公开/非个人数据 |  |
| `WHD` |  | **free** | 公开/非个人数据 |  |
| `WHH` |  | **free** | 公开/非个人数据 |  |
| `away_player_1` |  | **free** | 公开/非个人数据 |  |
| `away_player_10` |  | **free** | 公开/非个人数据 |  |
| `away_player_11` |  | **free** | 公开/非个人数据 |  |
| `away_player_2` |  | **free** | 公开/非个人数据 |  |
| `away_player_3` |  | **free** | 公开/非个人数据 |  |
| `away_player_4` |  | **free** | 公开/非个人数据 |  |
| `away_player_5` |  | **free** | 公开/非个人数据 |  |
| `away_player_6` |  | **free** | 公开/非个人数据 |  |
| `away_player_7` |  | **free** | 公开/非个人数据 |  |
| `away_player_8` |  | **free** | 公开/非个人数据 |  |
| `away_player_9` |  | **free** | 公开/非个人数据 |  |
| `away_player_X1` |  | **free** | 公开/非个人数据 |  |
| `away_player_X10` |  | **free** | 公开/非个人数据 |  |
| `away_player_X11` |  | **free** | 公开/非个人数据 |  |
| `away_player_X2` |  | **free** | 公开/非个人数据 |  |
| `away_player_X3` |  | **free** | 公开/非个人数据 |  |
| `away_player_X4` |  | **free** | 公开/非个人数据 |  |
| `away_player_X5` |  | **free** | 公开/非个人数据 |  |
| `away_player_X6` |  | **free** | 公开/非个人数据 |  |
| `away_player_X7` |  | **free** | 公开/非个人数据 |  |
| `away_player_X8` |  | **free** | 公开/非个人数据 |  |
| `away_player_X9` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y1` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y10` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y11` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y2` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y3` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y4` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y5` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y6` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y7` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y8` |  | **free** | 公开/非个人数据 |  |
| `away_player_Y9` |  | **free** | 公开/非个人数据 |  |
| `away_team_api_id` | the id of the away team api | **free** | 标识符，无个人语义 |  |
| `away_team_goal` | the goal of the away team | **free** | 公开/非个人数据 |  |
| `card` | the cards given in the match | **free** | 公开/非个人数据 |  |
| `corner` | Ball goes out of play for a corner kick in the match | **free** | 公开/非个人数据 |  |
| `country_id` | country id | **free** | 标识符，无个人语义 |  |
| `cross` | Balls sent into the opposition team's area from a wide position in the match | **free** | 公开/非个人数据 |  |
| `date` | the date of the match | **free** | 日期字段，未关联到特定个人 |  |
| `foulcommit` | the fouls occurred in the match | **free** | 公开/非个人数据 |  |
| `goal` | the goal of the match | **free** | 公开/非个人数据 |  |
| `home_player_1` |  | **free** | 公开/非个人数据 |  |
| `home_player_10` |  | **free** | 公开/非个人数据 |  |
| `home_player_11` |  | **free** | 公开/非个人数据 |  |
| `home_player_2` |  | **free** | 公开/非个人数据 |  |
| `home_player_3` |  | **free** | 公开/非个人数据 |  |
| `home_player_4` |  | **free** | 公开/非个人数据 |  |
| `home_player_5` |  | **free** | 公开/非个人数据 |  |
| `home_player_6` |  | **free** | 公开/非个人数据 |  |
| `home_player_7` |  | **free** | 公开/非个人数据 |  |
| `home_player_8` |  | **free** | 公开/非个人数据 |  |
| `home_player_9` |  | **free** | 公开/非个人数据 |  |
| `home_player_X1` |  | **free** | 公开/非个人数据 |  |
| `home_player_X10` |  | **free** | 公开/非个人数据 |  |
| `home_player_X11` |  | **free** | 公开/非个人数据 |  |
| `home_player_X2` |  | **free** | 公开/非个人数据 |  |
| `home_player_X3` |  | **free** | 公开/非个人数据 |  |
| `home_player_X4` |  | **free** | 公开/非个人数据 |  |
| `home_player_X5` |  | **free** | 公开/非个人数据 |  |
| `home_player_X6` |  | **free** | 公开/非个人数据 |  |
| `home_player_X7` |  | **free** | 公开/非个人数据 |  |
| `home_player_X8` |  | **free** | 公开/非个人数据 |  |
| `home_player_X9` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y1` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y10` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y11` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y2` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y3` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y4` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y5` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y6` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y7` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y8` |  | **free** | 公开/非个人数据 |  |
| `home_player_Y9` |  | **free** | 公开/非个人数据 |  |
| `home_team_api_id` | the id of the home team api | **free** | 标识符，无个人语义 |  |
| `home_team_goal` | the goal of the home team | **free** | 公开/非个人数据 |  |
| `id` | the unique id for matches | **free** | 标识符，无个人语义 |  |
| `league_id` | league id | **free** | 标识符，无个人语义 |  |
| `match_api_id` | the id of the match api | **free** | 标识符，无个人语义 |  |
| `possession` | The duration from a player taking over the ball in the match | **free** | 公开/非个人数据 |  |
| `season` | the season of the match | **free** | 公开/非个人数据 |  |
| `shotoff` | the shot off goal of the match, which is the opposite of shot on | **free** | 公开/非个人数据 |  |
| `shoton` | the shot on goal of the match | **free** | 公开/非个人数据 |  |
| `stage` | the stage of the match | **free** | 公开/非个人数据 |  |

## `Player`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `birthday` | the player's birthday | **controlled** | 个人身份属性 |  |
| `height` | the player's height | **controlled** | 个人或财务数据，需要受控暴露 |  |
| `id` | the unique id for players | **free** | 标识符，无个人语义 |  |
| `player_api_id` | the id of the player api | **free** | 标识符，无个人语义 |  |
| `player_fifa_api_id` | the id of the player fifa api | **free** | 标识符，无个人语义 |  |
| `player_name` | player name | **controlled** | 个人姓名 |  |
| `weight` | the player's weight | **controlled** | 个人或财务数据，需要受控暴露 |  |

## `Player_Attributes`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `acceleration` |  | **free** | 公开/非个人数据 |  |
| `aggression` |  | **free** | 公开/非个人数据 |  |
| `agility` |  | **free** | 公开/非个人数据 |  |
| `attacking_work_rate` |  | **free** | 聚合统计数据或计数，非个人级别 |  |
| `balance` |  | **free** | 公开/非个人数据 |  |
| `ball_control` |  | **free** | 公开/非个人数据 |  |
| `crossing` |  | **free** | 公开/非个人数据 |  |
| `curve` |  | **free** | 公开/非个人数据 |  |
| `date` |  | **free** | 日期字段，未关联到特定个人 |  |
| `defensive_work_rate` |  | **free** | 聚合统计数据或计数，非个人级别 |  |
| `dribbling` |  | **free** | 公开/非个人数据 |  |
| `finishing` |  | **free** | 公开/非个人数据 |  |
| `free_kick_accuracy` |  | **free** | 公开/非个人数据 |  |
| `gk_diving` |  | **free** | 公开/非个人数据 |  |
| `gk_handling` |  | **free** | 公开/非个人数据 |  |
| `gk_kicking` |  | **free** | 公开/非个人数据 |  |
| `gk_positioning` |  | **free** | 公开/非个人数据 |  |
| `gk_reflexes` |  | **free** | 公开/非个人数据 |  |
| `heading_accuracy` |  | **free** | 公开/非个人数据 |  |
| `id` |  | **free** | 标识符，无个人语义 |  |
| `interceptions` |  | **free** | 公开/非个人数据 |  |
| `jumping` |  | **free** | 公开/非个人数据 |  |
| `long_passing` |  | **free** | 公开/非个人数据 |  |
| `long_shots` |  | **free** | 公开/非个人数据 |  |
| `marking` |  | **free** | 公开/非个人数据 |  |
| `overall_rating` |  | **free** | 公开/非个人数据 |  |
| `penalties` |  | **free** | 公开/非个人数据 |  |
| `player_api_id` |  | **free** | 标识符，无个人语义 |  |
| `player_fifa_api_id` |  | **free** | 标识符，无个人语义 |  |
| `positioning` |  | **free** | 公开/非个人数据 |  |
| `potential` |  | **free** | 公开/非个人数据 |  |
| `preferred_foot` |  | **free** | 公开/非个人数据 |  |
| `reactions` |  | **free** | 公开/非个人数据 |  |
| `short_passing` |  | **free** | 公开/非个人数据 |  |
| `shot_power` |  | **free** | 公开/非个人数据 |  |
| `sliding_tackle` |  | **free** | 标识符，无个人语义 |  |
| `sprint_speed` |  | **free** | 公开/非个人数据 |  |
| `stamina` |  | **free** | 公开/非个人数据 |  |
| `standing_tackle` |  | **free** | 公开/非个人数据 |  |
| `strength` |  | **free** | 公开/非个人数据 |  |
| `vision` |  | **free** | 公开/非个人数据 |  |
| `volleys` |  | **free** | 公开/非个人数据 |  |

## `Team`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `id` | the unique id for teams | **free** | 标识符，无个人语义 |  |
| `team_api_id` | the id of the team api | **free** | 标识符，无个人语义 |  |
| `team_fifa_api_id` | the id of the team fifa api | **free** | 标识符，无个人语义 |  |
| `team_long_name` | the team's long name | **free** | 组织/实体名称，公开信息 |  |
| `team_short_name` | the team's short name | **free** | 组织/实体名称，公开信息 |  |

## `Team_Attributes`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `buildUpPlayDribbling` |  | **free** | 公开/非个人数据 |  |
| `buildUpPlayDribblingClass` |  | **free** | 公开/非个人数据 |  |
| `buildUpPlayPassing` |  | **free** | 公开/非个人数据 |  |
| `buildUpPlayPassingClass` |  | **free** | 公开/非个人数据 |  |
| `buildUpPlayPositioningClass` |  | **free** | 公开/非个人数据 |  |
| `buildUpPlaySpeed` |  | **free** | 公开/非个人数据 |  |
| `buildUpPlaySpeedClass` |  | **free** | 公开/非个人数据 |  |
| `chanceCreationCrossing` |  | **free** | 公开/非个人数据 |  |
| `chanceCreationCrossingClass` |  | **free** | 公开/非个人数据 |  |
| `chanceCreationPassing` |  | **free** | 公开/非个人数据 |  |
| `chanceCreationPassingClass` |  | **free** | 公开/非个人数据 |  |
| `chanceCreationPositioningClass` |  | **free** | 公开/非个人数据 |  |
| `chanceCreationShooting` |  | **free** | 公开/非个人数据 |  |
| `chanceCreationShootingClass` |  | **free** | 公开/非个人数据 |  |
| `date` |  | **free** | 日期字段，未关联到特定个人 |  |
| `defenceAggression` |  | **free** | 公开/非个人数据 |  |
| `defenceAggressionClass` |  | **free** | 公开/非个人数据 |  |
| `defenceDefenderLineClass` |  | **free** | 公开/非个人数据 |  |
| `defencePressure` |  | **free** | 公开/非个人数据 |  |
| `defencePressureClass` |  | **free** | 公开/非个人数据 |  |
| `defenceTeamWidth` |  | **free** | 标识符，无个人语义 |  |
| `defenceTeamWidthClass` |  | **free** | 标识符，无个人语义 |  |
| `id` |  | **free** | 标识符，无个人语义 |  |
| `team_api_id` |  | **free** | 标识符，无个人语义 |  |
| `team_fifa_api_id` |  | **free** | 标识符，无个人语义 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/european_football_2.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
