# Phase 1: Context Window Management - Setup Guide
**Start Date:** October 19, 2025  
**Estimated Duration:** 2 weeks  
**Current Step:** Database Setup & Dependencies

---

## ✅ Prerequisites Checklist

Before proceeding, ensure you have:
- [ ] PostgreSQL 14+ installed
- [ ] Redis installed and running
- [ ] Python 3.8+ (you have this)
- [ ] Virtual environment activated [[memory:5753892]]
- [ ] Backup of current billions.db

---

## 🔧 Step 1: Install PostgreSQL (Mac)

### Option A: Homebrew (Recommended)
```bash
# Install PostgreSQL
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Verify installation
psql --version
```

### Option B: Postgres.app
1. Download from https://postgresapp.com/
2. Drag to Applications
3. Open and initialize

### Option C: Cloud PostgreSQL (Easiest)
**Recommended for quick setup:**
- **Supabase:** https://supabase.com (Free tier: 500MB)
- **Railway:** https://railway.app (Free tier: 512MB)
- **Neon:** https://neon.tech (Free tier: 3GB)

---

## 🔧 Step 2: Install Redis (Mac)

```bash
# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

---

## 🔧 Step 3: Create PostgreSQL Database

### Local PostgreSQL:
```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE billions_bounty;

# Create user (optional, or use your account)
CREATE USER billions_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE billions_bounty TO billions_user;

# Exit
\q
```

### Cloud PostgreSQL:
1. Create database in your cloud provider dashboard
2. Copy the connection string
3. It will look like: `postgresql://user:pass@host:5432/dbname`

---

## 🔧 Step 4: Install pgvector Extension

```bash
# Connect to your database
psql billions_bounty

# Install extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify installation
\dx
# Should show 'vector' in the list

# Exit
\q
```

**If pgvector not available:**
```bash
# Install pgvector
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
make install  # May need sudo

# Then retry CREATE EXTENSION
```

---

## 🔧 Step 5: Update Environment Variables

Create/update `.env` file in project root:

```bash
# File: .env (create if doesn't exist)

# ===========================
# DATABASE CONFIGURATION
# ===========================

# OLD (SQLite - keep for backup)
# DATABASE_URL=sqlite+aiosqlite:///./billions.db

# NEW (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://billions_user:your_secure_password@localhost:5432/billions_bounty

# OR if using cloud PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# ===========================
# REDIS CONFIGURATION
# ===========================
REDIS_URL=redis://localhost:6379/0

# ===========================
# OPENAI API (for embeddings)
# ===========================
OPENAI_API_KEY=your_openai_api_key_here

# ===========================
# FEATURE FLAGS
# ===========================
USE_ENHANCED_CONTEXT=false  # Will enable after testing
USE_TOKEN_ECONOMICS=false   # Phase 2
USE_TEAM_FEATURES=false     # Phase 3

# ===========================
# EXISTING CONFIGURATION
# ===========================
# (Keep all your existing env vars below)
ANTHROPIC_API_KEY=your_existing_key
SOLANA_RPC_URL=your_existing_url
# ... etc
```

---

## 🔧 Step 6: Install Python Dependencies

```bash
# Activate virtual environment (you should do this in your venv)
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate  # or venv_new/bin/activate

# Upgrade pip
pip3 install --upgrade pip

# Install new dependencies
pip3 install -r requirements.txt

# Verify installations
python3 -c "import pgvector; print('pgvector:', pgvector.__version__)"
python3 -c "import openai; print('openai:', openai.__version__)"
python3 -c "import celery; print('celery:', celery.__version__)"
```

---

## 🔧 Step 7: Backup Current SQLite Database

**CRITICAL: Do this before migration!**

```bash
# Backup current database
cp billions.db billions.db.backup_$(date +%Y%m%d_%H%M%S)

# Verify backup exists
ls -lh billions.db.backup_*
```

---

## 🔧 Step 8: Create Database Migration Script

I'll create this script for you in the next step. It will:
1. Read all data from SQLite
2. Write all data to PostgreSQL
3. Verify data integrity
4. Provide rollback capability

---

## ✅ Verification Checklist

Before proceeding to migration, verify:
- [ ] PostgreSQL is running: `pg_isready`
- [ ] Redis is running: `redis-cli ping`
- [ ] Can connect to PostgreSQL: `psql billions_bounty -c "SELECT version();"`
- [ ] pgvector extension installed: `psql billions_bounty -c "\dx vector"`
- [ ] .env file updated with DATABASE_URL
- [ ] SQLite database backed up
- [ ] All Python dependencies installed successfully

---

## 🚨 Troubleshooting

### PostgreSQL won't start:
```bash
# Check if port 5432 is in use
lsof -i :5432

# Restart PostgreSQL
brew services restart postgresql@14
```

### Redis won't start:
```bash
# Check if port 6379 is in use
lsof -i :6379

# Restart Redis
brew services restart redis
```

### pgvector won't install:
- Try cloud PostgreSQL (Supabase/Railway) - they have pgvector pre-installed
- Or use Docker: `docker run -e POSTGRES_PASSWORD=postgres -p 5432:5432 pgvector/pgvector`

### Can't connect to PostgreSQL:
```bash
# Check PostgreSQL is running
brew services list | grep postgresql

# Try default connection
psql -d postgres -U $(whoami)
```

---

## 📋 Next Steps

Once all verification items are checked:
1. ✅ Run `python3 scripts/migrate_to_postgresql.py` (I'll create this)
2. ✅ Verify data migration
3. ✅ Update `src/models.py` with new models
4. ✅ Run Alembic migrations
5. ✅ Start implementing services

---

## ⏱️ Estimated Time

- PostgreSQL setup: 15-30 minutes
- Redis setup: 5-10 minutes
- Dependencies install: 10-15 minutes
- Database migration: 20-30 minutes
- **Total: 1-1.5 hours**

---

## 🆘 Need Help?

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Try cloud PostgreSQL if local setup fails
4. Let me know and I'll help debug!

---

**Ready?** Complete the verification checklist above, then let me know and I'll create the migration script! 🚀


