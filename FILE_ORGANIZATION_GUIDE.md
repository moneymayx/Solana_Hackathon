# File Organization Guide

## Overview
This guide explains how files are organized and protected in the Billions Bounty project to ensure security, maintainability, and proper version control.

## File Categories

### 🔒 **SECURITY CRITICAL** (Never Committed)
These files contain sensitive information and are **NEVER** committed to git:

#### Private Keys & Certificates
- `*.pem`, `*.key` - Private keys and certificates
- `*-key.pem`, `*-private.pem` - Specific key files
- `lottery-authority-*.json` - Wallet keypairs
- `WALLET_INFO.md` - Wallet information

#### Database Files
- `*.db`, `*.sqlite`, `*.sqlite3` - Database files
- `billions.db` - Main database
- `*.db.backup*` - Database backups

#### Environment Files
- `.env*` - All environment files
- `.env.local`, `.env.development.local` - Local environment files

### 🚫 **DEVELOPMENT FILES** (Keep Local)
These files are for development only and should not be committed:

#### Debug & Test Scripts
- `debug_*.py` - Debug scripts
- `*_debug.py` - Debug files
- `test_*.py` - Test scripts (except official tests)
- `*_test.py` - Test files
- `migrate_*.py` - Migration scripts
- `*_migrate.py` - Migration files
- `simple_*.py` - Simple utility scripts

#### Development Documentation
- `*_PROGRESS.md` - Progress tracking
- `*_SUMMARY.md` - Summary files
- `*_COMPLETE.md` - Completion files
- `START_HERE.md` - Getting started guides
- `IMPLEMENTATION_*.md` - Implementation docs
- `REDESIGN_*.md` - Redesign documentation
- `FRONTEND_*.md` - Frontend documentation

#### Frontend Development Files
- `frontend/*_GUIDE.md` - Frontend guides
- `frontend/*_REFERENCE.md` - Reference files
- `frontend/README_*.md` - README files
- `frontend/REDESIGN_*.md` - Redesign docs
- `frontend/update-*.sh` - Update scripts
- `frontend/*-banner-*.sh` - Banner scripts

#### Log Files
- `*.log` - All log files
- `logs/` - Log directories
- `frontend/*.log` - Frontend logs

#### Test API Endpoints
- `frontend/src/app/test-api/` - Test API routes
- `frontend/src/app/features/` - Feature routes
- `frontend/src/app/staking/` - Staking routes
- `frontend/src/app/stats/` - Stats routes
- `frontend/src/app/teams/` - Teams routes
- `frontend/src/app/token/` - Token routes

### ✅ **GAME FILES** (Should Be Committed)
These files are part of the core game and should be committed:

#### Core Backend
- `apps/backend/main.py` - Main FastAPI application
- `src/models.py` - Database models
- `src/repositories.py` - Data repositories
- `src/database.py` - Database configuration
- `src/smart_contract_service.py` - Smart contract service

#### Core Frontend
- `frontend/src/app/page.tsx` - Homepage
- `frontend/src/app/layout.tsx` - App layout
- `frontend/src/app/globals.css` - Global styles
- `frontend/tailwind.config.ts` - Tailwind configuration
- `frontend/next.config.ts` - Next.js configuration

#### Game Components
- `frontend/src/components/BountyCard.tsx` - Bounty card component
- `frontend/src/components/BountyGrid.tsx` - Bounty grid component
- `frontend/src/components/ScrollingBanner.tsx` - Scrolling banner
- `frontend/src/components/TopNavigation.tsx` - Top navigation
- `frontend/src/components/WinnerShowcase.tsx` - Winner showcase
- `frontend/src/components/ChatInterface.tsx` - Chat interface
- `frontend/src/components/BountyDisplay.tsx` - Bounty display

#### Game Assets
- `frontend/public/images/` - Game images
- `frontend/src/components/layouts/` - Layout components
- `frontend/src/components/ui/` - UI components
- `frontend/src/styles/` - Style files

#### Official Tests
- `tests/test_admin_endpoints_simple.py` - Official test files
- `tests/` - Official test directory

