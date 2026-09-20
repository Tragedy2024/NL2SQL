# superhero — SSA 标签审查

> **数据库**: `superhero`
> **表**: 10
> **列**: 31 总计 (free=29, controlled=2, blocked=0)
> **状态**: 自动生成 — 需要人工审查

---

## `alignment`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `alignment` | the alignment of the superhero | **free** | 公开/非个人数据 |  |
| `id` | the unique identifier of the alignment | **free** | 标识符，无个人语义 |  |

## `attribute`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `attribute_name` | the attribute | **free** | 实体名称，公开信息 |  |
| `id` | the unique identifier of the attribute | **free** | 标识符，无个人语义 |  |

## `colour`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `colour` | the color of the superhero's skin/eye/hair/etc | **free** | 公开/非个人数据 |  |
| `id` | the unique identifier of the color | **free** | 标识符，无个人语义 |  |

## `gender`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `gender` | the gender of the superhero | **free** | 公开/非个人数据 |  |
| `id` | the unique identifier of the gender | **free** | 标识符，无个人语义 |  |

## `hero_attribute`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `attribute_id` | the id of the attribute Maps to attribute(id) | **free** | 标识符，无个人语义 |  |
| `attribute_value` | the attribute value | **free** | 公开/非个人数据 |  |
| `hero_id` | the id of the hero Maps to superhero(id) | **free** | 标识符，无个人语义 |  |

## `hero_power`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `hero_id` | the id of the hero Maps to superhero(id) | **free** | 标识符，无个人语义 |  |
| `power_id` | the id of the power Maps to superpower(id) | **free** | 标识符，无个人语义 |  |

## `publisher`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `id` | the unique identifier of the publisher | **free** | 标识符，无个人语义 |  |
| `publisher_name` | the name of the publisher | **free** | 实体名称，公开信息 |  |

## `race`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `id` | the unique identifier of the race | **free** | 标识符，无个人语义 |  |
| `race` | the race of the superhero | **free** | 公开/非个人数据 |  |

## `superhero`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `alignment_id` | the id of the superhero's alignment | **free** | 标识符，无个人语义 |  |
| `eye_colour_id` | the id of the superhero's eye color | **free** | 标识符，无个人语义 |  |
| `full_name` | the full name of the superhero | **controlled** | 个人姓名，可追溯到个人 |  |
| `gender_id` | the id of the superhero's gender | **free** | 标识符，无个人语义 |  |
| `hair_colour_id` | the id of the superhero's hair color | **free** | 标识符，无个人语义 |  |
| `height_cm` | the height of the superhero | **free** | 公开/非个人数据 |  |
| `id` | the unique identifier of the superhero | **free** | 标识符，无个人语义 |  |
| `publisher_id` | the id of the publisher | **free** | 标识符，无个人语义 |  |
| `race_id` | the id of the superhero's race | **free** | 标识符，无个人语义 |  |
| `skin_colour_id` | the id of the superhero's skin color | **free** | 标识符，无个人语义 |  |
| `superhero_name` | the name of the superhero | **controlled** | 个人姓名 |  |
| `weight_kg` | the weight of the superhero | **free** | 公开/非个人数据 |  |

## `superpower`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `id` | the unique identifier of the superpower | **free** | 标识符，无个人语义 |  |
| `power_name` | the superpower name | **free** | 实体名称，公开信息 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/superhero.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
