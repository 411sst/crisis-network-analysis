#!/usr/bin/env python3
"""
Script to remove all emojis from dashboard pages and replace with professional text
"""

import re
from pathlib import Path

# Emoji replacements
EMOJI_REPLACEMENTS = {
    # General emojis
    '📊': '',
    '📥': '',
    '📈': '',
    '🔬': '',
    '⏰': '',
    '🧠': '',
    '📄': '',
    '🌐': '',
    '👥': '',
    '🔥': '',
    '📅': '',
    '🕐': '',
    '❤️': '',
    '⭐': '',
    '🎯': '',
    '✅': '',
    '❌': '',
    '⚠️': '',
    'ℹ️': '',
    '🚀': '',
    '💡': '',
    '🏆': '',
    '📁': '',
    '🔍': '',
    '📚': '',
    '📂': '',
    '🔧': '',
    '💾': '',
    '⬇️': '',
    '👁️': '',
    '✖️': '',
    '🎬': '',
    '💎': '',
    '🔗': '',
    '🌟': '',
    '📖': '',
    '⬆️': '',
    '🌡️': '',
    '🔴': '',
    '🟢': '',
    '🟡': '',
}

def remove_emojis_from_file(file_path):
    """Remove emojis from a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace each emoji
    for emoji, replacement in EMOJI_REPLACEMENTS.items():
        content = content.replace(emoji, replacement)
    
    # Clean up double spaces
    content = re.sub(r'  +', ' ', content)
    
    # Clean up markdown headers with trailing spaces
    content = re.sub(r'(#+\s+)\s+', r'\1', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    dashboard_dir = Path(__file__).parent
    pages_dir = dashboard_dir / 'pages'
    
    files_updated = []
    
    # Process all Python files in pages directory
    for py_file in pages_dir.glob('*.py'):
        print(f"Processing {py_file.name}...")
        if remove_emojis_from_file(py_file):
            files_updated.append(py_file.name)
            print(f"  ✓ Updated {py_file.name}")
        else:
            print(f"  - No changes needed for {py_file.name}")
    
    print(f"\n{'='*50}")
    print(f"Updated {len(files_updated)} files:")
    for filename in files_updated:
        print(f"  - {filename}")

if __name__ == '__main__':
    main()
