---
name: testcasegen-prompts
description: 按项目 rules 生成"需求解析/测试概要/测试用例"的可复制提示词块（适合不走 MCP 调模型，只用 Cursor 当前模型生成）。 
disable-model-invocation: true
---
# testcasegen-prompts

## 前置

规则文件已随本 Skill 内置（推荐直接引用 Skill 内的规则）：

- `.cursor/skills/testcasegen-prompts/rules/01prdreadrule.mdc`
- `.cursor/skills/testcasegen-prompts/rules/02testdesign.mdc`
- `.cursor/skills/testcasegen-prompts/rules/03testrequirement.mdc`

## 输出目录约定

**重要**：所有输出文件必须保存在**项目根目录**下的 `output/` 目录中，与 `input/` 目录同级。

项目目录结构示例：
```
<项目名>/
├── input/                    # 输入文件目录
│   ├── prd/                  # 需求文档（按迭代子目录组织，如 prd/V4.5/）
│   │   ├── <迭代>/           # 迭代专属需求文档
│   │   └── *.xlsx            # 根下为跨迭代共享辅助文档
│   └── knowledge/            # 知识库（md 格式，跨迭代共享）
│       ├── baseline_cases/   # 基线测试用例
│       ├── business/         # 业务规则 / 流程文档
│       ├── codedesign/       # 技术设计文档
│       └── prd/              # 历史需求文档
│
└── output/                   # 输出文件目录（与 input 同级）
    ├── prd/                  # 需求文档转换后的 Markdown（按迭代子目录）
    ├── prd_analysis/         # 需求解析报告（<迭代>_需求解析报告.md）
    ├── test_outline/         # 测试概要（<迭代>_测试概要.md）
    ├── test_cases/           # 测试用例（<迭代>_测试用例.md）
    └── xmind/                # XMind 脑图文件
```

**确定项目根目录**：包含 `input/` 目录的那一级目录即为项目根目录。

**迭代标识**：`<前缀>` 即迭代标识（如 V4.5），用于区分同一项目内不同版本的产出。

## 生成提示词（推荐流程）

### Step1 需求解析

在聊天中输入（替换文件路径）：

- `@<需求md文件>`（位于 `<项目>/output/prd/<迭代>/` 下）
- `@.cursor/skills/testcasegen-prompts/rules/01prdreadrule.mdc`（或 `@rules/01prdreadrule.mdc`）

并让模型输出最终 Markdown，保存为：

`<项目>/output/prd_analysis/<迭代>_需求解析报告.md`

### Step2 测试概要

- `@<项目>/output/prd_analysis/<迭代>_需求解析报告.md`（必选）
- `@<项目>/output/prd/<迭代>/<需求md>.md`（**可选**，当需求解析报告对某功能列表页/详情页不够细时，直接引用 PRD 原文可补充查询筛选项、列表字段、按钮规则等）
- `@<项目>/input/knowledge/knowledge_index.md`（**可选**，使用前须先用 `testcasegen-knowledge-index` skill 生成索引；约 200 行，Agent 按索引行范围精准 Read 所需章节，可读取 codedesign/business/baseline_cases 等知识库内容）
- `@.cursor/skills/testcasegen-prompts/rules/02testdesign.mdc`（或 `@rules/02testdesign.mdc`）

保存为：

`<项目>/output/test_outline/<迭代>_测试概要.md`

### Step3 测试用例

- `@<项目>/output/test_outline/<迭代>_测试概要.md`（必选）
- `@<项目>/output/prd/<迭代>/<需求md>.md`（**推荐**，用于回溯补充提示文案、校验规则、枚举值等细节）
- `@<项目>/output/prd/<通用业务规则清单>.md`（**可选**，用于生成通用业务规则验证用例，详见规则11.5）
- `@<项目>/input/knowledge/knowledge_index.md`（**可选**，需先生成索引；Agent 按索引精准读取基线用例对应章节）
- `@.cursor/skills/testcasegen-prompts/rules/03testrequirement.mdc`（或 `@rules/03testrequirement.mdc`）

保存为：

`<项目>/output/test_cases/<迭代>_测试用例.md`
