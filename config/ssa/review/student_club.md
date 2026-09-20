# student_club — SSA 标签审查

> **数据库**: `student_club`
> **表**: 8
> **列**: 48 总计 (free=37, controlled=11, blocked=0)
> **状态**: 自动生成 — 需要人工审查

---

## `attendance`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `link_to_event` | The unique identifier of the event which was attended | **free** | 标识符或代码 |  |
| `link_to_member` | The unique identifier of the member who attended the event | **free** | 标识符或代码 |  |

## `budget`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `amount` |  | **controlled** | 财务金额，可能关联到个人交易 |  |
| `budget_id` |  | **free** | 标识符，无个人语义 |  |
| `category` |  | **free** | 类别/标签，公开属性 |  |
| `event_status` |  | **free** | 类别/标签，公开属性 |  |
| `link_to_event` |  | **free** | 公开/非个人数据 |  |
| `remaining` |  | **controlled** | 个人或财务数据，需要受控暴露 |  |
| `spent` |  | **controlled** | 个人或财务数据，需要受控暴露 |  |

## `event`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `event_date` | The date the event took place or is scheduled to take place | **free** | 日期字段，未关联到特定个人 |  |
| `event_id` | A unique identifier for the event | **free** | 标识符，无个人语义 |  |
| `event_name` | event name | **free** | 实体名称，公开信息 |  |
| `location` | Address where the event was held or is to be held or the name of such a location | **free** | 地理坐标，公开数据 |  |
| `notes` | A free text field for any notes about the event | **free** | 公开/非个人数据 |  |
| `status` | One of three values indicating if the event is in planning, is opened, or is closed | **free** | 类别/标签，公开属性 |  |
| `type` | The kind of event, such as game, social, election | **free** | 类别/标签，公开属性 |  |

## `expense`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `approved` | A true or false value indicating if the expense was approved | **free** | 公开/非个人数据 |  |
| `cost` | The dollar amount of the expense | **controlled** | 财务数据，可聚合 |  |
| `expense_date` | The date the expense was incurred | **free** | 日期字段，未关联到特定个人 |  |
| `expense_description` | A textual description of what the money was spend for | **controlled** | 个人或财务数据，需要受控暴露 |  |
| `expense_id` | unique id of income | **free** | 标识符，无个人语义 |  |
| `link_to_budget` | The unique identifier of the record in the Budget table that indicates the expected total expenditur | **free** | 标识符或代码 |  |
| `link_to_member` | The member who incurred the expense | **free** | 公开/非个人数据 |  |

## `income`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `amount` | amount of funds | **controlled** | 财务金额，可能关联到个人交易 |  |
| `date_received` | the date that the fund received | **free** | 日期字段，未关联到特定个人 |  |
| `income_id` | A unique identifier for each record of income | **free** | 标识符，无个人语义 |  |
| `link_to_member` | link to member | **free** | 公开/非个人数据 |  |
| `notes` | A free-text value giving any needed details about the receipt of funds | **controlled** | 个人或财务数据，需要受控暴露 |  |
| `source` | A value indicating where the funds come from such as dues, or the annual university allocation | **free** | 公开/非个人数据 |  |

## `major`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `college` | The name college that houses the department that offers the major | **free** | 组织/实体公开信息 |  |
| `department` | The name of the department that offers the major | **free** | 组织/实体公开信息 |  |
| `major_id` | A unique identifier for each major | **free** | 标识符，无个人语义 |  |
| `major_name` | major name | **free** | 实体名称，公开信息 |  |

## `member`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `email` | member's email | **controlled** | 个人联系方式（电子邮件），可追溯到个人 |  |
| `first_name` | member's first name | **controlled** | 个人姓名，可追溯到个人 |  |
| `last_name` | member's last name | **controlled** | 个人姓名，可追溯到个人 |  |
| `link_to_major` | The unique identifier of the major of the member. References the Major table | **free** | 标识符或代码 |  |
| `member_id` | unique id of member | **free** | 标识符，无个人语义 |  |
| `phone` | The best telephone at which to contact the member | **controlled** | 个人联系方式（电话），可追溯到个人 |  |
| `position` | The position the member holds in the club | **free** | 公开/非个人数据 |  |
| `t_shirt_size` | The size of tee shirt that member wants when shirts are ordered | **free** | 公开/非个人数据 |  |
| `zip` | the zip code of the member's hometown | **free** | 标识符或代码 |  |

## `zip_code`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `city` | The city to which the ZIP pertains | **free** | 公开/非个人数据 |  |
| `county` | The county to which the ZIP pertains | **free** | 聚合统计数据或计数，非个人级别 |  |
| `short_state` | The abbreviation of the state to which the ZIP pertains | **free** | 公开/非个人数据 |  |
| `state` | The name of the state to which the ZIP pertains | **free** | 组织/实体公开信息 |  |
| `type` | The kind of ZIP code | **free** | 类别/标签，公开属性 |  |
| `zip_code` | The ZIP code itself. A five-digit number identifying a US post office. | **free** | 标识符，无个人语义 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/student_club.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
