#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
split_prd.py - 将超过阈值的需求 Markdown 文档拆分为模块子文档。

功能：
- 识别"共享前置章节"（术语/概述/参考文档等），追加到每个子文档开头保证上下文完整
- 按 H1/H2 标题边界将功能章节贪心分组，每组约 target_lines 行
- 超过 hard_max 的 H2 章节自动按 H3 二次拆分
- 行数过少的模块自动合并到相邻模块
- 写入模块子文档和 _manifest.json 清单
- 幂等：_manifest.json 已存在时直接输出摘要并退出

用法：
  python split_prd.py --config <config.json>

配置文件格式：
{
  "md_file": "<需求md文件绝对路径>",
  "output_dir": "<模块子文档输出目录绝对路径>",
  "target_lines": 600,
  "hard_max": 800,
  "min_lines": 80,
  "shared_keywords": []
}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_SHARED_KEYWORDS = [
    '术语', '定义', '缩略', '概述', '总体', '参考文档', '引用',
    '背景', '目的', '范围', '适用', '前言', '说明', '修订',
    '版本', '历史', '附录', '规范', '简介',
    '文档控制', '目录', '变更记录', '审批', '读者对象',
    '编写目的', '项目背景', '系统简介', '文档约定',
]


def setup_encoding() -> None:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def file_md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def parse_headers(lines: list[str], min_level: int = 1, max_level: int = 2) -> list[dict]:
    """解析指定层级范围的标题行及其位置（0-based）。"""
    headers = []
    for i, raw in enumerate(lines):
        line = raw.rstrip('\n')
        for level in range(min_level, max_level + 1):
            prefix = '#' * level + ' '
            deeper = '#' * (level + 1) + ' '
            if line.startswith(prefix) and not line.startswith(deeper):
                headers.append({'line': i, 'level': level, 'title': line[len(prefix):].strip()})
                break
    return headers


def is_shared(title: str, keywords: list[str]) -> bool:
    return any(kw in title for kw in keywords)


def sanitize(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\s]+', '_', name)
    return name.strip('_')[:40]


def split_large_chapter(chapter: dict, lines: list[str], target: int) -> list[dict]:
    """对超过 hard_max 的章节按 H3 子标题二次拆分。"""
    start, end = chapter['start'], chapter['end']
    sub_headers = []
    for i in range(start, end):
        raw = lines[i].rstrip('\n')
        if raw.startswith('### ') and not raw.startswith('#### '):
            sub_headers.append({'line': i, 'title': raw[4:].strip()})

    if len(sub_headers) < 2:
        return [chapter]

    sub_chapters: list[dict] = []
    header_line = start
    header_end = sub_headers[0]['line']
    if header_end > start:
        sub_chapters.append({
            'title': chapter['title'],
            'level': chapter['level'],
            'start': start,
            'end': header_end,
            'lines': header_end - start,
            'shared': False,
            'parent_title': chapter['title'],
        })

    for j, sh in enumerate(sub_headers):
        s = sh['line']
        e = sub_headers[j + 1]['line'] if j + 1 < len(sub_headers) else end
        sub_chapters.append({
            'title': sh['title'],
            'level': 3,
            'start': s,
            'end': e,
            'lines': e - s,
            'shared': False,
            'parent_title': chapter['title'],
        })

    return sub_chapters


def group_chapters(chapters: list[dict], target: int) -> list[list[dict]]:
    """将功能章节按目标行数贪心分组。"""
    groups: list[list[dict]] = []
    current: list[dict] = []
    current_size = 0

    for ch in chapters:
        if current and current_size + ch['lines'] > target:
            groups.append(current)
            current = [ch]
            current_size = ch['lines']
        else:
            current.append(ch)
            current_size += ch['lines']

    if current:
        groups.append(current)
    return groups


def merge_small_groups(groups: list[list[dict]], min_lines: int) -> list[list[dict]]:
    """将行数过少的模块合并到相邻模块。"""
    if len(groups) <= 1:
        return groups

    merged: list[list[dict]] = []
    i = 0
    while i < len(groups):
        g = groups[i]
        g_size = sum(c['lines'] for c in g)

        if g_size < min_lines and merged:
            merged[-1].extend(g)
        elif g_size < min_lines and i + 1 < len(groups):
            groups[i + 1] = g + groups[i + 1]
        else:
            merged.append(g)
        i += 1

    return merged


