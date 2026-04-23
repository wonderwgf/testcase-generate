# 测试用例生成 - 全流程编排

根据用户提供的项目名称、迭代标识和输入文件，依次执行完整的测试用例生成流程。

## 项目与迭代识别（Agent 必做）

### 项目识别

按以下优先级确定项目目录：
1. 用户显式提供项目名（如 `/testcasegen scpr V4.5`）
2. 用户 `@` 了文件 → 从路径中提取项目目录名（如 `@acflow/input/prd/` → `acflow`）
3. 工作区根下只有一个含 `input/` 的目录 → 自动选中
4. 以上都不满足 → 列出可选项目目录，询问用户

### 迭代标识

迭代标识用于隔离同一项目内多个版本/迭代的输入与产出。

**获取方式（按优先级）**：
1. 用户显式提供（如 `/testcasegen acflow V4.5`，第二个位置参数即迭代标识）
2. 用户使用 `--iter <标识>` 参数
3. 用户 `@` 了 `input/prd/<子目录>/` → 子目录名即迭代标识
4. 以上都未提供 → Agent 扫描 `input/prd/` 下的**子目录**，列出可选迭代：
   ```
   📋 项目 acflow 下识别到以下迭代：
     [1] V4.3（input/prd/V4.3/，含 2 个文件）
     [2] V4.5（input/prd/V4.5/，含 1 个文件）
   另有跨迭代共享文档：通用业务规则清单.xlsx、标品对接中台场景及功能.xlsx
   请选择迭代编号，或输入新的迭代标识（将创建对应子目录）：
   ```
5. `input/prd/` 下无子目录且只有根级文件 → 提示用户输入迭代标识，Agent 创建子目录并引导用户将文件移入

**迭代标识的作用（贯穿全流程）**：

| 环节 | 路径规则 |
|------|---------|
| 迭代需求文档（输入） | `input/prd/<迭代>/` |
| 迭代需求文档（转换产出） | `output/prd/<迭代>/` |
| 共享辅助文档（输入） | `input/prd/` 根下文件（不在任何子目录中） |
| 共享辅助文档（转换产出） | `output/prd/` 根下 |
| 需求解析报告 | `output/prd_analysis/<迭代>_需求解析报告.md` |
| 测试概要 | `output/test_outline/<迭代>_测试概要.md` |
| 测试用例 | `output/test_cases/<迭代>_测试用例.md` |
| XMind | `output/xmind/<迭代>_测试用例.xmind` |
| 知识库 | `input/knowledge/`（跨迭代共享，不区分） |

## 配置常量（唯一来源）

所有阈值、档位、目标行数集中在此。任意调整必须**同步**修改下游文件中标注「同步点」的位置（mdc 文件之间无法自动引用，依赖纪律保证一致）。

| 名称 | 值 | 含义 | 同步点 |
|------|----|----|-------|
| `SPLIT_HARD_MAX` | 800 行 | Step 2.7 触发拆分阈值；`split_prd.py` 的 `hard_max` 默认值 | `01prdreadrule.mdc § 第-2步`、`testcasegen-split-prd/SKILL.md` |
| `PARSE_SOFT_MAX` | 1500 行 | Step 4 概要生成的"友好建议"阈值（不强制） | `02testdesign.mdc § 第-1步` |
| `BUDGET_TIER` | ≤6 → 全量 / 7–12 → 上限 6 / >12 → 上限 4 | 模块循环模式下，每个 Step 内连续处理模块数上限 | `testcasegen.workflow.md § Phase 2「上下文预算管理」` |
| `MODULE_TARGET_LINES` | 600 行 | `split_prd.py` 拆分时模块的目标行数 | `testcasegen-split-prd/SKILL.md` |
| `MODULE_MIN_LINES` | 80 行 | `split_prd.py` 模块行数下限，低于此值会合并相邻模块 | `testcasegen-split-prd/SKILL.md` |

> 改 `SPLIT_HARD_MAX`、`PARSE_SOFT_MAX` 时，**必须**同步打开对应 mdc 修改对应数字；mdc 顶部已加同步 banner 提醒。

---

## 步骤识别（Agent 必做）

### 1. 显式参数（最高优先级）

| 形式 | 含义 |
|------|------|
| `--from <step>` | 从指定步骤开始，向后执行所有步骤 |
| `--only <step>` | 只执行该步骤，不向后传递 |

显式参数命中时，**直接采用，跳过下面的关键词推断**。

### 2. 关键词推断（无显式参数时）

按以下规则自顶向下匹配：

