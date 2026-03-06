---
name: testcasegen-excel2md
description: 将 Excel 文件转为 Markdown（每 sheet 为表格），输出到约定目录 output/prd。适合在生成测试用例前做表格类文档转换。
---
# testcasegen-excel2md

## 目标

将 Excel 文件（各 sheet）转换为 Markdown 表格，输出到约定目录：
- 默认单文件：`output/prd/<excel名>.md`（含目录与全部 sheet）
- 可选多文件：`output/prd/<sheet名>.md`（需传 `single_file: false`）

## 执行流程

统一使用**配置文件方案**执行，兼容中文路径和全平台。

### 步骤 1：查找脚本

使用 **Glob 工具** 搜索 `**/testcasegen-excel2md/scripts/excel_to_markdown.py`，优先在当前工作区搜索。

### 步骤 2：确定临时目录

根据用户 OS（从 user_info 获取）：

| OS | 临时目录 | Python 命令 |
|----|----------|-------------|
| Windows | `C:\Users\<用户名>\.cursor\temp\` | `python -X utf8` |
| macOS/Linux | `~/.cursor/temp/` | `python3` |

### 步骤 3：处理脚本路径

若**脚本路径**包含非 ASCII 字符（中文等），用 Read + Write 将脚本复制到 `<临时目录>/excel_to_markdown.py`，后续使用该路径；否则直接使用原脚本路径。

### 步骤 4：创建配置文件

使用 **Write 工具** 创建 `<临时目录>/excel2md_config.json`：

```json
{
  "excel": "<Excel 文件绝对路径>",
  "out": "<输出文件或目录绝对路径，可选>",
  "single_file": true
}
```

> 不填 `out` 时，脚本会输出到 Excel 同目录下的 `<excel名>.md`；建议填为工作区下 `output/excelmd/<excel名>.md`。

### 步骤 5：执行脚本

```bash
# Windows (PowerShell)
python -X utf8 "<脚本路径>" --config "<临时目录>\excel2md_config.json"

# macOS / Linux
python3 "<脚本路径>" --config "<临时目录>/excel2md_config.json"
```

### 步骤 6：清理

使用 **Delete 工具** 删除临时文件：`excel2md_config.json`，以及步骤 3 若复制过的 `excel_to_markdown.py`。

## 输出约定

- 单文件模式：`output/prd/<excel名>.md`（含目录 + 各 sheet 的 Markdown 表格）
- 多文件模式：`output/prd/<sheet名>.md`（每个 sheet 一个文件，需在配置中设 `"single_file": false`）

## 快速示例

工作区 `D:\code\project`，Excel 为 `test/input/prd/数据表.xlsx`，输出到 `test/output/prd/数据表.md`：

1. Write `C:\Users\test\.cursor\temp\excel2md_config.json`：
   ```json
   { "excel": "D:\\code\\project\\test\\input\\prd\\数据表.xlsx", "out": "D:\\code\\project\\test\\output\\prd\\数据表.md", "single_file": true }
   ```
2. 执行：`python -X utf8 "<脚本路径>" --config "C:\Users\test\.cursor\temp\excel2md_config.json"`
3. Delete 配置文件
