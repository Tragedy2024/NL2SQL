# california_schools — SSA 标签审查

> **数据库**: `california_schools`
> **表**: 3
> **列**: 89 总计 (free=78, controlled=11, blocked=0)
> **状态**: 自动生成 — 需要人工审查

---

## `frpm`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `2013-14 CALPADS Fall 1 Certification Status` | 2013-14 CALPADS Fall 1 Certification Status | **free** | 类别/标签，公开属性 |  |
| `Academic Year` | Academic Year | **free** | 日期字段，未关联到特定个人 |  |
| `CDSCode` | CDSCode | **free** | 标识符，无个人语义 |  |
| `Charter Funding Type` | Charter Funding Type | **free** | 类别/标签，公开属性 |  |
| `Charter School (Y/N)` | Charter School (Y/N) | **free** | 组织/实体公开信息 |  |
| `Charter School Number` | Charter School Number | **free** | 聚合统计数据或计数，非个人级别 |  |
| `County Code` | County Code | **free** | 标识符，无个人语义 |  |
| `County Name` | County Code | **free** | 组织/实体名称，公开信息 |  |
| `District Code` | District Code | **free** | 标识符，无个人语义 |  |
| `District Name` | District Name | **free** | 组织/实体名称，公开信息 |  |
| `District Type` | District Type | **free** | 类别/标签，公开属性 |  |
| `Educational Option Type` | Educational Option Type | **free** | 类别/标签，公开属性 |  |
| `Enrollment (Ages 5-17)` | Enrollment (Ages 5-17) | **free** | 聚合统计数据或计数，非个人级别 |  |
| `Enrollment (K-12)` | Enrollment (K-12) | **free** | 聚合统计数据或计数，非个人级别 |  |
| `FRPM Count (Ages 5-17)` |  | **free** | 聚合统计数据或计数，非个人级别 |  |
| `FRPM Count (K-12)` | Free or Reduced Price Meal Count (K-12) | **free** | 聚合统计数据或计数，非个人级别 |  |
| `Free Meal Count (Ages 5-17)` | Free Meal Count (Ages 5-17) | **free** | 聚合统计数据或计数，非个人级别 |  |
| `Free Meal Count (K-12)` | Free Meal Count (K-12) | **free** | 聚合统计数据或计数，非个人级别 |  |
| `High Grade` | High Grade | **free** | 公开/非个人数据 |  |
| `IRC` |  | **free** | 公开/非个人数据 |  |
| `Low Grade` | Low Grade | **free** | 公开/非个人数据 |  |
| `NSLP Provision Status` | NSLP Provision Status | **free** | 类别/标签，公开属性 |  |
| `Percent (%) Eligible FRPM (Ages 5-17)` |  | **free** | 聚合统计数据或计数，非个人级别 |  |
| `Percent (%) Eligible FRPM (K-12)` |  | **free** | 聚合统计数据或计数，非个人级别 |  |
| `Percent (%) Eligible Free (Ages 5-17)` |  | **free** | 聚合统计数据或计数，非个人级别 |  |
| `Percent (%) Eligible Free (K-12)` |  | **free** | 聚合统计数据或计数，非个人级别 |  |
| `School Code` | School Code | **free** | 标识符，无个人语义 |  |
| `School Name` | School Name | **free** | 组织/实体名称，公开信息 |  |
| `School Type` | School Type | **free** | 类别/标签，公开属性 |  |

## `satscores`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `AvgScrMath` | average scores in Math | **free** | 聚合统计数据或计数，非个人级别 |  |
| `AvgScrRead` | average scores in Reading | **free** | 聚合统计数据或计数，非个人级别 |  |
| `AvgScrWrite` | average scores in writing | **free** | 聚合统计数据或计数，非个人级别 |  |
| `NumGE1500` | Number of Test Takers Whose Total SAT Scores Are Greater or Equal to 1500 | **free** | 标识符或代码 |  |
| `NumTstTakr` | Number of Test Takers in this school | **free** | 标识符或代码 |  |
| `cds` | California Department Schools | **free** | 组织/实体公开信息 |  |
| `cname` | county name | **free** | 组织/实体名称，公开信息 |  |
| `dname` | district segment | **free** | 组织/实体名称，公开信息 |  |
| `enroll12` | enrollment (1st-12nd grade) | **free** | 聚合统计数据或计数，非个人级别 |  |
| `rtype` | rtype | **free** | 类别/标签，公开属性 |  |
| `sname` | school name | **free** | 组织/实体名称，公开信息 |  |

