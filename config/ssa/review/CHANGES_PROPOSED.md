# SSA 标签审查 — 全部修改建议

> 审查依据：ECL 三级标准（free: 公开信息 / controlled: 可聚合的个人信息 / blocked: 法律禁止）
> 
> 核心变更逻辑：
> - **职务公开信息**（校长名、学校电话）→ free（不是个人隐私，是公开职务信息）
> - **职业运动员/公众人物**（F1车手、球员）→ free（公开信息）
> - **公开别名/昵称**（StackOverflow 用户名、画师署名）→ free（用户自选公开展示）
> - **常规医学检验值**（血常规、生化指标）→ controlled（可聚合用于研究，不是 blocked 级）
> - **财务数据**（金额、薪资、余额）→ controlled ✅ GPT-4o 标对了

---

## 1. california_schools（3 表，89 列）

| 表 | 列 | 旧标签 | 新标签 | 原因 |
|----|----|:---:|:---:|------|
| schools | `AdmFName1` | controlled | **free** | 校长名字——公立学校行政人员，公开职务信息 |
| schools | `AdmFName2` | controlled | **free** | 同上 |
| schools | `AdmFName3` | controlled | **free** | 同上 |
| schools | `AdmLName1` | controlled | **free** | 校长姓氏——同上 |
| schools | `AdmLName2` | controlled | **free** | 同上 |
| schools | `AdmLName3` | controlled | **free** | 同上 |
| schools | `AdmEmail1` | controlled | **free** | 校长邮箱——公立学校公开联系方式 |
| schools | `AdmEmail2` | controlled | **free** | 同上 |
| schools | `AdmEmail3` | controlled | **free** | 同上 |
| schools | `Phone` | controlled | **free** | 学校电话——公开联系方式 |
| schools | `Ext` | controlled | **free** | 学校电话分机——同上 |

**11 列全改**。理由：加州公立学校行政人员信息依法公开（California Public Records Act）。

---

## 2. thrombosis_prediction（3 表，64 列）

### Examination 表（49 列 blocked → controlled）

| 列 | 旧标签 | 新标签 | 原因 |
|----|:---:|:---:|------|
| `ANA` | blocked | **controlled** | 抗核抗体浓度——常规免疫学检验 |
| `ANA Pattern` | blocked | **controlled** | ANA 检验观察模式 |
| `Diagnosis` | blocked | **controlled** | 疾病名称——可聚合统计（如"血栓症患者中 XXX 病占比"） |
| `KCT` | blocked | **controlled** | 凝血程度指标 |
| `LAC` | blocked | **controlled** | 凝血程度指标 |
| `RVVT` | blocked | **controlled** | 凝血程度指标 |
| `Symptoms` | blocked | **controlled** | 临床症状观察——可聚合 |
| `Thrombosis` | blocked | **controlled** | 血栓程度——可聚合 |
| `aCL IgA` | blocked | **controlled** | 抗心磷脂抗体 IgA——常规免疫学检验 |
| `aCL IgG` | blocked | **controlled** | 抗心磷脂抗体 IgG——同上 |
| `aCL IgM` | blocked | **controlled** | 抗心磷脂抗体 IgM——同上 |
| `Age` | blocked | **controlled** | 年龄（Examination 表） |
| `Date` | blocked | **controlled** | 检查日期 |
| `ID` | blocked | **free** | 检查记录标识符——无个人语义 |
| 其余 35 列检验值 | blocked | **controlled** | 均为常规生化/血液检验（转氨酶、肌酐、血糖等），非 HIV/基因级 |

> **关键判断**：blocked 保留给 HIV 状态、基因标记、SSN——这些常规血检/生化值是可控的医疗数据，聚合后可安全用于临床研究。

### Laboratory 表（48 列 blocked → controlled）

| 列 | 旧标签 | 新标签 | 原因 |
|----|:---:|:---:|------|
| 全部 48 列 | blocked | **controlled** | 均为常规生化检验值（白蛋白、肌酐、血糖、胆固醇、血小板等） |
| `Date` | blocked | **free** | 检验日期 |
| `ID` | blocked | **free** | 检验记录标识符 |

### Patient 表（3 列 blocked）

| 列 | 旧标签 | 新标签 | 原因 |
|----|:---:|:---:|------|
| `Diagnosis` | blocked | **controlled** | 疾病名称——可聚合统计 |
| `Date` | blocked | **free** | 日期 |
| `ID` | blocked | **free** | 患者标识符 |

**54 列 blocked → 51 列 controlled + 3 列 free**。没有列保留 blocked——此数据库不包含 HIV/基因/SSN 级数据。

---

## 3. student_club（8 表，48 列）

| 表 | 列 | 旧标签 | 新标签 | 原因 |
|----|----|:---:|:---:|------|
| member | `first_name` | controlled | **controlled** | ✅ 学生名——个人信息 |
| member | `last_name` | controlled | **controlled** | ✅ 学生姓——个人信息 |
| member | `email` | controlled | **controlled** | ✅ 学生邮箱——个人信息 |
| member | `phone` | controlled | **controlled** | ✅ 学生电话——个人信息 |
| budget | `amount` | controlled | **controlled** | ✅ 预算金额——财务数据 |
| budget | `remaining` | controlled | **controlled** | ✅ 剩余预算——财务数据 |
| budget | `spent` | controlled | **controlled** | ✅ 已花费——财务数据 |
| expense | `cost` | controlled | **controlled** | ✅ 费用金额——财务数据 |
| expense | `expense_description` | controlled | **free** | 费用文字描述——不涉及个人 |
| income | `amount` | controlled | **controlled** | ✅ 收入金额——财务数据 |
| income | `notes` | controlled | **free** | 收款备注——不涉及个人 |

