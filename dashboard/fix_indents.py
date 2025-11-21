#!/usr/bin/env python3
"""
Fix indentation issues in Python files caused by emoji removal
"""

import re
from pathlib import Path

def fix_indentation(file_path):
    """Fix indentation in a Python file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for line in lines:
        # Replace single-space indents with 4-space indents
        if line.startswith(' ') and not line.startswith('    '):
            # Count leading spaces
            leading_spaces = len(line) - len(line.lstrip(' '))
            if leading_spaces > 0 and leading_spaces < 4:
                # This is likely a broken indent - fix it
                fixed_line = '    ' + line.lstrip(' ')
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    return True

def main():
    dashboard_dir = Path(__file__).parent
    pages_dir = dashboard_dir / 'pages'
    
    files_to_fix = [
        '04_Temporal_Analysis.py',
    ]
    
    for filename in files_to_fix:
        file_path = pages_dir / filename
        if file_path.exists():
            print(f"Fixing {filename}...")
            fix_indentation(file_path)
            print(f"  ✓ Fixed {filename}")

if __name__ == '__main__':
    main()
