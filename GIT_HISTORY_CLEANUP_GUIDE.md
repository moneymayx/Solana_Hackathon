# Git History Cleanup Guide

**CRITICAL**: This process is IRREVERSIBLE. Follow steps carefully.

## What You're About To Do

You're removing these sensitive files from **all git history**:
- `ai_decision_key.pem`
- `ai_decision_key_public.pem`
- `backend_authority_key.pem`
- `backend_authority_key_public.pem`
- `src/personality.py`
- `.env` (if it exists in history)

## Step-by-Step Process

### Step 1: Create Backup (CRITICAL)

```bash
# Navigate to parent directory
cd /Users/jaybrantley/myenv/Hackathon

# Create a full backup
cp -r Billions_Bounty Billions_Bounty.backup.$(date +%Y%m%d_%H%M%S)

# Verify backup was created
ls -la | grep Billions_Bounty
```

### Step 2: Remove Remote Reference (Temporarily)

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty

# Show current remotes
git remote -v

# Backup remote URL (save this!)
git remote get-url origin

# Remove remote temporarily (prevents accidental push)
git remote remove origin
```

### Step 3: Clean Git History

Run these commands **one at a time**, checking for errors after each:

```bash
# Remove ai_decision_key.pem
git filter-repo --path ai_decision_key.pem --invert-paths --force

# Remove ai_decision_key_public.pem
git filter-repo --path ai_decision_key_public.pem --invert-paths --force

# Remove backend_authority_key.pem
git filter-repo --path backend_authority_key.pem --invert-paths --force

# Remove backend_authority_key_public.pem
git filter-repo --path backend_authority_key_public.pem --invert-paths --force

# Remove personality.py from history
git filter-repo --path src/personality.py --invert-paths --force

# Remove .env if it was ever committed
git filter-repo --path .env --invert-paths --force
```

### Step 4: Verify Cleanup

```bash
# Check that sensitive files are gone from history
git log --all --full-history --pretty=format: --name-only -- '*.pem' | head -10
git log --all --full-history --pretty=format: --name-only -- 'src/personality.py' | head -10
git log --all --full-history --pretty=format: --name-only -- '.env' | head -10

# If these return empty, cleanup was successful!
```

### Step 5: Re-add Remote

```bash
# Add remote back (use the URL you saved from Step 2)
git remote add origin <YOUR_REMOTE_URL>

# Verify
git remote -v
```

### Step 6: Force Push to Remote

⚠️ **WARNING**: This will overwrite remote history. Anyone else must re-clone!

```bash
# Push cleaned history to remote
git push origin --force --all
git push origin --force --tags

# Verify push was successful
git status
```

### Step 7: Verify on Remote

1. Go to your GitHub/GitLab repository
2. Check file history - sensitive files should be gone
3. Check GitGuardian dashboard - alerts should resolve within 24 hours

### Step 8: Rotate All Keys

Now that history is clean, generate new keys:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty

# Activate virtual environment
source venv/bin/activate

# Generate new keys
python3 scripts/setup/generate_backend_keys.py

# Verify new keys were created
ls -la config/keys/
```

### Step 9: Update .env File

```bash
# Create new .env from template
cp config/examples/.env.example .env

# Edit with your new credentials
nano .env  # or use your preferred editor

# Verify .env is in .gitignore
grep "^\.env" .gitignore
```

### Step 10: Final Verification

```bash
# Check git status - .env should NOT appear
git status

# Verify sensitive files are gitignored
git check-ignore .env config/keys/*.pem src/personality.py

# If all show as ignored, you're good!
```

## What If Something Goes Wrong?

### Restore from Backup

```bash
cd /Users/jaybrantley/myenv/Hackathon

# Remove corrupted repo
rm -rf Billions_Bounty

# Restore from backup
cp -r Billions_Bounty.backup.YYYYMMDD_HHMMSS Billions_Bounty

# Start over
cd Billions_Bounty
```

## Important Notes

### After Force Push

**Anyone with a clone of this repo MUST:**

```bash
# Delete their local clone
rm -rf Billions_Bounty

# Fresh clone from remote
git clone <YOUR_REMOTE_URL>
```

**DO NOT** try to pull or merge - it will fail and cause issues.

### GitGuardian Alerts

- Alerts may take 24-48 hours to resolve
- If alerts persist, contact GitGuardian support
- Show them proof that files were removed from history

### If You Can't Rewrite History

If you have collaborators who can't re-clone, or if rewriting history is too risky:

**Alternative Approach:**

1. **Create a new repository**
2. **Copy code (not .git folder) to new repo**
3. **Initialize fresh git history**
4. **Archive old repository as private**

This is safer but loses git history.

## Checklist

Before proceeding, confirm:

- [ ] I have created a backup
- [ ] I have saved my remote URL
- [ ] I understand this is irreversible
- [ ] I know anyone else must re-clone
- [ ] I have new keys ready to generate
- [ ] I understand .env must never be committed

## Ready to Proceed?

If all checkboxes are checked, proceed with Step 1.

If uncertain, ask for help or use the alternative approach.

