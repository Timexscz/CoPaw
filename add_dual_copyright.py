#!/usr/bin/env python3
"""为官方 CoPaw 0.0.5.post1 原有的修改文件添加双重版权声明。"""
import subprocess
from pathlib import Path

def get_modified_files():
    """获取官方 0.0.5.post1 修改过的文件列表（M 开头的）。"""
    result = subprocess.run(
        ['git', 'diff', 'fca6a17', '--name-status'],
        capture_output=True,
        text=True,
        cwd='/root/CoPaw'
    )
    
    modified_files = []
    for line in result.stdout.strip().split('\n'):
        if line.startswith('M') and 'src/copaw/' in line and line.endswith('.py'):
            file_path = line.split('\t')[1]
            modified_files.append(file_path)
    
    return modified_files

def add_dual_copyright(file_path: str) -> tuple[bool, str]:
    """为文件添加双重版权声明。"""
    full_path = Path('/root/CoPaw') / file_path
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已有双重版权
        if '# Copyright 2025 The CoPaw Authors' in content:
            return False, "已有双重版权"
        
        # 检查是否有 Timexscz 版权
        if '# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)' not in content:
            return False, "没有 Timexscz 版权"
        
        # 替换为双重版权
        old_line = '# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)'
        new_lines = '# Copyright 2025 The CoPaw Authors\n# Copyright 2025-2026 Timexscz (CoPaw-CE Community Edition)'
        
        new_content = content.replace(old_line, new_lines)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "已添加双重版权"
    except Exception as e:
        return False, f"错误：{e}"

def main():
    print("="*60)
    print("为官方 CoPaw 0.0.5.post1 原有的修改文件添加双重版权")
    print("="*60)
    print()
    
    print("获取官方 0.0.5.post1 修改过的文件列表...\n")
    modified_files = get_modified_files()
    
    print(f"找到 {len(modified_files)} 个修改过的官方 Python 文件\n")
    print("-"*60)
    
    updated = 0
    skipped = 0
    errors = []
    
    for file_path in modified_files:
        success, msg = add_dual_copyright(file_path)
        if success:
            updated += 1
            print(f"✓ {file_path}")
        else:
            skipped += 1
            if "已有双重版权" in msg:
                print(f"⊘ {file_path} - {msg}")
            else:
                errors.append((file_path, msg))
                print(f"✗ {file_path} - {msg}")
    
    print("-"*60)
    print(f"\n{'='*60}")
    print(f"修改过的官方文件：{len(modified_files)}")
    print(f"成功添加双重版权：{updated}")
    print(f"跳过：{skipped}")
    
    if errors:
        print(f"\n需要手动处理：{len(errors)}")
        for fp, err in errors:
            print(f"  - {fp}: {err}")

if __name__ == '__main__':
    main()
