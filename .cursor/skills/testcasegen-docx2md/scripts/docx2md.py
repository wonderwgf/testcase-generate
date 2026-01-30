#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOCX -> Markdown（用于 Cursor Skills）。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


def _stdout_utf8():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


_stdout_utf8()


def get_paragraph_style_level(paragraph):
    """获取段落的标题层级"""
    style_name = paragraph.style.name
    if "Heading" in style_name or "标题" in style_name:
        if "1" in style_name or "一" in style_name:
            return 1
        if "2" in style_name or "二" in style_name:
            return 2
        if "3" in style_name or "三" in style_name:
            return 3
        if "4" in style_name or "四" in style_name:
            return 4
        if "5" in style_name or "五" in style_name:
            return 5
        if "6" in style_name or "六" in style_name:
            return 6
    return 0


def rgb_to_hex(rgb):
    if rgb is None:
        return None
    try:
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    except Exception:
        return None


def get_text_color(run):
    try:
        if run.font.color and run.font.color.rgb:
            return rgb_to_hex(run.font.color.rgb)
    except Exception:
        pass
    return None


def format_run_text(run):
    text = run.text
    if not text:
        return ""

    is_bold = run.bold is True
    is_italic = run.italic is True
    is_underline = run.underline is True
    is_strike = run.font.strike is True
    color = get_text_color(run)

    if not any([is_bold, is_italic, is_underline, is_strike, color]):
        return text

    formatted_text = text
    if color:
        formatted_text = f'<span style="color: {color}">{formatted_text}</span>'
    if is_strike:
        formatted_text = f"~~{formatted_text}~~"
    if is_underline:
        formatted_text = f"<u>{formatted_text}</u>"
    if is_italic:
        formatted_text = f"*{formatted_text}*"
    if is_bold:
        formatted_text = f"**{formatted_text}**"
    return formatted_text


def extract_images_from_paragraph(paragraph, image_dir, image_counter, output_path=None):
    images_md = []
    try:
        for run in paragraph.runs:
            for drawing in run._element.findall(
                ".//a:blip",
                namespaces={"a": "http://schemas.openxmlformats.org/drawingml/2006/main"},
            ):
                embed = drawing.get(qn("r:embed"))
                if not embed:
                    continue
                try:
                    image_part = paragraph.part.related_parts[embed]
                    image_bytes = image_part.blob

                    content_type = image_part.content_type
                    ext_map = {
                        "image/png": "png",
                        "image/jpeg": "jpg",
                        "image/jpg": "jpg",
                        "image/gif": "gif",
                        "image/bmp": "bmp",
                        "image/tiff": "tiff",
                    }
                    ext = ext_map.get(content_type, "png")

                    image_filename = f"image_{image_counter:03d}.{ext}"
                    image_path = os.path.join(image_dir, image_filename)
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                    if output_path:
                        output_dir = os.path.dirname(os.path.abspath(output_path))
                        try:
                            rel_path = os.path.relpath(image_path, output_dir).replace("\\", "/")
                        except ValueError:
                            rel_path = os.path.join(os.path.basename(image_dir), image_filename).replace("\\", "/")
                    else:
                        rel_path = os.path.join(os.path.basename(image_dir), image_filename).replace("\\", "/")

                    images_md.append(f"![图片{image_counter}]({rel_path})")
                    image_counter += 1
                except Exception as e:
                    print(f"  警告：提取图片失败 - {e}")
    except Exception as e:
        print(f"  警告：处理段落图片时出错 - {e}")
    return images_md, image_counter


