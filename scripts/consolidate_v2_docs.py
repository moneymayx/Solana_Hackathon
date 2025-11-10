#!/usr/bin/env python3
"""
Comprehensive Code Reorganization Script
Organizes markdown documentation files AND scripts from root into appropriate directories.
When moving scripts, updates all references to maintain functionality.
"""
import os
import shutil
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = PROJECT_ROOT / "docs" / "archive" / "root_organization"
DEV_DIR = PROJECT_ROOT / "docs" / "development"
REPORTS_DIR = PROJECT_ROOT / "docs" / "reports"
SCRIPTS_UTILITIES_DIR = PROJECT_ROOT / "scripts" / "utilities"
SCRIPTS_ARCHIVE_DIR = PROJECT_ROOT / "scripts" / "archive"

# Smart contract organization directories
SMART_CONTRACT_DIR = PROJECT_ROOT / "smart_contract"
V1_CONTRACTS_DIR = SMART_CONTRACT_DIR / "v1"
V2_IMPL_DIR = SMART_CONTRACT_DIR / "v2_implementation"
V2_BACKEND_SERVICES = V2_IMPL_DIR / "backend" / "services"
V2_BACKEND_API = V2_IMPL_DIR / "backend" / "api"
V2_CONTRACTS = V2_IMPL_DIR / "contracts"
V2_SCRIPTS = V2_IMPL_DIR / "scripts"
V2_TESTS = V2_IMPL_DIR / "tests"

# Create all directories
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
DEV_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SCRIPTS_UTILITIES_DIR.mkdir(parents=True, exist_ok=True)
SCRIPTS_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
SMART_CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
V1_CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
V2_IMPL_DIR.mkdir(parents=True, exist_ok=True)
V2_BACKEND_SERVICES.mkdir(parents=True, exist_ok=True)
V2_BACKEND_API.mkdir(parents=True, exist_ok=True)
V2_CONTRACTS.mkdir(parents=True, exist_ok=True)
V2_SCRIPTS.mkdir(parents=True, exist_ok=True)
V2_TESTS.mkdir(parents=True, exist_ok=True)

# Track file moves for reference updates
FILE_MOVES: Dict[Path, Path] = {}

# Essential files to keep at root
ESSENTIAL_FILES = {
    "README.md",
    "ARCHITECTURE.md",
    "PRODUCTION_READINESS_V2.md",
    "QUICK_REFERENCE_V2.md",
}

# Files that should be archived (redundant/completed/completion docs)
FILES_TO_ARCHIVE = [
    # V2 consolidation files (already handled but may have duplicates)
    "V2_CONSOLIDATION_SUMMARY.md",
    "V2_DOCUMENTATION_CONSOLIDATION_COMPLETE.md",
    "V2_COMPLETE_ORGANIZATION_REPORT.md",
    "FINAL_V2_ORGANIZATION_SUMMARY.md",
    
    # Redundant completion/summary files
    "ALL_TODOS_COMPLETE.md",
    "EVERYTHING_COMPLETE_SUMMARY.md",
    "FINAL_SUMMARY.md",
    "ORGANIZATION_SUMMARY.md",
    "STAKING_AND_TODOS_COMPLETE.md",
    
    # Old organization files
    "FILE_ORGANIZATION_GUIDE.md",
]