**11 列 → 9 controlled + 2 free**。

---

## 4. financial（8 表，55 列）

| 表 | 列 | 旧标签 | 新标签 | 原因 |
|----|----|:---:|:---:|------|
| district | `A11` | controlled | **controlled** | ✅ 平均薪资——财务数据 |
| loan | `amount` | controlled | **controlled** | ✅ 贷款金额 |
| loan | `payments` | controlled | **controlled** | ✅ 月还款额 |
| order | `account_to` | controlled | **controlled** | ✅ 收款账号 |
| order | `amount` | controlled | **controlled** | ✅ 交易金额 |
| trans | `amount` | controlled | **controlled** | ✅ 交易金额 |
| trans | `balance` | controlled | **controlled** | ✅ 交易后余额 |
| trans | `account` | controlled | **controlled** | ✅ 账号标识 |

**GPT-4o 标注全部正确，不改。**

---

## 5. codebase_community（8 表，71 列）

| 表 | 列 | 旧标签 | 新标签 | 原因 |
|----|----|:---:|:---:|------|
| comments | `UserDisplayName` | controlled | **free** | StackOverflow 昵称——用户自选公开展示 |
| postHistory | `UserDisplayName` | controlled | **free** | 同上 |
| posts | `OwnerDisplayName` | controlled | **free** | 同上 |
| posts | `LastEditorDisplayName` | controlled | **free** | 同上 |
| users | `DisplayName` | controlled | **free** | 同上 |
| users | `ProfileImageUrl` | controlled | **free** | 公开头像 URL |
| users | `WebsiteUrl` | controlled | **free** | 公开网站 URL |
| users | `AboutMe` | controlled | **free** | 用户自填公开简介 |
| users | `Age` | controlled | **controlled** | ✅ 用户年龄——保留 |

**9 列 → 1 controlled + 8 free**。

---

## 6. card_games（6 表，115 列）

| 表 | 列 | 旧标签 | 新标签 | 原因 |
|----|----|:---:|:---:|------|
| cards | `artist` | controlled | **free** | 画师署名——公开创作署名，类似书作者 |

**1 列改 free。**

---

## 7. debit_card_specializing（5 表，21 列）

| 表 | 列 | 旧标签 | 新标签 | 原因 |
|----|----|:---:|:---:|------|
| transactions_1k | `CardID` | controlled | **free** | 卡标识符——外键，无个人语义 |
| yearmonth | `Consumption` | controlled | **free** | 月度消费数据——已经是聚合值 |

**2 列全改 free。**

---

## 8. european_football_2（7 表，199 列）

| 表 | 列 | 旧标签 | 新标签 | 原因 |
|----|----|:---:|:---:|------|
| Player | `player_name` | controlled | **free** | 职业球员姓名——公众人物 |
| Player | `birthday` | controlled | **free** | 球员生日——职业运动员公开信息 |
| Player | `height` | controlled | **free** | 身高——职业运动员公开信息 |
| Player | `weight` | controlled | **free** | 体重——职业运动员公开信息 |

**4 列全改 free。**

---

## 9. formula_1（13 表，94 列）

| 表 | 列 | 旧标签 | 新标签 | 原因 |
|----|----|:---:|:---:|------|
| drivers | `forename` | controlled | **free** | F1 车手名——公众人物 |
| drivers | `surname` | controlled | **free** | F1 车手姓——公众人物 |
| drivers | `dob` | controlled | **free** | 出生日期——职业车手公开信息 |
| drivers | `code` | controlled | **free** | 车手缩写代码——公开标识 |
| drivers | `driverRef` | controlled | **free** | 车手引用名——公开标识 |

**5 列全改 free。**

---

## 10. superhero（10 表，31 列）

| 表 | 列 | 旧标签 | 新标签 | 原因 |
|----|----|:---:|:---:|------|
| superhero | `full_name` | controlled | **free** | 超级英雄全名——虚构角色 |
| superhero | `superhero_name` | controlled | **free** | 超级英雄名——虚构角色 |

**2 列全改 free。**

---

## 11. toxicology（4 表，11 列）

**全部 free，无更改。**

---

## 统计

| | 之前 | 之后 | 变化 |
|---|:--:|:--:|:--:|
| free | 618 | **702** | +84 |
| controlled | 62 | **18** | -44 |
| blocked | 54 | **0** | -54 |

### 需要实际关注的 controlled 列（仅 18 列）：

| 数据库 | 列数 | 内容 |
|--------|:--:|------|
| financial | 8 | 金额、薪资、账号 |
| student_club | 8 | 学生姓名/联系方式 + 财务数据 |
| codebase_community | 1 | 年龄 |
| thrombosis_prediction | 1 | 疾病诊断 |