## File Organization Script

### Usage
```bash
# Run the organization script
./organize_files.sh

# Or run specific commands
./organize_files.sh categorize    # Categorize files
./organize_files.sh cleanup      # Clean up ignored files
./organize_files.sh status       # Show git status
./organize_files.sh protected    # Show protected files
./organize_files.sh add          # Add safe files to git
./organize_files.sh reset        # Reset all changes
```

### What the Script Does
1. **Categorizes files** into safe/unsafe categories
2. **Cleans up** accidentally tracked files
3. **Shows git status** with clear categorization
4. **Adds safe files** to git automatically
5. **Protects sensitive files** from being committed

## Git Ignore Patterns

### Root `.gitignore`
```gitignore
# Security Critical
*.pem, *.key, *.keypair.json
*.db, *.sqlite*
.env*

# Development Files
debug_*.py, *_debug.py
test_*.py, *_test.py
migrate_*.py, *_migrate.py
*_PROGRESS.md, *_SUMMARY.md
*_COMPLETE.md, START_HERE.md

# Frontend Development
frontend/*_GUIDE.md
frontend/*_REFERENCE.md
frontend/README_*.md
frontend/update-*.sh
frontend/*.log
frontend/src/app/test-api/
```

### Frontend `.gitignore`
```gitignore
# Development Files
*_GUIDE.md, *_REFERENCE.md
README_*.md, REDESIGN_*.md
update-*.sh, *-banner-*.sh
*.log, logs/

# Test API Endpoints
src/app/test-api/
src/app/features/
src/app/staking/
src/app/stats/
src/app/teams/
src/app/token/

# Build Artifacts
.next/, out/, build/
node_modules/
```

## Security Best Practices

### 1. **Never Commit Sensitive Data**
- Private keys, certificates, wallet files
- Database files with user data
- Environment files with secrets
- Debug logs with sensitive information

### 2. **Use Environment Variables**
- Store secrets in `.env` files
- Use different `.env` files for different environments
- Never commit `.env` files

### 3. **Regular Cleanup**
- Run `./organize_files.sh cleanup` regularly
- Check git status before committing
- Remove accidentally tracked sensitive files

### 4. **File Permissions**
- Ensure sensitive files have restricted permissions
- Use `chmod 600` for private keys
- Use `chmod 644` for regular files

## Development Workflow

### 1. **Before Starting Work**
```bash
# Check current status
./organize_files.sh status

# Clean up any issues
./organize_files.sh cleanup
```

### 2. **During Development**
- Create debug/test files as needed
- Use descriptive names for development files
- Keep sensitive data in environment variables

### 3. **Before Committing**
```bash
# Categorize files
./organize_files.sh categorize

# Add safe files
./organize_files.sh add

# Check final status
git status
```

### 4. **After Committing**
- Verify no sensitive files were committed
- Check git log for any accidental commits
- Clean up local development files

## Troubleshooting

### Common Issues

#### 1. **Accidentally Committed Sensitive File**
```bash
# Remove from git but keep locally
git rm --cached sensitive_file.txt

# Add to .gitignore
echo "sensitive_file.txt" >> .gitignore

# Commit the .gitignore change
git add .gitignore
git commit -m "Add sensitive_file.txt to .gitignore"
```

#### 2. **File Not Being Ignored**
- Check `.gitignore` patterns
- Ensure no conflicting patterns
- Use `git check-ignore -v filename` to debug

#### 3. **Development Files Being Tracked**
```bash
# Remove from tracking
git rm --cached development_file.py

# Add to .gitignore
echo "development_file.py" >> .gitignore
```

### Getting Help
- Run `./organize_files.sh protected` to see all protected patterns
- Check `.gitignore` files for specific patterns
- Use `git status --ignored` to see ignored files

## Summary

This organization system ensures:
- ✅ **Security**: Sensitive files are never committed
- ✅ **Clean Repository**: Only game-related files are tracked
- ✅ **Development Friendly**: Easy to work with development files
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Automated**: Scripts handle most organization tasks

Remember: When in doubt, run `./organize_files.sh categorize` to see how files are classified!
