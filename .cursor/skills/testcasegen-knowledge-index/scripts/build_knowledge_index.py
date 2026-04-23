#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知识库索引生成脚本（用于 Cursor Skills: testcasegen-knowledge-index）

功能：
- 扫描项目 knowledge/ 目录下所有 .md 文件
- 按知识库类型（基线用例/业务规则/技术设计/历史需求）分类
- 提取每个文件的 H1/H2 标题及行范围，生成章节索引
- 输出 knowledge_index.md，供 Agent 在 Step2/Step3 中替代原始大文件引用

用法：
  python build_knowledge_index.py --config <config.json>
  配置文件格式：
    {
      "knowledge_dir": "<knowledge目录绝对路径>",
      "project_name": "<项目名，可选，默认自动推断>",
      "output_file": "<输出路径，可选，默认 knowledge_dir/knowledge_index.md>"
    }
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── 目录名 → 知识库类型映射 ───────────────────────────────────────────────
# key: knowledge/ 下一级目录名（小写包含即匹配）
DIR_TYPE_MAP = [
    ("baseline_cases", "基线用例"),
    ("business",       "业务规则/流程文档"),
    ("codedesign",     "技术设计文档"),
    ("prd",            "历史需求文档"),
]

TYPE_ORDER = ["基线用例", "业务规则/流程文档", "技术设计文档", "历史需求文档", "其他"]


def detect_type(rel_path: str) -> str:
    """根据相对路径第一段目录名判断知识库类型。"""
    parts = Path(rel_path).parts
    first = parts[0].lower() if parts else ""
    for key, label in DIR_TYPE_MAP:
        if key in first:
            return label
    return "其他"


def extract_headings(filepath: Path) -> tuple[int, list[tuple[int, int, str]]]:
    """
    读取 md 文件，提取 H1/H2 标题及行号。
    返回 (总行数, [(行号, 级别, 标题文本), ...])
    """
    headings: list[tuple[int, int, str]] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw_lines = f.readlines()
        total = len(raw_lines)
        for i, line in enumerate(raw_lines, 1):
            s = line.strip()
            if s.startswith("#"):
                level = len(s) - len(s.lstrip("#"))
                if level <= 2:  # 只索引 H1/H2，保持索引简洁
                    title = s.lstrip("#").strip()
                    if title:
                        headings.append((i, level, title))
        return total, headings
    except Exception as e:
        print(f"  ⚠ 读取失败: {filepath} — {e}", file=sys.stderr)
        return 0, []


def compute_ranges(
    headings: list[tuple[int, int, str]], total: int
) -> list[tuple[int, int, int, str]]:
    """
    为每个标题计算行范围（到下一个同级或更高级标题前一行）。
    返回 [(start, end, level, title), ...]
    """
    result = []
    for idx, (line_no, level, title) in enumerate(headings):
        end = total
        for next_line, next_level, _ in headings[idx + 1 :]:
            if next_level <= level:
                end = next_line - 1
                break
        result.append((line_no, end, level, title))
    return result


def fmt_size(lines: int) -> str:
    if lines >= 10000:
        return f"{lines // 1000}k+"
    if lines >= 1000:
        return f"{lines / 1000:.1f}k"
    return str(lines)


