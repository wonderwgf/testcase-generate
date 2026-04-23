---
name: testcasegen-split-prd
description: 将超过阈值的大型需求 Markdown 文档拆分为多个模块子文档；并在各步骤产出完成后合并为最终文件。解决大文档分批确认的状态管理问题。
---

# testcasegen-split-prd

## 目标

提供两个工具脚本：

1. **split_prd.py**：将 `output/prd/<迭代>/` 下超过 800 行的 md 文件拆分为多个模块子文档，写入 `output/prd/<迭代>/modules/`
2. **merge_modules.py**：将 `output/modules/<迭代>/` 下各模块在某步骤的产出合并为标准输出文件

## 目录结构

```
<项目>/output/
├── prd/<迭代>/
│   ├── 需求规格说明书.md          ← 原始转换产出（不修改）
│   └── modules/                   ← split_prd.py 生成
│       ├── _manifest.json         ← 拆分清单与进度状态
│       ├── _shared_prefix.md      ← 共享前置内容（术语/概述等）
│       ├── 01_<模块名>.md         ← 模块子文档（含共享前置）
│       └── 02_<模块名>.md
│
├── modules/<迭代>/                 ← 各模块中间产出（Agent 按步骤写入）
│   ├── 01/
│   │   ├── prd_analysis.md       ← Step 3 产出
│   │   ├── test_outline.md       ← Step 4 产出
│   │   └── test_cases.md         ← Step 5 产出
│   └── 02/
│       └── ...
│
├── prd_analysis/<迭代>_需求解析报告.md   ← merge_modules.py 合并产出
├── test_outline/<迭代>_测试概要.md
├── test_cases/<迭代>_测试用例.md         ← 用于 XMind 导出
└── xmind/<迭代>_测试用例.xmind
```

---

## split_prd.py 执行流程

### 步骤 1：查找脚本

Glob 搜索 `**/testcasegen-split-prd/scripts/split_prd.py`

### 步骤 2：确定临时目录

| OS | 临时目录 | Python 命令 |
|----|----------|-------------|
| Windows | `C:\Users\<用户名>\.cursor\temp\` | `python -X utf8` |
| macOS/Linux | `~/.cursor/temp/` | `python3` |

### 步骤 3：处理脚本路径

检查脚本路径是否含非 ASCII（中文等）：
- 否 → 直接用原路径
- 是 → Read + Write 工具复制到临时目录，后续用临时路径

### 步骤 4：创建配置文件

Write 工具创建 `<临时目录>/split_prd_config.json`：

```json
{
  "md_file": "<output/prd/<迭代>/需求文档.md 的绝对路径>",
  "output_dir": "<output/prd/<迭代>/modules/ 的绝对路径>",
  "target_lines": 600,
  "hard_max": 800,
  "min_lines": 80,
  "shared_keywords": []
}
```

> - `hard_max` 可选（默认 800），超过此行数的 H2 章节会按 H3 二次拆分
> - `min_lines` 可选（默认 80），行数低于此值的模块会被合并到相邻模块
> - `shared_keywords` 可选，追加额外的共享章节关键词（默认已内置术语/概述/参考文档/文档控制/目录等）

### 步骤 5：执行脚本

```bash
# Windows
python -X utf8 "<脚本路径>" --config "<临时目录>\split_prd_config.json"

# macOS/Linux
python3 "<脚本路径>" --config "<临时目录>/split_prd_config.json"
```

脚本 stdout 输出拆分方案，包含：
- 识别到的共享前置章节及行数
- 各模块包含的章节及行数、文件名

**若 `modules/_manifest.json` 已存在，脚本直接输出清单摘要并退出（幂等，不重复拆分）。**

### 步骤 6：格式化展示并等用户确认

Agent 读取脚本 stdout，向用户输出：

```
📋 文档共 2400 行，已拆分为 3 个模块：

  共享前置（每模块均包含）：术语定义、系统概述（共 120 行）

  模块 01：OAuth认证 + 接口鉴权（功能 580 行，含共享共 700 行）→ 01_OAuth认证_接口鉴权.md
  模块 02：工单列表页 + 工单详情页（功能 600 行，含共享共 720 行）→ 02_工单列表页_工单详情页.md
  模块 03：报表查询 + 审批流程（功能 580 行，含共享共 700 行）→ 03_报表查询_审批流程.md

若有跨模块逻辑关联（如"状态机"与"详情页"应合并），请说明调整意见；
说「确认」即按此方案继续。
```

用户确认后进入下一步；若要调整，按用户意见手动修改 `modules/` 下的文件或重命名后更新 `_manifest.json`。

### 步骤 7：清理临时文件

Delete `split_prd_config.json` 和复制的脚本（若步骤 3 有复制）。

---

## merge_modules.py 执行流程

### 步骤 1-3：同 split_prd.py 步骤 1-3（查脚本、确定临时目录、处理路径）

### 步骤 4：创建配置文件

Write 工具创建 `<临时目录>/merge_modules_config.json`：

```json
{
  "manifest_file": "<output/prd/<迭代>/modules/_manifest.json 的绝对路径>",
  "modules_base_dir": "<output/modules/<迭代>/ 的绝对路径>",
  "step": "prd_analysis",
  "output_file": "<output/prd_analysis/<迭代>_需求解析报告.md 的绝对路径>"
}
```

`step` 取值：`prd_analysis` / `test_outline` / `test_cases`

### 步骤 5：执行脚本

```bash
# Windows
python -X utf8 "<脚本路径>" --config "<临时目录>\merge_modules_config.json"

# macOS/Linux
python3 "<脚本路径>" --config "<临时目录>/merge_modules_config.json"
```

脚本检查所有模块的产出文件是否存在：
- 存在 → 合并写入 output_file，输出「合并完成: N 个模块 → <路径>」
- 有缺失 → 报错列出缺失项，不合并

### 步骤 6：清理临时文件

Delete 配置文件和复制的脚本（若有）。

---

## 共享前置章节识别规则

以下关键词命中章节标题则认定为"共享前置"，提取后追加到**每个模块子文档的开头**：

`术语`、`定义`、`缩略`、`概述`、`总体`、`参考文档`、`引用`、`背景`、`目的`、`范围`、`适用`、`前言`、`说明`、`修订`、`版本`、`历史`、`附录`、`规范`、`简介`、`文档控制`、`目录`、`变更记录`、`审批`、`读者对象`、`编写目的`、`项目背景`、`系统简介`、`文档约定`

> 这些章节通常被多个功能章节依赖（如术语定义、系统背景），复制到每个子文档确保 AI 分析时有完整上下文，不因拆分丢失语义。

---

## 注意事项

- `split_prd.py` 是幂等的：若 `_manifest.json` 已存在，直接返回清单摘要，不重复拆分
- 超过 `hard_max`（默认 800 行）的 H2 章节会自动按 H3 子标题二次拆分，避免产出超阈值模块
- 行数低于 `min_lines`（默认 80 行）的模块会自动合并到相邻模块，避免极小模块浪费处理轮次
- `_manifest.json` 记录源文件 MD5 hash（`source_hash` 字段），用于检测源文件变更
- `_manifest.json` 不含 `step_done` 状态字段，进度判断完全由编排层基于文件系统完成
- `merge_modules.py` 要求所有模块的指定步骤产出均已存在，否则报错
- 合并文件中用 `<!-- ===== 模块 N: 章节名 ===== -->` 注释分隔，不影响 XMind 导出
- 若用户需要调整模块划分（如合并两个模块），删除 `_manifest.json` 和 `modules/` 下所有文件后重新运行拆分，或手动修改文件和 manifest
