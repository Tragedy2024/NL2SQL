# 数据集说明

本包内含 `data/` 目录（约 2.4G），**仅包含代码实际引用的数据集**，足以完整复现全部实验。

---

## 一、包内数据（复现实验所需）

以下 5 个路径由 `experiments/common.py:30-40` 引用，**缺失将无法运行实验**。

| 路径 | 体积 | 内容 | 用途 |
|------|------|------|------|
| `data/bird-dev/dev_20240627/` | 1.5G | BIRD dev 1,534 条查询 + 11 个 SQLite 库 | RQ1/RQ2 主实验 |
| `data/bird-dev/complex_queries.json` | 17K | 复杂查询 ID 清单 | 查询筛选 |
| `data/spider1.0/database/` | 926M | Spider 166 个 SQLite 库 | 执行评估（EX） |
| `data/spider1.0/tables.json` | 1.0M | Spider schema 定义 | Schema 加载 |
| `data/spider1.0/dev.json` | 3.5M | Spider dev 1,034 条查询 | RQ1/RQ2 主实验 |

**SSA 标注覆盖 31 个库**（11 BIRD + 20 Spider）。`spider1.0/database/` 内含 166 个库，
其中 20 个有对应 SSA 标注，其余库用于 EX 执行比对。

---

## 二、未包含的数据

为控制包体积，以下数据集**未打包**。它们在本项目的代码、配置、脚本中**零引用**，
不影响任何实验运行。如需可通过原始来源获取：

| 数据集 | 原体积 | 说明 | 获取地址 |
|--------|--------|------|---------|
| ScienceBenchmark | 7.8G | sdss / cordis / oncomx 三库，299 条查询。未纳入实验 | https://github.com/ServiceNow/sciencebenchmark |
| Spider test 集 | 982M | 本项目仅使用 dev 集 | https://yale-lily.github.io/spider |
| Spider-Syn | 55M | 同义改写基准，未使用 | https://github.com/ygan/Spider-Syn |
| Spider-DK | 3.3M | 领域知识基准，未使用 | https://github.com/ygan/Spider-DK |
| Spider-Realistic | 2.5M | 真实化改写基准，未使用 | https://github.com/tshu-w/spider-realistic |
| BIRD dev 原始压缩包 | 331M | 与包内已解压的 `dev_20240627/` 内容重复 | https://bird-bench.github.io/ |
| `ryplus_uni_workflow.sql` | 1.1M | 单个 SQL 文件，未使用 | — |

---

## 三、数据放置与校验

代码通过 `experiments/common.py` 从项目根目录相对定位数据，**无需额外配置**：

```python
_BASE = <项目根目录>
BIRD_DIR   = <root>/data/bird-dev/dev_20240627
SPIDER_DIR = <root>/data/spider1.0
```

确认解压后的目录结构为：

```
<项目根>/
├── data/
│   ├── bird-dev/
│   │   ├── complex_queries.json
│   │   └── dev_20240627/{dev.json, dev_tables.json, dev_databases/}
│   └── spider1.0/{dev.json, tables.json, database/}
├── src/
├── experiments/
└── ...
```

**环境自检**（需先 `pip install -r requirements.txt`）：

```bash
python -c "
from experiments.common import QuerysetLoader
from ssa.loader import load_ssa
from auditor.base import SecurityAuditor
loader = QuerysetLoader()
ssa = load_ssa('financial', 'config/ssa')
print('环境就绪')
"
```

**数据完整性抽查**：

```bash
python -c "
import json
print('BIRD dev  :', len(json.load(open('data/bird-dev/dev_20240627/dev.json', encoding='utf-8'))), '条')
print('Spider dev:', len(json.load(open('data/spider1.0/dev.json', encoding='utf-8'))), '条')
"
# 预期输出：BIRD dev 1534 条 / Spider dev 1034 条
```

---

## 四、数据集来源与许可

| 数据集 | 来源 | 许可 |
|--------|------|------|
| BIRD | https://bird-bench.github.io/ | 见数据集主页 |
| Spider 1.0 | https://yale-lily.github.io/spider | CC BY-SA 4.0 |

请遵循各数据集的原始许可协议使用。
