---
name: testcasegen-docx2md
description: 将需求/设计 DOCX 转为 Markdown，并按约定输出到 output 目录（prdmd/codedesignmd）。适合在生成测试用例前做文档格式转换。
disable-model-invocation: true
---
# testcasegen-docx2md

## 用法

`python .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx <path> --doc-type prd|design`

如果文件名包含中文导致命令行编码异常，可改用目录方式：

- 列出匹配列表：
  `python .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx-dir <dir> --pattern "*.docx" --list`
- 选择第 N 个：
  `python .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx-dir <dir> --pattern "*.docx" --docx-index 2 --doc-type prd|design`

示例：

- 需求：
  `python .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx input/prdword/需求.docx --doc-type prd`
- 设计：
  `python .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx input/codedesignword/设计.docx --doc-type design`

- 中文路径兜底（目录方式）：
  `python .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx-dir input/prdword --pattern "*.docx" --list`
  `python .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx-dir input/prdword --pattern "*.docx" --docx-index 1 --doc-type prd`


输出默认落到：
- `output/prdmd/<docx名>.md`
- `output/codedesignmd/<docx名>.md`

