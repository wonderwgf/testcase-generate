#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
XMind测试用例生成器
遵循规则：04-testcase-xmind.mdc

功能：
- 直接解析 .md 格式的详细测试用例文件生成 XMind
- 支持新的目录层级：所属模块 > 功能名称 > 场景分类 > 用例
- 支持目录自动合并和重复检测
- 支持Story ID标签和前置条件备注
- 默认逻辑图向右布局
- 自动识别优先级（从 .md 文件中读取）

依赖：pip install xmind

使用方式：
1. 命令行：python generate_test_cases_xmind.py <md文件路径> [输出目录]
2. 代码调用：create_xmind_from_md("详细测试用例.md", "输出目录")

目录层级说明：
- ## 所属模块（如：变更额度页面）
- ### 功能名称（如：计算额度小工具）
- #### 场景分类（如：正常场景）
- ##### 用例标题（如：R1-B01 验证xxx）
"""

import os
import sys
import re
from typing import List, Dict, Optional, Tuple


# ============================================================
# 常量定义
# ============================================================

# 正则表达式
RE_CASE_ID = re.compile(r'^([A-Z]\d+-[A-Z]\d+)\s+(.+)$')
RE_STEP_NUMBER = re.compile(r'^\s*(\d+)\.\s*(.+)$')
RE_VERSION = re.compile(r'^V\d+', re.IGNORECASE)
RE_PRODUCT_VERSION = re.compile(r'(.+?)[_]?(V\d+\.\d+(?:\.\d+)?)', re.IGNORECASE)

# 优先级映射
PRIORITY_MAP = {'P1': 1, 'P2': 2, 'P3': 3, 'P4': 4, '1': 1, '2': 2, '3': 3, '4': 4}

# 排除的目录名
EXCLUDE_DIR_NAMES = {'测试系统', '测试用例', '需求文档', '技术文档', '.', '..'}


# ============================================================
# 主入口：从 .md 文件生成 XMind
# ============================================================

def create_xmind_from_md(md_file_path, output_dir=None, custom_path=None):
    """
    从 .md 格式的详细测试用例文件直接生成 XMind
    
    参数：
        md_file_path (str): .md 文件路径
        output_dir (str): 输出目录，默认与 .md 文件同目录
        custom_path (str): XMind 内部结构，默认从文件名自动提取
    
    示例：
        create_xmind_from_md("额度服务V1.3.0版本_详细测试用例.md")
        create_xmind_from_md("详细测试用例.md", output_dir="测试系统/额度管理/V1.3.0")
    """
    
    if not os.path.exists(md_file_path):
        print("错误: 文件不存在: {}".format(md_file_path))
        return
    
    if output_dir is None:
        output_dir = _resolve_output_dir(md_file_path)
    print("\n" + "=" * 60)
    print("解析 Markdown 测试用例文件")
    print("=" * 60)
    print("输入文件: {}".format(md_file_path))
    
    # 1. 解析 .md 文件（新版本，支持5级标题）
    all_cases = parse_md_testcase_file_v2(md_file_path)
    
    if not all_cases:
        print("错误: 未找到有效的测试用例")
        return
    
    # 2. 确定输出目录
    if not output_dir:
        output_dir = os.path.dirname(md_file_path) or "."
    
    # 3. 从文件名提取产品名和版本号
    filename = os.path.basename(md_file_path)
    product_name, version = _extract_product_version_from_filename(filename)
    
    # 4. 生成 custom_path（根节点标题，优先包含功能概述或版本号）
    if not custom_path:
        if product_name and version:
            custom_path = "{}{}".format(product_name, version)
        elif product_name:
            custom_path = product_name
        else:
            # 无版本号时：优先从 md 文件第一行 # 标题提取，否则用文件名（去掉 .md）
            custom_path = _extract_root_title_from_md(md_file_path) or os.path.splitext(filename)[0]
    
    # 5. 统计信息
    print("\n解析完成:")
    print("   用例数: {}".format(len(all_cases)))
    
    print("\n生成 XMind 文件...")
    
    # 6. 一次性生成所有用例
    output_filename_hint = None
    if product_name and version:
        output_filename_hint = "{}{}测试用例.xmind".format(product_name, version)
    elif filename:
        output_filename_hint = os.path.splitext(filename)[0] + ".xmind"

    create_xmind_file_v2(
        all_cases,
        output_dir=output_dir,
        custom_path=custom_path,
        output_filename_hint=output_filename_hint
    )
    
    # 7. 打印统计
    _print_statistics_v2(all_cases)


def parse_md_testcase_file_v2(md_file_path: str) -> List[Dict]:
    """
    解析 .md 格式的详细测试用例文件（支持4级目录层级）

    目录结构：
        ## 所属模块 > ### 功能名称 > #### 场景分类 > ##### 用例标题

    返回：
        list: 测试用例列表，每个用例包含完整层级路径
    """
    with open(md_file_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    all_cases = []
    # 当前层级上下文
    ctx = {'module': None, 'feature': None, 'category': None}
    current_case = None
    current_field = None

    def save_case():
        """保存当前用例到列表"""
        nonlocal current_case
        if current_case:
            all_cases.append(current_case)
            current_case = None

    def create_case(case_title: str) -> Dict:
        """创建新用例"""
        # 提取用例ID
        match = RE_CASE_ID.match(case_title)
        case_id = match.group(1) if match else ''
        title = match.group(2).strip() if match else case_title

        # 构建完整层级路径
        parts = [v for v in [ctx['module'], ctx['feature'], ctx['category']] if v]
        parts.append(title)

        return {
            'id': case_id,
            'title': '-'.join(parts),
            'module': ctx['module'] or '',
            'feature': ctx['feature'] or '',
            'category': ctx['category'] or '',
            'case_title': title,
            'priority': 2,
            'precondition': '',
            'steps': [],
            'expected_list': []
        }

    for line in lines:
        stripped = line.strip()

        # 跳过空行和分隔线
        if not stripped or stripped == '---':
            continue

        # 解析各级标题
        if _is_heading(stripped, 2):
            save_case()
            ctx['module'] = _get_heading_content(stripped, 2)
            ctx['feature'] = ctx['category'] = None
            current_field = None
            continue

        if _is_heading(stripped, 3):
            save_case()
            ctx['feature'] = _get_heading_content(stripped, 3)
            ctx['category'] = None
            current_field = None
            continue

        if _is_heading(stripped, 4):
            save_case()
            ctx['category'] = _get_heading_content(stripped, 4)
            current_field = None
            continue

        if _is_heading(stripped, 5):
            save_case()
            current_case = create_case(_get_heading_content(stripped, 5))
            current_field = None
            continue

        # 解析用例内容
        if current_case:
            if stripped.startswith('- 前置：') or stripped.startswith('- 前置:'):
                current_case['precondition'] = _parse_field_value(stripped, '- 前置')
                current_field = None
            elif stripped.startswith('- 操作：') or stripped.startswith('- 操作:'):
                current_field = 'steps'
            elif stripped.startswith('- 预期：') or stripped.startswith('- 预期:'):
                current_field = 'expected'
            elif stripped.startswith('- 优先级：') or stripped.startswith('- 优先级:'):
                current_case['priority'] = _parse_priority(
                    _parse_field_value(stripped, '- 优先级')
                )
                current_field = None
            elif stripped.startswith('- ') and not stripped.startswith('-  '):
                current_field = None
            else:
                # 解析编号列表内容
                match = RE_STEP_NUMBER.match(stripped)
                if match and current_field:
                    content = match.group(2).strip()
                    if current_field == 'steps':
                        current_case['steps'].append(content)
                    elif current_field == 'expected':
                        current_case['expected_list'].append(content)

    save_case()
    return all_cases


def _extract_product_version_from_filename(filename: str) -> Tuple[Optional[str], Optional[str]]:
    """从文件名提取产品名和版本号"""
    match = RE_PRODUCT_VERSION.search(filename)
    return (match.group(1), match.group(2)) if match else (None, None)


def _extract_root_title_from_md(md_file_path: str) -> Optional[str]:
    """从 md 文件第一行 # 标题提取根节点标题（功能概述）"""
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('# ') and not stripped.startswith('## '):
                    return stripped[2:].strip()
                if stripped:
                    break
    except Exception:
        pass
    return None


