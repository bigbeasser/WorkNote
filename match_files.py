"""
Match obfuscated Java files to original Java files by structural similarity,
then extract name mappings (class, method, field, variable names).
"""
import os
import re
import json
from collections import defaultdict
from difflib import SequenceMatcher

OBF_DIR = r"C:\doWork\HME-客户服务器源码\hmeback\bcadmin-cashflowmodel\src\main\java\com\resrun"
ORI_DIR = r"C:\doWork\Kinstra代码仓库\hme\bcadmin-cashflowmodel\src\main\java\com\resrun"

def find_java_files(base_dir):
    result = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.java'):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, base_dir)
                result.append((rel, full))
    return result

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def count_lines(content):
    return len(content.splitlines())

def extract_string_literals(content):
    """Extract all string literals from Java code."""
    # Remove comments first
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    strings = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', content)
    return sorted(strings)

def extract_annotations(content):
    """Extract annotations like @Override, @Autowired etc."""
    return sorted(re.findall(r'@\w+', content))

def extract_structure_fingerprint(content):
    """Create a structural fingerprint by stripping identifiers."""
    # Remove comments
    code = re.sub(r'//.*', '', content)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Remove string literals
    code = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '"STR"', code)
    # Remove numbers
    code = re.sub(r'\b\d+\.?\d*[fFdDlL]?\b', 'NUM', code)
    # Count structural elements
    braces = code.count('{')
    parens = code.count('(')
    semicolons = code.count(';')
    lines = len(code.splitlines())
    return (lines, braces, parens, semicolons)

def extract_class_name(content):
    """Extract the main class/interface/enum name."""
    m = re.search(r'(?:public\s+)?(?:abstract\s+)?(?:class|interface|enum)\s+(\w+)', content)
    return m.group(1) if m else None

def extract_extends_implements(content):
    """Extract extends/implements class names."""
    extends = re.findall(r'extends\s+(\w+)', content)
    implements = re.findall(r'implements\s+([\w\s,]+)', content)
    return extends, implements

def extract_methods(content):
    """Extract method signatures."""
    # Remove comments
    code = re.sub(r'//.*', '', content)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Match method declarations
    pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:abstract\s+)?(?:[\w<>\[\],\s]+?)\s+(\w+)\s*\(([^)]*)\)'
    methods = re.findall(pattern, code)
    return methods

def extract_fields(content):
    """Extract field declarations."""
    code = re.sub(r'//.*', '', content)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Match field declarations (simplified)
    pattern = r'(?:private|protected|public)\s+(?:static\s+)?(?:final\s+)?(?:[\w<>\[\],\s]+?)\s+(\w+)\s*[;=]'
    fields = re.findall(pattern, code)
    return fields

def similarity_score(obf_content, ori_content):
    """Compute structural similarity between two files."""
    score = 0.0

    # 1. Line count similarity (weight: 30%)
    obf_lines = count_lines(obf_content)
    ori_lines = count_lines(ori_content)
    if max(obf_lines, ori_lines) > 0:
        line_sim = min(obf_lines, ori_lines) / max(obf_lines, ori_lines)
    else:
        line_sim = 1.0
    score += line_sim * 0.30

    # 2. Structure fingerprint similarity (weight: 20%)
    obf_struct = extract_structure_fingerprint(obf_content)
    ori_struct = extract_structure_fingerprint(ori_content)
    struct_sims = []
    for o, r in zip(obf_struct, ori_struct):
        if max(o, r) > 0:
            struct_sims.append(min(o, r) / max(o, r))
        else:
            struct_sims.append(1.0)
    score += (sum(struct_sims) / len(struct_sims)) * 0.20

    # 3. String literals similarity (weight: 30%)
    obf_strings = extract_string_literals(obf_content)
    ori_strings = extract_string_literals(ori_content)
    if obf_strings or ori_strings:
        sm = SequenceMatcher(None, obf_strings, ori_strings)
        score += sm.ratio() * 0.30
    else:
        score += 1.0 * 0.30

    # 4. Annotations similarity (weight: 10%)
    obf_ann = extract_annotations(obf_content)
    ori_ann = extract_annotations(ori_content)
    if obf_ann or ori_ann:
        sm = SequenceMatcher(None, obf_ann, ori_ann)
        score += sm.ratio() * 0.10
    else:
        score += 1.0 * 0.10

    # 5. Extends/implements similarity (weight: 10%)
    obf_ext, obf_imp = extract_extends_implements(obf_content)
    ori_ext, ori_imp = extract_extends_implements(ori_content)
    ext_sim = SequenceMatcher(None, obf_ext, ori_ext).ratio() if (obf_ext or ori_ext) else 1.0
    imp_sim = SequenceMatcher(None, obf_imp, ori_imp).ratio() if (obf_imp or ori_imp) else 1.0
    score += (ext_sim + imp_sim) / 2 * 0.10

    return score

def main():
    print("Scanning obfuscated files...")
    obf_files = find_java_files(OBF_DIR)
    print(f"Found {len(obf_files)} obfuscated files")

    print("Scanning original files...")
    ori_files = find_java_files(ORI_DIR)
    print(f"Found {len(ori_files)} original files")

    # Read all files
    obf_contents = {}
    for rel, full in obf_files:
        obf_contents[rel] = read_file(full)

    ori_contents = {}
    for rel, full in ori_files:
        ori_contents[rel] = read_file(full)

    # Match files
    print("\nMatching files...")
    matches = []
    used_ori = set()

    # Sort obfuscated files by line count for better matching
    obf_sorted = sorted(obf_contents.items(), key=lambda x: count_lines(x[1]), reverse=True)

    for obf_rel, obf_content in obf_sorted:
        obf_lc = count_lines(obf_content)
        best_score = -1
        best_ori_rel = None

        for ori_rel, ori_content in ori_contents.items():
            if ori_rel in used_ori:
                continue
            ori_lc = count_lines(ori_content)

            # Quick filter: line count must be within 20%
            if max(obf_lc, ori_lc) > 0 and min(obf_lc, ori_lc) / max(obf_lc, ori_lc) < 0.8:
                continue

            s = similarity_score(obf_content, ori_content)
            if s > best_score:
                best_score = s
                best_ori_rel = ori_rel

        if best_ori_rel and best_score > 0.5:
            matches.append((obf_rel, best_ori_rel, best_score))
            used_ori.add(best_ori_rel)
            obf_class = extract_class_name(obf_content)
            ori_class = extract_class_name(ori_contents[best_ori_rel])
            print(f"  {obf_rel} -> {best_ori_rel} (score={best_score:.3f}) [{obf_class} -> {ori_class}]")

    # Save raw matches
    with open(r"C:\StudyDataBase\file_matches.json", 'w', encoding='utf-8') as f:
        json.dump([(o, r, s) for o, r, s in matches], f, indent=2, ensure_ascii=False)

    print(f"\nMatched {len(matches)} / {len(obf_contents)} files")

    # Unmatched files
    unmatched_obf = [r for r in obf_contents if r not in [m[0] for m in matches]]
    unmatched_ori = [r for r in ori_contents if r not in used_ori]
    if unmatched_obf:
        print(f"\nUnmatched obfuscated files ({len(unmatched_obf)}):")
        for r in unmatched_obf:
            print(f"  {r} ({count_lines(obf_contents[r])} lines)")
    if unmatched_ori:
        print(f"\nUnmatched original files ({len(unmatched_ori)}):")
        for r in unmatched_ori:
            print(f"  {r} ({count_lines(ori_contents[r])} lines)")

if __name__ == '__main__':
    main()
