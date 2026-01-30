#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Markdown -> XMind（用于 Cursor Skills）。
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from testgen_mcp.converters.mdToxmind import md_to_xmind


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True, help="Markdown 路径")
    ap.add_argument("--out", default="", help="输出 xmind 路径（可选）")
    args = ap.parse_args()

    md_path = Path(args.md).expanduser().resolve()
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown 不存在: {md_path}")

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

