#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
merge_modules.py - 将各模块的步骤产出按清单顺序合并为最终文件。

功能：
- 读取 _manifest.json 获取模块顺序
- 从 output/modules/<迭代>/<n>/ 读取对应步骤的产出文件
- 按模块顺序合并，写入最终输出文件
- 缺少任意模块产出时报错，不生成不完整的合并文件

用法：
  python merge_modules.py --config <config.json>

配置文件格式：
{
  "manifest_file": "<output/prd/<迭代>/modules/_manifest.json 的绝对路径>",
  "modules_base_dir": "<output/modules/<迭代>/ 的绝对路径>",
  "step": "prd_analysis | test_outline | test_cases",
  "output_file": "<合并后输出文件的绝对路径>"
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

STEP_FILENAME: dict[str, str] = {
    'prd_analysis': 'prd_analysis.md',
    'test_outline': 'test_outline.md',
    'test_cases':   'test_cases.md',
}


def setup_encoding() -> None:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main() -> int:
    setup_encoding()

    ap = argparse.ArgumentParser(description='合并各模块步骤产出为最终文件')
    ap.add_argument('--config', required=True, help='JSON 配置文件路径')
    args = ap.parse_args()

    cfg = load_config(args.config)
    manifest_file   = Path(cfg['manifest_file'])
    modules_base    = Path(cfg['modules_base_dir'])
    step            = cfg['step']
    output_file     = Path(cfg['output_file'])

    # 校验 step 参数
    if step not in STEP_FILENAME:
        print(f'错误: step 必须是 {list(STEP_FILENAME.keys())} 之一，当前值: {step}',
              file=sys.stderr)
        return 1

    # 读取清单
    if not manifest_file.exists():
        print(f'错误: 清单文件不存在: {manifest_file}', file=sys.stderr)
        return 1

    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    modules    = sorted(manifest['modules'], key=lambda m: m['index'])
    step_fn    = STEP_FILENAME[step]

    # 检查每个模块的产出文件是否存在
    missing: list[str] = []
    found:   list[tuple[dict, Path]] = []

    for m in modules:
        mod_dir   = modules_base / f'{m["index"]:02d}'
        step_file = mod_dir / step_fn
        if step_file.exists():
            found.append((m, step_file))
        else:
            ch_desc = ' + '.join(m['chapters'][:2])
            missing.append(f'模块 {m["index"]:02d}（{ch_desc}）：{step_file}')

    if missing:
        print(f'错误：以下模块的 [{step}] 产出尚未生成，无法合并：', file=sys.stderr)
        for item in missing:
            print(f'  - {item}', file=sys.stderr)
        return 1

    # 合并
    output_file.parent.mkdir(parents=True, exist_ok=True)

    parts: list[str] = []
    for m, fp in found:
        ch_desc = ' / '.join(m['chapters'][:3])
        separator = f'\n\n<!-- ===== 模块 {m["index"]:02d}: {ch_desc} ===== -->\n\n'
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
        parts.append(separator + content)

    merged = ''.join(parts).lstrip('\n')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(merged)

    print(f'[完成] 合并 {len(parts)} 个模块的 [{step}] 产出 → {output_file}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
