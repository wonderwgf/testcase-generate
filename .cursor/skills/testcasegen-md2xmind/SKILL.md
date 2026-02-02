---
name: testcasegen-md2xmind
description: 将生成的测试用例 Markdown 转成 XMind（用于分享/评审）。适合用例生成完成后执行。
disable-model-invocation: true
---
# testcasegen-md2xmind

# testcasegen-md2xmind

## 推荐用法（当前规则）

**规则文档**：`rules/04-testcase-xmind.mdc`

**脚本**：`.cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py`

### 命令行方式（推荐）

```bash
python .cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py <md文件路径> [输出目录]
```

**示例：**

```bash
# 默认：输入在 output/test_cases 时，输出到 output/xmind
python .cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py output/test_cases/xxx_测试用例.md

# 指定输出目录
python .cursor/skills/testcasegen-md2xmind/scripts/markdown_to_xmind.py output/test_cases/xxx_测试用例.md output/xmind
```

### 脚本内配置方式（需要改文件）

在 `markdown_to_xmind.py` 文件底部配置：

- `md_file`：Markdown 测试用例路径（必填）
- `output_dir`：输出目录（可选；为空且输入在 output/test_cases 时默认输出到 output/xmind）

运行脚本即可生成 XMind。

