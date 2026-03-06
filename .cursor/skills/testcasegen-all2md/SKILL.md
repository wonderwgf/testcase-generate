---
name: testcasegen-all2md
description: 将单个文件或目录下所有 Word/Excel 转为 Markdown，输出到 output 下与 input 子目录同名的目录。Word 调用 docx2md、Excel 调用 excel2md 子 skill。适合批量转需求/设计/表格为 md。
---

# testcasegen-all2md

## 目标

将**单个文件**或**目录下所有支持的文件**转为 Markdown，并按约定输出：

- **输出目录**：`<工作区>/output/<子目录名>/`，与「输入所在子目录」同名；不存在则创建。
- **Word (.docx)**：调用子 skill **testcasegen-docx2md** 转换。
- **Excel (.xlsx, .xls)**：调用子 skill **testcasegen-excel2md** 转换。

支持的文件扩展名：`.docx`、`.doc`、`.xlsx`、`.xls`。

## 输入与输出路径规则

| 输入 | 子目录名 | 输出目录 |
|------|----------|----------|
| 单个文件 `.../input/prd/需求.docx` | `prd` | `output/prd/` |
| 目录 `.../input/prd/` | `prd` | `output/prd/` |

- **子目录名**：若输入为**文件**，取该文件**父目录名**；若输入为**目录**，取该**目录名**。
- **输出根**：默认为工作区下的 `output`（即 `<工作区>/output/<子目录名>/`）。若项目结构为 `test/input/` 与 `test/output/`，则输出目录为 `test/output/<子目录名>/`（与 input 同级的 output 下）。
- 执行前若 `output` 或 `output/<子目录名>` 不存在，**先创建目录**再转换。

## 执行流程

### 步骤 1：解析输入

- 若用户给出的是**文件路径**：得到该文件绝对路径，子目录名 = 该文件父目录名，待转换列表 = `[该文件]`（仅当扩展名为 .docx/.doc/.xlsx/.xls 时加入）。
- 若用户给出的是**目录路径**：子目录名 = 该目录名，待转换列表通过 **步骤 1.5（用配置文件列目录）** 得到，确保中文路径下也能可靠列出文件。

路径均解析为**绝对路径**（基于工作区根）。

### 步骤 1.5：用配置文件列目录（仅当输入为目录时执行）

当输入为**目录**时，因中文路径下 Glob / PowerShell 列目录可能失败，必须用「配置文件 + Python 脚本」列目录，结果写入**无中文的临时文件**再读取。

1. **查找脚本**：Glob 搜索 `**/testcasegen-all2md/scripts/list_dir_utf8.py`。
2. **脚本路径**：若脚本路径含非 ASCII（如工作区含中文），将脚本复制到临时目录 `<临时目录>/list_dir_utf8.py`，后续用该路径；否则用原路径。临时目录：Windows 为 `C:\Users\<用户名>\.cursor\temp\`，macOS/Linux 为 `~/.cursor/temp/`。
3. **创建配置文件**：在临时目录创建 `list_dir_config.json`（UTF-8）：
   ```json
   {
     "dir": "<输入目录的绝对路径>",
     "out": "<临时目录>/list_result.txt",
     "extensions": [".docx",".doc", ".xlsx", ".xls"]
   }
   ```
   `out` 必须为不含中文的路径（如 `C:\Users\...\.cursor\temp\list_result.txt`），以便 Agent 用 Read 工具读取。
4. **执行脚本**：  
   Windows: `python -X utf8 "<脚本路径>" --config "<临时目录>/list_dir_config.json"`  
   macOS/Linux: `python3 "<脚本路径>" --config "<临时目录>/list_dir_config.json"`
5. **读取结果**：用 Read 工具读取 `out` 指定文件，每行为一个文件名。待转换列表 = `[ 输入目录绝对路径 / 文件名 ]` 对每个非空行（跳过以 `ERROR:` 开头的行）。
6. **清理**：Delete 临时目录下的 `list_dir_config.json`、`list_result.txt`，以及步骤 2 若复制过的 `list_dir_utf8.py`。

### 步骤 2：确定输出目录

- 在工作区中定位「与 input 同级的 output」：若输入路径中包含 `input` 段（如 `test/input/prd`），则 output 基 = 该 `input` 的父级 + `output`（即 `test/output`）；否则 output 基 = 工作区根 + `output`。
- 输出目录 = `output基/output/<子目录名>/`，**不存在则创建**（使用 Run 命令或工具创建目录）。

### 步骤 3：按类型调用子 skill

对待转换列表中的**每个文件**：

1. **.docx**/**.doc**
   - 按 **testcasegen-docx2md** 的流程执行（查找脚本、临时目录、配置文件、执行、清理）。  
   - 配置中**必须**指定：`out` = `输出目录/<文件名不含扩展名>.md`，`images` = `输出目录/<文件名不含扩展名>_images`（与 docx2md 约定一致）。  
   - `doc_type` 默认 `prd`；若子目录名包含 `design` 或用户明确为设计文档，则用 `design`。

2. **.xlsx / .xls**  
   - 按 **testcasegen-excel2md** 的流程执行。  
   - 配置中**必须**指定：`out` = `输出目录/<文件名不含扩展名>.md`，`single_file` = `true`。

调用子 skill 时，**先读取**对应 SKILL（testcasegen-docx2md / testcasegen-excel2md）的 SKILL.md，再按其「执行流程」配置并执行；仅将输出路径改为本 skill 约定的 `output/<子目录名>/`。子 skill 的脚本路径通过 **Glob** 在工作区中搜索（docx2md：`**/testcasegen-docx2md/scripts/docx2md.py`，excel2md：`**/testcasegen-excel2md/scripts/excel_to_markdown.py`）。临时目录与 Python 命令按 **user_info OS**：Windows 用 `C:\Users\<用户名>\.cursor\temp\` 与 `python -X utf8`，macOS/Linux 用 `~/.cursor/temp/` 与 `python3`。

### 步骤 4：汇总

转换完成后，列出所有输出文件路径及所属 output 子目录，便于用户核对。

## 输出约定小结

- 输出目录名与 **input 下级目录名称一致**，放在 **output** 目录下。
- 单文件：`output/<子目录名>/<原名>.md`（docx 另有 `<原名>_images` 目录）。
- 目录批量：同上，每个支持的文件对应一个 md（及 docx 的 _images）。

## 快速示例

- 输入文件：`test/input/prd/需求.docx`  
  → 子目录名 = `prd`，输出 = `test/output/prd/需求.md` + `test/output/prd/需求_images/`，调用 **docx2md**。

- 输入目录：`test/input/prd/`（内含 `需求.docx`、`表.xlsx`）  
  → 子目录名 = `prd`，输出目录 = `test/output/prd/`；先创建该目录；`需求.docx` 用 **docx2md** 输出 `需求.md`，`表.xlsx` 用 **excel2md** 输出 `表.md`。

## 依赖

- 本 skill 依赖子 skill：**testcasegen-docx2md**、**testcasegen-excel2md**。执行前需能通过 Glob 找到对应脚本，并按各自 SKILL 的配置与执行步骤调用。
