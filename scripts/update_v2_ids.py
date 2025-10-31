#!/usr/bin/env python3
"""
Update all V2 program IDs, PDAs, and mint addresses in MD files.
"""
import os
import re
from pathlib import Path

# Old values to replace
REPLACEMENTS = {
    # Program IDs
    "GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm": "HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm",
    "4ChHkYCu5Q8KpBh1pPEx5KgKTQGySikhvzhi3KYrUMuW": "HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm",
    
    # PDAs
    "F4YATUC3tEA3Gb3Tt3v7sZBT9iKRhHXJsZ6s7nBWKDgh": "BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb",
    "AJC6D2mvMcktdzpJJQmbYXkTZn9xGpd2C3qm4VAZK83Z": "2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb",
    
    # USDC Mint
    "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr": "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh",
}

def update_file(filepath):
    """Update a single file with replacements."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        for old_value, new_value in REPLACEMENTS.items():
            if old_value in content:
                content = content.replace(old_value, new_value)
                updated = True
                print(f"  ✓ Replaced {old_value[:16]}... → {new_value[:16]}...")
        
        if updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  ✗ Error updating {filepath}: {e}")
        return False

def main():
    """Find and update all MD files."""
    project_root = Path(__file__).parent.parent
    md_files = list(project_root.rglob("*.md"))
    
    # Exclude certain directories
    excluded_dirs = {"node_modules", ".git", "target", "dist", "build"}
    md_files = [
        f for f in md_files 
        if not any(excluded in str(f) for excluded in excluded_dirs)
    ]
    
    print(f"Found {len(md_files)} markdown files to check...")
    print()
    
    updated_count = 0
    for md_file in md_files:
        relative_path = md_file.relative_to(project_root)
        print(f"Checking: {relative_path}")
        
        if update_file(md_file):
            updated_count += 1
            print(f"  ✅ Updated\n")
        else:
            print(f"  ✓ No changes needed\n")
    
    print(f"\n{'='*60}")
    print(f"✅ Updated {updated_count} files")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

