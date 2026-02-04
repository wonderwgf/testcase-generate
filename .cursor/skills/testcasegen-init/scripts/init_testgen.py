#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化测试用例生成目录（用于 Cursor Skills）。

- 默认以 workspace root 为基准创建目录
- 创建 input/output 目录结构
- 支持通过配置文件传递参数（推荐，避免中文路径编码问题）
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

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="", help="配置文件路径（JSON格式，推荐用于中文路径）")
    ap.add_argument("--workspace-root", default="", help="工作区根目录（可选；默认使用当前目录）")
    ap.add_argument("--project-name", default="testcasegen", help="项目目录名（默认 testcasegen）")
    args = ap.parse_args()

    # 优先从配置文件读取参数
    if args.config:
        config = load_config(args.config)
        workspace_root = config.get("workspace_root", "")
        project_name = config.get("project_name", "testcasegen")
    else:
        workspace_root = args.workspace_root
        project_name = args.project_name

    ws = resolve_workspace_root(workspace_root or None)
    name = sanitize_dir_name(project_name) or "testcasegen"
    project_dir = (ws / name).resolve()

    res = ensure_layout(project_dir)
    
    log_path = project_dir / "init_testgen.log"
    with log_path.open("w", encoding="utf-8") as f:
        f.write("初始化完成：\n")
        f.write(f"- workspace_root: {ws}\n")
        f.write(f"- base: {res['base']}\n")
    print(f"初始化完成：{project_dir}")
    print("详情已写入 init_testgen.log")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

