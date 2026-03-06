# -*- coding: utf-8 -*-
"""
Excel转Markdown工具
将Excel文件的每个sheet页转换为Markdown格式文档
支持 --config 配置文件，兼容中文路径与跨平台。
"""

import argparse
import json
import pandas as pd
import os
import sys
from pathlib import Path


def clean_cell_value(value):
    """清理单元格值，处理NaN和特殊字符"""
    if pd.isna(value):
        return ""
    # 转换为字符串
    value = str(value)
    # 处理换行符，将其替换为<br>标签以保持表格格式
    value = value.replace('\n', '<br>')
    # 处理管道符，这是Markdown表格的分隔符
    value = value.replace('|', '\\|')
    return value.strip()


def dataframe_to_markdown(df, sheet_name):
    """将DataFrame转换为Markdown表格格式"""
    if df.empty:
        return f"## {sheet_name}\n\n*该sheet页为空*\n\n"
    
    # 清理列名
    columns = [clean_cell_value(col) for col in df.columns]
    
    # 构建Markdown表格
    md_lines = []
    md_lines.append(f"## {sheet_name}\n")
    
    # 表头
    header = "| " + " | ".join(columns) + " |"
    md_lines.append(header)
    
    # 分隔行
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    md_lines.append(separator)
    
    # 数据行
    for _, row in df.iterrows():
        cells = [clean_cell_value(cell) for cell in row]
        row_line = "| " + " | ".join(cells) + " |"
        md_lines.append(row_line)
    
    md_lines.append("\n")  # 添加空行分隔不同sheet
    
    return "\n".join(md_lines)


def convert_excel_to_markdown(excel_path, output_path=None, single_file=True):
    """
    将Excel文件转换为Markdown格式
    
    参数:
        excel_path: Excel文件路径
        output_path: 输出路径（文件或目录）
        single_file: 是否输出为单个文件，False则每个sheet输出一个文件
    """
    excel_path = Path(excel_path)
    
    if not excel_path.exists():
        print(f"错误：文件不存在 - {excel_path}")
        return False
    
    print(f"正在读取Excel文件: {excel_path}")
    
    try:
        # 读取所有sheet页
        xlsx = pd.ExcelFile(excel_path)
        sheet_names = xlsx.sheet_names
        print(f"发现 {len(sheet_names)} 个sheet页: {sheet_names}")
        
        all_markdown_content = []
        all_markdown_content.append(f"# {excel_path.stem}\n\n")
        all_markdown_content.append(f"*源文件: {excel_path.name}*\n\n")
        all_markdown_content.append(f"---\n\n")
        
        # 添加目录
        all_markdown_content.append("## 目录\n\n")
        for i, sheet_name in enumerate(sheet_names, 1):
            # 创建锚点链接
            anchor = sheet_name.replace(' ', '-').lower()
            all_markdown_content.append(f"{i}. [{sheet_name}](#{anchor})\n")
        all_markdown_content.append("\n---\n\n")
        
        # 处理每个sheet
        for sheet_name in sheet_names:
            print(f"  正在处理sheet: {sheet_name}")
            
            try:
                # 读取sheet，保留所有数据
                df = pd.read_excel(xlsx, sheet_name=sheet_name, header=0)
                
                # 删除完全空白的行
                df = df.dropna(how='all')
                
                # 转换为Markdown
                md_content = dataframe_to_markdown(df, sheet_name)
                
                if single_file:
                    all_markdown_content.append(md_content)
                else:
                    # 每个sheet单独输出
                    if output_path:
                        output_dir = Path(output_path)
                    else:
                        output_dir = excel_path.parent
                    
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 清理文件名
                    safe_sheet_name = "".join(c for c in sheet_name if c.isalnum() or c in (' ', '-', '_')).strip()
                    sheet_output_path = output_dir / f"{safe_sheet_name}.md"
                    
                    with open(sheet_output_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {sheet_name}\n\n")
                        f.write(f"*源文件: {excel_path.name}*\n\n")
                        f.write("---\n\n")
                        f.write(md_content)
                    
                    print(f"    已保存: {sheet_output_path}")
                    
            except Exception as e:
                print(f"    警告：处理sheet '{sheet_name}' 时出错: {e}")
                all_markdown_content.append(f"## {sheet_name}\n\n*处理此sheet时出错: {e}*\n\n")
        
        if single_file:
            # 输出到单个文件
            if output_path:
                output_file = Path(output_path)
            else:
                output_file = excel_path.with_suffix('.md')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("".join(all_markdown_content))
            
            print(f"\n转换完成！输出文件: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"错误：读取Excel文件失败 - {e}")
        import traceback
        traceback.print_exc()
        return False


def load_config(config_path):
    """从 JSON 配置文件加载参数（UTF-8），用于兼容中文路径"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """主函数：支持命令行参数或 --config 配置文件"""
    parser = argparse.ArgumentParser(description="Excel 转 Markdown")
    parser.add_argument("--config", type=str, help="配置文件路径（JSON），含 excel、out、single_file")
    parser.add_argument("--excel", type=str, help="Excel 文件路径")
    parser.add_argument("--out", type=str, default=None, help="输出文件或目录路径")
    parser.add_argument("--multi", action="store_true", help="每个 sheet 输出一个文件")
    parser.add_argument("excel_positional", nargs="?", help="Excel 路径（位置参数）")
    parser.add_argument("out_positional", nargs="?", help="输出路径（位置参数）")
    args = parser.parse_args()

    excel_path = None
    output_path = None
    single_file = True

    if args.config:
        cfg = load_config(args.config)
        excel_path = cfg.get("excel")
        output_path = cfg.get("out")
        single_file = cfg.get("single_file", True)
        if not excel_path:
            print("错误：配置文件中缺少 excel 路径")
            sys.exit(1)
    elif args.excel or args.excel_positional:
        excel_path = args.excel or args.excel_positional
        output_path = args.out or args.out_positional
        single_file = not args.multi
    else:
        # 兼容旧用法：仅位置参数
        default_excel = r"e:\cursorProjects\test\02_紫金项目\V3.12.0\票交所报送接口字段(3).xlsx"
        excel_path = sys.argv[1] if len(sys.argv) > 1 else default_excel
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        single_file = True
        if len(sys.argv) > 3 and sys.argv[3].lower() == "multi":
            single_file = False

    print("=" * 60)
    print("Excel 转 Markdown 工具")
    print("=" * 60)
    print()

    success = convert_excel_to_markdown(excel_path, output_path, single_file)

    if success:
        print("\n转换成功！")
    else:
        print("\n转换失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
