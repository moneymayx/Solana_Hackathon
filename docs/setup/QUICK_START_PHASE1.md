# Phase 1: Quick Start Commands
**Copy and paste these commands to get started!**

---

## 📋 Step-by-Step Commands

### **Step 1: Install PostgreSQL & Redis (Mac)**

```bash
# Install both with Homebrew
brew install postgresql@14 redis

# Start services
brew services start postgresql@14
brew services start redis

# Verify installations
psql --version
redis-cli ping  # Should return PONG
```

---

### **Step 2: Create Database**

```bash
# Connect to PostgreSQL
psql postgres

# Run these commands in psql:
```

```sql
CREATE DATABASE billions_bounty;
CREATE EXTENSION IF NOT EXISTS vector;
\c billions_bounty
\dx  -- Verify vector extension
\q
```

---

### **Step 3: Install Python Dependencies**

```bash
# Activate your virtual environment
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate  # or source venv_new/bin/activate

# Install dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Verify key packages
python3 -c "import pgvector; print('✅ pgvector installed')"
python3 -c "import openai; print('✅ openai installed')"
python3 -c "import celery; print('✅ celery installed')"
```

---

### **Step 4: Update .env File**

Create or update `.env` in project root:

```bash
# Open .env in your editor
nano .env  # or code .env, vim .env, etc.
```

Add these lines (update with your values):

```env
# PostgreSQL Configuration
DATABASE_URL=postgresql+asyncpg://$(whoami)@localhost:5432/billions_bounty

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=your_openai_key_here

# Feature Flags
USE_ENHANCED_CONTEXT=false
USE_TOKEN_ECONOMICS=false
USE_TEAM_FEATURES=false

# Keep all your existing environment variables below...
```

---

### **Step 5: Backup Current Database**

```bash
# Backup SQLite database
cp billions.db billions.db.backup_$(date +%Y%m%d_%H%M%S)

# Verify backup
ls -lh billions.db*
```

---

### **Step 6: Run Migration**

```bash
# Make script executable
chmod +x scripts/migrate_to_postgresql.py

# Run migration
python3 scripts/migrate_to_postgresql.py
```

**The script will:**
1. ✅ Verify PostgreSQL connection
2. ✅ Check pgvector extension
3. ✅ Count SQLite records
4. ✅ Ask for confirmation
5. ✅ Create PostgreSQL schema
6. ✅ Migrate all data
7. ✅ Verify data integrity

---

## 🚨 If You Encounter Issues

### PostgreSQL not installing:
```bash
# Try updating Homebrew
brew update
brew upgrade

# Retry installation
brew install postgresql@14
```

### Redis not starting:
```bash
# Check status
brew services list

# Restart Redis
brew services restart redis
```

### Can't create vector extension:
```bash
# Install pgvector manually
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Then try again in psql:
psql billions_bounty -c "CREATE EXTENSION vector;"
```

### Python packages failing:
```bash
# Make sure you're in virtual environment
which python3  # Should show path in venv

# Try installing one by one
pip3 install pgvector
pip3 install openai
pip3 install celery
pip3 install asyncpg
pip3 install psycopg2-binary
```

---

## ✅ Verification Commands

**Run these to verify setup:**

```bash
# 1. Check PostgreSQL
pg_isready
psql billions_bounty -c "SELECT version();"

# 2. Check pgvector
psql billions_bounty -c "\dx vector"

# 3. Check Redis
redis-cli ping

# 4. Check Python packages
python3 << EOF
import pgvector
import openai
import celery
import asyncpg
print("✅ All packages installed!")
EOF

# 5. Check database connection
python3 << EOF
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()
async def test():
    engine = create_async_engine(os.getenv("DATABASE_URL"))
    async with engine.begin() as conn:
        result = await conn.execute_text("SELECT 1")
        print("✅ PostgreSQL connection works!")
    await engine.dispose()

asyncio.run(test())
EOF
```

---

## 📞 Need Help?

If setup takes longer than expected or you hit errors:

**Option 1: Use Cloud PostgreSQL (Easiest)**
- Go to https://supabase.com/dashboard
- Create free project
- Copy connection string
- Update DATABASE_URL in .env
- They have pgvector pre-installed!

**Option 2: Let me know**
- Tell me what error you're seeing
- Copy/paste the error message
- I'll help troubleshoot

---

## ⏭️ What's Next?

Once migration is complete:

1. ✅ Test your existing app still works
2. ✅ Add new models to `src/models.py`
3. ✅ Create semantic search service
4. ✅ Create pattern detector service
5. ✅ Create context builder service
6. ✅ Integrate with AI agent

**Estimated time for setup: 1-2 hours**

Let me know when you're ready for the next steps! 🚀


