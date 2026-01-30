---
name: testcasegen-init
description: 初始化测试用例生成目录结构（input/output）。适合新工程开始做测试用例生成时使用。
disable-model-invocation: true
---
# testcasegen-init

## 目标

在当前工作区（workspace）下初始化一个测试用例生成项目目录（默认目录名为 `testcasegen`，也可自定义项目名），并写入：

- `input/`：`prdword/`、`knowledge/`、`codedesignword/`、`baseline_cases/`
- `output/`：`prdmd/`、`codedesignmd/`、`requirement_analysis/`、`test_outline/`、`test_cases/`、`xmind/`

说明：规则与转换脚本已经以 Skills 形式提供（`.cursor/skills/`），不再需要落到项目目录。

## 使用方式

在 Agent 聊天里运行：

`python .cursor/skills/testcasegen-init/scripts/init_testgen.py --project-name <name>`

示例：

`python .cursor/skills/testcasegen-init/scripts/init_testgen.py --project-name wklt`

如需显式指定工作区根目录（当 Cursor 把 cwd 设置到用户目录时很有用）：

`python .cursor/skills/testcasegen-init/scripts/init_testgen.py --workspace-root D:\\code\\testgenmcp --project-name wklt`

