---
name: testcasegen-md2xmind
description: 将生成的测试用例 Markdown 转成 XMind（用于分享/评审）。适合用例生成完成后执行。支持中文路径配置文件方案。
disable-model-invocation: true
---
# testcasegen-md2xmind

## 用法

**规则文档**：`rules/04-testcase-xmind.mdc`

**脚本**：`.cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py`

### 标准用法（路径不含中文）

```powershell
python -X utf8 .cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py <md文件路径> [输出目录]
```

**示例：**

```powershell
# 默认：输入在 output/test_cases 时，输出到 output/xmind
python -X utf8 .cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py output/test_cases/xxx_test.md

# 指定输出目录
python -X utf8 .cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py output/test_cases/xxx_test.md output/xmind
```

### 中文路径完整解决方案（推荐）

当**工作区路径**或**脚本路径**包含中文时，PowerShell 传递路径给 Python 会出现编码问题。需要按以下步骤操作：

**步骤 1：复制脚本到不含中文的路径**

将脚本复制到用户目录下（路径不含中文）：

```powershell
Copy-Item ".cursor\skills\testcasegen-md2xmind\scripts\markdown_to_xmind.py" "$env:USERPROFILE\.cursor\temp\markdown_to_xmind.py" -Force
```

或者使用 Cursor 的 Write 工具将脚本内容写入到 `C:\Users\<用户名>\.cursor\temp\markdown_to_xmind.py`。

**步骤 2：创建配置文件（UTF-8 编码）**

在 `C:\Users\<用户名>\.cursor\temp\md2xmind_config.json` 写入：

```json
{
  "md_file": "D:\\code\\中文项目\\output\\test_cases\\需求_测试用例.md",
  "output_dir": "D:\\code\\中文项目\\output\\xmind"
}
```

**步骤 3：使用配置文件执行**

```powershell
python -X utf8 "$env:USERPROFILE\.cursor\temp\markdown_to_xmind.py" --config "$env:USERPROFILE\.cursor\temp\md2xmind_config.json"
```

## 输出位置

输出默认落到：
- `output/xmind/<md名>.xmind`

## 完整示例

### 示例 1：标准转换（路径无中文）

```powershell
python -X utf8 .cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py output/test_cases/requirement_test.md
```

### 示例 2：中文路径完整流程

```powershell
# 1. 复制脚本
Copy-Item ".cursor\skills\testcasegen-md2xmind\scripts\markdown_to_xmind.py" "$env:USERPROFILE\.cursor\temp\markdown_to_xmind.py" -Force

# 2. 创建配置文件（使用 Cursor Write 工具写入 JSON）

# 3. 执行转换
python -X utf8 "$env:USERPROFILE\.cursor\temp\markdown_to_xmind.py" --config "$env:USERPROFILE\.cursor\temp\md2xmind_config.json"
```

