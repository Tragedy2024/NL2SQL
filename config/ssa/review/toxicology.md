# toxicology — SSA 标签审查

> **数据库**: `toxicology`
> **表**: 4
> **列**: 11 总计 (free=11, controlled=0, blocked=0)
> **状态**: 自动生成 — 需要人工审查

---

## `atom`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `atom_id` | the unique id of atoms | **free** | 标识符，无个人语义 |  |
| `element` | the element of the toxicology | **free** | 公开/非个人数据 |  |
| `molecule_id` | identifying the molecule to which the atom belongs | **free** | 标识符，无个人语义 |  |

## `bond`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `bond_id` | unique id representing bonds | **free** | 标识符，无个人语义 |  |
| `bond_type` | type of the bond | **free** | 类别/标签，公开属性 |  |
| `molecule_id` | identifying the molecule in which the bond appears | **free** | 标识符，无个人语义 |  |

## `connected`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `atom_id` | id of the first atom | **free** | 标识符，无个人语义 |  |
| `atom_id2` | id of the second atom | **free** | 标识符，无个人语义 |  |
| `bond_id` | bond id representing bond between two atoms | **free** | 标识符，无个人语义 |  |

## `molecule`

| Column | Description | ECL | Reason | Review |
|--------|-------------|-----|--------|--------|
| `label` | whether this molecule is carcinogenic or not | **free** | 公开/非个人数据 |  |
| `molecule_id` | unique id of molecule | **free** | 标识符，无个人语义 |  |

## 跨域规则

（尚未定义）

---
*审查后编辑 `config/ssa/toxicology.yaml`。然后重新运行 pilot/RQ1 获取更新结果。*