def main() -> int:
    setup_encoding()

    ap = argparse.ArgumentParser(description='拆分大型需求 Markdown 文档为模块子文档')
    ap.add_argument('--config', required=True, help='JSON 配置文件路径')
    args = ap.parse_args()

    cfg = load_config(args.config)
    md_file    = Path(cfg['md_file'])
    output_dir = Path(cfg['output_dir'])
    target     = int(cfg.get('target_lines', 600))
    hard_max   = int(cfg.get('hard_max', 800))
    min_lines  = int(cfg.get('min_lines', 80))
    extra_kw   = cfg.get('shared_keywords', [])
    all_kw     = DEFAULT_SHARED_KEYWORDS + [kw for kw in extra_kw if kw not in DEFAULT_SHARED_KEYWORDS]

    manifest_path = output_dir / '_manifest.json'
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            mf = json.load(f)

        if md_file.exists() and 'source_hash' in mf:
            current_hash = file_md5(md_file)
            if current_hash != mf['source_hash']:
                print(f'⚠️ 源文件已变更（hash 不匹配），拆分产物可能过期。')
                print(f'  记录: {mf["source_hash"][:12]}...  当前: {current_hash[:12]}...')
                print(f'  若需重新拆分，请删除 {output_dir} 目录后重新执行。')

        print(f'[跳过] 拆分清单已存在，共 {mf["module_count"]} 个模块：')
        for m in mf['modules']:
            ch_desc = ' + '.join(m['chapters'][:3])
            print(f'  模块 {m["index"]:02d}: {ch_desc} ({m["total_lines"]} 行) → {m["filename"]}')
        return 0

    if not md_file.exists():
        print(f'错误：源文件不存在: {md_file}', file=sys.stderr)
        return 1

    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    total = len(lines)

    if total <= hard_max:
        print(f'[跳过] 文档共 {total} 行，未超过阈值（{hard_max} 行），无需拆分。')
        return 0

    source_hash = file_md5(md_file)

    headers = parse_headers(lines, min_level=1, max_level=2)
    if not headers:
        print(f'[警告] 文档共 {total} 行，未发现 H1/H2 标题，无法自动拆分。\n'
              f'       请手动将文档拆分后放入 {output_dir}，并创建 _manifest.json。')
        return 1

    chapters: list[dict] = []
    for i, h in enumerate(headers):
        start = h['line']
        end   = headers[i + 1]['line'] if i + 1 < len(headers) else total
        chapters.append({
            'title':  h['title'],
            'level':  h['level'],
            'start':  start,
            'end':    end,
            'lines':  end - start,
            'shared': is_shared(h['title'], all_kw),
        })

    shared_chs = [c for c in chapters if c['shared']]
    func_chs   = [c for c in chapters if not c['shared']]

    expanded_func: list[dict] = []
    h3_split_notes: list[str] = []
    for ch in func_chs:
        if ch['lines'] > hard_max:
            subs = split_large_chapter(ch, lines, target)
            if len(subs) > 1:
                h3_split_notes.append(
                    f'「{ch["title"]}」({ch["lines"]}行) 按 H3 拆为 {len(subs)} 段')
                expanded_func.extend(subs)
            else:
                expanded_func.append(ch)
        else:
            expanded_func.append(ch)
    func_chs = expanded_func

    shared_lines: list[str] = []
    for c in shared_chs:
        shared_lines.extend(lines[c['start']:c['end']])

    output_dir.mkdir(parents=True, exist_ok=True)

    if shared_lines:
        shared_path = output_dir / '_shared_prefix.md'
        with open(shared_path, 'w', encoding='utf-8') as f:
            f.writelines(shared_lines)
        print(f'共享前置: {len(shared_chs)} 个章节，{len(shared_lines)} 行 → _shared_prefix.md')
        shared_titles = '、'.join(c['title'] for c in shared_chs)
        print(f'  章节：{shared_titles}')
    else:
        print('未识别到共享前置章节（如有需要可在 shared_keywords 中追加关键词）')

    if not func_chs:
        print('[警告] 所有章节均被识别为共享前置，没有功能章节可拆分。')
        return 1

    groups = group_chapters(func_chs, target)
    groups = merge_small_groups(groups, min_lines)

    modules: list[dict] = []
    print(f'\n拆分方案（{len(groups)} 个模块）：')

    for idx, group in enumerate(groups, 1):
        ch_names  = [c['title'] for c in group]
        safe_name = sanitize('_'.join(ch_names[:2]))
        filename  = f'{idx:02d}_{safe_name}.md'
        filepath  = output_dir / filename

        module_content: list[str] = []
        if shared_lines:
            module_content.extend(shared_lines)
            module_content.append('\n\n---\n\n')
        for c in group:
            module_content.extend(lines[c['start']:c['end']])

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(module_content)

        func_line_count    = sum(c['lines'] for c in group)
        total_module_lines = len(shared_lines) + func_line_count
        desc = ' + '.join(ch_names)
        print(f'  模块 {idx:02d}: {desc}')
        print(f'          功能章节 {func_line_count} 行，含共享前置共 {total_module_lines} 行 → {filename}')

        modules.append({
            'index':      idx,
            'filename':   filename,
            'chapters':   ch_names,
            'func_lines': func_line_count,
            'total_lines': total_module_lines,
        })

    notes_parts = []
    if h3_split_notes:
        notes_parts.append('H3 二次拆分: ' + '; '.join(h3_split_notes))

    manifest = {
        'source_file':             str(md_file),
        'source_hash':             source_hash,
        'total_lines':             total,
        'split_time':              datetime.now().strftime('%Y-%m-%d %H:%M'),
        'target_lines_per_module': target,
        'hard_max':                hard_max,
        'min_lines_merge':         min_lines,
        'has_shared_prefix':       bool(shared_lines),
        'shared_line_count':       len(shared_lines),
        'module_count':            len(modules),
        'modules':                 modules,
    }
    if notes_parts:
        manifest['split_note'] = '；'.join(notes_parts)

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f'\n[完成] 拆分完毕，清单已写入: {manifest_path}')
    if h3_split_notes:
        print(f'[备注] {"; ".join(h3_split_notes)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