# Pattern-based categorization
def categorize_file(filename: str) -> str:
    """Categorize file based on name patterns."""
    filename_upper = filename.upper()
    
    # SDK files → development
    if filename.startswith("SDK_") or "SDK" in filename_upper:
        return "development"
    
    # Test results → reports
    if any(x in filename_upper for x in ["_TEST_RESULTS", "TEST_RESULTS", "TEST_SUMMARY", 
                                          "TESTING_COMPLETE", "TEST_COMPLETE", "TEST_STATUS"]):
        return "reports"
    
    # Implementation files → development
    if filename.startswith("IMPLEMENTATION_") or "IMPLEMENTATION" in filename_upper:
        return "development"
    
    # Progress/Status/Summary files → development or archive
    if any(x in filename_upper for x in ["_PROGRESS", "_STATUS", "_SUMMARY", "PROGRESS"]):
        if any(x in filename_upper for x in ["COMPLETE", "FINAL", "FIXED"]):
            return "archive"  # Completed items go to archive
        return "development"
    
    # Completion files → archive
    if filename.endswith("_COMPLETE.md") or "COMPLETE" in filename_upper:
        return "archive"
    
    # Deployment/Fix files → development
    if filename.startswith("DEPLOYMENT_") or filename.startswith(("FRONTEND_", "MOBILE_", "PAYMENT_", "CHAT_")) or "_FIX" in filename_upper:
        return "development"
    
    # Fix/update files → development
    if any(x in filename_upper for x in ["_FIX", "_UPDATE", "_RESTORED", "_FIXES"]):
        return "development"
    
    # Guide files → development or keep
    if filename.endswith("_GUIDE.md") or "GUIDE" in filename_upper:
        if filename.startswith("MOCK_") or filename.startswith("SMART_CONTRACT_"):
            return "development"
        return "development"
    
    # Setup/Configuration → development
    if any(x in filename_upper for x in ["SETUP", "CONFIG", "INITIALIZATION", "KORA"]):
        return "development"
    
    # Default: archive if it's not essential
    return "archive"

def find_script_references(script_path: Path) -> List[Path]:
    """Find all files that reference this script."""
    references = []
    script_name = script_path.name
    script_relative = script_path.relative_to(PROJECT_ROOT)
    
    # Search patterns
    patterns = [
        re.compile(rf'[\'"]([^\'"]*{re.escape(script_name)})[\'"]', re.IGNORECASE),
        re.compile(rf'[\'"]([^\'"]*{re.escape(str(script_relative))})[\'"]', re.IGNORECASE),
        re.compile(rf'python.*?{re.escape(script_name)}', re.IGNORECASE),
        re.compile(rf'\./{re.escape(script_name)}', re.IGNORECASE),
        re.compile(rf'scripts/[^\s]*{re.escape(script_name)}', re.IGNORECASE),
    ]
    
    # Search in Python, shell, markdown, and config files
    search_extensions = {'.py', '.sh', '.md', '.txt', '.toml', '.json', '.yaml', '.yml'}
    
    for file_path in PROJECT_ROOT.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in search_extensions:
            # Skip the script itself and binary files
            if file_path == script_path:
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                for pattern in patterns:
                    if pattern.search(content):
                        references.append(file_path)
                        break
            except Exception:
                continue
    
    return references

def update_references(old_path: Path, new_path: Path) -> int:
    """Update all references to a moved file."""
    updates_count = 0
    old_relative = old_path.relative_to(PROJECT_ROOT)
    new_relative = new_path.relative_to(PROJECT_ROOT)
    
    # More specific patterns for replacement
    replacements = []
    
    # Only add replacements that make sense
    if old_path.parent == PROJECT_ROOT and new_path.parent != PROJECT_ROOT:
        # Moving from root to subdirectory
        replacements.extend([
            (f'python {old_path.name}', f'python {new_relative}'),
            (f'python3 {old_path.name}', f'python3 {new_relative}'),
            (f'./{old_path.name}', f'./{new_relative}'),
            (f"'{old_path.name}'", f"'{new_relative}'"),
            (f'"{old_path.name}"', f'"{new_relative}"'),
        ])
        
        # Handle scripts/ prefix variations
        if str(old_relative) not in str(new_relative.parent):
            replacements.extend([
                (f'scripts/{old_path.name}', str(new_relative)),
                (f"'scripts/{old_path.name}'", f"'{new_relative}'"),
                (f'"scripts/{old_path.name}"', f'"{new_relative}"'),
            ])
    
    # General relative path updates
    replacements.extend([
        (f'python {old_relative}', f'python {new_relative}'),
        (f'python3 {old_relative}', f'python3 {new_relative}'),
        (f"'{old_relative}'", f"'{new_relative}'"),
        (f'"{old_relative}"', f'"{new_relative}"'),
    ])
    
    # Find all files that might reference this script
    search_extensions = {'.py', '.sh', '.md', '.txt', '.toml', '.json'}
    
    for file_path in PROJECT_ROOT.rglob('*'):
        if not file_path.is_file() or file_path.suffix.lower() not in search_extensions:
            continue
        if file_path == new_path or file_path == old_path:
            continue
        # Skip node_modules and venv
        if 'node_modules' in str(file_path) or 'venv' in str(file_path) or '__pycache__' in str(file_path):
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            original_content = content
            
            # Apply replacements in order
            for old_ref, new_ref in replacements:
                # Escape special regex chars in old_ref for safe replacement
                escaped_old = re.escape(old_ref)
                # Use word boundary or quote boundary for safer matching
                pattern = rf'(?<![a-zA-Z0-9_/]){escaped_old}(?![a-zA-Z0-9_])'
                content = re.sub(pattern, new_ref, content)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                updates_count += 1
        except Exception as e:
            # Silently continue on errors (binary files, permission issues, etc.)
            continue
    
    return updates_count