def build_index(knowledge_dir: str, output_file: str, project_name: str) -> None:
    kb_path = Path(knowledge_dir).resolve()

    # ── 扫描所有 .md 文件（排除已生成的索引自身）──────────────────────────
    all_rel: list[str] = []
    for root, dirs, files in os.walk(kb_path):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for fname in sorted(files):
            if fname.endswith(".md") and fname != "knowledge_index.md":
                rel = os.path.relpath(os.path.join(root, fname), kb_path)
                all_rel.append(rel)

    if not all_rel:
        print("⚠ knowledge/ 目录下未找到任何 .md 文件，索引未生成。")
        return

    # ── 提取每个文件的元数据 ──────────────────────────────────────────────
    file_meta: dict[str, dict] = {}
    for rel in all_rel:
        full = kb_path / rel
        total, headings = extract_headings(full)
        sections = compute_ranges(headings, total)
        file_meta[rel] = {
            "type": detect_type(rel),
            "total": total,
            "sections": sections,  # (start, end, level, title)
        }

    # ── 按类型分组 ─────────────────────────────────────────────────────────
    grouped: dict[str, list[str]] = {t: [] for t in TYPE_ORDER}
    for rel, meta in file_meta.items():
        grouped[meta["type"]].append(rel)

    # ── 输出 Markdown ─────────────────────────────────────────────────────
    out: list[str] = []

    def w(*args: str) -> None:
        out.append(" ".join(args) if args else "")

    total_files = len(all_rel)
    total_lines_all = sum(m["total"] for m in file_meta.values())

    w("# 知识库索引")
    w()
    w(
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        f"项目：{project_name} | "
        f"共 {total_files} 个文件，合计 {fmt_size(total_lines_all)} 行"
    )
    w(
        "> **用途**：Step2/Step3 中替代原始知识库大文件。"
        "Agent 按「章节速查」列的行范围用 `Read(offset=起行, limit=行数)` 精准读取，不全量载入原文。"
    )
    w()
    w("---")
    w()

    # ── 第一节：紧凑合并表（目录 + 章节索引合一）────────────────────────
    w("## 一、文件目录 & 章节速查")
    w()
    w("> 章节格式：`§标题(起行–终行)`，超过 6 节时仅列前 6 节，完整列表见原文。")
    w()
    w("| 类型 | 文件（相对 knowledge/） | 行数 | 章节速查 |")
    w("|------|----------------------|------|---------|")

    for t in TYPE_ORDER:
        for rel in grouped[t]:
            m = file_meta[rel]
            fpath = rel.replace("\\", "/")
            sections_h12 = [(s[0], s[1], s[3]) for s in m["sections"] if s[2] <= 2]
            if sections_h12:
                ch_parts = [f"§{title}({start}–{end})" for start, end, title in sections_h12[:6]]
                ch_str = " | ".join(ch_parts)
                if len(sections_h12) > 6:
                    ch_str += f" | …共{len(sections_h12)}节"
            else:
                ch_str = "_(无H2标题，全文引用)_"
            w(f"| {t} | `{fpath}` | {fmt_size(m['total'])} | {ch_str} |")

    w()
    w("---")
    w()

    # ── 第二节：模块映射表（手动维护区）─────────────────────────────────
    w("## 二、测试模块 × 知识库映射（手动维护）")
    w()
    w(
        "> ⚠️ **本表为自动生成模板**，请将「测试模块关键词」列替换为实际模块名。  \n"
        "> 维护一次后每次迭代可直接复用；重新生成索引不会覆盖本节（需手动更新）。"
    )
    w()
    w("| 测试模块关键词 | 推荐知识库文件 | 推荐章节行范围 |")
    w("|--------------|--------------|--------------|")

    for t in TYPE_ORDER:
        for rel in grouped[t]:
            m = file_meta[rel]
            fpath = rel.replace("\\", "/")
            fname_stem = Path(rel).stem
            sections_h12 = [(s[0], s[1], s[3]) for s in m["sections"] if s[2] <= 2]
            if sections_h12:
                # 只列前 2 节作为示例，避免列过长
                ch_hint = "、".join(
                    f"§{t3}({s3}–{e3})" for s3, e3, t3 in sections_h12[:2]
                )
                if len(sections_h12) > 2:
                    ch_hint += f"、…"
            else:
                ch_hint = "全文"
            w(f"| _{fname_stem}_ | `{fpath}` | {ch_hint} |")

    w()
    w("---")
    w()

    # ── 第三节：使用说明 ──────────────────────────────────────────────────
    w("## 三、使用说明")
    w()
    w("**Step2 测试概要**：")
    w("```")
    w("@output/prd_analysis/<前缀>_需求解析报告.md  ← 必选")
    w("@input/knowledge/knowledge_index.md          ← 替代原始知识库（本文件）")
    w("@.cursor/skills/testcasegen-prompts/rules/02testdesign.mdc")
    w("```")
    w()
    w("**Step3 测试用例**：")
    w("```")
    w("@output/test_outline/<前缀>_测试概要.md      ← 必选")
    w("@input/knowledge/knowledge_index.md          ← 替代原始知识库（本文件）")
    w("@.cursor/skills/testcasegen-prompts/rules/03testrequirement.mdc")
    w("```")
    w()
    w(
        "Agent 在生成概要/用例时，需要参考某文件具体内容时，"
        "按第一节章节速查找到对应行范围，使用 Read 工具精准读取，不全量载入原文。"
    )
    w()
    w("**更新索引**：知识库新增/修改文件后，重新执行 `testcasegen-knowledge-index` skill 刷新。")
    w()
    w("---")
    w()
    w(f"_由 `testcasegen-knowledge-index` skill 自动生成 · {datetime.now().strftime('%Y-%m-%d')}_")

    # ── 写文件 ────────────────────────────────────────────────────────────
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print(f"✅ 知识库索引已生成：{out_path}")
    print(f"   文件数：{total_files}   行数合计：{total_lines_all}")
    print(f"   索引文件大小：{out_path.stat().st_size // 1024 + 1} KB")


def main() -> None:
    parser = argparse.ArgumentParser(description="生成知识库索引 knowledge_index.md")
    parser.add_argument("--config", required=True, help="JSON 配置文件路径")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8-sig") as f:
        cfg = json.load(f)

    knowledge_dir = cfg.get("knowledge_dir", "")
    if not knowledge_dir:
        print("❌ 配置文件缺少 knowledge_dir 字段", file=sys.stderr)
        sys.exit(1)

    kb_path = Path(knowledge_dir)
    project_name = cfg.get(
        "project_name",
        kb_path.parent.parent.name if kb_path.parent.parent != kb_path.parent else kb_path.name,
    )
    output_file = cfg.get(
        "output_file", str(kb_path / "knowledge_index.md")
    )

    build_index(knowledge_dir, output_file, project_name)


if __name__ == "__main__":
    main()
