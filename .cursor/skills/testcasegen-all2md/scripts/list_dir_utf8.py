# -*- coding: utf-8 -*-
"""
列出目录下的文件（支持中文路径）。

用于 testcasegen-all2md：当输入为目录且路径含中文时，Glob/Shell 列目录可能失败，
通过本脚本 + 配置文件（路径写在 JSON 中）列目录，结果写入无中文的临时文件供读取。

用法：
  python list_dir_utf8.py --config <config.json>

配置文件格式（JSON，UTF-8）：
  {
    "dir": "<要列出的目录绝对路径>",
    "out": "<结果输出文件绝对路径，建议在临时目录>",
    "extensions": [".docx", ".doc", ".xlsx", ".xls"]
  }
  extensions 为空或不写则不过滤扩展名。
"""
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("用法: python list_dir_utf8.py --config <config.json>")
    sys.exit(1)
if sys.argv[1] != "--config" or len(sys.argv) < 3:
    print("用法: python list_dir_utf8.py --config <config.json>")
    sys.exit(1)

config_path = Path(sys.argv[2])
with config_path.open("r", encoding="utf-8") as f:
    cfg = json.load(f)

dir_path = Path(cfg["dir"])
out_path = Path(cfg["out"])
extensions = cfg.get("extensions") or []  # 空则不过滤
ext_set = {e.lower() for e in extensions} if extensions else None

if not dir_path.is_dir():
    lines = [f"ERROR: 不是目录或不存在: {dir_path}"]
else:
    lines = []
    for p in sorted(dir_path.iterdir()):
        if p.is_file():
            if ext_set is None or p.suffix.lower() in ext_set:
                lines.append(p.name)

out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text("\n".join(lines), encoding="utf-8")
print(f"已写入 {len(lines)} 个文件名到: {out_path}")
