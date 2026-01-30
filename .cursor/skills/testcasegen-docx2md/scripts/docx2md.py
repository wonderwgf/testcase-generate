#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DOCX -> Markdown（用于 Cursor Skills）。
"""

from __future__ import annotations

import argparse
from pathlib import Path

from testgen_mcp.converters.docTomd import convert_docx_to_markdown


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", required=True, help="DOCX 路径")
    ap.add_argument("--doc-type", choices=["prd", "design"], default="prd", help="文档类型（影响默认输出目录）")
    ap.add_argument("--out", default="", help="输出 md 路径（可选）")
    ap.add_argument("--images", default="", help="图片目录（可选）")
    args = ap.parse_args()

    docx_path = Path(args.docx).expanduser().resolve()
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX 不存在: {docx_path}")

    if args.out:
        out_md = Path(args.out).expanduser().resolve()
    else:
        out_dir = Path.cwd() / "output" / ("prdmd" if args.doc_type == "prd" else "codedesignmd")
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