1. 用户文字含「只」「仅」「单独」其中之一 → **only 模式**
2. 用户文字含「从」「开始」 → **from 模式**
3. 否则 → **默认 from 模式**，但 Agent **必须在第一行明确告知用户当前选择并给出修改方式**：
   > 检测到关键词「文档转换」，将从 Step 2 开始执行后续全部步骤；如只想执行 Step 2，请补充「只」字或加 `--only 2`。

| 关键词 | 解析结果 |
|--------|---------|
| 初始化 / 只初始化 | `only Step 1` |
| 文档转换 / 转md | `from Step 2`（含「只」→ `only Step 2`） |
| 知识库索引 / 索引 / 只刷索引 | `only Step 2.5` |
| 需求解析 | `from Step 3` |
| 测试概要 | `from Step 4` |
| 测试用例 / 生成用例 | `from Step 5` |
| xmind / 导出 | `only Step 6` |

### 3. 自动检测（无显式参数也无关键词时）

由「进度判断」按文件系统快照决定起跑点。

---

## 进度判断（按迭代过滤）

若用户未指定步骤、也未提供匹配关键词，Agent 扫描 `output/` 目录，**仅匹配当前迭代标识**的文件，按下面伪代码逐行判断（**自上而下首条命中即返回**）。

```text
mode = "module_loop" if exists("output/prd/<迭代>/modules/_manifest.json") else "normal"
snap = scan_iter_outputs(<迭代>)

# ---- 模块循环模式 ----
if mode == "module_loop":
    if snap.merged.test_cases:                  return Step 6   # 合并产出已存在 → 仅导出
    if snap.modules.test_cases    == "all":     return Step 6   # 全模块完成 → 合并+导出
    if snap.modules.test_cases    == "partial": return Step 5   # 接力未完成模块
    if snap.modules.test_outline  == "all":     return Step 5   # 第一个未完成模块
    if snap.modules.test_outline  == "partial": return Step 4
    if snap.modules.prd_analysis  == "all":     return Step 4
    if snap.modules.prd_analysis  == "partial": return Step 3
    return Step 3                                                # 模块循环起步

# ---- 普通模式 ----
else:
    if snap.merged.test_cases:    return ask("Step 5 补充 / Step 6 导出 ?")
    if snap.merged.test_outline:  return Step 5
    if snap.merged.prd_analysis:  return Step 4
    if snap.prd_md_exists:        return Step 3
    return Step 1
```

**`snap` 字段含义**：

| 字段 | 含义 |
|------|------|
| `snap.merged.<step>` | `output/<step>/<迭代>_*.md` 是否存在（合并/总产出） |
| `snap.modules.<step>` | `output/modules/<迭代>/*/<step>.md` 的覆盖度：`"none"` / `"partial"` / `"all"` |
| `snap.prd_md_exists` | `output/prd/<迭代>/` 下是否有 md（普通模式判断 Step 3 起步用） |

## 目录结构

```
<项目>/
├── input/
│   ├── prd/                           ← 需求文档（可以是 docx/xlsx，按迭代子目录组织）
│   │   ├── <迭代1>/                   ← 迭代专属需求文档
│   │   ├── <迭代2>/
│   │   └── 通用业务规则清单.xlsx       ← 根下 = 跨迭代共享辅助文档
│   │
│   └── knowledge/                     ← 知识库（要求 md 格式，跨迭代共享）
│       ├── baseline_cases/            ← 基线测试用例
│       ├── business/                  ← 业务规则 / 流程文档
│       ├── codedesign/                ← 技术设计文档
│       └── prd/                       ← 历史需求文档
│
└── output/
    ├── prd/
    │   ├── <迭代1>/                   ← 转换后的 md（与 input 迭代子目录对应）
    │   └── 通用业务规则清单.md         ← 共享文档转换产出
    ├── prd_analysis/                  ← <迭代>_需求解析报告.md
    ├── test_outline/                  ← <迭代>_测试概要.md
    ├── test_cases/                    ← <迭代>_测试用例.md
    └── xmind/                         ← <迭代>_测试用例.xmind
```

## 执行流程

按以下顺序执行。**Phase 1 全自动执行，不暂停；Phase 2 的走停由「步间引导 · 单一判定表」决策（阈值与档位见「配置常量」）；Phase 3 全自动。**

> 各 Step 的具体执行规则（含模式判断、预算管理、规则路径表、产出路径）独立在 `testcasegen.workflow.md`。
>
> Agent 必须按需 Read：根据「步骤识别」确定的起跑步骤，仅加载本次需要的 Step 段落，不要整文件加载。

