#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Markdown -> XMind（用于 Cursor Skills）。
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

import xmind

# 设置输出编码为UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def parse_markdown_to_structure(md_content):
    """
    直接解析Markdown内容，支持完整的层级结构
    改进的列表项处理逻辑，特别优化Tab缩进处理
    """
    lines = md_content.split("\n")
    structure = []
    stack = []

    def calculate_indent_level(line):
        """
        精确计算缩进级别，支持Tab和空格混合
        Tab视为4个空格的缩进
        """
        stripped = line.lstrip()
        if len(stripped) == len(line):
            return 0
        indent_part = line[: len(line) - len(stripped)]
        normalized_indent = indent_part.replace("\t", "    ")
        return len(normalized_indent)

    for original_line in lines:
        stripped_line = original_line.strip()
        if not stripped_line:
            continue

        title_match = re.match(r"^(#{1,6})\s+(.+)$", stripped_line)
        if title_match:
            level = len(title_match.group(1))
            title = title_match.group(2).strip()

            while len(stack) >= level:
                stack.pop()

            node = {"title": title, "level": level, "children": [], "type": "heading", "raw_indent": 0}
            if stack:
                stack[-1]["children"].append(node)
            else:
                structure.append(node)
            stack.append(node)
            continue

        if stripped_line.startswith("-") or stripped_line.startswith("*"):
            raw_indent = calculate_indent_level(original_line)
            list_content = stripped_line.lstrip("-* ").strip()
            if not list_content:
                continue

            logical_indent_level = raw_indent // 4

            while len(stack) > 0:
                top_node = stack[-1]
                if top_node["type"] == "heading":
                    break
                if top_node["type"] in ["list", "content"]:
                    if top_node.get("raw_indent", 0) < raw_indent:
                        break
                    if top_node.get("raw_indent", 0) == raw_indent:
                        stack.pop()
                        continue
                stack.pop()

            if stack:
                if stack[-1]["type"] == "heading":
                    target_level = stack[-1]["level"] + 1 + logical_indent_level
                else:
                    target_level = stack[-1]["level"] + 1
            else:
                target_level = 1 + logical_indent_level

            node = {
                "title": list_content,
                "level": target_level,
                "children": [],
                "type": "list",
                "raw_indent": raw_indent,
            }
            if stack:
                stack[-1]["children"].append(node)
            else:
                structure.append(node)
            stack.append(node)
            continue

        if original_line.startswith("  ") or original_line.startswith("\t"):
            if stack:
                content = stripped_line
                if content and not content.startswith("#") and not content.startswith("-") and not content.startswith("*"):
                    raw_indent = calculate_indent_level(original_line)
                    logical_indent_level = raw_indent // 4

                    while len(stack) > 0:
                        top_node = stack[-1]
                        if top_node.get("raw_indent", 0) < raw_indent:
                            break
                        if top_node.get("raw_indent", 0) == raw_indent:
                            stack.pop()
                            continue
                        stack.pop()

                    if stack:
                        target_level = stack[-1]["level"] + 1
                    else:
                        target_level = 1 + logical_indent_level

                    node = {
                        "title": content,
                        "level": target_level,
                        "children": [],
                        "type": "content",
                        "raw_indent": raw_indent,
                    }
                    if stack:
                        stack[-1]["children"].append(node)
                    else:
                        structure.append(node)

    return structure


def create_xmind_from_structure(structure, parent_topic):
    for node in structure:
        sub_topic = parent_topic.addSubTopic()
        sub_topic.setTitle(node["title"])
        if node["children"]:
            create_xmind_from_structure(node["children"], sub_topic)


def md_to_xmind(md_file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    if os.path.isabs(md_file_name):
        md_file_path = md_file_name
    else:
        md_file_path = os.path.join(current_dir, md_file_name)

    if not os.path.exists(md_file_path):
        print(f"未找到 Markdown 文件: {md_file_path}")
        return

    with open(md_file_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    print(f"正在解析 Markdown 文件: {md_file_path}")
    structure = parse_markdown_to_structure(md_content)
    if not structure:
        print("未找到有效的Markdown结构")
        return

    try:
        template_path = os.path.join(current_dir, "temp.xmind")
        workbook = xmind.load(template_path)
    except Exception:
        try:
            workbook = xmind.load("default.xmind")
        except Exception:
            workbook = xmind.load()

    sheet = workbook.getPrimarySheet()
    root_topic = sheet.getRootTopic()
    base_name = os.path.splitext(os.path.basename(md_file_path))[0]
    root_topic.setTitle(base_name)

    create_xmind_from_structure(structure, root_topic)

    md_file_dir = os.path.dirname(md_file_path)
    xmind_file_name = f"{base_name}_完整版.xmind"
    xmind_file_path = os.path.join(md_file_dir, xmind_file_name)
    os.makedirs(md_file_dir, exist_ok=True)

    xmind.save(workbook, path=xmind_file_path)
    print(f"✅ 已成功将 {md_file_path} 转换为 {xmind_file_path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default="", help="Markdown 路径（与 --md-dir 二选一）")
    ap.add_argument("--md-dir", default="", help="Markdown 所在目录（Windows 中文路径乱码时用）")
    ap.add_argument("--md-index", type=int, default=0, help="--md-dir 下第几个 .md，0 起（默认 0）")
    ap.add_argument("--out", default="", help="输出 xmind 路径（可选）")
    args = ap.parse_args()

    if args.md_dir:
        md_dir = Path(args.md_dir).expanduser().resolve()
        if not md_dir.is_dir():
            raise FileNotFoundError(f"目录不存在: {md_dir}")
        md_files = sorted(md_dir.glob("*.md"))
        if not md_files:
            raise FileNotFoundError(f"目录下无 .md 文件: {md_dir}")
        idx = args.md_index
        if idx < 0 or idx >= len(md_files):
            raise IndexError(f"--md-index {idx} 超出范围（共 {len(md_files)} 个 .md）")
        md_path = md_files[idx]
    elif args.md:
        md_path = Path(args.md).expanduser().resolve()
        if not md_path.exists():
            raise FileNotFoundError(f"Markdown 不存在: {md_path}")
    else:
        ap.error("请指定 --md 或 --md-dir")

    md_to_xmind(str(md_path))

    generated = md_path.parent / f"{md_path.stem}_完整版.xmind"
    if not generated.exists():
        raise RuntimeError(f"未找到生成的 xmind 文件: {generated}")

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(generated), str(out_path))
        result = out_path
    else:
        result = generated

    print("转换完成：")
    print(f"- md:    {md_path}")
    print(f"- xmind: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

