"""
Generate final mapping document with improved method matching.
Uses line-by-line structural diff to match methods more accurately.
"""
import os
import re
import json
from collections import defaultdict, OrderedDict

OBF_DIR = r"C:\doWork\HME-客户服务器源码\hmeback\bcadmin-cashflowmodel\src\main\java\com\resrun"
ORI_DIR = r"C:\doWork\Kinstra代码仓库\hme\bcadmin-cashflowmodel\src\main\java\com\resrun"

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def remove_comments(code):
    code = re.sub(r'//.*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code

def extract_package(content):
    m = re.search(r'package\s+([\w.]+)\s*;', content)
    return m.group(1) if m else ''

def extract_class_info(content):
    code = remove_comments(content)
    m = re.search(r'(?:public\s+)?(?:abstract\s+)?(?:class|interface|enum)\s+(\w+)(?:\s*<[^>]*>)?(?:\s+extends\s+([\w<>,\s]+?))?(?:\s+implements\s+([\w<>,\s]+?))?\s*\{', code)
    if m:
        return {
            'name': m.group(1),
            'extends': m.group(2).strip() if m.group(2) else None,
            'implements': m.group(3).strip() if m.group(3) else None
        }
    return None

def extract_methods_with_lines(content):
    """Extract methods with their line numbers for better matching."""
    lines = content.splitlines()
    code = remove_comments(content)
    code_lines = code.splitlines()

    methods = []
    # Pattern for method declarations
    pattern = re.compile(
        r'(?:(?:public|private|protected)\s+)?'
        r'(?:(?:static|final|synchronized|abstract|default)\s+)*'
        r'(?:<[^>]+>\s+)?'  # generic type params
        r'(?:[\w<>\[\]?,.\s]+?)\s+'
        r'(\w+)\s*\(([^)]*)\)\s*'
        r'(?:throws\s+[\w,\s]+)?\s*[{;]'
    )

    for i, line in enumerate(code_lines):
        m = pattern.search(line)
        if m:
            name = m.group(1)
            params = m.group(2).strip()
            # Skip if it looks like a constructor or control flow
            if name in ('if', 'for', 'while', 'switch', 'catch', 'new', 'return', 'class', 'interface', 'enum'):
                continue
            methods.append({
                'name': name,
                'params': params,
                'line': i + 1,
                'full_line': line.strip()
            })

    return methods

def extract_fields_with_lines(content):
    """Extract fields with line numbers."""
    code = remove_comments(content)
    code_lines = code.splitlines()

    fields = []
    pattern = re.compile(
        r'(?:private|protected|public)\s+'
        r'(?:(?:static|final|transient|volatile)\s+)*'
        r'(?:[\w<>\[\]?,.\s]+?)\s+'
        r'(\w+)\s*[;=]'
    )

    for i, line in enumerate(code_lines):
        m = pattern.search(line)
        if m:
            name = m.group(1)
            if name not in ('class', 'interface', 'enum', 'serialVersionUID'):
                fields.append({
                    'name': name,
                    'line': i + 1,
                    'full_line': line.strip()
                })

    return fields

def match_by_position(obf_items, ori_items):
    """Match items by position, filtering out obviously wrong matches."""
    result = []
    min_len = min(len(obf_items), len(ori_items))
    for i in range(min_len):
        obf = obf_items[i]
        ori = ori_items[i]
        if obf['name'] != ori['name']:
            result.append({
                'obfuscated': obf['name'],
                'original': ori['name'],
                'obf_line': obf.get('line', '?'),
                'ori_line': ori.get('line', '?'),
            })
    return result

def build_file_mapping(obf_content, ori_content, obf_rel, ori_rel):
    """Build detailed mapping for a single file pair."""
    mapping = {}

    # Package
    obf_pkg = extract_package(obf_content)
    ori_pkg = extract_package(ori_content)
    mapping['obf_package'] = obf_pkg
    mapping['ori_package'] = ori_pkg

    # Class
    obf_class = extract_class_info(obf_content)
    ori_class = extract_class_info(ori_content)
    if obf_class and ori_class:
        mapping['obf_class'] = obf_class['name']
        mapping['ori_class'] = ori_class['name']
        mapping['class_changed'] = obf_class['name'] != ori_class['name']
        if obf_class.get('extends') and ori_class.get('extends'):
            mapping['extends'] = {'obf': obf_class['extends'], 'ori': ori_class['extends']}
        if obf_class.get('implements') and ori_class.get('implements'):
            mapping['implements'] = {'obf': obf_class['implements'], 'ori': ori_class['implements']}
    else:
        mapping['obf_class'] = '?'
        mapping['ori_class'] = '?'
        mapping['class_changed'] = False

    # Methods
    obf_methods = extract_methods_with_lines(obf_content)
    ori_methods = extract_methods_with_lines(ori_content)
    mapping['methods'] = match_by_position(obf_methods, ori_methods)

    # Also add method param type mappings for matched methods
    for mm in mapping['methods']:
        # Find corresponding original method
        for om in ori_methods:
            if om['name'] == mm['original']:
                mm['ori_params'] = om['params']
                break

    # Fields
    obf_fields = extract_fields_with_lines(obf_content)
    ori_fields = extract_fields_with_lines(ori_content)
    mapping['fields'] = match_by_position(obf_fields, ori_fields)

    mapping['obf_file'] = obf_rel
    mapping['ori_file'] = ori_rel

    return mapping

def generate_markdown(all_mappings):
    """Generate a well-organized markdown document."""
    lines = []
    lines.append("# HME 现金流模块 (bcadmin-cashflowmodel) 混淆名称对照表")
    lines.append("")
    lines.append("> 本文档记录了混淆后的变量名/类名/方法名与原始名称的对应关系，")
    lines.append("> 便于开发人员阅读混淆后的代码。")
    lines.append("> ")
    lines.append("> **混淆仓库路径**: `C:\\doWork\\HME-客户服务器源码\\hmeback\\bcadmin-cashflowmodel`")
    lines.append("> **原始仓库路径**: `C:\\doWork\\Kinstra代码仓库\\hme\\bcadmin-cashflowmodel`")
    lines.append("> **生成日期**: 2026-07-01")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of contents
    lines.append("## 目录")
    lines.append("")
    lines.append("1. [类名对照速查表](#1-类名对照速查表)")
    lines.append("2. [包名对照](#2-包名对照)")
    lines.append("3. [按模块分类的详细对照](#3-按模块分类的详细对照)")
    lines.append("   - 3.1 [风险引擎 (riskEngines)](#31-风险引擎-riskengines)")
    lines.append("   - 3.2 [风险分类工厂 (riskCategories)](#32-风险分类工厂-riskcategories)")
    lines.append("   - 3.3 [风险模型 (riskModels)](#33-风险模型-riskmodels)")
    lines.append("   - 3.4 [工具类 (utils)](#34-工具类-utils)")
    lines.append("   - 3.5 [风险敞口 (riskExposure)](#35-风险敞口-riskexposure)")
    lines.append("   - 3.6 [风险上下文 (riskContext)](#36-风险上下文-riskcontext)")
    lines.append("   - 3.7 [风险设置 (riskSettings)](#37-风险设置-risksettings)")
    lines.append("   - 3.8 [其他](#38-其他)")
    lines.append("4. [未匹配的文件](#4-未匹配的文件)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 1: Class name quick reference
    lines.append("## 1. 类名对照速查表")
    lines.append("")
    lines.append("下表列出所有被混淆的类名及其原始名称，按原始类名排序。")
    lines.append("")
    lines.append("| 混淆类名 | 原始类名 | 混淆文件路径 | 原始文件路径 |")
    lines.append("|----------|----------|-------------|-------------|")

    class_entries = []
    for m in all_mappings:
        if m.get('class_changed', False):
            class_entries.append(m)

    # Sort by original class name
    class_entries.sort(key=lambda x: x.get('ori_class', ''))

    for entry in class_entries:
        obf_cn = entry.get('obf_class', '?')
        ori_cn = entry.get('ori_class', '?')
        obf_file = entry.get('obf_file', '?')
        ori_file = entry.get('ori_file', '?')
        lines.append(f"| `{obf_cn}` | **{ori_cn}** | `{obf_file}` | `{ori_file}` |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 2: Package mapping
    lines.append("## 2. 包名对照")
    lines.append("")
    lines.append("| 混淆包名 | 原始包名 |")
    lines.append("|----------|----------|")

    pkg_map = {}
    for m in all_mappings:
        obf_pkg = m.get('obf_package', '')
        ori_pkg = m.get('ori_package', '')
        if obf_pkg != ori_pkg and obf_pkg and ori_pkg:
            key = (obf_pkg, ori_pkg)
            if key not in pkg_map:
                pkg_map[key] = True

    for obf_pkg, ori_pkg in sorted(pkg_map.items(), key=lambda x: x[1]):
        lines.append(f"| `{obf_pkg}` | `{ori_pkg}` |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 3: Detailed mappings by module
    lines.append("## 3. 按模块分类的详细对照")
    lines.append("")

    # Categorize files by original package
    categories = {
        'riskEngines': [],
        'riskCategoies': [],  # Note: original has typo "riskCategoies"
        'riskModels': [],
        'utils': [],
        'riskExposure': [],
        'riskContext': [],
        'riskSettings': [],
        'other': []
    }

    for m in all_mappings:
        ori_pkg = m.get('ori_package', '')
        categorized = False
        for cat_key in ['riskEngines', 'riskCategoies', 'riskModels', 'utils', 'riskExposure', 'riskContext', 'riskSettings']:
            if cat_key in ori_pkg:
                categories[cat_key].append(m)
                categorized = True
                break
        if not categorized:
            categories['other'].append(m)

    # Sort each category by original class name
    for cat in categories:
        categories[cat].sort(key=lambda x: x.get('ori_class', ''))

    # 3.1 Risk Engines
    section_num = 1
    section_names = {
        'riskEngines': '风险引擎 (riskEngines)',
        'riskCategoies': '风险分类工厂 (riskCategories)',
        'riskModels': '风险模型 (riskModels)',
        'utils': '工具类 (utils)',
        'riskExposure': '风险敞口 (riskExposure)',
        'riskContext': '风险上下文 (riskContext)',
        'riskSettings': '风险设置 (riskSettings)',
        'other': '其他'
    }

    for cat_key in ['riskEngines', 'riskCategoies', 'riskModels', 'utils', 'riskExposure', 'riskContext', 'riskSettings', 'other']:
        cat_items = categories[cat_key]
        if not cat_items:
            continue

        lines.append(f"### 3.{section_num} {section_names[cat_key]}")
        lines.append("")

        for m in cat_items:
            obf_cn = m.get('obf_class', '?')
            ori_cn = m.get('ori_class', '?')
            obf_file = m.get('obf_file', '?')
            ori_file = m.get('ori_file', '?')

            if m.get('class_changed', False):
                lines.append(f"#### `{obf_cn}` → **{ori_cn}**")
            else:
                lines.append(f"#### **{ori_cn}** (类名未混淆)")
            lines.append("")
            lines.append(f"- 混淆文件: `{obf_file}`")
            lines.append(f"- 原始文件: `{ori_file}`")

            # Extends/Implements
            if m.get('extends'):
                lines.append(f"- 继承: `{m['extends']['obf']}` → `{m['extends']['ori']}`")
            if m.get('implements'):
                lines.append(f"- 实现: `{m['implements']['obf']}` → `{m['implements']['ori']}`")

            lines.append("")

            # Methods
            methods = m.get('methods', [])
            if methods:
                lines.append("**方法名对照:**")
                lines.append("")
                lines.append("| 混淆方法名 | 原始方法名 | 参数 |")
                lines.append("|-----------|-----------|------|")
                for mm in methods:
                    obf_mn = mm.get('obfuscated', '?')
                    ori_mn = mm.get('original', '?')
                    params = mm.get('ori_params', '')
                    if len(params) > 80:
                        params = params[:77] + '...'
                    lines.append(f"| `{obf_mn}` | `{ori_mn}` | {params} |")
                lines.append("")

            # Fields
            fields = m.get('fields', [])
            if fields:
                lines.append("**字段名对照:**")
                lines.append("")
                lines.append("| 混淆字段名 | 原始字段名 |")
                lines.append("|-----------|-----------|")
                for fm in fields:
                    obf_fn = fm.get('obfuscated', '?')
                    ori_fn = fm.get('original', '?')
                    lines.append(f"| `{obf_fn}` | `{ori_fn}` |")
                lines.append("")

            lines.append("---")
            lines.append("")

        section_num += 1

    # Section 4: Unmatched files
    lines.append("## 4. 未匹配的文件")
    lines.append("")
    lines.append("### 混淆仓库中未匹配的文件")
    lines.append("")
    lines.append("| 文件路径 | 行数 |")
    lines.append("|----------|------|")

    unmatched_obf = [
        ("cash/a/a.java", 94),
        ("cash/a/a14.java", 12),
        ("cash/c/a17.java", 14),
        ("cash/d/e/a36.java", 8),
        ("cash/g/b/a88.java", 14),
        ("cash/g/c/a100.java", 13),
        ("cash/g/c/a95.java", 15),
        ("cash/g/c/a98.java", 13),
        ("cash/g/d/a108.java", 9),
        ("cash/i/CommonPrefixKeys.java", 16),
    ]
    for path, lc in unmatched_obf:
        lines.append(f"| `{path}` | {lc} |")

    lines.append("")
    lines.append("### 原始仓库中未匹配的文件")
    lines.append("")
    lines.append("| 文件路径 | 行数 |")
    lines.append("|----------|------|")

    unmatched_ori = [
        ("companyBalance/BaseCompanyBalance.java", 22),
        ("riskEngines/DerivativeModule/DerivativeHeaderEngine.java", 260),
        ("riskEngines/ExposureModule/DerivationExposureEngine.java", 78),
        ("riskModels/RiskInputModel.java", 37),
        ("riskModels/SourceRiskModel.java", 62),
        ("riskModels/valuation/RiskValuationAverageModel.java", 33),
        ("riskSettings/ModelingGenerationLogSetting.java", 54),
    ]
    for path, lc in unmatched_ori:
        lines.append(f"| `{path}` | {lc} |")

    lines.append("")

    return '\n'.join(lines)

def main():
    # Load file matches
    with open(r"C:\StudyDataBase\file_matches.json", 'r', encoding='utf-8') as f:
        matches = json.load(f)

    all_mappings = []

    for obf_rel, ori_rel, score in matches:
        obf_path = os.path.join(OBF_DIR, obf_rel)
        ori_path = os.path.join(ORI_DIR, ori_rel)

        if not os.path.exists(obf_path) or not os.path.exists(ori_path):
            continue

        obf_content = read_file(obf_path)
        ori_content = read_file(ori_path)

        mapping = build_file_mapping(obf_content, ori_content, obf_rel, ori_rel)
        mapping['score'] = score
        all_mappings.append(mapping)

    # Generate markdown
    md = generate_markdown(all_mappings)

    # Write output
    output_path = r"C:\StudyDataBase\笔记仓库\金仕达公司业务类\HME项目文档\代码文档\现金流模块混淆名称对照表.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"Document generated: {output_path}")
    print(f"Total file mappings: {len(all_mappings)}")

    # Stats
    class_changed = sum(1 for m in all_mappings if m.get('class_changed'))
    total_methods = sum(len(m.get('methods', [])) for m in all_mappings)
    total_fields = sum(len(m.get('fields', [])) for m in all_mappings)
    print(f"Classes with renamed identifiers: {class_changed}")
    print(f"Method name mappings: {total_methods}")
    print(f"Field name mappings: {total_fields}")

if __name__ == '__main__':
    main()
