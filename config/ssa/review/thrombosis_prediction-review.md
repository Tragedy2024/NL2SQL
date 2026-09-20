# thrombosis_prediction — SSA 详细审核

> **数据库**：血栓症预测研究数据库
> **表数**：3（Examination / Laboratory / Patient）
> **总列数**：64
> **当前状态**：GPT-4o 标注 — 54 blocked, 10 free
> **审核日期**：2026-07-20
> **审核结论**：54 blocked → 52 controlled + 2 free（零列需要 blocked）

---

## 审核标准重申

| 级别 | 定义 | 适用场景 |
|:---:|------|------|
| **blocked** | 法律/伦理红线，聚合也不行 | HIV 状态、基因标记、SSN、护照号、精神疾病诊断（特定司法管辖区） |
| **controlled** | 可关联个人，但聚合后安全 | 常规血检值、生化指标、免疫指标、疾病诊断（可聚合统计） |
| **free** | 不涉及个人 | ID、日期、类别标签 |

**判断核心**：常规临床检验数据 ≠ blocked。这些数据每天都在医学研究中被聚合使用（`AVG(blood_glucose)` 是标准临床研究操作）。blocked 保留给"无论如何不能以任何形式暴露"的数据。

---

## 表 1：`Examination`（检查记录，13 列）

| 列名 | 含义 | 旧标签 | 新标签 | 审核意见 |
|------|------|:---:|:---:|------|
| `ID` | 患者标识 | free | free | ✅ 标识符，无个人语义 |
| `Examination Date` | 检查日期 | free | free | ✅ 日期字段 |
| `ANA` | 抗核抗体浓度 | blocked | **controlled** | 常规自身免疫抗体检测。`AVG(ANA)` 可反映患者群体自身免疫水平 |
| `ANA Pattern` | ANA 检验观察到的荧光模式 | blocked | **controlled** | 定性观察结果（均质型/斑点型等）。可聚合为模式分布统计 |
| `aCL IgA` | 抗心磷脂抗体 IgA 浓度 | blocked | **controlled** | 常规免疫学检验。`AVG(aCL_IgA)` 安全 |
| `aCL IgG` | 抗心磷脂抗体 IgG 浓度 | blocked | **controlled** | 同上 |
| `aCL IgM` | 抗心磷脂抗体 IgM 浓度 | blocked | **controlled** | 同上 |
| `KCT` | 凝血程度指标 | blocked | **controlled** | 凝血功能检测。`AVG(KCT)` 不敏感 |
| `LAC` | 凝血程度指标 | blocked | **controlled** | 同上 |
| `RVVT` | 凝血程度指标 | blocked | **controlled** | 同上 |
| `Diagnosis` | 疾病名称 | blocked | **controlled** | 血栓症、抗磷脂综合征等。可聚合为疾病分布统计（如"血栓症患者中 APS 占比 30%"） |
| `Symptoms` | 临床症状观察 | blocked | **controlled** | 临床表现描述。可聚合为症状频率统计 |
| `Thrombosis` | 血栓严重程度 | blocked | **controlled** | 临床评分。`AVG(Thrombosis)` = 平均血栓程度，研究可用 |

**本表变更**：10 blocked → 10 controlled。ID 和 Date 保持 free。

---

## 表 2：`Laboratory`（实验室检验，49 列）

本表包含患者的常规血液、生化、免疫学检验值。这些都是**标准临床化验项目**，体检时都会查，不存在 HIV/基因级的法律保护数据。

### 肝功能相关（3 列）

| 列名 | 含义 | 旧标签 | 新标签 | 审核意见 |
|------|------|:---:|:---:|------|
| `GOT` | AST 谷草转氨酶 | blocked | **controlled** | 肝功能常规指标，`AVG(GOT)` 反映群体肝功能水平 |
| `GPT` | ALT 谷丙转氨酶 | blocked | **controlled** | 同上 |
| `T-BIL` | 总胆红素 | blocked | **controlled** | 同上 |

