---
name: testcasegen-knowledge-index
description: 扫描项目 knowledge/ 目录，为基线用例/业务规则/技术设计/历史需求四类知识库文件生成结构化索引（knowledge_index.md），供 Step2/Step3 替代原始大文件引用，Agent 按章节行范围精准读取，避免超阈值。
---

# testcasegen-knowledge-index

## 目标

扫描 `<项目>/input/knowledge/` 目录下所有 `.md` 文件，按知识库类型自动分类：

| 目录名（包含匹配） | 知识库类型 |
|----------------|----------|
| `baseline_cases` | 基线用例 |
| `business` | 业务规则/流程文档 |
| `codedesign` | 技术设计文档 |
| `prd` | 历史需求文档 |

生成 `knowledge/knowledge_index.md`，包含：
- **文件目录**：类型、路径、行数、章节数
- **章节索引**：每个文件的 H1/H2 标题 + 行范围（供精准 Read）
- **模块映射表**：测试模块 → 推荐知识库文件/章节（自动生成模板，可手动补充）
- **使用说明**：Step2/Step3 如何引用索引替代原始文件

## 适用场景

- 项目初始化时，知识库准备完毕后**首次执行**
- 知识库新增/更新文件后**重新执行**刷新索引
- 基线用例/设计文档体积大（>1000 行），不宜整体引入 Step2/Step3 时

## 执行流程

统一使用**配置文件方案**执行，兼容中文路径和全平台。

### 步骤 1：确定项目路径

从用户输入中解析项目名或路径：
- 若用户给出项目名（如 `acflow`），工作区根目录下找 `<项目名>/input/knowledge/`
- 若用户给出完整路径，直接使用

### 步骤 2：查找脚本

使用 **Glob 工具** 搜索：
```
**/testcasegen-knowledge-index/scripts/build_knowledge_index.py
```

### 步骤 3：确定临时目录

根据用户 OS（从 user_info 获取）：

| OS | 临时目录 | Python 命令 |
|----|----------|-------------|
| Windows | `C:\Users\<用户名>\.cursor\temp\` | `python -X utf8` |
| macOS/Linux | `~/.cursor/temp/` | `python3` |

### 步骤 4：处理脚本路径

检查**脚本路径**是否包含非 ASCII 字符（中文等）：
- **否** → 直接使用原始路径，跳到步骤 5
- **是** → 用 Read + Write 工具将脚本内容复制到 `<临时目录>/build_knowledge_index.py`，后续使用该临时路径

### 步骤 5：创建配置文件

使用 **Write 工具** 创建 `<临时目录>/knowledge_index_config.json`：

```json
{
  "knowledge_dir": "<knowledge目录绝对路径>",
  "project_name": "<项目名>",
  "output_file": "<knowledge目录绝对路径>/knowledge_index.md"
}
```

> `project_name` 和 `output_file` 可省略，脚本会自动推断。

### 步骤 6：执行脚本

```bash
# Windows (PowerShell)
python -X utf8 "<脚本路径>" --config "<临时目录>\knowledge_index_config.json"

# macOS / Linux
python3 "<脚本路径>" --config "<临时目录>/knowledge_index_config.json"
```

### 步骤 7：告知结果

读取 `knowledge_index.md` 前 80 行，向用户展示：
- 扫描到的文件数与合计行数
- 各类型文件分布
- 后续使用方式（Step2/Step3 中如何引用）

### 步骤 8：清理

使用 **Delete 工具** 删除临时文件：
- `<临时目录>/knowledge_index_config.json`
- `<临时目录>/build_knowledge_index.py`（仅步骤 4 复制过时）

---

## 快速示例

用户输入：`/testcasegen-knowledge-index acflow`，工作区 `D:\code\testcase-generate`

1. knowledge 路径：`D:\code\testcase-generate\acflow\input\knowledge`
2. Write 配置文件 `C:\Users\xxx\.cursor\temp\knowledge_index_config.json`：
   ```json
   {
     "knowledge_dir": "D:\\code\\testcase-generate\\acflow\\input\\knowledge",
     "project_name": "acflow"
   }
   ```
3. 执行：`python -X utf8 "<脚本路径>" --config "C:\Users\xxx\.cursor\temp\knowledge_index_config.json"`
4. 输出：`D:\code\testcase-generate\acflow\input\knowledge\knowledge_index.md`
5. Delete 临时文件

---

## 生成索引的使用方式

### Step2 测试概要中引用

```
@<project>/output/prd_analysis/<前缀>_需求解析报告.md   ← 必选
@<project>/input/knowledge/knowledge_index.md           ← 替代原始知识库文件
@.cursor/skills/testcasegen-prompts/rules/02testdesign.mdc
```

Agent 读取索引后，按「章节索引」中的行范围，使用 Read 工具精准读取所需章节，
**不全量加载原始大文件**，保持总输入在阈值以内。

### Step3 测试用例中引用

```
@<project>/output/test_outline/<前缀>_测试概要.md       ← 必选
@<project>/input/knowledge/knowledge_index.md           ← 替代原始知识库文件
@.cursor/skills/testcasegen-prompts/rules/03testrequirement.mdc
```

### 手动维护模块映射表

索引生成后，打开 `knowledge_index.md` 第三节「测试模块 × 知识库映射」，
将「测试模块关键词」列从自动生成的文件名替换为实际测试模块名称，
如 `建档模块-基线用例` → `客户审核（建档/变更）`。

此步骤**只需做一次**，迭代更新时重新生成索引不会覆盖模块映射表（若需要可手动重置）。

---

## 注意事项

- 索引本身体积约 100~500 行，视知识库规模而定，始终可纳入 Step2/Step3 输入
- 脚本只读取 `.md` 文件，其他格式（Word/Excel）请先用 `testcasegen-all2md` 转换
- `knowledge_index.md` 本身被脚本自动排除，不会被重复索引
