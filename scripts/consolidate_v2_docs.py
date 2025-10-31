#!/usr/bin/env python3
"""
Consolidate V2 Documentation Script
Moves redundant V2 documentation files to archive and creates consolidated versions.
"""
import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = PROJECT_ROOT / "docs" / "archive" / "v2_consolidation"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# Files to archive (redundant, merged into consolidated docs)
FILES_TO_ARCHIVE = [
    # Integration files (merged into docs/V2_INTEGRATION_GUIDE.md)
    "V2_INTEGRATION_COMPLETE.md",
    "V2_INTEGRATION_COMPLETE_SUMMARY.md",
    "V2_INTEGRATION_SUMMARY.md",
    "V2_INTEGRATION_TEST_REPORT.md",
    
    # Deployment files (merged into docs/V2_DEPLOYMENT_GUIDE.md)
    "V2_DEPLOYMENT_STATUS.md",
    "V2_SWITCH_FIX.md",
    "ENABLE_V2_GUIDE.md",
    "docs/deployment/V2_DEPLOYMENT_SUMMARY.md",
    "docs/deployment/V2_STAGING_SUMMARY.md",
    
    # Testing files (merged into docs/V2_TESTING_GUIDE.md)
    "V2_PAYMENT_TEST_GUIDE.md",
    "V2_PAYMENT_TEST_INSTRUCTIONS.md",
    "V2_TEST_STATUS.md",
    
    # Status files (merged into docs/V2_STATUS.md)
    "V2_COMPLETE_STATUS.md",
    "V2_COMPLETION_REPORT.md",
    "V2_FINAL_COMPLETION_REPORT.md",
    "V2_FINAL_STATUS.md",
    "V2_ACTIVATION_SUCCESS.md",
    "V2_ID_UPDATE_SUMMARY.md",
    
    # Organization summary (merged into PRODUCTION_READINESS_V2.md)
    "V2_PRODUCTION_ORGANIZATION_SUMMARY.md",
]

def archive_file(file_path: Path):
    """Archive a file to the archive directory."""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False
    
    archive_path = ARCHIVE_DIR / file_path.name
    
    # If archive already exists, add number suffix
    counter = 1
    while archive_path.exists():
        archive_path = ARCHIVE_DIR / f"{file_path.stem}_{counter}{file_path.suffix}"
        counter += 1
    
    try:
        shutil.move(str(file_path), str(archive_path))
        print(f"✅ Archived: {file_path.name} → {archive_path.name}")
        return True
    except Exception as e:
        print(f"❌ Error archiving {file_path.name}: {e}")
        return False

def main():
    """Main consolidation function."""
    print("=" * 60)
    print("V2 Documentation Consolidation")
    print("=" * 60)
    print()
    
    archived_count = 0
    not_found_count = 0
    
    for file_rel_path in FILES_TO_ARCHIVE:
        file_path = PROJECT_ROOT / file_rel_path
        if file_path.exists():
            if archive_file(file_path):
                archived_count += 1
        else:
            print(f"⚠️  Not found: {file_rel_path}")
            not_found_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ Archived: {archived_count} files")
    print(f"⚠️  Not found: {not_found_count} files")
    print(f"📁 Archive location: {ARCHIVE_DIR}")
    print()
    print("Consolidated documentation:")
    print("  • docs/V2_INTEGRATION_GUIDE.md")
    print("  • docs/V2_DEPLOYMENT_GUIDE.md")
    print("  • docs/V2_TESTING_GUIDE.md")
    print("  • docs/V2_STATUS.md")
    print("  • PRODUCTION_READINESS_V2.md")
    print("=" * 60)

if __name__ == "__main__":
    main()



