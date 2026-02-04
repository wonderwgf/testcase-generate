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
│   ├── prdword/              # 需求文档（.docx）
│   ├── codedesignword/       # 设计文档（.docx）
│   ├── knowledge/            # 领域知识文档
│   └── baseline_cases/       # 基线测试用例
│
└── output/                   # 输出文件目录（与 input 同级）
    ├── prdmd/                # 需求文档转换后的 Markdown
    ├── codedesignmd/         # 设计文档转换后的 Markdown
    ├── requirement_analysis/ # 需求解析报告
    ├── test_outline/         # 测试概要
    ├── test_cases/           # 测试用例
    └── xmind/                # XMind 脑图文件
```

**确定项目根目录**：包含 `input/` 目录的那一级目录即为项目根目录。

## 生成提示词（推荐流程）

### Step1 需求解析

在聊天中输入（替换文件路径）：

- `@<需求md文件>`（位于 `<项目>/output/prdmd/` 下）
- `@.cursor/skills/testcasegen-prompts/rules/01prdreadrule.mdc`（或 `@rules/01prdreadrule.mdc`）

并让模型输出最终 Markdown，保存为：

`<项目>/output/requirement_analysis/<前缀>_需求解析报告.md`

### Step2 测试概要

- `@<项目>/output/requirement_analysis/<前缀>_需求解析报告.md`
- `@<项目>/output/codedesignmd/<设计md>.md`（可选）
- `@<项目>/input/knowledge/<知识库文件>`（可选）
- `@.cursor/skills/testcasegen-prompts/rules/02testdesign.mdc`（或 `@rules/02testdesign.mdc`）

保存为：

`<项目>/output/test_outline/<前缀>_测试概要.md`

### Step3 测试用例

- `@<项目>/output/test_outline/<前缀>_测试概要.md`
- `@.cursor/skills/testcasegen-prompts/rules/03testrequirement.mdc`（或 `@rules/03testrequirement.mdc`）

保存为：

`<项目>/output/test_cases/<前缀>_测试用例.md`
