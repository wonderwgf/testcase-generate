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

`python .cursor/skills/testcasegen-init/scripts/init_testgen.py --project-name testmyproject`

如需显式指定工作区根目录（当 Cursor 把 cwd 设置到用户目录时很有用）：

`python .cursor/skills/testcasegen-init/scripts/init_testgen.py --workspace-root D:\\code\\testgenmcp --project-name testmyproject`

## 常见问题：找不到脚本

如果是通过 **add from gitUrl** 加载 skill，脚本会落在用户目录下的 `.cursor\\projects\\<项目路径(用-连接)>\\skills\\...`。
例如你的项目路径是 `d:\\code\\testtesttest`，对应目录一般是：
`%USERPROFILE%\\.cursor\\projects\\d-code-testtesttest\\skills\\testcase-generate`

可以用“搜索变量版”（更直观，不用手改 `d-code-xxx`）：

PowerShell：

`$ws='D:\code\testgenmcp'; $slug=($ws -replace ':','' -replace '\\','-'); $p=Join-Path $env:USERPROFILE ".cursor\projects\$slug\skills\testcase-generate\.cursor\skills\testcasegen-init\scripts\init_testgen.py"; python "$p" --workspace-root $ws --project-name testmyproject`

也可直接用下面的“一键启动”命令自动定位脚本路径并执行：

`python -X utf8 -c "from pathlib import Path; import os, runpy, sys; root = Path(os.environ.get('USERPROFILE',''))/'.cursor'/'projects'; matches = sorted(root.rglob('testcasegen-init/scripts/init_testgen.py')); assert matches, '找不到 init_testgen.py'; script = matches[0]; sys.argv = ['init_testgen.py','--workspace-root', r'D:\\code\\testgenmcp','--project-name','testmyproject']; runpy.run_path(str(script), run_name='__main__')"`

说明：
- 把 `D:\\code\\testgenmcp` 改成你自己的工作区路径
- 把 `testmyproject` 改成你的项目目录名

