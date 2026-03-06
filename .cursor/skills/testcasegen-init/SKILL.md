---
name: testcasegen-init
description: 初始化测试用例生成目录结构（input/output）。适合新工程开始做测试用例生成时使用。
---
# testcasegen-init

## 目标

在当前工作区下初始化一个测试用例生成项目目录（默认目录名 `testcasegen`，可自定义），写入：

- `input/`：`prd/`、`knowledge/`、`codedesign/`、`baseline_cases/`
- `output/`：`prd/`、`codedesign/`、`prd_analysis/`、`test_outline/`、`test_cases/`、`xmind/`

## 执行流程

统一使用**配置文件方案**执行，兼容中文路径和全平台。

### 步骤 1：查找脚本

使用 **Glob 工具** 搜索 `**/testcasegen-init/scripts/init_testgen.py`，优先在当前工作区搜索。

### 步骤 2：确定临时目录

根据用户 OS（从 user_info 获取）：

| OS | 临时目录 | Python 命令 |
|----|----------|-------------|
| Windows | `C:\Users\<用户名>\.cursor\temp\` | `python -X utf8` |
| macOS/Linux | `~/.cursor/temp/` | `python3` |

### 步骤 3：处理脚本路径

检查**脚本路径**是否包含非 ASCII 字符（中文等）：
- **否** → 直接使用原始脚本路径，跳到步骤 4
- **是** → 用 Read + Write 工具将脚本内容复制到 `<临时目录>/init_testgen.py`，后续使用该临时路径

### 步骤 4：创建配置文件

使用 **Write 工具** 创建 `<临时目录>/testcasegen_config.json`：

```json
{
  "workspace_root": "<当前工作区绝对路径>",
  "project_name": "<项目名，默认 testcasegen>"
}
```

### 步骤 5：执行脚本

```bash
# Windows (PowerShell)
python -X utf8 "<脚本路径>" --config "<临时目录>\testcasegen_config.json"

# macOS / Linux
python3 "<脚本路径>" --config "<临时目录>/testcasegen_config.json"
```

### 步骤 6：清理

使用 **Delete 工具** 删除临时文件：
- `<临时目录>/testcasegen_config.json`
- `<临时目录>/init_testgen.py`（仅步骤 3 复制过时需要删除）

## 快速示例

### 示例 1：Windows 用户

用户输入：`/testcasegen-init mytest`，工作区 `D:\code\project`

1. Write `C:\Users\test\.cursor\temp\testcasegen_config.json`：
   ```json
   { "workspace_root": "D:\\code\\project", "project_name": "mytest" }
   ```
2. 执行：`python -X utf8 "<脚本路径>" --config "C:\Users\test\.cursor\temp\testcasegen_config.json"`
3. Delete 配置文件

### 示例 2：macOS/Linux 用户

用户输入：`/testcasegen-init mytest`，工作区 `/home/dev/project`

1. Write `~/.cursor/temp/testcasegen_config.json`：
   ```json
   { "workspace_root": "/home/dev/project", "project_name": "mytest" }
   ```
2. 执行：`python3 "<脚本路径>" --config "~/.cursor/temp/testcasegen_config.json"`
3. Delete 配置文件
