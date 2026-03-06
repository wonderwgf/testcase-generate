---
name: testcasegen-docx2md
description: 将需求/设计 DOCX 转为 Markdown，并按约定输出到 output 目录（prd/codedesign）。适合在生成测试用例前做文档格式转换。
---
# testcasegen-docx2md

## 目标

将 DOCX 文档（需求/设计）转换为 Markdown 格式，输出到约定目录：
- 需求文档（prd）→ `output/prd/<docx名>.md`
- 设计文档（design）→ `output/codedesign/<docx名>.md`

## 执行流程

统一使用**配置文件方案**执行，兼容中文路径和全平台。

### 步骤 1：查找脚本

使用 **Glob 工具** 搜索 `**/testcasegen-docx2md/scripts/docx2md.py`，优先在当前工作区搜索。

### 步骤 2：确定临时目录

根据用户 OS（从 user_info 获取）确定临时目录和 Python 命令：

| OS | 临时目录 | Python 命令 |
|----|----------|-------------|
| Windows | `C:\Users\<用户名>\.cursor\temp\` | `python -X utf8` |
| macOS/Linux | `~/.cursor/temp/` | `python3` |

### 步骤 3：处理脚本路径

检查**脚本路径**是否包含非 ASCII 字符（中文等）：
- **否** → 直接使用原始脚本路径，跳到步骤 4
- **是** → 用 Read + Write 工具将脚本内容复制到 `<临时目录>/docx2md.py`，后续使用该临时路径

### 步骤 4：创建配置文件

使用 **Write 工具** 创建 `<临时目录>/docx2md_config.json`：

```json
{
  "docx": "<docx文件绝对路径>",
  "doc_type": "prd 或 design"
}
```

> `out` 和 `images` 字段可选，不填则自动按约定目录输出。

### 步骤 5：执行脚本

```bash
# Windows (PowerShell)
python -X utf8 "<脚本路径>" --config "<临时目录>\docx2md_config.json"

# macOS / Linux
python3 "<脚本路径>" --config "<临时目录>/docx2md_config.json"
```

### 步骤 6：清理

使用 **Delete 工具** 删除临时文件：
- `<临时目录>/docx2md_config.json`
- `<临时目录>/docx2md.py`（仅步骤 3 复制过时需要删除）

## 输出位置

- `output/prd/<docx名>.md` + `output/prd/<docx名>_images/`（需求文档）
- `output/codedesign/<docx名>.md` + `output/codedesign/<docx名>_images/`（设计文档）

## 快速示例

用户工作区 `D:\code\project`，DOCX 为 `test/input/prd/需求文档.docx`：

1. Write `C:\Users\test\.cursor\temp\docx2md_config.json`：
   ```json
   { "docx": "D:\\code\\project\\test\\input\\prdword\\需求文档.docx", "doc_type": "prd" }
   ```
2. 执行：`python -X utf8 "<脚本路径>" --config "C:\Users\test\.cursor\temp\docx2md_config.json"`
3. Delete 配置文件