def move_file(file_path: Path, target_dir: Path, category: str, is_script: bool = False, update_refs: bool = True) -> bool:
    """Move a file to target directory, handling duplicates and updating references."""
    if not file_path.exists():
        return False
    
    target_path = target_dir / file_path.name
    
    # Handle duplicates
    counter = 1
    while target_path.exists():
        target_path = target_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
        counter += 1
    
    try:
        # If it's a script or code file, find references first
        references_updated = 0
        if (is_script or file_path.suffix == '.py') and update_refs:
            refs = find_script_references(file_path)
            if refs:
                print(f"      Found {len(refs)} reference(s) to update")
        
        shutil.move(str(file_path), str(target_path))
        
        # Track the move
        FILE_MOVES[file_path] = target_path
        
        # Update references if it's a script or code file
        if (is_script or file_path.suffix == '.py') and update_refs:
            references_updated = update_references(file_path, target_path)
            if references_updated > 0:
                print(f"      ✅ Updated {references_updated} file(s) with new path")
        
        print(f"  ✅ {category:12} {file_path.name} → {target_path.name}")
        return True
    except Exception as e:
        print(f"  ❌ Error moving {file_path.name}: {e}")
        return False

def categorize_script(script_path: Path) -> Tuple[str, Path]:
    """Categorize a script based on name and location patterns."""
    filename = script_path.name.lower()
    filename_upper = script_path.name.upper()
    
    # Skip if already in organized location
    if "scripts/" in str(script_path) and script_path.parent != PROJECT_ROOT:
        # Already organized, keep structure but might consolidate
        if script_path.parent.name in ['deployment', 'testing', 'monitoring', 'setup', 'sdk', 'devnet', 'utilities', 'obsolete']:
            return "keep", script_path.parent  # Already organized
    
    # Debug/test scripts in root → archive or utilities
    if filename.startswith(('debug_', 'test_')) or filename.endswith(('_debug.py', '_test.py')):
        return "archive", SCRIPTS_ARCHIVE_DIR
    
    # Migration scripts → utilities
    if 'migrate' in filename or 'migration' in filename:
        return "utilities", SCRIPTS_UTILITIES_DIR
    
    # Demo/example scripts → utilities
    if filename.startswith('demo_') or 'demo' in filename:
        return "utilities", SCRIPTS_UTILITIES_DIR
    
    # Simple utility scripts → utilities
    if filename.startswith('simple_') or filename.startswith('update_'):
        return "utilities", SCRIPTS_UTILITIES_DIR
    
    # Default: keep in scripts root if it's important, otherwise archive
    if script_path.parent == PROJECT_ROOT:
        # Important scripts stay in scripts root
        if filename in ['verify_setup.py', 'analyze_codebase_stats.py']:
            return "keep", PROJECT_ROOT / "scripts"
        # Others go to utilities
        return "utilities", SCRIPTS_UTILITIES_DIR
    
    return "keep", script_path.parent

