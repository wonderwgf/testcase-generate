---
name: testcasegen-docx2md
description: 将需求/设计 DOCX 转为 Markdown，并按约定输出到 output 目录（prdmd/codedesignmd）。适合在生成测试用例前做文档格式转换。支持自动检测中文路径并使用配置文件方案。
disable-model-invocation: true
---
# testcasegen-docx2md

## 用法

### 标准用法（路径不含中文）

`python -X utf8  .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx <path> --doc-type prd|design`

### 中文路径完整解决方案（推荐）

当**工作区路径**或**脚本路径**包含中文时，PowerShell 传递路径给 Python 会出现编码问题。需要按以下步骤操作：

**步骤 1：复制脚本到不含中文的路径**

将脚本复制到用户目录下（路径不含中文）：

```powershell
Copy-Item ".cursor\skills\testcasegen-docx2md\scripts\docx2md.py" "$env:USERPROFILE\.cursor\temp\docx2md.py" -Force
```

或者使用 Cursor 的 Write 工具将脚本内容写入到 `C:\Users\<用户名>\.cursor\temp\docx2md.py`。

**步骤 2：创建配置文件（UTF-8 编码）**

在 `C:\Users\<用户名>\.cursor\temp\docx2md_config.json` 写入：

```json
{
  "docx": "D:\\code\\中文项目\\input\\prdword\\需求规格说明书.docx",
  "doc_type": "prd",
  "out": "D:\\code\\中文项目\\output\\prdmd\\需求规格说明书.md",
  "images": "D:\\code\\中文项目\\output\\prdmd\\需求规格说明书_images"
}
```

**步骤 3：使用配置文件执行**

```powershell
python -X utf8 "$env:USERPROFILE\.cursor\temp\docx2md.py" --config "$env:USERPROFILE\.cursor\temp\docx2md_config.json"
```

### 自动配置（仅适用于脚本路径不含中文）

如果只有参数路径包含中文，脚本会**自动检测**并使用配置文件方案：

- 配置文件自动保存到：`%USERPROFILE%\.cursor\temp\docx2md_auto_config.json`
- 禁用自动配置：添加 `--no-auto-config` 参数

## 输出位置

输出默认落到：
- `output/prdmd/<docx名>.md`（需求文档）
- `output/codedesignmd/<docx名>.md`（设计文档）

## 目录方式（备选）

如果只是文件名包含中文，可用目录方式：

- 列出匹配列表：

```powershell
python -X utf8 .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx-dir input/prdword --pattern "*.docx" --list
```

- 选择第 N 个：

```powershell
python -X utf8 .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx-dir input/prdword --pattern "*.docx" --docx-index 1 --doc-type prd
```

## 完整示例

### 示例 1：标准转换（路径无中文）

```powershell
python -X utf8 .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx input/prdword/requirement.docx --doc-type prd
```

### 示例 2：中文路径完整流程

```powershell
# 1. 复制脚本
Copy-Item ".cursor\skills\testcasegen-docx2md\scripts\docx2md.py" "$env:USERPROFILE\.cursor\temp\docx2md.py" -Force

# 2. 创建配置文件（使用 Cursor Write 工具写入 JSON）

# 3. 执行转换
python -X utf8 "$env:USERPROFILE\.cursor\temp\docx2md.py" --config "$env:USERPROFILE\.cursor\temp\docx2md_config.json"
```