def _parse_priority(priority_str: str) -> int:
    """解析优先级字符串，默认返回 P2"""
    priority_str = priority_str.upper().strip()
    for key, value in PRIORITY_MAP.items():
        if key in priority_str:
            return value
    return 2


def _parse_field_value(line: str, prefix: str) -> str:
    """解析字段值，支持中英文冒号"""
    if '：' in line:
        return line.split('：', 1)[-1].strip()
    elif ':' in line:
        return line.split(':', 1)[-1].strip()
    return line[len(prefix):].strip()


def _is_heading(line: str, level: int) -> bool:
    """检查是否为指定级别的标题"""
    prefix = '#' * level + ' '
    next_prefix = '#' * (level + 1) + ' '
    return line.startswith(prefix) and not line.startswith(next_prefix)


def _get_heading_content(line: str, level: int) -> str:
    """获取标题内容"""
    return line[level + 1:].strip()


def _print_statistics_v2(all_cases: List[Dict]):
    """打印统计信息"""
    print("\n" + "=" * 60)
    print("测试用例统计")
    print("=" * 60)
    
    # 按模块和功能统计
    module_stats = {}
    p1_count = p2_count = p3_count = p4_count = 0
    
    for tc in all_cases:
        module = tc.get('module', '未分类')
        feature = tc.get('feature', '未分类')
        key = "{} > {}".format(module, feature)
        
        if key not in module_stats:
            module_stats[key] = 0
        module_stats[key] += 1
        
        priority = tc.get('priority', 2)
        if priority == 1:
            p1_count += 1
        elif priority == 2:
            p2_count += 1
        elif priority == 3:
            p3_count += 1
        else:
            p4_count += 1
    
    for key, count in module_stats.items():
        print("   {}: {} 条".format(key, count))
    
    print("   {}".format('─' * 40))
    print("   总计: {} 条".format(len(all_cases)))
    
    print("\n优先级分布:")
    total = len(all_cases)
    if total > 0:
        print("   P1 高: {} 条 ({:.1f}%)".format(p1_count, p1_count/total*100))
        print("   P2 中: {} 条 ({:.1f}%)".format(p2_count, p2_count/total*100))
        print("   P3 低: {} 条 ({:.1f}%)".format(p3_count, p3_count/total*100))
        if p4_count > 0:
            print("   P4 可选: {} 条 ({:.1f}%)".format(p4_count, p4_count/total*100))


