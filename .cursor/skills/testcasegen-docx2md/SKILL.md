---
name: testcasegen-docx2md
description: 将需求/设计 DOCX 转为 Markdown，并按约定输出到 output 目录（prdmd/codedesignmd）。适合在生成测试用例前做文档格式转换。
disable-model-invocation: true
---
# testcasegen-docx2md

## 用法

`python .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx <path> --doc-type prd|design`

示例：

- 需求：
  `python .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx input/prdword/需求.docx --doc-type prd`
- 设计：
  `python .cursor/skills/testcasegen-docx2md/scripts/docx2md.py --docx input/codedesignword/设计.docx --doc-type design`

输出默认落到：
- `output/prdmd/<docx名>.md`
- `output/codedesignmd/<docx名>.md`

