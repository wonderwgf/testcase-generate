---
name: testcasegen-md2xmind
description: 将生成的测试用例 Markdown 转成 XMind（用于分享/评审）。适合用例生成完成后执行。
---
# testcasegen-md2xmind

## 目标

将测试用例 Markdown 文件转换为 XMind 格式，输出到约定目录：
- 输入：`output/test_cases/<name>.md`
- 输出：`output/xmind/<name>.xmind`

## Agent 执行流程

当用户调用 `/testcasegen-md2xmind` 时，Agent 按以下步骤操作：

### 步骤 1：查找脚本路径

使用 **Glob 工具** 查找脚本：
- 搜索模式：`**/testcasegen-md2xmind/scripts/markdown_to_xmind.py`
- 搜索目录：当前工作区 或 `C:\Users\<用户名>\.cursor\projects`

### 步骤 2：判断中文路径情况

检查以下路径是否包含中文字符（非 ASCII）：

| 检查项 | 示例 |
|--------|------|
| 脚本路径 | `C:\Users\test\.cursor\projects\中文目录\scripts\markdown_to_xmind.py` |
| 工作区路径 | `D:\代码\项目` |
| 文件名/参数 | `需求_测试用例.md` |

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
python -X utf8 "<脚本路径>" "<md文件路径>" [输出目录]
```

**示例：**
```powershell
python -X utf8 "C:\Users\test\.cursor\skills\testcasegen-md2xmind\scripts\markdown_to_xmind.py" "D:\code\project\output\test_cases\requirement_test.md"
```

---

### 方案 B：配置文件（仅文件名/参数含中文）

脚本路径是英文，但文件名或工作区路径含中文时，**只需要配置文件，不需要复制脚本**。

#### B-1：创建配置文件

使用 **Write 工具** 在用户目录创建 `C:\Users\<用户名>\.cursor\temp\md2xmind_config.json`：

```json
{
  "md_file": "D:\\code\\project\\output\\test_cases\\需求_测试用例.md",
  "output_dir": "D:\\code\\project\\output\\xmind"
}
```

#### B-2：执行脚本

```powershell
python -X utf8 "<脚本路径>" --config "C:\Users\<用户名>\.cursor\temp\md2xmind_config.json"
```

#### B-3：清理临时文件

使用 **Delete 工具** 删除配置文件。

---

### 方案 C：复制脚本 + 配置文件（脚本路径含中文）

只有当**脚本路径本身包含中文**时，才需要复制脚本。

#### C-1：复制脚本

使用 **Shell** 或 **Read + Write 工具**：

```powershell
Copy-Item "<脚本路径>" "$env:USERPROFILE\.cursor\temp\markdown_to_xmind.py" -Force
```

或：
1. 使用 **Read 工具** 读取脚本内容
2. 使用 **Write 工具** 写入 `C:\Users\<用户名>\.cursor\temp\markdown_to_xmind.py`

#### C-2：创建配置文件

同方案 B-1。

#### C-3：执行脚本

```powershell
python -X utf8 "$env:USERPROFILE\.cursor\temp\markdown_to_xmind.py" --config "$env:USERPROFILE\.cursor\temp\md2xmind_config.json"
```

#### C-4：清理临时文件

使用 **Delete 工具** 删除：
- `C:\Users\<用户名>\.cursor\temp\md2xmind_config.json`
- `C:\Users\<用户名>\.cursor\temp\markdown_to_xmind.py`

---

## 输出位置

输出默认落到：
- `output/xmind/<md名>.xmind`

如果输入路径包含 `output/test_cases`，脚本会自动将输出目录设为 `output/xmind`。

---

## 示例

### 示例 1：路径全英文（方案 A）

```powershell
python -X utf8 ".cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py" "output/test_cases/requirement_test.md"
```

### 示例 2：仅文件名含中文（方案 B）

工作区：`D:\code\project`（英文）
文件名：`V1.8.0_晶澳交行_测试用例.md`（中文）
脚本路径：英文

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

脚本路径：`C:\Users\test\.cursor\projects\中文项目\skills\...\markdown_to_xmind.py`

Agent 执行：
1. 复制脚本到 `C:\Users\test\.cursor\temp\markdown_to_xmind.py`
2. 创建配置文件
3. 执行临时脚本
4. 删除临时脚本和配置文件

---

## 判断逻辑总结

```
是否需要复制脚本？→ 仅当脚本路径含中文
是否需要配置文件？→ 当文件名、工作区路径、或输出路径任一含中文
```

优先使用最简单的方案，避免不必要的复杂操作。

---

## 相关文件

- 规则文档：`rules/04-testcase-xmind.mdc`
- 脚本：`.cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py`