def _resolve_output_dir(md_file_path: str) -> str:
    """解析默认输出目录：output/test_cases -> output/xmind"""
    md_dir = os.path.dirname(md_file_path)
    if not md_dir:
        return "."
    normalized = md_dir.replace('\\', '/')
    marker = '/output/test_cases'
    if marker in normalized:
        base = normalized.split(marker)[0].rstrip('/')
        return os.path.join(base, 'output', 'xmind')
    return md_dir


# ============================================================
# XMind 生成：一次性生成所有用例，避免重复
# ============================================================

def create_xmind_file_v2(test_cases, output_dir=None, custom_path=None, output_filename_hint=None):
    """
    创建 XMind 测试用例文件（新版本，一次性生成）
    
    参数：
        test_cases: 测试用例列表，title 格式为 "模块-功能-场景-用例名"
        output_dir: 输出目录
        custom_path: XMind 根节点名称
    """
    try:
        import xmind
        from xmind.core.markerref import MarkerId
    except ImportError:
        print("错误：未安装xmind库")
        print("请运行：pip install xmind")
        sys.exit(1)
    
    # 1. 生成输出文件路径
    output_file = _generate_output_path(output_dir, output_filename_hint)
    
    # 2. 创建新工作簿（覆盖旧文件）
    workbook = xmind.load(output_file)
    sheet = workbook.getPrimarySheet()
    root_topic = sheet.getRootTopic()
    
    # 3. 设置逻辑图向右布局
    _set_logic_right_layout(sheet, root_topic)
    
    # 4. 设置根节点标题
    root_topic.setTitle(custom_path or "测试用例")
    
    # 5. 使用缓存避免重复创建节点
    node_cache = {}
    category_nodes = set()  # 记录已添加任务标记的场景分类节点
    
    for tc in test_cases:
        title = tc.get('title', '')
        priority = tc.get('priority', 2)
        precondition = tc.get('precondition', '')
        steps = tc.get('steps', [])
        expected_list = tc.get('expected_list', [])
        
        # 解析标题层级：模块-功能-场景-用例名
        title_parts = [p.strip() for p in title.split('-') if p.strip()]
        if len(title_parts) < 2:
            continue
        
        # 构建节点层级
        current = root_topic
        current_path = custom_path or "测试用例"
        
        # 创建中间层级（模块、功能、场景分类）
        for i, part in enumerate(title_parts[:-1]):
            current_path = "{}/{}".format(current_path, part)
            
            if current_path in node_cache:
                current = node_cache[current_path]
            else:
                # 创建新节点
                new_topic = current.addSubTopic()
                new_topic.setTitle(part)
                _set_topic_layout(new_topic)
                
                # 第三级（场景分类，对应 #### 标题）添加任务完成标记
                if i == 2 and current_path not in category_nodes:
                    new_topic.addMarker(MarkerId.task8_8)
                    category_nodes.add(current_path)
                
                node_cache[current_path] = new_topic
                current = new_topic
        
        # 创建用例节点（最后一级，不复用）
        case_title = title_parts[-1]
        case_topic = current.addSubTopic()
        case_topic.setTitle(case_title)
        _set_topic_layout(case_topic)
        
        # 添加优先级标记
        _add_priority_marker(case_topic, priority, MarkerId)
        
        # 添加前置条件备注
        if precondition:
            try:
                case_topic.setPlainNotes("前置条件：{}".format(precondition))
            except Exception:
                pass
        
        # 添加测试步骤和预期结果
        for j, step in enumerate(steps):
            step_topic = case_topic.addSubTopic()
            step_topic.setTitle(step)
            _set_topic_layout(step_topic)
            
            # 添加对应的预期结果
            if j < len(expected_list):
                expected_topic = step_topic.addSubTopic()
                expected_topic.setTitle(expected_list[j])
                _set_topic_layout(expected_topic)
    
    # 6. 保存文件
    xmind.save(workbook, output_file)
    print("XMind文件已生成: {}".format(output_file))