## `schools`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `AdmEmail1` | administrator's email address | **controlled** | 个人联系方式（电子邮件），可追溯到个人 |  |
| `AdmEmail2` |  | **controlled** | 个人联系方式（电子邮件），可追溯到个人 |  |
| `AdmEmail3` |  | **controlled** | 个人联系方式（电子邮件），可追溯到个人 |  |
| `AdmFName1` | administrator's first name | **controlled** | 管理员姓名，个人标识符 |  |
| `AdmFName2` |  | **controlled** | 管理员姓名，个人标识符 |  |
| `AdmFName3` |  | **controlled** | 管理员姓名，个人标识符 |  |
| `AdmLName1` | administrator's last name | **controlled** | 管理员姓名，个人标识符 |  |
| `AdmLName2` |  | **controlled** | 管理员姓名，个人标识符 |  |
| `AdmLName3` |  | **controlled** | 管理员姓名，个人标识符 |  |
| `CDSCode` | CDSCode | **free** | 标识符，无个人语义 |  |
| `Charter` | This field identifies a charter school. | **free** | 组织/实体公开信息 |  |
| `CharterNum` | The charter school number, | **free** | 标识符或代码 |  |
| `City` | City | **free** | 公开/非个人数据 |  |
| `ClosedDate` | The date the school closed. | **free** | 日期字段，未关联到特定个人 |  |
| `County` | County name | **free** | 聚合统计数据或计数，非个人级别 |  |
| `DOC` | District Ownership Code | **free** | 标识符或代码 |  |
| `DOCType` | The District Ownership Code Type is the text description of the DOC category. | **free** | 类别/标签，公开属性 |  |
| `District` | District | **free** | 组织/实体公开信息 |  |
| `EILCode` | The Educational Instruction Level Code is a short text description of the institution's type relativ | **free** | 标识符，无个人语义 |  |
| `EILName` | The Educational Instruction Level Name is the long text description of the institution's type relati | **free** | 实体名称，公开信息 |  |
| `EdOpsCode` | The Education Option Code is a short text description of the type of education offered. | **free** | 标识符，无个人语义 |  |
| `EdOpsName` | Educational Option Name | **free** | 实体名称，公开信息 |  |
| `Ext` | The phone number extension of the school, district, or administrative authority. | **controlled** | 个人联系方式 |  |
| `FundingType` | Indicates the charter school funding type | **free** | 类别/标签，公开属性 |  |
| `GSoffered` | The grade span offered is the lowest grade and the highest grade offered or supported by the school, | **free** | 组织/实体公开信息 |  |
| `GSserved` | It is the lowest grade and the highest grade of student enrollment as reported in the most recent ce | **free** | 公开/非个人数据 |  |
| `LastUpdate` |  | **free** | 日期字段，未关联到特定个人 |  |
| `Latitude` | The angular distance (expressed in degrees) between the location of the school, district, or adminis | **free** | 地理坐标，公开数据 |  |
| `Longitude` | The angular distance (expressed in degrees) between the location of the school, district, or adminis | **free** | 地理坐标，公开数据 |  |
| `Magnet` | This field identifies whether a school is a magnet school and/or provides a magnet program. | **free** | 组织/实体公开信息 |  |
| `MailCity` |  | **free** | 公开/非个人数据 |  |
| `MailState` |  | **free** | 公开/非个人数据 |  |
| `MailStrAbr` |  | **free** | 公开/非个人数据 |  |
| `MailStreet` | MailStreet | **free** | 公开/非个人数据 |  |
| `MailZip` |  | **free** | 公开/非个人数据 |  |
| `NCESDist` | This field represents the 7-digit National Center for Educational Statistics (NCES) school district  | **free** | 标识符或代码 |  |
| `NCESSchool` | This field represents the 5-digit NCES school identification number. The NCESSchool combined with th | **free** | 标识符或代码 |  |
| `OpenDate` | The date the school opened. | **free** | 日期字段，未关联到特定个人 |  |
| `Phone` | Phone | **controlled** | 个人联系方式（电话），可追溯到个人 |  |
| `SOC` | The School Ownership Code is a numeric code used to identify the type of school. | **free** | 标识符或代码 |  |
| `SOCType` | The School Ownership Code Type is the text description of the type of school. | **free** | 类别/标签，公开属性 |  |
| `School` | School | **free** | 组织/实体公开信息 |  |
| `State` | State | **free** | 公开/非个人数据 |  |
| `StatusType` | This field identifies the status of the district. | **free** | 类别/标签，公开属性 |  |
| `Street` | Street | **free** | 公开/非个人数据 |  |
| `StreetAbr` | The abbreviated street address of the school, district, or administrative authority's physical locat | **free** | 组织/实体公开信息 |  |
| `Virtual` | This field identifies the type of virtual instruction offered by the school. Virtual instruction is  | **free** | 组织/实体公开信息 |  |
| `Website` | The website address of the school, district, or administrative authority. | **free** | 公开网站地址 |  |
| `Zip` | Zip | **free** | 公开/非个人数据 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/california_schools.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
