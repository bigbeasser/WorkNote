"""
v5: Copy original files, then remove obfuscated duplicates.
"""
import os
import json
import shutil

TARGET_REPO = r"C:\doWork\HME-客户服务器源码\hmeback - read版本"
TARGET_MODULE = os.path.join(TARGET_REPO, "bcadmin-cashflowmodel", "src", "main", "java", "com", "resrun")
ORIGINAL_REPO = r"C:\doWork\Kinstra代码仓库\hme\bcadmin-cashflowmodel"
ORIGINAL_MODULE = os.path.join(ORIGINAL_REPO, "src", "main", "java", "com", "resrun")
MATCHES_FILE = r"C:\StudyDataBase\file_matches.json"


def main():
    with open(MATCHES_FILE, 'r', encoding='utf-8') as f:
        file_matches = json.load(f)

    # Build map: obf_rel -> ori_rel
    file_map = {}
    for obf_rel, ori_rel, score in file_matches:
        file_map[obf_rel.replace('\\', '/')] = ori_rel.replace('\\', '/')

    print(f"File mappings: {len(file_map)}")

    # ══════════════════════════════════════════════
    # Step 1: Remove ALL java files in target module
    # ══════════════════════════════════════════════
    print("\n═══ Step 1: Clearing target module ═══")
    removed = 0
    for root, dirs, files in os.walk(TARGET_MODULE):
        for fname in files:
            if fname.endswith('.java'):
                os.remove(os.path.join(root, fname))
                removed += 1
    print(f"  Removed {removed} files")

    # Clean empty dirs
    for root, dirs, files in os.walk(TARGET_MODULE, topdown=False):
        for d in dirs:
            dp = os.path.join(root, d)
            try:
                if not os.listdir(dp):
                    os.rmdir(dp)
            except OSError:
                pass

    # ══════════════════════════════════════════════
    # Step 2: Copy ALL original files
    # ══════════════════════════════════════════════
    print("\n═══ Step 2: Copying all original files ═══")
    copied = 0
    for root, dirs, files in os.walk(ORIGINAL_MODULE):
        for fname in files:
            if fname.endswith('.java'):
                src = os.path.join(root, fname)
                rel = os.path.relpath(src, ORIGINAL_MODULE).replace('\\', '/')
                dst = os.path.join(TARGET_MODULE, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
    print(f"  Copied {copied} files from original repo")

    # ══════════════════════════════════════════════
    # Step 3: Copy unmatched obfuscated files
    # ══════════════════════════════════════════════
    print("\n═══ Step 3: Copying unmatched obfuscated files ═══")

    # Get original file set (relative paths)
    original_files = set()
    for root, dirs, files in os.walk(ORIGINAL_MODULE):
        for fname in files:
            if fname.endswith('.java'):
                rel = os.path.relpath(os.path.join(root, fname), ORIGINAL_MODULE).replace('\\', '/')
                original_files.add(rel)

    # Get matched original files
    matched_ori = set(file_map.values())

    # Unmatched original files (already copied in step 2)
    unmatched_ori = original_files - matched_ori
    print(f"  Unmatched original files: {len(unmatched_ori)} (already copied)")

    # Now get unmatched obfuscated files from git
    # These are obfuscated files whose counterparts were NOT in the original
    # We need to restore them from git
    import subprocess

    # Get list of obfuscated files that are NOT in file_map (unmatched)
    matched_obf = set(file_map.keys())

    # Get all obfuscated files from git
    result = subprocess.run(
        ['git', 'ls-tree', '-r', '--name-only', 'HEAD', '--', 'bcadmin-cashflowmodel/src/main/java/com/resrun/'],
        cwd=TARGET_REPO,
        capture_output=True, text=True
    )
    git_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip().endswith('.java')]

    # Convert to relative paths within module
    prefix = 'bcadmin-cashflowmodel/src/main/java/com/resrun/'
    obf_files = []
    for gf in git_files:
        if gf.startswith(prefix):
            rel = gf[len(prefix):]
            obf_files.append(rel)

    # Find unmatched obfuscated files
    unmatched_obf = []
    for rel in obf_files:
        if rel not in matched_obf:
            unmatched_obf.append(rel)

    print(f"  Unmatched obfuscated files: {len(unmatched_obf)}")

    # Restore unmatched obfuscated files from git
    for rel in unmatched_obf:
        git_path = prefix + rel
        result = subprocess.run(
            ['git', 'show', f'HEAD:{git_path}'],
            cwd=TARGET_REPO,
            capture_output=True
        )
        if result.returncode == 0:
            target_path = os.path.join(TARGET_MODULE, rel)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'wb') as f:
                f.write(result.stdout)
            print(f"    Restored: {rel}")

    # ══════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════
    print("\n═══ Done ═══")
    total = 0
    for root, dirs, files in os.walk(TARGET_MODULE):
        for fname in files:
            if fname.endswith('.java'):
                total += 1
    print(f"Total Java files: {total}")
    print(f"  From original repo: {copied}")
    print(f"  Unmatched obfuscated (kept as-is): {len(unmatched_obf)}")


if __name__ == '__main__':
    main()
