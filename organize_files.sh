#!/bin/bash

# File Organization Script for Billions Bounty
# This script helps organize development files and ensure proper gitignore protection

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗂️  Billions Bounty File Organization Script${NC}"
echo "=================================================="
echo ""

# Function to check if file should be ignored
should_ignore() {
    local file="$1"
    
    # Check against gitignore patterns
    if [[ "$file" =~ debug_.*\.py$ ]] || \
       [[ "$file" =~ .*_debug\.py$ ]] || \
       [[ "$file" =~ test_.*\.py$ ]] || \
       [[ "$file" =~ .*_test\.py$ ]] || \
       [[ "$file" =~ migrate_.*\.py$ ]] || \
       [[ "$file" =~ .*_migrate\.py$ ]] || \
       [[ "$file" =~ simple_.*\.py$ ]] || \
       [[ "$file" =~ .*_PROGRESS\.md$ ]] || \
       [[ "$file" =~ .*_SUMMARY\.md$ ]] || \
       [[ "$file" =~ .*_COMPLETE\.md$ ]] || \
       [[ "$file" =~ START_HERE\.md$ ]] || \
       [[ "$file" =~ IMPLEMENTATION_.*\.md$ ]] || \
       [[ "$file" =~ REDESIGN_.*\.md$ ]] || \
       [[ "$file" =~ FRONTEND_.*\.md$ ]] || \
       [[ "$file" =~ .*\.backup$ ]] || \
       [[ "$file" =~ .*\.bak$ ]] || \
       [[ "$file" =~ .*_backup\.py$ ]] || \
       [[ "$file" =~ .*_backup\..*$ ]] || \
       [[ "$file" =~ .*\.log$ ]] || \
       [[ "$file" =~ frontend/.*_GUIDE\.md$ ]] || \
       [[ "$file" =~ frontend/.*_REFERENCE\.md$ ]] || \
       [[ "$file" =~ frontend/README_.*\.md$ ]] || \
       [[ "$file" =~ frontend/REDESIGN_.*\.md$ ]] || \
       [[ "$file" =~ frontend/update-.*\.sh$ ]] || \
       [[ "$file" =~ frontend/.*-banner-.*\.sh$ ]] || \
       [[ "$file" =~ frontend/.*\.log$ ]] || \
       [[ "$file" =~ frontend/src/app/test-api/ ]] || \
       [[ "$file" =~ frontend/src/app/features/ ]] || \
       [[ "$file" =~ frontend/src/app/staking/ ]] || \
       [[ "$file" =~ frontend/src/app/stats/ ]] || \
       [[ "$file" =~ frontend/src/app/teams/ ]] || \
       [[ "$file" =~ frontend/src/app/token/ ]] || \
       [[ "$file" =~ FILE_ORGANIZATION_GUIDE\.md$ ]] || \
       [[ "$file" =~ CLEANUP_COMPLETE\.md$ ]] || \
       [[ "$file" =~ GIT_HISTORY_CLEANUP_GUIDE\.md$ ]] || \
       [[ "$file" =~ REORGANIZATION_SUMMARY\.md$ ]]; then
        return 0  # Should be ignored
    else
        return 1  # Should not be ignored
    fi
}