def paragraph_to_markdown(paragraph, image_dir, image_counter, output_path=None):
    level = get_paragraph_style_level(paragraph)
    text = paragraph.text.strip()

    images_md, image_counter = extract_images_from_paragraph(paragraph, image_dir, image_counter, output_path)

    if not text and images_md:
        return "\n".join(images_md) + "\n", image_counter
    if not text:
        return "", image_counter

    if level > 0:
        result = f"{'#' * level} {text}\n"
        if images_md:
            result += "\n".join(images_md) + "\n"
        return result, image_counter

    if paragraph.runs:
        all_bold = all(run.bold is True for run in paragraph.runs if run.text.strip())
        if all_bold and len(text) < 100:
            result = f"### {text}\n"
            if images_md:
                result += "\n".join(images_md) + "\n"
            return result, image_counter

    if text.startswith(("•", "-", "·")):
        result = f"- {text.lstrip('•-· ')}\n"
        if images_md:
            result += "\n".join(images_md) + "\n"
        return result, image_counter

    if len(text) > 0 and text[0].isdigit() and ("." in text[:5] or "、" in text[:5]):
        result = f"{text}\n"
        if images_md:
            result += "\n".join(images_md) + "\n"
        return result, image_counter

    formatted_text = "".join(format_run_text(run) for run in paragraph.runs).strip()
    result = formatted_text + "\n"
    if images_md:
        result += "\n" + "\n".join(images_md) + "\n"
    return result, image_counter


def format_cell_text(cell):
    formatted_parts = []
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            formatted_parts.append(format_run_text(run))
    return "".join(formatted_parts).strip().replace("\n", " ")


def convert_table_to_markdown(table):
    if not table.rows:
        return ""
    markdown = "\n"

    header_cells = table.rows[0].cells
    header = "| " + " | ".join(format_cell_text(cell) for cell in header_cells) + " |\n"
    separator = "| " + " | ".join(["---"] * len(header_cells)) + " |\n"
    markdown += header
    markdown += separator

    for row in table.rows[1:]:
        cells = row.cells
        row_text = "| " + " | ".join(format_cell_text(cell) for cell in cells) + " |\n"
        markdown += row_text
    markdown += "\n"
    return markdown


