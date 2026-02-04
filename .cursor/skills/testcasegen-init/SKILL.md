---
name: testcasegen-init
description: 初始化测试用例生成目录结构（input/output）。适合新工程开始做测试用例生成时使用。
---
# testcasegen-init

## 目标

在当前工作区（workspace）下初始化一个测试用例生成项目目录（默认目录名为 `testcasegen`，也可自定义项目名），并写入：

- `input/`：`prdword/`、`knowledge/`、`codedesignword/`、`baseline_cases/`
- `output/`：`prdmd/`、`codedesignmd/`、`requirement_analysis/`、`test_outline/`、`test_cases/`、`xmind/`

## Agent 执行流程

当用户调用 `/testcasegen-init [项目名]` 时，Agent 按以下步骤操作：

### 步骤 1：查找脚本路径

使用 **Glob 工具** 查找脚本：
- 搜索模式：`**/testcasegen-init/scripts/init_testgen.py`
- 搜索目录：当前工作区 或 `C:\Users\<用户名>\.cursor\projects`

### 步骤 2：判断是否包含中文路径

检查以下路径是否包含中文字符（非 ASCII）：
1. 工作区路径（`workspace_root`）
2. 脚本路径（步骤 1 找到的路径）
3. 项目名（用户指定的，默认 `testcasegen`）

**如果全部为纯英文** → 使用 **方案 A（简单方案）**
**如果任意一项包含中文** → 使用 **方案 B（配置文件方案）**

---

### 方案 A：直接执行（推荐，路径全英文时使用）

直接执行脚本，参数通过命令行传递：

```powershell
python -X utf8 "<脚本路径>" "<工作区路径>" "<项目名>"
```

**示例：**
```powershell
python -X utf8 "C:\Users\test\.cursor\skills\testcasegen-init\scripts\init_testgen.py" "D:\code\myproject" "testcasegen"
```

执行完成后，验证目录结构并报告结果。

---

### 方案 B：配置文件方案（路径包含中文时使用）

Windows 命令行传递中文参数会乱码，需要通过配置文件传参。

#### B-1：生成临时配置文件

使用 **Write 工具** 在用户目录创建 `C:\Users\<用户名>\.cursor\temp\testcasegen_config.json`：

```json
{
  "workspace_root": "<当前工作区路径>",
  "project_name": "<用户指定的项目名>"
}
```

#### B-2：执行脚本（根据脚本路径是否含中文）

**B-2a. 脚本路径是纯英文** → 直接执行：
```powershell
python -X utf8 "<脚本路径>" --config "C:\Users\<用户名>\.cursor\temp\testcasegen_config.json"
```

**B-2b. 脚本路径包含中文** → 需要先复制脚本：
1. 使用 **Read 工具** 读取脚本内容
2. 使用 **Write 工具** 写入 `C:\Users\<用户名>\.cursor\temp\init_testgen.py`
3. 执行：
```powershell
python -X utf8 "C:\Users\<用户名>\.cursor\temp\init_testgen.py" --config "C:\Users\<用户名>\.cursor\temp\testcasegen_config.json"
```

#### B-3：清理临时文件

使用 **Delete 工具** 删除临时文件：
- `C:\Users\<用户名>\.cursor\temp\testcasegen_config.json`
- `C:\Users\<用户名>\.cursor\temp\init_testgen.py`（仅当 B-2b 时）

---

## 示例

### 示例 1：路径全英文（方案 A）

用户输入：`/testcasegen-init mytest`
工作区：`D:\code\project`

Agent 执行：
```powershell
python -X utf8 "C:\Users\test\.cursor\skills\testcasegen-init\scripts\init_testgen.py" "D:\code\project" "mytest"
```

### 示例 2：项目名包含中文（方案 B）

用户输入：`/testcasegen-init 我的测试项目`
工作区：`D:\code\project`

Agent 执行：
1. 写入配置文件 `{"workspace_root": "D:\\code\\project", "project_name": "我的测试项目"}`
2. 执行 `python -X utf8 "<脚本路径>" --config "C:\Users\xxx\.cursor\temp\testcasegen_config.json"`
3. 删除临时配置文件
4. 验证并报告结果

### 示例 3：工作区路径包含中文（方案 B）

用户输入：`/testcasegen-init testcasegen`
工作区：`D:\代码\项目`

Agent 执行：
1. 写入配置文件 `{"workspace_root": "D:\\代码\\项目", "project_name": "testcasegen"}`
2. 执行脚本（如果脚本路径也含中文，先复制脚本）
3. 删除临时文件
4. 验证并报告结果

---

## 为什么区分两种方案

Windows 命令行（PowerShell/cmd）在传递中文参数时存在编码问题。解决方案：

1. **方案 A（简单）**：路径全英文时，直接传参执行，简单高效
2. **方案 B（兼容）**：路径含中文时，通过 UTF-8 编码的 JSON 配置文件传参，避免乱码

优先使用方案 A，仅在必要时才使用方案 B，减少不必要的复杂性。
