# debit_card_specializing — SSA 标签审查

> **数据库**: `debit_card_specializing`
> **表**: 5
> **列**: 21 总计 (free=19, controlled=2, blocked=0)
> **状态**: 自动生成 — 需要人工审查

---

## `customers`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `Currency` | Currency | **free** | 公开/非个人数据 |  |
| `CustomerID` | identification of the customer | **free** | 标识符，无个人语义 |  |
| `Segment` | client segment | **free** | 公开/非个人数据 |  |

## `gasstations`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `ChainID` | Chain ID | **free** | 标识符，无个人语义 |  |
| `Country` |  | **free** | 聚合统计数据或计数，非个人级别 |  |
| `GasStationID` | Gas Station ID | **free** | 标识符，无个人语义 |  |
| `Segment` | chain segment | **free** | 公开/非个人数据 |  |

## `products`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `Description` | Description | **free** | 公开/非个人数据 |  |
| `ProductID` | Product ID | **free** | 标识符，无个人语义 |  |

## `transactions_1k`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `Amount` | Amount | **free** | 公开/非个人数据 |  |
| `CardID` | Card ID | **controlled** | 个人或财务数据，需要受控暴露 |  |
| `CustomerID` | Customer ID | **free** | 标识符，无个人语义 |  |
| `Date` | Date | **free** | 日期字段，未关联到特定个人 |  |
| `GasStationID` | Gas Station ID | **free** | 标识符，无个人语义 |  |
| `Price` | Price | **free** | 公开/非个人数据 |  |
| `ProductID` | Product ID | **free** | 标识符，无个人语义 |  |
| `Time` | Time | **free** | 公开/非个人数据 |  |
| `TransactionID` | Transaction ID | **free** | 标识符，无个人语义 |  |

## `yearmonth`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `Consumption` | consumption | **controlled** | 个人或财务数据，需要受控暴露 |  |
| `CustomerID` | Customer ID | **free** | 标识符，无个人语义 |  |
| `Date` | Date | **free** | 日期字段，未关联到特定个人 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/debit_card_specializing.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
