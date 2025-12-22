#!/usr/bin/env python3
"""
Carefully remove emojis from dashboard - preserve all formatting and indentation
"""

import re
from pathlib import Path

# Simple regex pattern to match most common emojis
EMOJI_PATTERN = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    u"\u2600-\u26FF"
    u"\u2700-\u27BF"
    "]+", flags=re.UNICODE)

def remove_emojis_from_file(file_path):
    """Remove emojis from file while preserving formatting"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    
    for line in lines:
        original_line = line
        # Remove emojis but keep all spaces
        cleaned_line = EMOJI_PATTERN.sub('', line)
        
        # Only clean up if we're in a string, not code indentation
        if cleaned_line != original_line:
            modified = True
        
        new_lines.append(cleaned_line)
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    dashboard_dir = Path(__file__).parent
    
    # Process Home.py (already done, but let's be thorough)
    home_file = dashboard_dir / 'Home.py'
    if home_file.exists():
        print(f"Processing {home_file.name}...")
        if remove_emojis_from_file(home_file):
            print(f"  ✓ Cleaned {home_file.name}")
    
    # Process all page files
    pages_dir = dashboard_dir / 'pages'
    for py_file in sorted(pages_dir.glob('*.py')):
        print(f"Processing {py_file.name}...")
        if remove_emojis_from_file(py_file):
            print(f"  ✓ Cleaned {py_file.name}")
        else:
            print(f"  - No emojis found in {py_file.name}")

if __name__ == '__main__':
    main()
