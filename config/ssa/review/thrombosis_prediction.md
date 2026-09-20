# thrombosis_prediction — SSA 标签审查

> **数据库**: `thrombosis_prediction`
> **表**: 3
> **列**: 64 总计 (free=10, controlled=0, blocked=54)
> **状态**: 自动生成 — 需要人工审查

---

## `Examination`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `ANA` | anti-nucleus antibody concentration | **blocked** | 法律保护的敏感数据 |  |
| `ANA Pattern` | pattern observed in the sheet of ANA examination | **blocked** | 医学检查数据，受法律保护 |  |
| `Diagnosis` | disease names | **blocked** | 医疗数据，严格受法律保护 |  |
| `Examination Date` | Examination Date | **free** | 日期字段，未关联到特定个人 |  |
| `ID` | identification of the patient | **free** | 标识符，无个人语义 |  |
| `KCT` | measure of degree of coagulation | **blocked** | 法律保护的敏感数据 |  |
| `LAC` | measure of degree of coagulation | **blocked** | 法律保护的敏感数据 |  |
| `RVVT` | measure of degree of coagulation | **blocked** | 法律保护的敏感数据 |  |
| `Symptoms` | other symptoms observed | **blocked** | 法律保护的敏感数据 |  |
| `Thrombosis` | degree of thrombosis | **blocked** | 法律保护的敏感数据 |  |
| `aCL IgA` | anti-Cardiolipin antibody (IgA) concentration | **blocked** | 法律保护的敏感数据 |  |
| `aCL IgG` | anti-Cardiolipin antibody (IgG) concentration | **blocked** | 法律保护的敏感数据 |  |
| `aCL IgM` | anti-Cardiolipin antibody (IgM) concentration | **blocked** | 法律保护的敏感数据 |  |

## `Laboratory`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `ALB` | albumin | **blocked** | 法律保护的敏感数据 |  |
| `ALP` | alkaliphophatase | **blocked** | 法律保护的敏感数据 |  |
| `APTT` | activated partial prothrombin time | **blocked** | 法律保护的敏感数据 |  |
| `C3` | complement 3 | **blocked** | 法律保护的敏感数据 |  |
| `C4` | complement 4 | **blocked** | 法律保护的敏感数据 |  |
| `CENTROMEA` | anti-centromere | **blocked** | 法律保护的敏感数据 |  |
| `CPK` | creatinine phosphokinase | **blocked** | 法律保护的敏感数据 |  |
| `CRE` | creatinine | **blocked** | 法律保护的敏感数据 |  |
| `CRP` | C-reactive protein | **blocked** | 法律保护的敏感数据 |  |
| `DNA` | anti-DNA | **blocked** | 法律保护的数据，不得以任何形式暴露 |  |
| `DNA-II` | anti-DNA | **blocked** | 法律保护的数据，不得以任何形式暴露 |  |
| `Date` | Date of the laboratory tests (YYMMDD) | **free** | 日期字段，未关联到特定个人 |  |
| `FG` | fibrinogen | **blocked** | 法律保护的敏感数据 |  |
| `GLU` | blood glucose | **blocked** | 实验室检测结果，受法律保护 |  |
| `GOT` | AST glutamic oxaloacetic transaminase | **blocked** | 法律保护的敏感数据 |  |
| `GPT` | ALT glutamic pyruvic transaminase | **blocked** | 法律保护的敏感数据 |  |
| `HCT` | Hematoclit | **blocked** | 法律保护的敏感数据 |  |
| `HGB` | Hemoglobin | **blocked** | 法律保护的敏感数据 |  |
| `ID` | identification of the patient | **free** | 标识符，无个人语义 |  |
| `IGA` | Ig A | **blocked** | 法律保护的敏感数据 |  |
| `IGG` | Ig G | **blocked** | 法律保护的敏感数据 |  |
| `IGM` | Ig M | **blocked** | 法律保护的敏感数据 |  |
| `LDH` | lactate dehydrogenase | **blocked** | 法律保护的敏感数据 |  |
| `PIC` |  | **blocked** | 法律保护的敏感数据 |  |
| `PLT` | platelet | **blocked** | 实验室检测结果，受法律保护 |  |
| `PT` | prothrombin time | **blocked** | 法律保护的敏感数据 |  |
| `RA` | Rhuematoid Factor | **blocked** | 法律保护的敏感数据 |  |
| `RBC` | Red blood cell | **blocked** | 实验室检测结果，受法律保护 |  |
| `RF` | RAHA | **blocked** | 法律保护的敏感数据 |  |
| `RNP` | anti-ribonuclear protein | **blocked** | 法律保护的敏感数据 |  |
| `SC170` | anti-scl70 | **blocked** | 法律保护的敏感数据 |  |
| `SM` | anti-SM | **blocked** | 法律保护的敏感数据 |  |
| `SSA` | anti-SSA | **blocked** | 法律保护的敏感数据 |  |
| `SSB` | anti-SSB | **blocked** | 法律保护的敏感数据 |  |
| `T-BIL` | total bilirubin | **blocked** | 法律保护的敏感数据 |  |
| `T-CHO` | total cholesterol | **blocked** | 法律保护的敏感数据 |  |
| `TAT` |  | **blocked** | 法律保护的敏感数据 |  |
| `TAT2` |  | **blocked** | 法律保护的敏感数据 |  |
| `TG` | triglyceride | **blocked** | 法律保护的敏感数据 |  |
| `TP` | total protein | **blocked** | 法律保护的敏感数据 |  |
| `U-PRO` | proteinuria | **blocked** | 法律保护的敏感数据 |  |
| `UA` | uric acid | **blocked** | 实验室检测结果，受法律保护 |  |
| `UN` | urea nitrogen | **blocked** | 法律保护的敏感数据 |  |
| `WBC` | White blood cell | **blocked** | 实验室检测结果，受法律保护 |  |

## `Patient`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `Admission` | patient was admitted to the hospital (+) or followed at the outpatient clinic (-) | **free** | 公开/非个人数据 |  |
| `Birthday` | Birthday | **free** | 日期字段，未关联到特定个人 |  |
| `Description` | the first date when a patient data was recorded | **free** | 公开/非个人数据 |  |
| `Diagnosis` | disease names | **blocked** | 医疗数据，严格受法律保护 |  |
| `First Date` | the date when a patient came to the hospital | **free** | 日期字段，未关联到特定个人 |  |
| `ID` | identification of the patient | **free** | 标识符，无个人语义 |  |
| `SEX` | Sex | **free** | 公开/非个人数据 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/thrombosis_prediction.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