# Function to categorize files
categorize_files() {
    echo -e "${YELLOW}📋 Categorizing files...${NC}"
    echo ""
    
    local ignored_files=()
    local tracked_files=()
    local untracked_files=()
    
    # Get git status
    while IFS= read -r line; do
        if [[ "$line" =~ ^\?\? ]]; then
            # Untracked file
            local file="${line:3}"
            if should_ignore "$file"; then
                ignored_files+=("$file")
            else
                untracked_files+=("$file")
            fi
        elif [[ "$line" =~ ^[AM] ]]; then
            # Modified/Added file
            local file="${line:3}"
            tracked_files+=("$file")
        fi
    done < <(git status --porcelain)
    
    echo -e "${GREEN}✅ Files that should be tracked:${NC}"
    if [ ${#tracked_files[@]} -eq 0 ] && [ ${#untracked_files[@]} -eq 0 ]; then
        echo "  (none)"
    else
        for file in "${tracked_files[@]}" "${untracked_files[@]}"; do
            echo "  ✓ $file"
        done
    fi
    echo ""
    
    echo -e "${YELLOW}🚫 Files that should be ignored:${NC}"
    if [ ${#ignored_files[@]} -eq 0 ]; then
        echo "  (none)"
    else
        for file in "${ignored_files[@]}"; do
            echo "  ✗ $file"
        done
    fi
    echo ""
    
    return 0
}

# Function to clean up ignored files
cleanup_ignored_files() {
    echo -e "${YELLOW}🧹 Cleaning up ignored files...${NC}"
    echo ""
    
    # Remove ignored files from git tracking if they were accidentally added
    git status --porcelain | grep -E "^\?\?" | cut -c4- | while read -r file; do
        if should_ignore "$file"; then
            echo -e "${YELLOW}  Removing from git tracking: $file${NC}"
            git rm --cached "$file" 2>/dev/null || true
        fi
    done
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    echo ""
}

# Function to show git status
show_git_status() {
    echo -e "${BLUE}📊 Current Git Status:${NC}"
    echo ""
    git status --short
    echo ""
}

# Function to show protected files
show_protected_files() {
    echo -e "${BLUE}🔒 Protected Files (in .gitignore):${NC}"
    echo ""
    
    echo "Security Critical:"
    echo "  - Private keys and certificates (*.pem, *.key)"
    echo "  - Wallet keypairs (*.keypair.json)"
    echo "  - Database files (*.db, *.sqlite*)"
    echo "  - Environment files (.env*)"
    echo ""
    
    echo "Development Files:"
    echo "  - Debug scripts (debug_*.py, *_debug.py)"
    echo "  - Test scripts (test_*.py, *_test.py)"
    echo "  - Migration scripts (migrate_*.py, *_migrate.py)"
    echo "  - Development docs (*_PROGRESS.md, *_SUMMARY.md)"
    echo "  - Frontend guides (*_GUIDE.md, *_REFERENCE.md)"
    echo "  - Log files (*.log)"
    echo ""
    
    echo "Build Artifacts:"
    echo "  - Next.js build (.next/, out/, build/)"
    echo "  - Node modules (node_modules/)"
    echo "  - Python cache (__pycache__/, *.pyc)"
    echo ""
}

# Main menu
show_menu() {
    echo "Options:"
    echo "  1) Categorize files"
    echo "  2) Clean up ignored files"
    echo "  3) Show git status"
    echo "  4) Show protected files"
    echo "  5) Add all safe files to git"
    echo "  6) Reset all changes"
    echo "  7) Exit"
    echo ""
}

# Function to add safe files
add_safe_files() {
    echo -e "${YELLOW}➕ Adding safe files to git...${NC}"
    echo ""
    
    # Add modified files (only if they exist and are not ignored)
    for file in apps/backend/main.py frontend/next.config.ts frontend/src/app/dashboard/page.tsx frontend/src/app/globals.css frontend/src/app/layout.tsx frontend/src/app/page.tsx frontend/src/components/BountyDisplay.tsx frontend/src/components/ChatInterface.tsx frontend/src/components/PublicDashboard.tsx frontend/src/components/WalletProvider.tsx frontend/src/middleware.ts src/database.py src/models.py src/repositories.py src/smart_contract_service.py tests/test_admin_endpoints_simple.py; do
        if [ -f "$file" ] && ! should_ignore "$file"; then
            git add "$file"
            echo "  ✓ Added: $file"
        fi
    done
    
    # Add new game-related files (only if they exist and are not ignored)
    for file in frontend/public/images/ frontend/src/components/BountyCard.tsx frontend/src/components/BountyGrid.tsx frontend/src/components/Navigation.tsx frontend/src/components/ScrollingBanner.tsx frontend/src/components/StakingInterface.tsx frontend/src/components/TeamBrowse.tsx frontend/src/components/TeamChat.tsx frontend/src/components/TokenDashboard.tsx frontend/src/components/TopNavigation.tsx frontend/src/components/WinnerShowcase.tsx frontend/src/components/layouts/ frontend/src/components/ui/ frontend/src/styles/ frontend/tailwind.config.ts scripts/simple_migrate_bounties.py; do
        if [ -e "$file" ] && ! should_ignore "$file"; then
            git add "$file"
            echo "  ✓ Added: $file"
        fi
    done
    
    echo -e "${GREEN}✅ Safe files added to git${NC}"
    echo ""
}

# Function to reset changes
reset_changes() {
    echo -e "${RED}⚠️  This will reset all changes. Are you sure? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        git reset --hard HEAD
        git clean -fd
        echo -e "${GREEN}✅ All changes reset${NC}"
    else
        echo -e "${YELLOW}❌ Reset cancelled${NC}"
    fi
    echo ""
}

# Main script logic
case "${1:-menu}" in
    "categorize")
        categorize_files
        ;;
    "cleanup")
        cleanup_ignored_files
        ;;
    "status")
        show_git_status
        ;;
    "protected")
        show_protected_files
        ;;
    "add")
        add_safe_files
        ;;
    "reset")
        reset_changes
        ;;
    "menu"|*)
        while true; do
            show_menu
            read -p "Choose an option (1-7): " choice
            echo ""
            
            case $choice in
                1) categorize_files ;;
                2) cleanup_ignored_files ;;
                3) show_git_status ;;
                4) show_protected_files ;;
                5) add_safe_files ;;
                6) reset_changes ;;
                7) echo -e "${GREEN}👋 Goodbye!${NC}"; exit 0 ;;
                *) echo -e "${RED}❌ Invalid option${NC}" ;;
            esac
            echo ""
        done
        ;;
esac