def convert_docx_to_markdown(docx_path, output_path, image_dir):
    """
    将 Word 文档转换为 Markdown，并把图片提取到 image_dir。
    """
    try:
        docx_path_obj = Path(docx_path)
        if not docx_path_obj.is_absolute():
            docx_path = str(docx_path_obj.resolve())
        else:
            docx_path = str(docx_path_obj)

        output_path_obj = Path(output_path)
        if not output_path_obj.is_absolute():
            output_path = str(output_path_obj.resolve())
        else:
            output_path = str(output_path_obj)

        image_dir_obj = Path(image_dir)
        if not image_dir_obj.is_absolute():
            image_dir = str(image_dir_obj.resolve())
        else:
            image_dir = str(image_dir_obj)

        print(f"正在读取Word文档: {docx_path}")
        doc = Document(str(Path(docx_path)))

        os.makedirs(image_dir, exist_ok=True)
        print(f"图片保存目录: {image_dir}")

        markdown_content = []
        image_counter = 1

        for element in doc.element.body:
            if element.tag.endswith("p"):
                for paragraph in doc.paragraphs:
                    if paragraph._element == element:
                        md_text, image_counter = paragraph_to_markdown(
                            paragraph, image_dir, image_counter, output_path
                        )
                        if md_text:
                            markdown_content.append(md_text)
                        break
            elif element.tag.endswith("tbl"):
                for table in doc.tables:
                    if table._element == element:
                        md_table = convert_table_to_markdown(table)
                        if md_table:
                            markdown_content.append(md_table)
                        break

        print(f"正在写入Markdown文件: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_content))

        print("✅ 转换完成！")
        print(f"📄 输出文件: {output_path}")
        print(f"🖼️  提取图片数量: {image_counter - 1}")
        print(f"📊 共转换 {len(markdown_content)} 个元素")
        return True
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", default="", help="DOCX 路径（包含中文时可改用 --docx-path-file 或 --docx-dir）")
    ap.add_argument("--docx-path-file", default="", help="包含 DOCX 路径的文本文件（UTF-8）")
    ap.add_argument("--docx-dir", default="", help="DOCX 所在目录（避免中文路径编码问题）")
    ap.add_argument("--pattern", default="*.docx", help="从目录中匹配的文件模式（默认 *.docx）")
    ap.add_argument("--docx-index", type=int, default=0, help="从目录匹配结果中选择第 N 个（1 开始）")
    ap.add_argument("--list", action="store_true", help="仅列出目录下匹配文件并退出")
    ap.add_argument("--docx-name-file", default="", help="包含 DOCX 文件名的文本文件（UTF-8，配合 --docx-dir）")
    ap.add_argument("--doc-type", choices=["prd", "design"], default="prd", help="文档类型（影响默认输出目录）")
    ap.add_argument("--out", default="", help="输出 md 路径（可选）")
    ap.add_argument("--images", default="", help="图片目录（可选）")
    args = ap.parse_args()

    docx_path = None
    if args.docx_path_file:
        path_file = Path(args.docx_path_file).expanduser()
        if not path_file.exists():
            raise FileNotFoundError(f"路径文件不存在: {path_file}")
        raw_path = path_file.read_text(encoding="utf-8").strip()
        if not raw_path:
            raise ValueError("路径文件为空")
        docx_path = Path(raw_path).expanduser()
        if not docx_path.is_absolute():
            docx_path = (Path.cwd() / docx_path).resolve()
    elif args.docx:
        docx_path = Path(args.docx).expanduser()
    elif args.docx_dir:
        docx_dir = Path(args.docx_dir).expanduser()
        if not docx_dir.exists():
            raise FileNotFoundError(f"DOCX 目录不存在: {docx_dir}")
        candidates = sorted(docx_dir.glob(args.pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            raise FileNotFoundError(f"目录下未找到匹配文件: {docx_dir} / {args.pattern}")
        if args.list:
            print("匹配到的 DOCX 列表（按修改时间从新到旧）：")
            for i, p in enumerate(candidates, start=1):
                print(f"{i:>2}. {p.name}")
            return 0
        if args.docx_name_file:
            name_file = Path(args.docx_name_file).expanduser()
            if not name_file.exists():
                raise FileNotFoundError(f"文件名文件不存在: {name_file}")
            target_name = name_file.read_text(encoding="utf-8").strip()
            if not target_name:
                raise ValueError("文件名文件为空")
            matched = [p for p in candidates if p.name == target_name]
            if not matched:
                print(f"未找到文件名匹配: {target_name}")
                print("可用文件名：")
                for p in candidates:
                    print(f"- {p.name}")
                return 1
            docx_path = matched[0]
            print(f"按文件名选择: {docx_path}")
        elif args.docx_index > 0:
            if args.docx_index > len(candidates):
                raise IndexError(f"--docx-index 超出范围（1..{len(candidates)}）")
            docx_path = candidates[args.docx_index - 1]
            print(f"按 --docx-index 选择: {docx_path}")
        else:
            if len(candidates) > 1:
                print("目录下有多个 DOCX，请用 --docx-index 选择，或用 --list 查看列表：")
                for i, p in enumerate(candidates, start=1):
                    print(f"{i:>2}. {p.name}")
                return 1
            docx_path = candidates[0]
            print(f"未指定 --docx，自动选择唯一文件: {docx_path}")
    else:
        raise ValueError("请提供 --docx、--docx-path-file 或 --docx-dir")

    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX 不存在: {docx_path}")

    # 推导项目根目录：优先根据 .../input/xxx 结构
    project_root = None
    for parent in docx_path.parents:
        if parent.name.lower() == "input":
            project_root = parent.parent
            break
    if project_root is None:
        project_root = Path.cwd()

    if args.out:
        out_md = Path(args.out).expanduser().resolve()
    else:
        out_dir = project_root / "output" / ("prdmd" if args.doc_type == "prd" else "codedesignmd")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_md = (out_dir / f"{docx_path.stem}.md").resolve()

    if args.images:
        img_dir = Path(args.images).expanduser().resolve()
    else:
        img_dir = (out_md.parent / f"{out_md.stem}_images").resolve()

    ok = convert_docx_to_markdown(str(docx_path), str(out_md), str(img_dir))
    if not ok:
        raise RuntimeError("转换失败（convert_docx_to_markdown 返回 False）")

    print("转换完成：")
    print(f"- docx: {docx_path}")
    print(f"- md:   {out_md}")
    print(f"- img:  {img_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

