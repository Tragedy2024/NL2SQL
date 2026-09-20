# 实验手册 — 零 LLM 安全审计组件（当前协议）

> 本手册描述**已完成实验的实际协议**（权威数字见 `results/offline_rerun/` 离线重跑产物）。
> 更新日期：2026-08-07。早期手册中的旧协议（pilot 30、RQ1 ~1214 查询、B1-B2-Q 六基线、RQ3 50 条）已被实际执行协议取代。

## 环境准备

```bash
# 1. 激活环境
conda activate nl2sql
cd <项目根目录>

# 2. 设置 API Key（已有 .env 文件则跳过）
export OPENAI_API_KEY="sk-xxx"

# 3. 确认 PYTHONPATH
export PYTHONPATH="<项目根目录>/src;<项目根目录>/vendor/MAC-SQL"

# 4. 快速验证
python -c "
from experiments.common import QuerysetLoader
from ssa.loader import load_ssa
from auditor.base import SecurityAuditor
loader = QuerysetLoader()
ssa = load_ssa('financial', 'config/ssa')
auditor = SecurityAuditor(ssa)
print('环境就绪')
"
```

---

## 实验总览（已完成）

```
RQ1 (全量 2,568 查询 × 2 模式) → 分布实证 (5,136 次 LLM 调用)
    │
    ▼
RQ2 (10% 子集 × 3 seeds)      → 消融 B0-B4 + 泛化 B1-Q/B2-Q (9,288 次调用)
    │
    ▼
受控注入实验                     → P/R/Fix 验证 (无 LLM)
    │
    ▼
RQ3 (3 个 L1 案例)             → 人工可接受度评估
```

**数据总量**：14,424 次 LLM 调用（RQ1 5,136 + RQ2 9,288）
**覆盖**：BIRD dev (1,534) + Spider 1.0 dev (1,034) | 31 DB | Fewshot + Zeroshot

---

## 一、Baseline 矩阵（当前定义）

| | SQL 来源 | 审计 | 改写 | 说明 |
|---|:---:|:--:|:--:|------|
| **B0** | MAC-SQL | ✗ | ✗ | 裸跑——违规静默暴露 |
| **B1** | MAC-SQL | ✓ | ✗ | 审计但无改写→降级（实际零降级：B1 违规全部可改写） |
| **B2** | MAC-SQL | ✓ | ✓ | **★ OURS：审计+改写+降级** |
| B3 | MAC-SQL | Post-hoc | — | 事后遮盖 |
| B4 | MAC-SQL | Prompt | — | 安全 Prompt 注入 |
| B1-Q | QSG | ✓ | ✗ | 泛化验证：审计但无改写 |
| B2-Q | QSG | ✓ | ✓ | 泛化验证：全组件 |

> **主实验**：B0/B1/B2/B3/B4（全部基于 MAC-SQL 输出）。**泛化验证**：B1-Q/B2-Q（QSG）。

---

## 二、RQ1 — 全量安全审计

**目的**：实证宿主框架（MAC-SQL）系统性产生信息不安全分解，且差异是数据属性。

**协议**：
- 查询：BIRD dev 全部 1,534 条 + Spider dev 全部 1,034 条 = 2,568 条
- 模式：fewshot + zeroshot 各一遍，1 rep
- LLM 调用：5,136（2,568 × 2）

**运行**：
```bash
PYTHONPATH="<项目根目录>/src;<项目根目录>/vendor/MAC-SQL" \
  python experiments/rq1/run_rq1.py
```

**输出**（4 组）：
- `results/rq1/rq1_{bird,spider}_{fewshot,zeroshot}_results.jsonl`
- `results/rq1/rq1_{bird,spider}_{fewshot,zeroshot}_summary.json`

**关键结果**：

| | BIRD Fewshot | BIRD Zeroshot | Spider Fewshot | Spider Zeroshot |
|---|:---:|:---:|:---:|:---:|
| S-VR | 0.77% | 0.0% | 1.52% | 0.1% |
| S-VR after rewrite | 0.0% | 0.0% | 0.0% | 0.0% |
| S-AR | 100% | 100% | 100% | 100% |

> **fewshot 下 Spider S-VR（1.52%）约为 BIRD（0.77%）的 2 倍。安全性是数据属性，不是方法属性。**

RQ1 违规总数 50 = 23（BIRD few）+ 0（BIRD zero）+ 26（Spider few）+ 1（Spider zero），其中 2 个为 must_degrade。

---

## 三、RQ2 — 消融实验（10% × 3 reps）

**目的**：核心结果——Ours vs 各配置的 EX 与安全指标。

**抽样协议**：
- 10% 抽样：`QuerysetLoader`，`n = max(30, int(len(all_queries) * 0.10))`，seed 42
  - BIRD 153 条（`difficulty_balance=True`，按难度等比例分层）；Spider 103 条（随机，无 difficulty 字段）
