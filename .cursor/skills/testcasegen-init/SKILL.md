---
name: testcasegen-init
description: 初始化测试用例生成目录结构（input/output）。适合新工程开始做测试用例生成时使用。
---
# testcasegen-init

## 目标

在当前工作区（workspace）下初始化一个测试用例生成项目目录（默认目录名为 `testcasegen`，也可自定义项目名），并写入：

- `input/`：`prdword/`、`knowledge/`、`codedesignword/`、`baseline_cases/`
- `output/`：`prdmd/`、`codedesignmd/`、`requirement_analysis/`、`test_outline/`、`test_cases/`、`xmind/`

## Agent 执行流程（必须严格按照此流程执行）

当用户调用 `/testcasegen-init <项目名>` 时，Agent 必须按以下步骤操作：

### 步骤 1：生成临时配置文件

使用 **Write 工具** 在用户目录创建临时配置文件 `C:\Users\<用户名>\testcasegen_config.json`：

```json
{
  "workspace_root": "<当前工作区路径>",
  "project_name": "<用户指定的项目名>"
}
```

- `workspace_root`：从 user_info 的 `Workspace Path` 获取
- `project_name`：从用户输入获取，默认为 `testcasegen`

### 步骤 2：查找脚本路径

使用 **Glob 工具** 查找脚本：
- 搜索模式：`**/testcasegen-init/scripts/init_testgen.py`
- 搜索目录：当前工作区 或 `C:\Users\<用户名>\.cursor\projects`

### 步骤 3：执行脚本（根据路径是否含中文选择方式）

**判断脚本路径是否包含中文字符：**

**A. 脚本路径是纯英文** → 直接执行，无需复制：
```
python -X utf8 "<脚本路径>" --config C:\Users\<用户名>\testcasegen_config.json
```

**B. 脚本路径包含中文** → 需要复制到用户目录再执行：
1. 使用 **Read 工具** 读取脚本内容
2. 使用 **Write 工具** 写入 `C:\Users\<用户名>\init_testgen.py`
3. 执行：`python -X utf8 C:\Users\<用户名>\init_testgen.py --config C:\Users\<用户名>\testcasegen_config.json`

### 步骤 4：清理临时文件

使用 **Delete 工具** 删除：
- `C:\Users\<用户名>\testcasegen_config.json`
- `C:\Users\<用户名>\init_testgen.py`（仅当步骤 3 选择了方式 B 时）

### 步骤 5：验证结果

使用 **Write 工具** 创建验证脚本 `C:\Users\<用户名>\check_dir.py`：

```python
# -*- coding: utf-8 -*-
from pathlib import Path
p = Path(r"<workspace_root>/<project_name>")
if p.exists():
    print(f"创建成功: {p}")
    for d in sorted(p.iterdir()):
        print(f"  - {d.name}")
else:
    print(f"创建失败: {p}")
```

执行验证脚本，然后删除它。

## 示例

用户输入：`/testcasegen-init 我的测试项目`

Agent 执行：
1. 写入配置文件 `{"workspace_root": "d:\\代码\\项目", "project_name": "我的测试项目"}`
2. 复制 `init_testgen.py` 到用户目录
3. 执行 `python -X utf8 C:\Users\xxx\init_testgen.py --config C:\Users\xxx\testcasegen_config.json`
4. 删除临时的配置文件和脚本
5. 验证并报告结果

## 为什么使用配置文件 + 复制脚本

Windows 命令行（PowerShell/cmd）在传递中文参数和中文路径时存在编码问题，会导致路径乱码。解决方案：

1. **配置文件**：将中文路径/项目名写入 UTF-8 编码的 JSON 文件
2. **复制脚本**：将脚本复制到纯英文路径（用户目录）下执行

这样可以完美支持中文路径和项目名，避免任何编码问题。