# ============================================================
# 原有功能：保留兼容性
# ============================================================

def parse_md_testcase_file(md_file_path):
    """
    解析 .md 格式的详细测试用例文件（旧版本，兼容3级标题）
    """
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modules = []
    current_module = None
    current_category = None
    current_case = None
    current_field = None
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if not stripped or stripped == '---':
            i += 1
            continue
        
        if stripped.startswith('## ') and not stripped.startswith('### '):
            if current_case and current_module:
                current_module['test_cases'].append(current_case)
                current_case = None
            
            module_match = re.match(r'^##\s+(R\d+)\s*[-–—]\s*(.+)$', stripped)
            if module_match:
                current_module = {
                    'id': module_match.group(1),
                    'name': module_match.group(2).strip(),
                    'test_cases': []
                }
                modules.append(current_module)
                current_category = None
                current_field = None
            i += 1
            continue
        
        if stripped.startswith('### ') and not stripped.startswith('#### '):
            if current_case and current_module:
                current_module['test_cases'].append(current_case)
                current_case = None
            
            current_category = stripped[4:].strip()
            current_field = None
            i += 1
            continue
        
        if stripped.startswith('#### '):
            if current_case and current_module:
                current_module['test_cases'].append(current_case)
            
            case_match = re.match(r'^####\s+([A-Z]\d+-[A-Z]\d+)\s+(.+)$', stripped)
            if case_match:
                case_id = case_match.group(1)
                case_title = case_match.group(2).strip()
                
                current_case = {
                    'id': case_id,
                    'title': case_title,
                    'category': current_category or '',
                    'priority': 2,
                    'precondition': '',
                    'steps': [],
                    'expected_list': []
                }
            else:
                case_title = stripped[5:].strip()
                current_case = {
                    'id': '',
                    'title': case_title,
                    'category': current_category or '',
                    'priority': 2,
                    'precondition': '',
                    'steps': [],
                    'expected_list': []
                }
            current_field = None
            i += 1
            continue
        
        if current_case:
            if stripped.startswith('- 前置：') or stripped.startswith('- 前置:'):
                current_case['precondition'] = stripped[5:].strip()
                current_field = None
                i += 1
                continue
            
            if stripped.startswith('- 操作：') or stripped.startswith('- 操作:'):
                current_field = 'steps'
                i += 1
                continue
            
            if stripped.startswith('- 预期：') or stripped.startswith('- 预期:'):
                current_field = 'expected'
                i += 1
                continue
            
            if stripped.startswith('- 优先级：') or stripped.startswith('- 优先级:'):
                priority_str = stripped.split('：')[-1].strip() if '：' in stripped else stripped.split(':')[-1].strip()
                current_case['priority'] = _parse_priority(priority_str)
                current_field = None
                i += 1
                continue
            
            if stripped.startswith('- ') and not stripped.startswith('-  '):
                current_field = None
                i += 1
                continue
            
            step_match = re.match(r'^\s*(\d+)\.\s*(.+)$', stripped)
            if step_match:
                content_text = step_match.group(2).strip()
                if current_field == 'steps':
                    current_case['steps'].append(content_text)
                elif current_field == 'expected':
                    current_case['expected_list'].append(content_text)
        
        i += 1
    
    if current_case and current_module:
        current_module['test_cases'].append(current_case)
    
    return modules


