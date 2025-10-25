# Database Migrations Guide

## Overview

This guide covers how database migrations are handled in the Billions Bounty project, including the recent referral system migration.

## Migration Files

All migration files are located in the project root and follow the naming convention:
- `migrate_<description>.sql` - SQL migration files
- `migrate_<description>.py` - Python migration scripts (if complex logic needed)

### Current Migrations

1. **`migrate_add_referral_fields.sql`** - Adds referral tracking fields to `free_question_usage` table
   - Added: `referred_by` (wallet address of the referrer)
   - Added: `referrer_reward_pending` (boolean to track pending rewards)
   - Added: Index on `referred_by` for faster lookups

## Running Migrations

### Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run the migration
python3 << 'EOF'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', '')

async def run():
    engine = create_async_engine(DATABASE_URL)
    with open('migrate_add_referral_fields.sql', 'r') as f:
        sql = f.read()
    async with engine.begin() as conn:
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    await conn.execute(statement)
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"Error: {e}")
    await engine.dispose()

asyncio.run(run())
EOF
```

### Production Deployment

#### Option 1: Manual Migration (Recommended for Production)

```bash
# SSH into your production server
ssh user@your-production-server.com

# Navigate to project directory
cd /path/to/Billions_Bounty

# Activate virtual environment
source venv/bin/activate

# Run migration
python3 -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', '')

async def run():
    engine = create_async_engine(DATABASE_URL)
    with open('migrate_add_referral_fields.sql', 'r') as f:
        sql = f.read()
    async with engine.begin() as conn:
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    await conn.execute(statement)
                    print(f'✅ Executed: {statement[:60]}')
                except Exception as e:
                    if 'already exists' not in str(e):
                        print(f'⚠️  Error: {e}')
                    else:
                        print(f'✅ Already exists: {statement[:60]}')
    await engine.dispose()
    print('✅ Migration completed!')

asyncio.run(run())
"
```

#### Option 2: Using psql (If Available)

```bash
# Set your database URL
export DATABASE_URL="postgresql://user:password@host:5432/database"

# Run the migration
psql "$DATABASE_URL" -f migrate_add_referral_fields.sql
```

#### Option 3: Automated Migration (Future)

Create a `deploy.sh` script that automates this:

```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e  # Exit on error

echo "🚀 Starting production deployment..."

# Pull latest code
git pull origin main

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
echo "📦 Running database migrations..."
python3 << 'EOF'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os
import glob

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', '')

async def run_migration(file):
    engine = create_async_engine(DATABASE_URL)
    with open(file, 'r') as f:
        sql = f.read()
    async with engine.begin() as conn:
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    await conn.execute(statement)
                except Exception as e:
                    if 'already exists' not in str(e):
                        print(f'Error: {e}')
    await engine.dispose()

async def run_all_migrations():
    migrations = sorted(glob.glob('migrate_*.sql'))
    for migration in migrations:
        print(f'Running {migration}...')
        await run_migration(migration)
        print(f'✅ {migration} completed')

asyncio.run(run_all_migrations())
EOF

# Restart the backend
echo "🔄 Restarting backend..."
sudo systemctl restart billions-bounty-backend

echo "✅ Deployment complete!"
```

## Migration Best Practices

### 1. Always Backup First

```bash
# Create a database backup before running migrations
pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Test Migrations on Staging

Always test migrations on a staging environment that mirrors production before running them in production.

### 3. Run Migrations During Low Traffic

Schedule migrations during periods of low user activity to minimize downtime.

### 4. Monitor After Deployment

After running migrations, monitor:
- Application logs for errors
- Database performance metrics
- User-facing features that depend on the migrated tables

### 5. Keep Migration Files in Version Control

All migration files should be committed to version control so:
- All developers can run them locally
- Production deployments are reproducible
- Migration history is tracked

## Rollback Procedures

If a migration causes issues, you can rollback:

```bash
# Rollback the referral fields migration
python3 -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', '')

async def rollback():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Drop the added fields
        await conn.execute('ALTER TABLE free_question_usage DROP COLUMN IF EXISTS referred_by CASCADE')
        await conn.execute('ALTER TABLE free_question_usage DROP COLUMN IF EXISTS referrer_reward_pending CASCADE')
        await conn.execute('DROP INDEX IF EXISTS idx_free_question_usage_referred_by')
    await engine.dispose()
    print('✅ Rollback completed!')

asyncio.run(rollback())
"
```

## Adding New Migrations

When you need to add a new migration:

1. **Create the migration file**: `migrate_<description>.sql`
2. **Add SQL statements**: Use `IF NOT EXISTS` clauses where possible
3. **Test locally**: Run the migration on your local database
4. **Commit to git**: Add and commit the migration file
5. **Document**: Update this file with the new migration details

Example new migration:

```sql
-- migrate_add_<feature>.sql

-- Add new fields to existing table
ALTER TABLE table_name
ADD COLUMN IF NOT EXISTS new_field VARCHAR(255);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_table_name_new_field ON table_name(new_field);
```

## Continuous Integration

To automatically run migrations in CI/CD:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run migrations
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          python3 -m pip install sqlalchemy asyncpg python-dotenv
          python3 run_migration.py
```

## Monitoring and Verification

After running migrations, verify they completed successfully:

```python
# Verify migration applied
from src.database import get_db
from sqlalchemy import inspect

async def verify_migration():
    async for session in get_db():
        inspector = inspect(session.bind)
        columns = [col['name'] for col in inspector.get_columns('free_question_usage')]
        
        assert 'referred_by' in columns, "Migration failed: referred_by not found"
        assert 'referrer_reward_pending' in columns, "Migration failed: referrer_reward_pending not found"
        
        print("✅ Migration verified successfully!")
        break

# Run verification
import asyncio
asyncio.run(verify_migration())
```

## Questions?

If you encounter issues with migrations, check:
1. Database connection is working
2. User has ALTER TABLE permissions
3. No conflicting migrations running simultaneously
4. Migration file syntax is correct

For help, contact the development team.
