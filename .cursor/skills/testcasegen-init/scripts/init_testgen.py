#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化测试用例生成目录（用于 Cursor Skills）。

- 默认以 workspace root 为基准创建目录
- 创建 input/output 目录结构
"""

from __future__ import annotations

import argparse
import json
import re
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

    # config（保留 .testgen 目录名，避免影响现有 MCP/流程）
    cfg_dir = (project_dir.parent / ".testgen").resolve()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cfg_dir / "config.json"
    cfg = {
        "base_dir": str(project_dir.resolve().relative_to(project_dir.parent.resolve())),
        "input": {
            "prd_docx_dir": str((project_dir / "input" / "prdword").relative_to(project_dir.parent)),
            "knowledge_dir": str((project_dir / "input" / "knowledge").relative_to(project_dir.parent)),
            "design_docx_dir": str((project_dir / "input" / "codedesignword").relative_to(project_dir.parent)),
            "baseline_cases_dir": str((project_dir / "input" / "baseline_cases").relative_to(project_dir.parent)),
        },
        "output": {
            "prd_md_dir": str((project_dir / "output" / "prdmd").relative_to(project_dir.parent)),
            "design_md_dir": str((project_dir / "output" / "codedesignmd").relative_to(project_dir.parent)),
            "requirement_analysis_dir": str((project_dir / "output" / "requirement_analysis").relative_to(project_dir.parent)),
            "test_outline_dir": str((project_dir / "output" / "test_outline").relative_to(project_dir.parent)),
            "test_cases_dir": str((project_dir / "output" / "test_cases").relative_to(project_dir.parent)),
            "xmind_dir": str((project_dir / "output" / "xmind").relative_to(project_dir.parent)),
        },
    }
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "config": str(cfg_path),
        "base": str(project_dir),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace-root", default="", help="工作区根目录（可选；默认使用当前目录）")
    ap.add_argument("--project-name", default="testcasegen", help="项目目录名（默认 testcasegen）")
    args = ap.parse_args()

    ws = resolve_workspace_root(args.workspace_root or None)
    name = sanitize_dir_name(args.project_name) or "testcasegen"
    project_dir = (ws / name).resolve()

    res = ensure_layout(project_dir)
    print("初始化完成：")
    print(f"- workspace_root: {ws}")
    print(f"- base: {res['base']}")
    print(f"- config: {res['config']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