def create_xmind_file(test_cases, output_dir=None, custom_path=None,
                      story_id=None, clear_duplicates=True):
    """创建XMind测试用例文件（原版本，保留兼容性）"""
    try:
        import xmind
        from xmind.core.markerref import MarkerId
    except ImportError:
        print("错误：未安装xmind库")
        print("请运行：pip install xmind")
        sys.exit(1)
    
    output_file = _generate_output_path(output_dir)
    workbook, root_topic = _load_or_create_workbook(
        xmind, output_file, custom_path, clear_duplicates
    )
    sheet = workbook.getPrimarySheet()
    _set_logic_right_layout(sheet, root_topic)
    base_parent = _build_directory_structure(root_topic, custom_path, story_id)
    _generate_test_cases(base_parent, test_cases, xmind, MarkerId)
    xmind.save(workbook, output_file)
    print("XMind文件已生成: {}".format(output_file))


def _generate_output_path(output_dir: str, filename_hint: Optional[str] = None) -> str:
    """生成输出文件路径"""
    if not output_dir:
        return "测试用例.xmind"

    os.makedirs(output_dir, exist_ok=True)
    parts = output_dir.replace('\\', '/').split('/')

    product_name = None
    version = None

    for part in parts:
        part = part.strip()
        if not part or part in EXCLUDE_DIR_NAMES:
            continue
        if re.match(r'^[A-Za-z]:$', part):
            continue
        if RE_VERSION.match(part):
            version = part
        elif not product_name:
            product_name = part

    # 生成文件名
    if filename_hint:
        filename = filename_hint
    elif product_name and version:
        filename = "{}{}测试用例.xmind".format(product_name, version)
    elif product_name:
        filename = "{}测试用例.xmind".format(product_name)
    else:
        filename = "测试用例.xmind"

    output_file = os.path.join(output_dir, filename)
    print("输出文件: {}".format(filename))
    return output_file


