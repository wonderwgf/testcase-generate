---
name: testcasegen-docx2md
description: 将需求/设计 DOCX 转为 Markdown，并按约定输出到 output 目录（prdmd/codedesignmd）。适合在生成测试用例前做文档格式转换。
---
# testcasegen-docx2md

## 目标

将 DOCX 文档（需求/设计）转换为 Markdown 格式，输出到约定目录：
- 需求文档（prd）→ `output/prdmd/<docx名>.md`
- 设计文档（design）→ `output/codedesignmd/<docx名>.md`

## Agent 执行流程

当用户调用 `/testcasegen-docx2md` 时，Agent 按以下步骤操作：

### 步骤 1：查找脚本路径

使用 **Glob 工具** 查找脚本：
- 搜索模式：`**/testcasegen-docx2md/scripts/docx2md.py`
- 搜索目录：当前工作区 或 `C:\Users\<用户名>\.cursor\projects`

### 步骤 2：判断中文路径情况

检查以下路径是否包含中文字符（非 ASCII）：

| 检查项 | 示例 |
|--------|------|
| 脚本路径 | `C:\Users\test\.cursor\projects\中文目录\scripts\docx2md.py` |
| 工作区路径 | `D:\代码\项目` |
| 文件名/参数 | `需求规格说明书.docx` |

**根据检查结果选择方案：**

| 脚本路径 | 工作区/文件名 | 使用方案 |
|----------|---------------|----------|
| 英文 | 英文 | **方案 A**：直接执行 |
| 英文 | 中文 | **方案 B**：配置文件 |
| 中文 | 任意 | **方案 C**：复制脚本 + 配置文件 |

---

### 方案 A：直接执行（路径全英文）

直接执行脚本，参数通过命令行传递：

```powershell
python -X utf8 "<脚本路径>" --docx "<docx文件路径>" --doc-type prd|design
```

**示例：**
```powershell
python -X utf8 "C:\Users\test\.cursor\skills\testcasegen-docx2md\scripts\docx2md.py" --docx "D:\code\project\input\prdword\requirement.docx" --doc-type prd
```

---

### 方案 B：配置文件（仅文件名/参数含中文）

脚本路径是英文，但文件名或工作区路径含中文时，**只需要配置文件，不需要复制脚本**。

#### B-1：创建配置文件

使用 **Write 工具** 在用户目录创建 `C:\Users\<用户名>\.cursor\temp\docx2md_config.json`：

```json
{
  "docx": "D:\\code\\project\\input\\prdword\\需求规格说明书.docx",
  "doc_type": "prd",
  "out": "D:\\code\\project\\output\\prdmd\\需求规格说明书.md",
  "images": "D:\\code\\project\\output\\prdmd\\需求规格说明书_images"
}
```

#### B-2：执行脚本

```powershell
python -X utf8 "<脚本路径>" --config "C:\Users\<用户名>\.cursor\temp\docx2md_config.json"
```

#### B-3：清理临时文件

使用 **Delete 工具** 删除配置文件。

---

### 方案 C：复制脚本 + 配置文件（脚本路径含中文）

只有当**脚本路径本身包含中文**时，才需要复制脚本。

#### C-1：复制脚本

使用 **Shell** 或 **Read + Write 工具**：

```powershell
Copy-Item "<脚本路径>" "$env:USERPROFILE\.cursor\temp\docx2md.py" -Force
```

或：
1. 使用 **Read 工具** 读取脚本内容
2. 使用 **Write 工具** 写入 `C:\Users\<用户名>\.cursor\temp\docx2md.py`

#### C-2：创建配置文件

同方案 B-1。

#### C-3：执行脚本

```powershell
python -X utf8 "$env:USERPROFILE\.cursor\temp\docx2md.py" --config "$env:USERPROFILE\.cursor\temp\docx2md_config.json"
```

#### C-4：清理临时文件

使用 **Delete 工具** 删除：
- `C:\Users\<用户名>\.cursor\temp\docx2md_config.json`
- `C:\Users\<用户名>\.cursor\temp\docx2md.py`

---

## 输出位置

输出默认落到：
- `output/prdmd/<docx名>.md`（需求文档）
- `output/codedesignmd/<docx名>.md`（设计文档）
- `output/prdmd/<docx名>_images/`（图片目录）

---

## 示例

### 示例 1：路径全英文（方案 A）

```powershell
python -X utf8 ".cursor/skills/testcasegen-docx2md/scripts/docx2md.py" --docx "input/prdword/requirement.docx" --doc-type prd
```

### 示例 2：仅文件名含中文（方案 B）

工作区：`D:\code\project`（英文）
文件名：`需求规格说明书.docx`（中文）
脚本路径：`C:\Users\test\.cursor\skills\...\docx2md.py`（英文）

Agent 执行：
1. 创建配置文件（包含中文文件名）
2. 直接执行脚本（不复制）：`python -X utf8 "<脚本路径>" --config "<配置文件>"`
3. 删除配置文件

### 示例 3：工作区路径含中文（方案 B）

工作区：`D:\代码\项目`（中文）
脚本路径：英文

Agent 执行：
1. 创建配置文件
2. 直接执行脚本（不复制）
3. 删除配置文件

### 示例 4：脚本路径含中文（方案 C）

脚本路径：`C:\Users\test\.cursor\projects\中文项目\skills\...\docx2md.py`

Agent 执行：
1. 复制脚本到 `C:\Users\test\.cursor\temp\docx2md.py`
2. 创建配置文件
3. 执行临时脚本
4. 删除临时脚本和配置文件

---

## 备选：目录方式

如果只是文件名包含中文，也可以用目录索引方式（无需配置文件）：

```powershell
# 列出匹配文件
python -X utf8 "<脚本路径>" --docx-dir input/prdword --pattern "*.docx" --list

# 选择第 N 个文件
python -X utf8 "<脚本路径>" --docx-dir input/prdword --pattern "*.docx" --docx-index 1 --doc-type prd
```

---

## 判断逻辑总结

```
是否需要复制脚本？→ 仅当脚本路径含中文
是否需要配置文件？→ 当文件名、工作区路径、或输出路径任一含中文
```

优先使用最简单的方案，避免不必要的复杂操作。
