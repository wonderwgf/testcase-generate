# 测试用例生成 - 执行流程详细规则

> 本文件配套 `testcasegen.md`，记录 Phase 1/2/3 各 Step 的具体执行步骤。
>
> Agent 使用方式：在 `testcasegen.md` 完成"决策"后（确定起跑步骤、当前模式），按本文件章节锚点 Read 对应 Step 段落，仅加载需要的部分；不要一次性整文件加载。
>
> 阈值与档位的"唯一来源"在 `testcasegen.md § 配置常量`，本文件中出现的具体数字仅为执行说明，**调整请从配置常量入手**。

---

## Phase 1：环境准备（自动）

### Step 1 - 初始化目录

检查项目目录结构是否已存在（包含 `input/` 和 `output/`）：
- 已存在 → 跳过
- 不存在 → 调用 skill `testcasegen-init`，读取其 SKILL.md 并按流程执行

若用户提供了迭代标识，检查 `input/prd/<迭代>/` 和 `output/prd/<迭代>/` 是否存在，不存在则创建。

### Step 1.5 - 输入文件检查（自动）

初始化完成后，扫描输入目录：

1. **检查迭代需求文档**：`input/prd/<迭代>/` 是否有文件
   - 有文件 → 继续
   - 为空 → 暂停，输出引导：
     ```
     📂 迭代目录 input/prd/<迭代>/ 当前为空。
     请将本迭代的需求文档（docx/xlsx）放入该目录，然后说「继续」。
     ```
   - **⚠️ 恢复点约定（强制）**：用户说「继续」后，Agent 必须从 **Step 2** 重新开始，依次执行完整 Phase 1 序列：Step 2 → Step 2.5 → Step 2.7，不得跳过中间步骤。

2. **提示知识库**（首次使用该项目时）：若 `input/knowledge/` 整体为空，输出一次性提示：
   ```
   💡 知识库目录 input/knowledge/ 当前为空。如有以下材料可放入对应子目录（要求 md 格式）：
     · baseline_cases/  — 基线测试用例
     · business/        — 业务规则、流程文档
     · codedesign/      — 技术设计文档
     · prd/             — 历史迭代需求文档
   若文档为 docx/xlsx，可先用「/testcasegen <项目> 文档转换」转为 md 后放入。
   放入后建议执行知识库索引（Step 2.5 会自动处理）。
   ```

### Step 2 - 文档转换

仅扫描 `input/prd/` 下的 .docx / .xlsx / .xls 文件（含迭代子目录和根级共享文档）：

- **迭代子目录** `input/prd/<迭代>/` 中的文件 → 转换产出到 `output/prd/<迭代>/`
- **根级共享文档** `input/prd/` 直接下的文件 → 转换产出到 `output/prd/`
- 对应 output 下已有同名 .md → 跳过该文件
- 全部已转换 → 跳过

调用 skill `testcasegen-all2md` 执行转换。完成后列出 `output/prd/<迭代>/` 和 `output/prd/` 根下所有可用的 md 文件。

### Step 2.5 - 知识库索引（自动）

扫描 `input/knowledge/` 目录：

- **无 .md 文件** → 跳过
- **有 .md 文件，但 `knowledge_index.md` 不存在** → 自动调用 skill `testcasegen-knowledge-index` 生成索引
- **`knowledge_index.md` 已存在，但知识库有变更**（以下任一条件满足即视为有变更）：
  · 存在 .md 文件更新时间晚于 `knowledge_index.md`
  · 存在新增 .md 文件（索引中未收录）
  · 索引中收录的文件已不存在
  → 自动调用 skill `testcasegen-knowledge-index` 刷新索引
- **已是最新** → 跳过，告知用户「知识库索引已是最新，跳过」

### Step 2.7 - 文档拆分（大文档检测，自动）

> 阈值 `SPLIT_HARD_MAX`（默认 800 行）见 `testcasegen.md § 配置常量`。

扫描 `output/prd/<迭代>/` 下所有 md 文件（不含 `modules/` 子目录）：