def _load_or_create_workbook(xmind_module, output_file, custom_path, clear_duplicates):
    """加载现有工作簿或创建新的"""
    file_exists = os.path.exists(output_file)
    if file_exists and clear_duplicates and custom_path:
        workbook = _try_clear_duplicates(xmind_module, output_file, custom_path)
        if workbook:
            sheet = workbook.getPrimarySheet()
            return workbook, sheet.getRootTopic()
    workbook = xmind_module.load(output_file)
    sheet = workbook.getPrimarySheet()
    return workbook, sheet.getRootTopic()


def _try_clear_duplicates(xmind_module, output_file, custom_path):
    """尝试清除重复的测试用例目录"""
    try:
        workbook = xmind_module.load(output_file)
        sheet = workbook.getPrimarySheet()
        root = sheet.getRootTopic()
        path_parts = _parse_path(custom_path)
        target_node = _find_path_node(root, path_parts)
        if target_node:
            print("警告: 检测到重复目录：{}".format(custom_path))
            print("警告: 正在清除旧记录...")
            for subtopic in list(target_node.getSubTopics()):
                target_node.removeChild(subtopic)
            print("已清除重复记录")
            return workbook
    except Exception as exc:
        print("警告: 无法读取现有文件：{}".format(exc))
    return None


def _parse_path(path):
    """解析路径，支持 / 或 - 分隔符"""
    separator = '/' if '/' in path else '-'
    return [part.strip() for part in path.split(separator) if part.strip()]


def _find_path_node(root, path_parts):
    """查找路径对应的节点"""
    if not path_parts or root.getTitle() != path_parts[0]:
        return None
    current = root
    for part in path_parts[1:]:
        found = False
        for subtopic in current.getSubTopics():
            if subtopic.getTitle() == part:
                current = subtopic
                found = True
                break
        if not found:
            return None
    return current


def _set_logic_right_layout(sheet, root_topic):
    """设置逻辑图向右布局"""
    def set_layout(element):
        try:
            impl = element.getImplementation()
            if hasattr(impl, 'setAttribute'):
                impl.setAttribute('structure-class', 'org.xmind.ui.logic.right')
        except Exception:
            pass
    set_layout(sheet)
    set_layout(root_topic)


def _build_directory_structure(root_topic, custom_path, story_id):
    """构建目录结构并返回基准父节点"""
    if not custom_path:
        root_topic.setTitle("测试用例")
        return root_topic
    path_parts = _parse_path(custom_path)
    if not path_parts:
        root_topic.setTitle("测试用例")
        return root_topic
    root_topic.setTitle(path_parts[0])
    current = root_topic
    for part in path_parts[1:]:
        current = _get_or_create_subtopic(current, part)
    if story_id:
        try:
            current.addLabel(story_id)
            print("已添加Story标签: {}".format(story_id))
        except Exception as exc:
            print("警告: 添加Story标签失败: {}".format(exc))
    return current


def _get_or_create_subtopic(parent, title):
    """获取或创建子主题"""
    for subtopic in parent.getSubTopics():
        if subtopic.getTitle() == title:
            return subtopic
    subtopic = parent.addSubTopic()
    subtopic.setTitle(title)
    _set_topic_layout(subtopic)
    return subtopic


def _set_topic_layout(topic):
    """设置主题布局为逻辑图向右"""
    try:
        impl = topic.getImplementation()
        if hasattr(impl, 'setAttribute'):
            impl.setAttribute('structure-class', 'org.xmind.ui.logic.right')
    except Exception:
        pass


def _generate_test_cases(base_parent, test_cases_list, xmind_module, marker_id):
    """生成测试用例内容"""
    marked_topics = set()
    for test_case in test_cases_list:
        _create_test_case(base_parent, test_case, marked_topics, marker_id)