def organize_v2_smart_contracts() -> Dict[str, int]:
    """Organize V2 smart contract implementation files into smart-contract/v2_implementation/"""
    stats = {
        "v1_contracts": 0,
        "v2_backend_services": 0,
        "v2_backend_api": 0,
        "v2_contracts": 0,
        "v2_scripts": 0,
        "v2_tests": 0,
    }
    
    print()
    print("=" * 80)
    print("Organizing Smart Contract Files")
    print("=" * 80)
    print()
    
    # 1. Move V1 contracts (programs/billions-bounty/) to smart-contract/v1/
    v1_contracts_dir = PROJECT_ROOT / "programs" / "billions-bounty"
    if v1_contracts_dir.exists():
        print("Moving V1 contracts to smart-contract/v1/...")
        try:
            # Move entire directory
            target_v1 = V1_CONTRACTS_DIR / "billions-bounty"
            if not target_v1.exists():
                shutil.move(str(v1_contracts_dir), str(target_v1))
                stats["v1_contracts"] = 1
                print(f"  ✅ Moved V1 contracts: programs/billions-bounty/ → smart-contract/v1/billions-bounty/")
            else:
                print(f"  ⚠️  V1 contracts already exist at {target_v1}")
        except Exception as e:
            print(f"  ❌ Error moving V1 contracts: {e}")
    
    # 2. Move V2 backend services (src/services/v2/) to smart-contract/v2_implementation/backend/services/
    v2_services_dir = PROJECT_ROOT / "src" / "services" / "v2"
    if v2_services_dir.exists():
        print("\nMoving V2 backend services...")
        for file_path in v2_services_dir.rglob('*'):
            if file_path.is_file() and file_path.name != '__pycache__':
                rel_path = file_path.relative_to(v2_services_dir)
                target_path = V2_BACKEND_SERVICES / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.move(str(file_path), str(target_path))
                    FILE_MOVES[file_path] = target_path
                    stats["v2_backend_services"] += 1
                    print(f"  ✅ {rel_path}")
                except Exception as e:
                    print(f"  ❌ Error moving {file_path.name}: {e}")
        
        # Remove empty directory
        try:
            if v2_services_dir.exists() and not any(v2_services_dir.iterdir()):
                v2_services_dir.rmdir()
        except:
            pass
    
    # 3. Move V2 API files to smart-contract/v2_implementation/backend/api/
    v2_api_files = [
        PROJECT_ROOT / "src" / "api" / "v2_payment_router.py",
        PROJECT_ROOT / "src" / "services" / "contract_adapter_v2.py",
    ]
    
    print("\nMoving V2 API files...")
    for file_path in v2_api_files:
        if file_path.exists():
            try:
                move_file(file_path, V2_BACKEND_API, "V2_API", is_script=True)
                stats["v2_backend_api"] += 1
            except Exception as e:
                print(f"  ❌ Error moving {file_path.name}: {e}")
    
    # 4. Move V2 contracts (programs/billions-bounty-v2/) to smart-contract/v2_implementation/contracts/
    v2_contracts_dir = PROJECT_ROOT / "programs" / "billions-bounty-v2"
    if v2_contracts_dir.exists():
        print("\nMoving V2 contracts to smart-contract/v2_implementation/contracts/...")
        try:
            target_v2 = V2_CONTRACTS / "billions-bounty-v2"
            if not target_v2.exists():
                shutil.move(str(v2_contracts_dir), str(target_v2))
                stats["v2_contracts"] = 1
                print(f"  ✅ Moved V2 contracts: programs/billions-bounty-v2/ → smart-contract/v2_implementation/contracts/billions-bounty-v2/")
            else:
                print(f"  ⚠️  V2 contracts already exist at {target_v2}")
        except Exception as e:
            print(f"  ❌ Error moving V2 contracts: {e}")
    
    # 5. Move V2 scripts
    print("\nMoving V2 scripts...")
    v2_script_files = [
        (PROJECT_ROOT / "scripts" / "devnet" / "test_v2_integration.py", "devnet/test_v2_integration.py"),
        (PROJECT_ROOT / "scripts" / "devnet" / "init_v2.py", "devnet/init_v2.py"),
        (PROJECT_ROOT / "scripts" / "testing" / "test_v2_integration.py", "testing/test_v2_integration.py"),
        (PROJECT_ROOT / "scripts" / "staging" / "validate_v2_deployment.sh", "staging/validate_v2_deployment.sh"),
        (PROJECT_ROOT / "scripts" / "update_v2_ids.py", "update_v2_ids.py"),
    ]
    
    for file_path, _ in v2_script_files:
        if file_path.exists():
            try:
                move_file(file_path, V2_SCRIPTS, "V2_SCRIPT", is_script=True)
                stats["v2_scripts"] += 1
            except Exception as e:
                print(f"  ❌ Error moving {file_path.name}: {e}")
    
    # 6. Move V2 tests
    print("\nMoving V2 tests...")
    v2_test_files = [
        PROJECT_ROOT / "tests" / "test_v2_service.py",
        PROJECT_ROOT / "tests" / "integration" / "test_contract_v2_adapter.py",
    ]
    
    for file_path in v2_test_files:
        if file_path.exists():
            target_test_dir = V2_TESTS / file_path.parent.name if file_path.parent != PROJECT_ROOT / "tests" else V2_TESTS
            target_test_dir.mkdir(parents=True, exist_ok=True)
            try:
                move_file(file_path, target_test_dir, "V2_TEST", is_script=False, update_refs=True)
                stats["v2_tests"] += 1
            except Exception as e:
                print(f"  ❌ Error moving {file_path.name}: {e}")
    
    return stats