| Phase | 涉及步骤 | 一句话职责 | 详细规则锚点 |
|-------|---------|-----------|-------------|
| Phase 1（自动） | Step 1 / 1.5 / 2 / 2.5 / 2.7 | 初始化目录、检查输入、文档转 md、知识库建索引、超阈值文档拆模块 | `testcasegen.workflow.md § Phase 1` |
| Phase 2（按判定表走停） | Step 3 / 4 / 5 | 需求解析 → 测试概要 → 测试用例（普通模式整篇 / 模块循环模式逐模块） | `testcasegen.workflow.md § Phase 2`（含上下文预算管理） |
| Phase 3（自动） | Step 6 | 模块循环模式合并多模块产出，导出 XMind | `testcasegen.workflow.md § Phase 3` |

**起跑后的执行原则**：

- 每个 Step 开始前，Agent **先 Read** `testcasegen.workflow.md` 中对应章节，再按其内容执行
- 已完成的 Step（产出已存在）跳过；详见各 Step 段落"已有产出的跳过"约定
- 每步完成后，按本文「步间引导 · 单一判定表」决定自动继续或暂停

## 步间引导（Agent 必做）

### 核心规则（强制 · 单一判定表）

每步完成后，Agent 仅依据本表决定**自动继续 / 暂停等待**，**不要再翻别处**。判定使用以下三类信号（按当前步取对应列）：

- **完成度**：本步是否已全量完成（普通模式 = 单文件全跑完；模块循环模式 = 当前预算窗口内的模块全跑完）
- **质量信号**：Step 3 → 风险点条数；Step 4 → 信息源冲突 / 关键缺口；Step 5 → 是否触发分功能模块分批
- **预算状态**：仅模块循环模式相关。`BUDGET_TIER`（见「配置常量」表）触顶 = 暂停

| 步骤 | 自动继续 ↩ 进入下一步 | 暂停等待 ⏸ 用户确认后继续 |
|------|----------------------|--------------------------|
| Step 3 | 完成度 = 全量 **且** 风险点 = 0 **且** 预算未触顶 | 完成度 = 部分 / 风险点 > 0 / 预算触顶（任一） |
| Step 4 | 完成度 = 全量 **且** 无冲突/缺口 **且** 预算未触顶 | 完成度 = 部分 / 有信息源冲突或关键缺口 / 预算触顶（任一） |
| Step 5 | 完成度 = 全量 **且** 预算未触顶 | 完成度 = 部分 / 预算触顶（任一） |
| Step 6 | 始终自动执行，完成后汇报结果 | — |

> 设计意图：原「自动继续条件」与「暂停等待条件」是**同一组信号的两种表述**，合并为单表后只看本表即可，避免改一处忘一处。

**自动继续时的输出格式**（一行）：
```
✅ Step N 完成（全量，无阻断项）→ 自动进入 Step N+1。
```

### 引导格式（仅暂停时输出）

**默认模式**（2~3 行，然后停止等待）：

1. **汇报本步结果**：产出文件路径 + 关键数量（如用例条数、要素数等）。
2. **提示补充材料**：Agent 主动扫描 `input/knowledge/`，若有文件则**列出分类统计**（如 baseline_cases 3 个、codedesign 2 个）并建议纳入；若为空则提一句「若有知识库材料（基线用例/设计文档/业务规则），放入 input/knowledge/ 对应子目录可提升质量」。
3. **给出下一步话术**：明确告知用户说什么即可继续（如「说『继续』进入 Step 4（测试概要）」），并在此**停止等待**。

### 引导禁止事项

- 不得在引导中展示规则路径、`.mdc` 文件名或让用户 @ 规则。

### 示例与命令调用

> 各类输出范例（暂停 / 全自动 / 预算暂停 / 接续恢复）以及完整的 `/testcasegen` 命令调用示例集中放在 `testcasegen.examples.md`。**Agent 仅在需要给用户演示输出格式时按需 Read，决策本身不依赖该文件。**

## 注意事项

- **上下文与跨会话接力**：大文档（拆分后 > 6 个模块）的 Step 3/4/5 通常需要多次会话接力完成。每次新开会话执行 `/testcasegen <项目> <迭代>`，Agent 通过文件系统进度判断自动从上次中断处继续，无需用户记忆执行到哪一步。模块循环模式下 Agent 会主动监控上下文预算并在合适时机暂停。
- 规则由 Agent 按内置表自行读取，**不向用户展示为 @ 项**。
- 所有路径相对于项目目录（如 `acflow/input/prd/`），项目目录位于工作区根下。
- 知识库要求 md 格式。若用户有 docx/xlsx 格式的知识库材料，引导其先用 `/testcasegen <项目> 文档转换` 转为 md 后放入 `input/knowledge/` 对应子目录。
- 进度判断完全基于文件系统（`output/modules/<迭代>/<n>/` 下是否存在对应步骤的产出文件），不依赖 `_manifest.json` 中的状态字段。
