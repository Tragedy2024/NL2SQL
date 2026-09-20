# financial — SSA 标签审查

> **数据库**: `financial`
> **表**: 8
> **列**: 55 总计 (free=47, controlled=8, blocked=0)
> **状态**: 自动生成 — 需要人工审查

---

## `account`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `account_id` | the id of the account | **free** | 标识符，无个人语义 |  |
| `date` | the creation date of the account | **free** | 日期字段，未关联到特定个人 |  |
| `district_id` | location of branch | **free** | 标识符，无个人语义 |  |
| `frequency` | frequency of the acount | **free** | 聚合/统计数据 |  |

## `card`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `card_id` | id number of credit card | **free** | 标识符，无个人语义 |  |
| `disp_id` | disposition id | **free** | 标识符，无个人语义 |  |
| `issued` | the date when the credit card issued | **free** | 公开/非个人数据 |  |
| `type` | type of credit card | **free** | 类别/标签，公开属性 |  |

## `client`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `birth_date` | birth date | **free** | 日期字段，未关联到特定个人 |  |
| `client_id` | the unique number | **free** | 标识符，无个人语义 |  |
| `district_id` | location of branch | **free** | 标识符，无个人语义 |  |
| `gender` |  | **free** | 公开/非个人数据 |  |

## `disp`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `account_id` | id number of account | **free** | 标识符，无个人语义 |  |
| `client_id` | id number of client | **free** | 标识符，无个人语义 |  |
| `disp_id` | unique number of identifying this row of record | **free** | 标识符，无个人语义 |  |
| `type` | type of disposition | **free** | 类别/标签，公开属性 |  |

## `district`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `A10` | ratio of urban inhabitants | **free** | 公开/非个人数据 |  |
| `A11` | average salary | **controlled** | BIRD 匿名列；CSV 描述可能涉及个人/财务数据 |  |
| `A12` | unemployment rate 1995 | **free** | 公开/非个人数据 |  |
| `A13` | unemployment rate 1996 | **free** | 公开/非个人数据 |  |
| `A14` | no. of entrepreneurs per 1000 inhabitants | **free** | 公开/非个人数据 |  |
| `A15` | no. of committed crimes 1995 | **free** | 公开/非个人数据 |  |
| `A16` | no. of committed crimes 1996 | **free** | 公开/非个人数据 |  |
| `A2` | district_name | **free** | 组织/实体公开信息 |  |
| `A3` | region | **free** | 公开/非个人数据 |  |
| `A4` |  | **free** | 公开/非个人数据 |  |
| `A5` | municipality < district < region | **free** | 组织/实体公开信息 |  |
| `A6` | municipality < district < region | **free** | 组织/实体公开信息 |  |
| `A7` | municipality < district < region | **free** | 组织/实体公开信息 |  |
| `A8` | municipality < district < region | **free** | 组织/实体公开信息 |  |
| `A9` |  | **free** | 公开/非个人数据 |  |
| `district_id` | location of branch | **free** | 标识符，无个人语义 |  |

## `loan`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `account_id` | the id number identifying the account | **free** | 标识符，无个人语义 |  |
| `amount` | approved amount | **controlled** | 财务金额，可能关联到个人交易 |  |
| `date` | the date when the loan is approved | **free** | 日期字段，未关联到特定个人 |  |
| `duration` | loan duration | **free** | 公开/非个人数据 |  |
| `loan_id` | the id number identifying the loan data | **free** | 标识符，无个人语义 |  |
| `payments` | monthly payments | **controlled** | 财务金额，可能关联到个人交易 |  |
| `status` | repayment status | **free** | 类别/标签，公开属性 |  |

## `order`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `account_id` | id number of account | **free** | 标识符，无个人语义 |  |
| `account_to` | account of the recipient | **controlled** | 金融账户标识符 |  |
| `amount` | debited amount | **controlled** | 财务金额，可能关联到个人交易 |  |
| `bank_to` | bank of the recipient | **free** | 公开/非个人数据 |  |
| `k_symbol` | purpose of the payment | **free** | 公开/非个人数据 |  |
| `order_id` | identifying the unique order | **free** | 标识符，无个人语义 |  |

## `trans`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `account` |  | **controlled** | 个人或财务数据，需要受控暴露 |  |
| `account_id` |  | **free** | 标识符，无个人语义 |  |
| `amount` | amount of money | **controlled** | 财务金额，可能关联到个人交易 |  |
| `balance` | balance after transaction | **controlled** | 财务金额，可能关联到个人交易 |  |
| `bank` |  | **free** | 公开/非个人数据 |  |
| `date` | date of transaction | **free** | 日期字段，未关联到特定个人 |  |
| `k_symbol` |  | **free** | 公开/非个人数据 |  |
| `operation` | mode of transaction | **free** | 公开/非个人数据 |  |
| `trans_id` | transaction id | **free** | 标识符，无个人语义 |  |
| `type` | +/- transaction | **free** | 类别/标签，公开属性 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/financial.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
