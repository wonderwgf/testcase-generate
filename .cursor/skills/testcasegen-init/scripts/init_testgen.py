#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化测试用例生成目录（用于 Cursor Skills）。

功能：
- 在指定工作区下创建项目目录及 input/output 子目录结构
- 创建 input/：prdword、knowledge、codedesignword、baseline_cases
- 创建 output/：prdmd、codedesignmd、requirement_analysis、test_outline、test_cases、xmind

用法：
  方案 A（路径全英文，推荐）：
    python init_testgen.py <workspace_root> <project_name>
    python init_testgen.py "D:\\code\\project" "mytest"

  方案 B（路径含中文，使用配置文件）：
    python init_testgen.py --config <config.json>
    配置文件格式：{"workspace_root": "...", "project_name": "..."}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def sanitize_dir_name(name: str) -> str:
    n = (name or "").strip()
    if not n:
        return ""
    n = re.sub(r'[<>:"/\\\\|?*]+', "_", n)
    n = re.sub(r"\s+", "_", n)
    n = n.rstrip(" .")
    return n


def resolve_workspace_root(workspace_root: str | None) -> Path:
    if workspace_root:
        p = Path(workspace_root).expanduser()
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        else:
            p = p.resolve()
        return p
    return Path.cwd().resolve()


def load_config(config_path: str) -> dict:
    """从配置文件加载参数（UTF-8 编码）"""
    p = Path(config_path)
    if not p.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_layout(project_dir: Path) -> dict:
    # input
    (project_dir / "input" / "prdword").mkdir(parents=True, exist_ok=True)
    (project_dir / "input" / "knowledge").mkdir(parents=True, exist_ok=True)
    (project_dir / "input" / "codedesignword").mkdir(parents=True, exist_ok=True)
    (project_dir / "input" / "baseline_cases").mkdir(parents=True, exist_ok=True)

    # output
    (project_dir / "output" / "prdmd").mkdir(parents=True, exist_ok=True)
    (project_dir / "output" / "codedesignmd").mkdir(parents=True, exist_ok=True)
    (project_dir / "output" / "requirement_analysis").mkdir(parents=True, exist_ok=True)
    (project_dir / "output" / "test_outline").mkdir(parents=True, exist_ok=True)
    (project_dir / "output" / "test_cases").mkdir(parents=True, exist_ok=True)
    (project_dir / "output" / "xmind").mkdir(parents=True, exist_ok=True)

    return {
        "base": str(project_dir),
    }


def main() -> int:
    # 配置 stdout/stderr 编码
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(
        description="初始化测试用例生成目录结构",
        usage="%(prog)s [workspace_root] [project_name] | --config <config.json>"
    )
    # 位置参数（可选）- 方案 A：直接传参
    ap.add_argument("workspace_root", nargs="?", default="", help="工作区根目录（可选；默认使用当前目录）")
    ap.add_argument("project_name", nargs="?", default="testcasegen", help="项目目录名（默认 testcasegen）")
    # 命名参数 - 方案 B：配置文件
    ap.add_argument("--config", default="", help="配置文件路径（JSON格式，用于中文路径）")
    args = ap.parse_args()

    # 优先级：配置文件 > 位置参数 > 默认值
    if args.config:
        # 方案 B：从配置文件读取参数
        config = load_config(args.config)
        workspace_root = config.get("workspace_root", "")
        project_name = config.get("project_name", "testcasegen")
    else:
        # 方案 A：从位置参数读取
        workspace_root = args.workspace_root
        project_name = args.project_name

    ws = resolve_workspace_root(workspace_root or None)
    name = sanitize_dir_name(project_name) or "testcasegen"
    project_dir = (ws / name).resolve()

    ensure_layout(project_dir)
    
    print(f"初始化完成：{project_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