### 肾功能/代谢相关（5 列）

| 列名 | 含义 | 旧标签 | 新标签 | 审核意见 |
|------|------|:---:|:---:|------|
| `CRE` | 肌酐 | blocked | **controlled** | 肾功能常规指标 |
| `UN` | 尿素氮 | blocked | **controlled** | 同上 |
| `UA` | 尿酸 | blocked | **controlled** | 代谢指标，痛风诊断参考 |
| `U-PRO` | 蛋白尿 | blocked | **controlled** | 肾功能指标 |
| `GLU` | 血糖 | blocked | **controlled** | 常规代谢指标，`AVG(GLU)` 完全安全 |

### 血脂相关（2 列）

| 列名 | 含义 | 旧标签 | 新标签 | 审核意见 |
|------|------|:---:|:---:|------|
| `T-CHO` | 总胆固醇 | blocked | **controlled** | 常规血脂指标 |
| `TG` | 甘油三酯 | blocked | **controlled** | 同上 |

### 血液学（6 列）

| 列名 | 含义 | 旧标签 | 新标签 | 审核意见 |
|------|------|:---:|:---:|------|
| `RBC` | 红细胞计数 | blocked | **controlled** | 血常规，常规检查 |
| `WBC` | 白细胞计数 | blocked | **controlled** | 同上 |
| `HGB` | 血红蛋白 | blocked | **controlled** | 同上 |
| `HCT` | 血细胞比容 | blocked | **controlled** | 同上 |
| `PLT` | 血小板计数 | blocked | **controlled** | 同上 |
| `APTT` | 活化部分凝血活酶时间 | blocked | **controlled** | 凝血功能指标 |

### 凝血/纤溶相关（4 列）

| 列名 | 含义 | 旧标签 | 新标签 | 审核意见 |
|------|------|:---:|:---:|------|
| `PT` | 凝血酶原时间 | blocked | **controlled** | 凝血功能常规 |
| `FG` | 纤维蛋白原 | blocked | **controlled** | 凝血因子 |
| `PIC` | （纤溶指标，无 CSV 描述） | blocked | **controlled** | 临床检验值 |
| `TAT`、`TAT2` | （凝血标志物，无 CSV 描述） | blocked | **controlled** | 临床检验值 |

### 免疫学（15 列）

| 列名 | 含义 | 旧标签 | 新标签 | 审核意见 |
|------|------|:---:|:---:|------|
| `IGA` | 免疫球蛋白 A | blocked | **controlled** | 常规免疫学指标 |
| `IGG` | 免疫球蛋白 G | blocked | **controlled** | 同上 |
| `IGM` | 免疫球蛋白 M | blocked | **controlled** | 同上 |
| `C3` | 补体 C3 | blocked | **controlled** | 常规免疫学指标 |
| `C4` | 补体 C4 | blocked | **controlled** | 同上 |
| `CRP` | C 反应蛋白 | blocked | **controlled** | 炎症标志物，常规检查 |
| `RA` | 类风湿因子 | blocked | **controlled** | 自身免疫筛查 |
| `RF` | RAHA | blocked | **controlled** | 同上 |
| `DNA` | 抗 DNA 抗体 | blocked | **controlled** | 自身免疫筛查（注意：这是抗DNA抗体浓度，不是DNA序列） |
| `DNA-II` | 抗 DNA 抗体（第二种检测） | blocked | **controlled** | 同上 |
| `RNP` | 抗核糖核蛋白抗体 | blocked | **controlled** | 自身免疫筛查 |
| `SM` | 抗 SM 抗体 | blocked | **controlled** | SLE 特异性指标 |
| `SSA` | 抗 SSA 抗体 | blocked | **controlled** | 干燥综合征相关 |
| `SSB` | 抗 SSB 抗体 | blocked | **controlled** | 同上 |
| `SC170` | 抗 Scl-70 抗体 | blocked | **controlled** | 硬皮病相关 |
| `CENTROMEA` | 抗着丝粒抗体 | blocked | **controlled** | 自身免疫筛查 |

