"""
v2: Fix external references - ONLY import paths and class names.
Do NOT replace method/field names (too risky for false positives).
"""
import os
import re
import json

REPO_DIR = r"C:\doWork\HME-客户服务器源码\hmeback - read版本"
MATCHES_FILE = r"C:\StudyDataBase\file_matches.json"
MAPPINGS_FILE = r"C:\StudyDataBase\name_mappings.json"
CASHFLOW_MODULE = "bcadmin-cashflowmodel"


def main():
    with open(MATCHES_FILE, 'r', encoding='utf-8') as f:
        file_matches = json.load(f)
    with open(MAPPINGS_FILE, 'r', encoding='utf-8') as f:
        name_mappings = json.load(f)

    # Build file map
    file_map = {}
    for obf_rel, ori_rel, score in file_matches:
        file_map[obf_rel.replace('\\', '/')] = ori_rel.replace('\\', '/')

    # Build FQN import map
    fqn_map = {}
    for obf_rel, ori_rel in file_map.items():
        obf_parts = obf_rel.split('/')
        ori_parts = ori_rel.split('/')
        obf_class = obf_parts[-1].replace('.java', '')
        ori_class = ori_parts[-1].replace('.java', '')
        obf_pkg = 'com.resrun.' + '.'.join(obf_parts[:-1]) if len(obf_parts) > 1 else 'com.resrun'
        ori_pkg = 'com.resrun.' + '.'.join(ori_parts[:-1]) if len(ori_parts) > 1 else 'com.resrun'
        old_fqn = f"{obf_pkg}.{obf_class}"
        new_fqn = f"{ori_pkg}.{ori_class}"
        if old_fqn != new_fqn:
            fqn_map[old_fqn] = new_fqn

    # Build class name map (only for obfuscated names like a1, a58, etc.)
    class_map = {}
    for obf_cn, ori_cn in name_mappings.get('class_names', {}).items():
        if obf_cn != ori_cn:
            # Only include names that look like obfuscation (a + digits)
            if re.match(r'^a\d+$', obf_cn):
                class_map[obf_cn] = ori_cn

    # Sort by key length desc
    fqn_sorted = sorted(fqn_map.items(), key=lambda x: len(x[0]), reverse=True)
    class_sorted = sorted(class_map.items(), key=lambda x: len(x[0]), reverse=True)

    print(f"FQN map: {len(fqn_map)}")
    print(f"Class map (obfuscated only): {len(class_map)}")

    # Find Java files outside cashflow module
    all_java = []
    for root, dirs, files in os.walk(REPO_DIR):
        if '/target/' in root or '\\target\\' in root:
            continue
        if CASHFLOW_MODULE in root:
            continue
        for fname in files:
            if fname.endswith('.java'):
                all_java.append(os.path.join(root, fname))

    print(f"\nScanning {len(all_java)} files outside cashflow module...")

    updated_count = 0
    for java_file in all_java:
        with open(java_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        original = content

        # 1. Replace full FQN imports (most important)
        for old_fqn, new_fqn in fqn_sorted:
            content = content.replace(f"import {old_fqn};", f"import {new_fqn};")
            content = content.replace(f"import static {old_fqn}", f"import static {new_fqn}")

        # 2. Replace class name references ONLY in type contexts
        # Look for patterns like: "a58 var", "extends a58", "new a58()", "List<a58>"
        for obf_cn, ori_cn in class_sorted:
            # Type declaration: "a58 varName" or "a58[] varName"
            content = re.sub(rf'\b{re.escape(obf_cn)}\b(\s+[\w\[\]]+\s*[=;,)])', rf'{ori_cn}\1', content)
            # extends/implements: "extends a58" or "implements a58"
            content = re.sub(rf'(extends|implements)\s+{re.escape(obf_cn)}\b', rf'\1 {ori_cn}', content)
            # new: "new a58(" or "new a58()"
            content = re.sub(rf'\bnew\s+{re.escape(obf_cn)}\s*\(', f'new {ori_cn}(', content)
            # Generic type: "List<a58>" or "Map<String, a58>"
            content = re.sub(rf'(<|,)\s*{re.escape(obf_cn)}\b(>|,)', rf'\1{ori_cn}\2', content)
            # Cast: "(a58)" or "(a58) "
            content = re.sub(rf'\(\s*{re.escape(obf_cn)}\s*\)', f'({ori_cn})', content)
            # Return type: "public a58 method(" or "private a58 method("
            content = re.sub(rf'(public|private|protected)\s+{re.escape(obf_cn)}\b', rf'\1 {ori_cn}', content)

        if content != original:
            with open(java_file, 'w', encoding='utf-8') as f:
                f.write(content)
            updated_count += 1
            rel = os.path.relpath(java_file, REPO_DIR)
            print(f"  {rel}")

    print(f"\nUpdated {updated_count} / {len(all_java)} files")
    print("\nDone! Only import paths and class name references were updated.")
    print("Method and field names were NOT changed to avoid false positives.")


if __name__ == '__main__':
    main()