def main():
    """Main reorganization function."""
    print("=" * 80)
    print("Comprehensive Code Reorganization Script")
    print("=" * 80)
    print()
    
    # Get all MD files in root
    root_md_files = list(PROJECT_ROOT.glob("*.md"))
    
    # Get all scripts in root (Python and shell scripts)
    root_scripts = []
    root_scripts.extend(PROJECT_ROOT.glob("*.py"))
    root_scripts.extend(PROJECT_ROOT.glob("*.sh"))
    # Exclude this script itself
    root_scripts = [s for s in root_scripts if s.name != "consolidate_v2_docs.py"]
    
    # Counts for markdown files
    md_kept = 0
    md_moved_to_dev = 0
    md_moved_to_reports = 0
    md_moved_to_archive = 0
    md_skipped = 0
    
    # Counts for scripts
    script_kept = 0
    script_moved_to_utilities = 0
    script_moved_to_archive = 0
    script_skipped = 0
    
    print(f"Found {len(root_md_files)} markdown files in root directory")
    print(f"Found {len(root_scripts)} scripts in root directory")
    print()
    print("Processing markdown files...")
    print()
    
    # Process markdown files
    for file_path in sorted(root_md_files):
        filename = file_path.name
        
        # Skip essential files
        if filename in ESSENTIAL_FILES:
            print(f"  ⏭️  KEEPING    {filename} (essential file)")
            md_kept += 1
            continue
        
        # Check explicit archive list first
        if filename in FILES_TO_ARCHIVE:
            if move_file(file_path, ARCHIVE_DIR, "ARCHIVE"):
                md_moved_to_archive += 1
            continue
        
        # Categorize file
        category = categorize_file(filename)
        
        if category == "development":
            if move_file(file_path, DEV_DIR, "DEVELOPMENT"):
                md_moved_to_dev += 1
        elif category == "reports":
            if move_file(file_path, REPORTS_DIR, "REPORTS"):
                md_moved_to_reports += 1
        elif category == "archive":
            if move_file(file_path, ARCHIVE_DIR, "ARCHIVE"):
                md_moved_to_archive += 1
        else:
            print(f"  ⚠️  UNKNOWN    {filename} (kept in root)")
            md_skipped += 1
    
    print()
    print("Processing scripts...")
    print()
    
    # Process scripts
    for script_path in sorted(root_scripts):
        filename = script_path.name
        is_script_file = script_path.suffix in {'.py', '.sh'}
        
        # Categorize script
        category, target_dir = categorize_script(script_path)
        
        if category == "keep":
            if target_dir == script_path.parent:
                print(f"  ⏭️  KEEPING    {filename} (already organized)")
                script_kept += 1
            else:
                # Move to scripts root
                target_script_path = PROJECT_ROOT / "scripts" / filename
                if script_path != target_script_path:
                    if move_file(script_path, PROJECT_ROOT / "scripts", "SCRIPTS", is_script=is_script_file):
                        script_kept += 1
                else:
                    script_kept += 1
        elif category == "utilities":
            if move_file(script_path, target_dir, "UTILITIES", is_script=is_script_file):
                script_moved_to_utilities += 1
        elif category == "archive":
            if move_file(script_path, target_dir, "ARCHIVE", is_script=is_script_file):
                script_moved_to_archive += 1
        else:
            print(f"  ⚠️  UNKNOWN    {filename} (kept in root)")
            script_skipped += 1
    
    print()
    print("Organizing smart contract files...")
    v2_stats = organize_v2_smart_contracts()
    
    print()
    print("=" * 80)
    print("Reorganization Summary")
    print("=" * 80)
    print()
    print("Markdown Files:")
    print(f"  ✅ Kept at root:        {md_kept} files")
    print(f"  📁 Moved to development: {md_moved_to_dev} files")
    print(f"  📊 Moved to reports:     {md_moved_to_reports} files")
    print(f"  📦 Moved to archive:     {md_moved_to_archive} files")
    print(f"  ⚠️  Skipped (unknown):   {md_skipped} files")
    print()
    print("Scripts:")
    print(f"  ✅ Kept in place:       {script_kept} files")
    print(f"  🔧 Moved to utilities:  {script_moved_to_utilities} files")
    print(f"  📦 Moved to archive:    {script_moved_to_archive} files")
    print(f"  ⚠️  Skipped (unknown):   {script_skipped} files")
    print()
    print("Smart Contract Organization:")
    print(f"  ✅ V1 Contracts:       {v2_stats['v1_contracts']} directory(ies)")
    print(f"  ✅ V2 Backend Services: {v2_stats['v2_backend_services']} files")
    print(f"  ✅ V2 Backend API:     {v2_stats['v2_backend_api']} files")
    print(f"  ✅ V2 Contracts:       {v2_stats['v2_contracts']} directory(ies)")
    print(f"  ✅ V2 Scripts:         {v2_stats['v2_scripts']} files")
    print(f"  ✅ V2 Tests:            {v2_stats['v2_tests']} files")
    print()
    print("Directory locations:")
    print(f"  • Development:        {DEV_DIR}")
    print(f"  • Reports:            {REPORTS_DIR}")
    print(f"  • Archive (docs):     {ARCHIVE_DIR}")
    print(f"  • Scripts Utilities:  {SCRIPTS_UTILITIES_DIR}")
    print(f"  • Scripts Archive:    {SCRIPTS_ARCHIVE_DIR}")
    print(f"  • Smart Contracts:    {SMART_CONTRACT_DIR}")
    print(f"    ├── v1/             (Original contracts)")
    print(f"    └── v2_implementation/")
    print(f"        ├── backend/")
    print(f"        │   ├── services/")
    print(f"        │   └── api/")
    print(f"        ├── contracts/")
    print(f"        ├── scripts/")
    print(f"        └── tests/")
    print()
    print("Essential files kept at root:")
    for essential in sorted(ESSENTIAL_FILES):
        if (PROJECT_ROOT / essential).exists():
            print(f"  • {essential}")
    print()
    if FILE_MOVES:
        print(f"📝 Updated references in {len(FILE_MOVES)} moved file(s)")
    print("=" * 80)

if __name__ == "__main__":
    main()



