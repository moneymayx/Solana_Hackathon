# Database Configuration Guide

## Current Setup

Your backend supports **two database configurations**:

### 1. 🏠 Local Development (SQLite)
- **Database:** `billions_local.db` (SQLite file)
- **Purpose:** Fast local testing without affecting production
- **Location:** Project root directory
- **Setup:** Zero configuration required
- **Use when:** Developing locally on localhost

### 2. 🚀 Production (PostgreSQL)  
- **Database:** DigitalOcean Managed PostgreSQL
- **Purpose:** Production data with backups and scaling
- **Location:** `billionsbounty-do-user-28276936-0.m.db.ondigitalocean.com`
- **Setup:** Connection string in `.env`
- **Use when:** Deploying to DigitalOcean or testing with production data

---

## How It Works

The backend (`src/database.py`) reads the `DATABASE_URL` environment variable:

```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./billions_local.db")
```

- **If `DATABASE_URL` is set** → Uses that database (PostgreSQL in production)
- **If `DATABASE_URL` is NOT set** → Falls back to local SQLite

---

## Current Status (Your Setup)

✅ **You are currently using:** **PostgreSQL (DigitalOcean)**

Your `.env` file contains:
```
DATABASE_URL=postgresql+asyncpg://doadmin:...@billionsbounty-do-user-28276936-0.m.db.ondigitalocean.com:25060/defaultdb?ssl=require
```

This means:
- ✅ All your chat messages are in the PostgreSQL database
- ✅ Backend is connected to production database
- ✅ Running on localhost but using production data

The local `billions.db` file exists but is **NOT being used** - it's empty.

---

## Recommended Setup

### Option A: Local Development (Recommended for Testing)

**When to use:** Building new features, testing locally without affecting production

**Setup:**
1. Comment out or remove `DATABASE_URL` from `.env`:
   ```bash
   # DATABASE_URL=postgresql+asyncpg://...  (commented out)
   ```

2. Backend will automatically use local SQLite:
   ```
   sqlite+aiosqlite:///./billions_local.db
   ```

3. Restart backend:
   ```bash
   cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
   python3 apps/backend/main.py
   ```

4. Database will be created automatically at project root

**Benefits:**
- ✅ Fast and lightweight
- ✅ No impact on production data
- ✅ No network latency
- ✅ Easy to reset/test

### Option B: Production Database (Current Setup)

**When to use:** Testing with real production data, deploying to production

**Setup:**
1. Keep `DATABASE_URL` in `.env`:
   ```bash
   DATABASE_URL=postgresql+asyncpg://doadmin:...@billionsbounty-do-user-28276936-0.m.db.ondigitalocean.com:25060/defaultdb?ssl=require
   ```

2. Backend connects to DigitalOcean PostgreSQL

3. All data persists in production database

**Benefits:**
- ✅ Real production data for testing
- ✅ Managed backups
- ✅ Scalable for production use
- ⚠️ **Caution:** Changes affect production!

---

## Switching Between Databases

### To use LOCAL SQLite:
```bash
# In your .env file, comment out DATABASE_URL:
# DATABASE_URL=postgresql+asyncpg://...

# Restart backend
python3 apps/backend/main.py
```

### To use PRODUCTION PostgreSQL:
```bash
# In your .env file, uncomment DATABASE_URL:
DATABASE_URL=postgresql+asyncpg://doadmin:...@billionsbounty...

# Restart backend
python3 apps/backend/main.py
```

---

## Checking Which Database You're Using

### Method 1: Check Backend Logs
When backend starts, it shows:
```
✅ Database connected: postgresql://...  (Production)
✅ Database connected: sqlite://...      (Local)
```

### Method 2: Check .env File
```bash
cat .env | grep DATABASE_URL
```

- If you see `postgresql+asyncpg://...` → Using PostgreSQL (production)
- If commented or missing → Using SQLite (local)

### Method 3: Query Your Data
```bash
# Check if conversations table has data
curl http://localhost:8000/api/bounty/1/messages/public?limit=1
```

- If you see messages → Connected to production PostgreSQL
- If empty/no messages → Using local SQLite

---

## Database Files

### PostgreSQL (Production)
- **Host:** `billionsbounty-do-user-28276936-0.m.db.ondigitalocean.com`
- **Port:** `25060`
- **Database:** `defaultdb`
- **Managed by:** DigitalOcean (automatic backups, scaling, etc.)

### SQLite (Local)
- **File:** `billions_local.db` (recommended name)
- **Location:** Project root `/Users/jaybrantley/myenv/Hackathon/Billions_Bounty/`
- **Managed by:** You (manual backups if needed)
- **Can be deleted** and recreated anytime for fresh start

---

## Your Messages Are Safe! ✅

Your chat messages are in the **PostgreSQL production database**, not the local SQLite file.

The empty `billions.db` file in your project root is unused because your backend is configured to use PostgreSQL.

To see your messages, keep using the current setup (PostgreSQL) or switch to local development if you want to test in isolation.

---

## Quick Reference

| Scenario | Database | DATABASE_URL in .env | Chat Messages Location |
|----------|----------|---------------------|----------------------|
| **Current Setup** | PostgreSQL | ✅ Set | DigitalOcean PostgreSQL |
| **Local Dev (Recommended)** | SQLite | ❌ Commented out | `billions_local.db` file |
| **Production Deploy** | PostgreSQL | ✅ Set | DigitalOcean PostgreSQL |

---

## Need Help?

- **To see your production messages:** Keep current setup, refresh browser
- **To test locally without affecting production:** Comment out `DATABASE_URL` in `.env`
- **To reset local database:** Delete `billions_local.db` and restart backend

Your messages are safe in PostgreSQL! 🎉