- **总行数 ≤ SPLIT_HARD_MAX** → 跳过，进入 Phase 2 正常流程
- **`modules/_manifest.json` 已存在** → 跳过，复用上次拆分，告知用户「已有拆分方案（N 个模块），直接使用」
- **总行数 > SPLIT_HARD_MAX** → 调用 skill `testcasegen-split-prd`，读取其 SKILL.md 并执行：
  1. 对超阈值的 md 文件运行 `split_prd.py`
  2. 脚本识别共享前置章节（术语/概述/参考文档等）+ 将功能章节分组，输出拆分方案
  3. Agent 格式化展示方案后**暂停，等用户确认**：
     ```
     📋 文档共 N 行，建议拆分为 M 个模块：
       共享前置（每模块均包含）：<章节名>（共 X 行）
       模块 01：<章节A> + <章节B>（功能 X 行，含共享共 Y 行）
       模块 02：...
     若有跨模块关联（如"状态机"与"详情页"应合并），请说明；说「确认」即接受此方案。
     ```
  4. 用户确认后进入 Phase 2；若用户提出调整意见，Agent 按意见手动修改 `modules/` 下文件并更新 `_manifest.json`
  - **⚠️ 恢复点约定（强制）**：用户说「确认」（或提出调整意见并 Agent 处理完毕）后，立即进入 **Step 3**，开始 Phase 2 模块循环，不得在此额外等待。

---

## Phase 2：AI 生成（模块循环模式 / 普通模式）

### 共用约定

**规则文件**（Agent 自行读取，不要求用户 @）：

| 步骤 | 规则路径（相对工作区根） |
|------|--------------------------|
| Step 3 | `.cursor/skills/testcasegen-prompts/rules/01prdreadrule.mdc` |
| Step 4 | `.cursor/skills/testcasegen-prompts/rules/02testdesign.mdc` |
| Step 5 | `.cursor/skills/testcasegen-prompts/rules/03testrequirement.mdc` |

**模式判断（Steps 3/4/5 共用）**：

每步开始前检查 `output/prd/<迭代>/modules/_manifest.json`：
- **不存在** → 普通模式（文档 ≤ SPLIT_HARD_MAX，一次全量处理）
- **存在** → 模块循环模式（按 manifest 顺序逐模块处理）

**上下文预算管理（模块循环模式专用，强制）**：

> 分档值 `BUDGET_TIER` 见 `testcasegen.md § 配置常量`。

模块循环模式下，多模块串行处理会累积上下文。Agent 必须遵循以下预算规则：

1. **模块计数器**：进入模块循环时初始化计数器 = 0；每处理完一个模块，计数器 +1
2. **分档预算策略**：先读取 manifest 的 `module_count`，按总模块数确定本步骤的连续处理上限（按 `BUDGET_TIER`）
3. **预算检查点**：每处理完一个模块后检查——若本步骤内已连续处理达到当前档位上限，且仍有剩余模块：
   - **主动暂停**，输出：
     ```
     ⏸️ 上下文预算检查：本步骤已连续处理 N/M 个模块（当前档位上限 = X），为保证后续模块质量，建议新开会话继续。
     请新开会话执行 /testcasegen <项目> <迭代> 即可自动从模块 N+1 恢复。
     ```
   - **停止等待**，不再继续处理剩余模块
4. **已完成模块不计入预算**：跳过的模块（产出已存在）不消耗计数器
5. **跨步骤不累加**：每个 Step 的计数器独立（Step 3 触顶后暂停，Step 4 重新从 0 开始）

> 经验值说明：模块数越多，单步骤连续处理上限要更保守。分档策略比固定阈值更稳，也便于向用户解释。

### Step 3 - 需求解析

**普通模式**：
1. Agent 读取规则 `01prdreadrule.mdc`
2. 读取 `output/prd/<迭代>/` 下的需求 md（迭代专属）+ `output/prd/` 根下共享 md（可选）
3. 按规则生成需求解析报告，保存到 `output/prd_analysis/<迭代>_需求解析报告.md`

**模块循环模式**：
1. 读取 `_manifest.json`，获取模块列表
2. 对每个模块，按序执行（已有产出的跳过）：
   - 检查 `output/modules/<迭代>/<模块序号>/prd_analysis.md` 是否已存在 → 存在则跳过（不计入预算计数器）
   - 创建 `output/modules/<迭代>/<模块序号>/` 目录
   - 读取 `output/prd/<迭代>/modules/<模块序号>_*.md`（含共享前置，全量处理）
   - 按规则 `01prdreadrule.mdc` 全量分析，保存到 `output/modules/<迭代>/<模块序号>/prd_analysis.md`
   - 预算计数器 +1，执行预算检查