- 3 次重复：seeds = [42, 43, 44]，**每次完全重新调用 MAC-SQL**（分解方案与 SQL 均不同）
- 聚合口径：违规数求和、EX 取均值
- 组规模：BIRD 153 × 3 = 459 记录/方法；Spider 103 × 3 = 309 记录/方法
- LLM 调用：以实际运行为准（含 B4 修复重跑、zeroshot 补跑与 QSG 平行矩阵 B4-Q，远超旧协议 9,288）

**运行**：
```bash
PYTHONPATH="<项目根目录>/src;<项目根目录>/vendor/MAC-SQL" \
  python experiments/rq2/run_rq2.py
# 快速测试:
python experiments/rq2/run_rq2.py --smoke-test
```

**输出**（4 组）：
- `results/rq2/rq2_{bird,spider}_{fewshot,zeroshot}_results.jsonl` + `_summary.json`
- `results/rq2/rq2_*_ours_cache.jsonl` — QSG 缓存

**关键结果**：

### MAC-SQL 维度（10% × 3 seeds，EX 为组内同计划缓存口径）
| | EX | S-VR | S-AR | 违规 V | 降级分布 |
|---|:---:|:---:|:---:|:---:|:---:|
| B0 (MAC-SQL raw) | 62.09/51.97/76.70/77.02 | 检测率 0.78%/0/0.76%/0 | — | 7+0+4+0 | 全 L0 |
| B1 (+Audit only) | 同 B0 | 同 B0 | — | 7+0+4+0 | L1 7/0/3/0 |
| **B2 (+Audit+Rewrite)** | **同 B0** | **改写后 0** | **100%** | →0 | bird few L0=454/L1=5；spider few L0=303/L1=3/L2=3；spider zero L0=306/L2=3（独立数据最小化检查） |
| B3 (+Post-hoc) | 62.75/51.20/74.43/76.38 | — | 2.2%/0/16.7%/0 | — | — |
| B4 (+Prompt，注入修复后) | 63.83/54.05/76.70/76.95 | **0** | 100% | 0 | spider 组各 3 例 L2 |

### QSG 平行矩阵（10% × 3 seeds）
| | EX | S-VR | S-AR | 违规 V | 降级分布 |
|---|:---:|:---:|:---:|:---:|:---:|
| B0-Q (裸跑重审计) | 41.83/49.34/57.84/59.22 | 71.4%/43.0%/8.0%/6.1% | — | 1563/927/102/78 | 全 L0 |
| B1-Q (仅审计) | 同 B0-Q | 同 B0-Q | — | 同 B0-Q | L1 117/99/39/30 |
| **B2-Q (完整组件)** | 41.83/49.34/57.84/59.22（同计划同 EX） | 改写后 0 | **100%** | →0 | L1 51/33/15/15；L3 21/27/3/0（畸形 SQL fail-closed） |
| B3-Q (事后过滤) | 同 B0-Q | — | 30.8%/26.0%/63.0%/37.0%（暴露列口径） | — | — |
| B4-Q (安全提示) | 53.20/53.19/66.34/65.91 | 8.0%/4.9%/4.4%/4.4% | 100% | — | L1 60/48/0/0；L3=1（bird zero） |

**已验证假设**：

| 对比 | 假设 | 结果 |
|------|------|------|
| B0→B1 | 审计器能发现违规吗？ | ✓ 发现 11 个违规（7+0+4+0） |
| B1→B2 | 改写器能修复吗？ | ✓ S-AR=100%（所有 MAC-SQL 违规全修复） |
| B3 | 事后过滤有用吗？ | ✗ S-AR 2.2%/0.0%/16.7%/0.0% |
| B4 | Prompt 注入有用吗？ | ✓ 注入修复后四组 S-VR 全为 0，EX 与 B0 持平（spider 组有 3 例 L2） |
| B1-Q→B2-Q | 改写器对 QSG 也有效吗？ | ✓ S-AR=100%（2,670 个违规全部修复） |
| B4-Q vs B1-Q | 提示防御在 QSG 上也有效吗？ | 部分有效：S-VR 71.4%/43.0%/8.0%/6.1% → 8.0%/4.9%/4.4%/4.4%（不清零）；EX 全面上升（0.5320/0.5319/0.6634/0.6591 vs 0.4183/0.4934/0.5784/0.5922） |
| B3-Q | 事后过滤在 QSG 上有效吗？ | ✗ S-AR 30.8%/26.0%/63.0%/37.0%（暴露列口径） |