def _create_test_case(parent, test_case, marked_topics, marker_id):
    """创建单个测试用例"""
    title = test_case.get('title', '')
    priority = test_case.get('priority')
    precondition = test_case.get('precondition')
    steps = test_case.get('steps', [])

    title_parts = [p.strip() for p in title.split('-') if p.strip()]
    if not title_parts:
        return

    current = parent
    path = []

    for i in range(len(title_parts) - 1):
        part = title_parts[i]
        path.append(part)
        path_key = '-'.join(path)

        found_topic = None
        for subtopic in current.getSubTopics():
            if subtopic.getTitle() == part:
                found_topic = subtopic
                break

        if found_topic:
            current = found_topic
        else:
            topic = current.addSubTopic()
            topic.setTitle(part)
            _set_topic_layout(topic)
            if i == 0 and path_key not in marked_topics:
                topic.addMarker(marker_id.task8_8)
                marked_topics.add(path_key)
            current = topic

    if title_parts:
        last_part = title_parts[-1]
        last_topic = current.addSubTopic()
        last_topic.setTitle(last_part)
        _set_topic_layout(last_topic)
        if priority:
            _add_priority_marker(last_topic, priority, marker_id)
        current = last_topic

    if precondition:
        try:
            current.setPlainNotes("前置条件：{}".format(precondition))
        except Exception:
            pass

    for step_data in steps:
        _add_step_and_expected(current, step_data)


def _add_priority_marker(topic, priority, marker_id):
    """添加优先级标记"""
    markers = {
        1: marker_id.priority1,
        2: marker_id.priority2,
        3: marker_id.priority3,
        4: marker_id.priority4
    }
    if priority in markers:
        topic.addMarker(markers[priority])


def _add_step_and_expected(parent, step_data):
    """添加测试步骤和预期结果"""
    step = step_data.get('step', '')
    expected = step_data.get('expected', '')
    if not step:
        return
    step_topic = parent.addSubTopic()
    step_topic.setTitle(step)
    _set_topic_layout(step_topic)
    if expected:
        expected_topic = step_topic.addSubTopic()
        expected_topic.setTitle(expected)
        _set_topic_layout(expected_topic)


# ============================================================
# 命令行入口
# ============================================================

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("XMind 测试用例生成器")
        print("=" * 50)
        print("\n用法:")
        print("  python markdown_to_xmind.py <md文件路径> [输出目录]")
        print("  python markdown_to_xmind.py --path-file <路径文件> [输出目录]")
        print("\n示例:")
        print("  python markdown_to_xmind.py 详细测试用例.md")
        print("  python markdown_to_xmind.py 额度服务V1.3.0版本_详细测试用例.md output/xmind")
        print("  python markdown_to_xmind.py --path-file tmp_path.txt output/xmind")
        print("\n格式说明：")
        print("  - 目录层级：## 模块 > ### 功能 > #### 场景 > ##### 用例")
        print("  - 用例字段：- 前置 / - 操作 / - 预期 / - 优先级")
        return

    if sys.argv[1] == "--path-file":
        if len(sys.argv) < 3:
            print("错误: 缺少路径文件")
            return
        path_file = sys.argv[2]
        if not os.path.exists(path_file):
            print("错误: 路径文件不存在: {}".format(path_file))
            return
        with open(path_file, "r", encoding="utf-8") as f:
            md_file = f.readline().strip()
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        md_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(md_file):
        print("错误: 文件不存在: {}".format(md_file))
        return
    
    create_xmind_from_md(md_file, output_dir)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
        sys.exit(0)

    # ============================================================
    # 配置区域：修改以下参数来转换不同的文件
    # ============================================================

    # 优先读取路径文件（与脚本同级的 path.txt）
    default_path_file = os.path.join(os.path.dirname(__file__), "path.txt")
    if os.path.exists(default_path_file):
        with open(default_path_file, "r", encoding="utf-8") as f:
            md_file = f.readline().strip()
        output_dir = None
        create_xmind_from_md(md_file, output_dir)
        sys.exit(0)

    # Markdown 测试用例文件路径（必填）
    md_file = r"output\test_cases\示例_测试用例.md"

    # 输出目录（可选，留空则输出到 md_file 同级目录）
    output_dir = None

    # ============================================================

    create_xmind_from_md(md_file, output_dir)