3. **不合并**——逐模块产出直接供 Step 4 读取，节省上下文
4. **本批次完成后（无论是因预算触顶暂停，还是全部模块处理完毕），必须执行以下操作后再向用户发出提示**：
   - 读取本批次所有已处理模块的 `prd_analysis.md`，提取"需求不完备 / 测试风险点"章节
   - 按模块汇总，输出以下格式的风险摘要（风险点较多时可合并同类项，但每模块至少列出前3条最重要的风险）：
     ```
     📋 本批次需求解析完成，共发现以下需求不完备 / 测试风险点，请在进入下一步前确认是否需要补充材料或与产品/开发核对：

     【模块01 - <模块名称>】（共 N 条）
       ⚠️ <风险点1>
       ⚠️ <风险点2>
       ⚠️ ...（共 N 条，完整列表见 output/modules/<迭代>/01/prd_analysis.md）

     【模块02 - <模块名称>】（共 N 条）
       ⚠️ ...

     💡 如需补充说明或调整，请告知；说「继续」则直接进入下一步。
     ```

### Step 4 - 测试概要

**普通模式**：
1. Agent 读取规则 `02testdesign.mdc`
2. 读取 `output/prd_analysis/<迭代>_需求解析报告.md`（必选）+ `output/prd/<迭代>/` 需求 md（推荐）+ `input/knowledge/` 索引（可选）
3. 按规则生成测试概要（**必须包含完整的 `<!-- COVERAGE_LIST_START/END -->` 覆盖清单**），保存到 `output/test_outline/<迭代>_测试概要.md`

**模块循环模式**：
1. 对每个模块，按序执行（已有产出的跳过）：
   - 读取 `output/modules/<迭代>/<模块序号>/prd_analysis.md`（小文件，全量处理）
   - **跨模块上下文补充**：读取 `_manifest.json` 中当前模块的前后各 1 个相邻模块（若存在），从其 `prd_analysis.md` 中仅提取 MTS 的 `id` + `功能描述` + `核心流程`（每个模块约 3-5 行），作为关联上下文传入。不读取完整内容，仅用于识别跨模块依赖（如状态流转、接口调用关系）
   - 按规则 `02testdesign.mdc` 生成测试概要，保存到 `output/modules/<迭代>/<模块序号>/test_outline.md`
   - 预算计数器 +1，执行预算检查
2. **不合并**——逐模块产出直接供 Step 5 读取，节省上下文

### Step 5 - 测试用例

**普通模式**：
1. Agent 读取规则 `03testrequirement.mdc`
2. 读取 `output/test_outline/<迭代>_测试概要.md`（必选）+ `output/prd/<迭代>/` 需求 md（推荐）+ `input/knowledge/` 索引（可选）
3. 按规则生成测试用例，保存到 `output/test_cases/<迭代>_测试用例.md`

**模块循环模式**：
1. 对每个模块，按序执行（已有产出的跳过）：
   - 读取 `output/modules/<迭代>/<模块序号>/test_outline.md`（小文件，全量处理）
   - 同时读取 `output/prd/<迭代>/modules/<模块序号>_*.md` 中的对应需求 md（回溯细节）
   - 按规则 `03testrequirement.mdc` 生成测试用例，保存到 `output/modules/<迭代>/<模块序号>/test_cases.md`
   - 预算计数器 +1，执行预算检查
2. **不合并**——合并统一在 Step 6 前执行

---

## Phase 3：导出（自动）

### Step 6 - 合并 + 生成 XMind

**模块循环模式下**，在 XMind 导出前，先一次性合并所有模块产出：

1. 检查所有模块的 `test_cases.md` 是否均已生成：
   - **全部存在** → 执行合并
   - **有缺失** → 提示用户哪些模块尚未完成，暂停等待
2. 调用 skill `testcasegen-split-prd` 依次运行 `merge_modules.py`，合并三份文件：
   - `merge_modules.py`（step=prd_analysis）→ `output/prd_analysis/<迭代>_需求解析报告.md`
   - `merge_modules.py`（step=test_outline）→ `output/test_outline/<迭代>_测试概要.md`
   - `merge_modules.py`（step=test_cases）→ `output/test_cases/<迭代>_测试用例.md`
3. 调用 skill `testcasegen-md2xmind`，将合并后的 `output/test_cases/<迭代>_测试用例.md` 转为 XMind
4. 本步骤**全自动执行**，完成后汇报合并结果和 XMind 路径

**普通模式下**：无需合并，直接调用 `testcasegen-md2xmind` 导出。