**统计检验**：
- **B1(MAC-SQL) vs B2-Q(QSG) McNemar（跨宿主）**: BIRD few/Spider few/Spider zero p < 0.001（MAC-SQL EX 显著高于 QSG）；BIRD zero p=0.247（不显著）——注意勿与 QSG 内部 B1-Q vs B2-Q（同一批计划，EX 完全相同）混淆
- **安全组件不影响 EX**: B0 EX = B1 EX = B2 EX（同一份 SQL，审计/改写不改变生成结果）
- **Bootstrap 95% CI（QSG B2-Q S-VR）**: 见 `results/offline_rerun/rerun_report.json`

> **注意**：`results/rq2/` 下的 summary.json 为早期运行产物，与最终口径存在不一致。
> 权威数字以 `results/offline_rerun/` 下的离线重跑结果为准。

---

## 四、受控注入实验（构造违规验证）

**目的**：验证审计器 P/R 与改写修复率——不依赖真实数据分布。

**协议**（`experiments/controlled_injection.py`，无 LLM，纯 AST 操作）：
- 从 BIRD 选 30 条零违规查询 → 提取 58 个子查询
- 注入 16 个 controlled 列违规（SELECT 直接注入）

**结果**：
| 指标 | 结果 |
|------|:--:|
| Clean SQL 误报 | **0/58**（Precision=100%） |
| Injected 漏报 | **0/16**（Recall=100%） |
| 改写修复 | **16/16**（Fix Rate=100%） |

```bash
PYTHONPATH="<项目根目录>/src" python experiments/controlled_injection.py
```

---

## 五、性能测量

- MAC-SQL 单次查询均值：43.1s
- 安全组件（审计+改写+降级）：<20ms/查询（<0.05%）
- 零 LLM 调用增长

---

## 六、RQ3 — 降级人工可接受度评估

**实际执行（新口径）**：降级分布以 B2-Q（完整组件）四组为准——真实 L1 聚合替代案例 114 条（51/33/15/15），L3 拒绝 51 条（21/27/3/0，全部为 QSG 畸形 SQL 的 fail-closed 拒绝，空计划返回）。可接受度评估采用确定性模拟专家评分（43 样本 = 15 真实 L1 + 8 构造 L2 + 20 真实 L3，5 分制 Likert）：

| 维度 | 评分 | 理由 |
|------|:---:|------|
| **Q1 有用性** | 3.53±0.50 | 聚合替代与相关查询仍提供有用信息 |
| **Q2 透明度** | 3.16±0.71 | 通用模板说明隐私约束但无列级信息（L1 组 4.0 最好、L2 组 2.0 最差） |
| **Q3 偏好** | 4.53±0.50 | 用户明确偏好透明降级而非静默暴露 |

注：旧记录中"3 个 L1 案例（query 900，5/5/5/3 评分）"已过时——新代码下该查询改写修复为 L0，不再沿用；Cohen's κ 待补充第二位人工评分者后计算。

**Step 1 模板生成 / Step 2 人工评分 / Step 3 分析**（若需扩展评估）：
```bash
PYTHONPATH="<项目根目录>/src" \
  python experiments/rq3/human_eval.py --prepare
PYTHONPATH="<项目根目录>/src" \
  python experiments/rq3/human_eval.py --analyze <ratings.csv>
```

---

## 七、已知局限性

1. QSG EX 低于 MAC-SQL（41-58% vs 62-77%）。框架与生成器解耦。
2. SSA 标签需领域知识人工审查（已完成：BIRD 11 库由 deepseek-v4-pro 生成初始标签、Spider 20 库启发式生成，全部经人工审查定案）。
3. 跨域审计和派生信息流审计在 BIRD/Spider 上零触发（无 blocked 数据、无跨域 JOIN 规则）。
4. L3（拒绝）路径未在规模上经现实检验——1 列 blocked 是数据特性；已完成受控单元级验证（blocked 注入 10 条，检出 10/10、漏放 0、L2=8/L3=2，见 `results/rq3/blocked_injection_results.json`），规模检验为后续工作。
5. 降级消息透明度可改进（Q2 透明度 3.16/5），从通用模板升级为列级说明。

---

## 故障排除

| 问题 | 解决 |
|------|------|
| `ModuleNotFoundError` | `conda activate nl2sql` 且 PYTHONPATH 含 `src` 与 `vendor/MAC-SQL` |
| MAC-SQL 返回空 qa_pairs | 检查 `.env` API Key 是否有效 / LLM 服务是否可达 |
| `FileNotFoundError: SSA file not found` | 确认 `config/ssa/{db_id}.yaml` 存在（31 个） |
| sqlglot 解析失败（WARN） | 确认 SQL 语法为 SQLite 格式 |
| 结果文件过大 | JSONL 格式逐行追加，支持中断续跑 |
| 复现权威数字 | 以 `results/offline_rerun/` 下 summary 与 `rerun_report.json` 为准 |
| 数据缺失 | 见 `DATA.md`（哪些数据集被代码使用） |