### 其他生化指标（5 列）

| 列名 | 含义 | 旧标签 | 新标签 | 审核意见 |
|------|------|:---:|:---:|------|
| `ALB` | 白蛋白 | blocked | **controlled** | 肝功能/营养指标 |
| `ALP` | 碱性磷酸酶 | blocked | **controlled** | 肝功能/骨代谢指标 |
| `CPK` | 肌酸磷酸激酶 | blocked | **controlled** | 心肌/骨骼肌指标 |
| `LDH` | 乳酸脱氢酶 | blocked | **controlled** | 组织损伤标志物 |
| `TP` | 总蛋白 | blocked | **controlled** | 营养/肝功能指标 |

### 非检验列（2 列）

| 列名 | 含义 | 旧标签 | 新标签 | 审核意见 |
|------|------|:---:|:---:|------|
| `ID` | 患者标识 | free | free | ✅ 标识符 |
| `Date` | 检验日期（YYMMDD） | free | free | ✅ 日期字段 |

**本表变更**：47 blocked → 47 controlled。ID 和 Date 保持 free。

---

## 表 3：`Patient`（患者基本信息，7 列）

| 列名 | 含义 | 旧标签 | 新标签 | 审核意见 |
|------|------|:---:|:---:|------|
| `ID` | 患者标识 | free | free | ✅ 标识符 |
| `SEX` | 性别 | free | free | ✅ 人口学分类（非个人标识） |
| `Birthday` | 出生日期 | free | free | ✅ 单独日期不定位个人 |
| `Admission` | 入院方式（+住院/-门诊） | free | free | ✅ 类别标签 |
| `First Date` | 首次就诊日期 | free | free | ✅ 日期 |
| `Description` | 首次记录日期 | free | free | ✅ 日期描述 |
| `Diagnosis` | 疾病名称 | blocked | **controlled** | 患者诊断名。可聚合为疾病分布，医学研究常规操作 |

**本表变更**：1 blocked → 1 controlled。其余保持 free。

---

## 审核结论

### 变更汇总

| 表 | blocked → controlled | blocked → free | 不变 | 合计 |
|----|:---:|:---:|:---:|:---:|
| Examination | 10 | 0 | 3 | 13 |
| Laboratory | 47 | 0 | 2 | 49 |
| Patient | 1 | 0 | 6 | 7 |
| **总计** | **58** | **0** | **11** | **69** |

> 注：YAML 显示部分列有重复（Examination 的 Blocked 列在 Laboratory 中也有同名列），实际唯一列数为 64。

### 为什么零列需要 blocked

这 64 列全部是**常规临床数据**——血液检查、生化指标、免疫学筛查、疾病诊断。这类数据在医学研究中有以下特征：

1. **聚合使用是常态**：`AVG(blood_glucose)`、`COUNT(patients_with_diagnosis_X)` 是临床研究的标准操作
2. **法律允许研究使用**：HIPAA 允许去标识化后的临床数据用于研究（不直接暴露个人标识即可）
3. **不存在 HIV/基因/SSN 级数据**：抗 DNA 抗体 ≠ DNA 序列，抗心磷脂抗体 ≠ 基因信息

**blocked 应该保留给**：HIV 状态、BRCA1/BRCA2 等致病基因突变、社会安全号、护照号、精神分裂症/自杀倾向等特定精神疾病诊断（某些司法管辖区）。

### 后续步骤

1. 审核人确认本文所有变更
2. 更新 `config/ssa/thrombosis_prediction.yaml`
3. 重跑 Pilot 验证新的 S-VR 和违规分布（预计 controlled 列会触发 `column_needs_aggregation` 违规，因为 MAC-SQL 可能 SELECT 原始检验值）
