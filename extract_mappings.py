"""
Extract detailed name mappings from matched file pairs.
Generates a comprehensive mapping document.
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
    """Remove Java comments."""
    code = re.sub(r'//.*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code

def extract_package(content):
    m = re.search(r'package\s+([\w.]+)\s*;', content)
    return m.group(1) if m else ''

def extract_imports(content):
    return re.findall(r'import\s+([\w.*]+)\s*;', content)

def extract_class_info(content):
    """Extract class/interface/enum declaration with extends/implements."""
    code = remove_comments(content)
    m = re.search(r'(?:public\s+)?(?:abstract\s+)?(?:class|interface|enum)\s+(\w+)(?:\s+extends\s+([\w<>,\s]+?))?(?:\s+implements\s+([\w<>,\s]+?))?\s*\{', code)
    if m:
        return {
            'name': m.group(1),
            'extends': m.group(2).strip() if m.group(2) else None,
            'implements': m.group(3).strip() if m.group(3) else None
        }
    return None

def extract_methods_detail(content):
    """Extract method declarations with full signatures."""
    code = remove_comments(content)
    methods = []
    # Match method declarations - handles generics, arrays, etc.
    pattern = r'(?:(?:public|private|protected)\s+)?(?:(?:static|final|synchronized|abstract|default)\s+)*(?:[\w<>\[\]?,\s]+?)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w,\s]+)?\s*[{;]'
    for m in re.finditer(pattern, code):
        name = m.group(1)
        params = m.group(2).strip()
        # Skip constructors that match class name (we handle them separately)
        methods.append({
            'name': name,
            'params': params,
            'full': m.group(0).strip()
        })
    return methods

def extract_fields_detail(content):
    """Extract field declarations."""
    code = remove_comments(content)
    fields = []
    # Match field declarations
    pattern = r'(?:private|protected|public)\s+(?:(?:static|final|transient|volatile)\s+)*(?:[\w<>\[\]?,\s]+?)\s+(\w+)\s*[;=]'
    for m in re.finditer(pattern, code):
        fields.append(m.group(1))
    # Also match constants (static final)
    pattern2 = r'(?:public|private|protected)\s+static\s+final\s+(?:[\w<>\[\]?,\s]+?)\s+(\w+)\s*='
    for m in re.finditer(pattern2, code):
        if m.group(1) not in fields:
            fields.append(m.group(1))
    return fields

def extract_enum_constants(content):
    """Extract enum constant names."""
    code = remove_comments(content)
    # Check if it's an enum
    if not re.search(r'(?:public\s+)?enum\s+\w+', code):
        return []
    # Find enum body
    m = re.search(r'enum\s+\w+[^{]*\{([^}]+)', code, re.DOTALL)
    if m:
        body = m.group(1)
        # Extract constant names (before any '(' or ',' or ';')
        constants = re.findall(r'\b([A-Z][A-Z0-9_]*)\b', body)
        return constants
    return []

def extract_local_variables(content):
    """Extract local variable names from method bodies."""
    code = remove_comments(content)
    # Remove string literals to avoid false matches
    code = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '""', code)
    # Match local variable declarations
    pattern = r'(?:final\s+)?(?:[\w<>\[\]]+)\s+(\w+)\s*='
    vars_found = re.findall(pattern, code)
    # Filter out common keywords and class names
    keywords = {'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'return', 'new', 'this', 'super', 'class', 'interface', 'enum'}
    return [v for v in vars_found if v not in keywords and not v[0].isupper()]

def extract_all_identifiers(content):
    """Extract all identifiers that look like meaningful names (camelCase/PascalCase)."""
    code = remove_comments(content)
    code = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '""', code)
    # Find all identifiers
    identifiers = re.findall(r'\b([a-zA-Z_]\w*)\b', code)
    # Filter out Java keywords and common patterns
    keywords = {
        'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class',
        'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final',
        'finally', 'float', 'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int',
        'interface', 'long', 'native', 'new', 'package', 'private', 'protected', 'public',
        'return', 'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this',
        'throw', 'throws', 'transient', 'try', 'void', 'volatile', 'while',
        'true', 'false', 'null', 'var', 'String', 'Integer', 'Long', 'Double', 'Float',
        'Boolean', 'List', 'Map', 'Set', 'HashMap', 'ArrayList', 'HashSet', 'BigDecimal',
        'Object', 'Optional', 'Collections', 'Arrays', 'Objects', 'System', 'Math',
        'StringBuilder', 'BufferedReader', 'IOException', 'Exception', 'RuntimeException',
        'Override', 'Autowired', 'Service', 'Component', 'Controller', 'Repository',
        'NotNull', 'Nullable', 'Slf4j', 'Data', 'Builder', 'AllArgsConstructor',
        'NoArgsConstructor', 'Getter', 'Setter', 'ToString', 'EqualsAndHashCode',
        'Value', 'Param', 'RequestBody', 'ResponseBody', 'PathVariable', 'RequestParam',
        'Bean', 'Configuration', 'PropertySource', 'SpringBootApplication',
        'log', 'logger', 'serialVersionUID'
    }
    # Also filter out single-char and very short names
    result = set()
    for ident in identifiers:
        if ident not in keywords and len(ident) > 2:
            result.add(ident)
    return result

def build_name_mapping(obf_content, ori_content, obf_rel, ori_rel):
    """Build detailed name mapping between obfuscated and original file."""
    mapping = {}

    # Package mapping
    obf_pkg = extract_package(obf_content)
    ori_pkg = extract_package(ori_content)
    if obf_pkg != ori_pkg:
        mapping['package'] = {'obfuscated': obf_pkg, 'original': ori_pkg}

    # Class info
    obf_class = extract_class_info(obf_content)
    ori_class = extract_class_info(ori_content)
    if obf_class and ori_class:
        mapping['class'] = {'obfuscated': obf_class['name'], 'original': ori_class['name']}
        if obf_class.get('extends') and ori_class.get('extends'):
            mapping['extends'] = {'obfuscated': obf_class['extends'], 'original': ori_class['extends']}
        if obf_class.get('implements') and ori_class.get('implements'):
            mapping['implements'] = {'obfuscated': obf_class['implements'], 'original': ori_class['implements']}

    # Methods
    obf_methods = extract_methods_detail(obf_content)
    ori_methods = extract_methods_detail(ori_content)
    if obf_methods and ori_methods:
        method_map = []
        # Match by position (since structure is preserved)
        for i, (om, rm) in enumerate(zip(obf_methods, ori_methods)):
            if om['name'] != rm['name']:
                method_map.append({
                    'obfuscated': om['name'],
                    'original': rm['name'],
                    'params_original': rm['params'][:100] if rm['params'] else ''
                })
        if method_map:
            mapping['methods'] = method_map

    # Fields
    obf_fields = extract_fields_detail(obf_content)
    ori_fields = extract_fields_detail(ori_content)
    if obf_fields and ori_fields:
        field_map = []
        for of, rf in zip(obf_fields, ori_fields):
            if of != rf:
                field_map.append({'obfuscated': of, 'original': rf})
        if field_map:
            mapping['fields'] = field_map

    # Enum constants
    obf_enums = extract_enum_constants(obf_content)
    ori_enums = extract_enum_constants(ori_content)
    if obf_enums and ori_enums:
        enum_map = []
        for oe, re_ in zip(obf_enums, ori_enums):
            if oe != re_:
                enum_map.append({'obfuscated': oe, 'original': re_})
        if enum_map:
            mapping['enum_constants'] = enum_map

    return mapping

def main():
    # Load file matches
    with open(r"C:\StudyDataBase\file_matches.json", 'r', encoding='utf-8') as f:
        matches = json.load(f)

    all_mappings = []
    class_name_map = {}  # obfuscated class -> original class
    all_method_mappings = []  # (obf_class, obf_method, ori_class, ori_method)
    all_field_mappings = []

    for obf_rel, ori_rel, score in matches:
        obf_path = os.path.join(OBF_DIR, obf_rel)
        ori_path = os.path.join(ORI_DIR, ori_rel)

        if not os.path.exists(obf_path) or not os.path.exists(ori_path):
            continue

        obf_content = read_file(obf_path)
        ori_content = read_file(ori_path)

        mapping = build_name_mapping(obf_content, ori_content, obf_rel, ori_rel)
        mapping['obfuscated_file'] = obf_rel
        mapping['original_file'] = ori_rel
        mapping['score'] = score

        # Collect class name mapping
        if 'class' in mapping:
            obf_cn = mapping['class']['obfuscated']
            ori_cn = mapping['class']['original']
            if obf_cn != ori_cn:
                class_name_map[obf_cn] = ori_cn

        # Collect method mappings
        if 'methods' in mapping:
            ori_class_name = mapping.get('class', {}).get('original', '?')
            obf_class_name = mapping.get('class', {}).get('obfuscated', '?')
            for mm in mapping['methods']:
                all_method_mappings.append({
                    'obf_class': obf_class_name,
                    'ori_class': ori_class_name,
                    'obf_method': mm['obfuscated'],
                    'ori_method': mm['original'],
                    'params': mm.get('params_original', '')
                })

        # Collect field mappings
        if 'fields' in mapping:
            ori_class_name = mapping.get('class', {}).get('original', '?')
            obf_class_name = mapping.get('class', {}).get('obfuscated', '?')
            for fm in mapping['fields']:
                all_field_mappings.append({
                    'obf_class': obf_class_name,
                    'ori_class': ori_class_name,
                    'obf_field': fm['obfuscated'],
                    'ori_field': fm['original']
                })

        all_mappings.append(mapping)

    # Save detailed mappings
    with open(r"C:\StudyDataBase\name_mappings.json", 'w', encoding='utf-8') as f:
        json.dump({
            'class_names': class_name_map,
            'methods': all_method_mappings,
            'fields': all_field_mappings,
            'file_mappings': all_mappings
        }, f, indent=2, ensure_ascii=False)

    print(f"Class name mappings: {len(class_name_map)}")
    print(f"Method mappings: {len(all_method_mappings)}")
    print(f"Field mappings: {len(all_field_mappings)}")
    print(f"File mappings: {len(all_mappings)}")

if __name__ == '__main__':
    main()
