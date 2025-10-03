#!/usr/bin/env python3
"""
Migrate data from benita_agent.db to billions.db
"""
import sqlite3
import os
import shutil
from datetime import datetime

def migrate_database():
    """Migrate data from benita_agent.db to billions.db"""
    
    source_db = "benita_agent.db"
    target_db = "billions.db"
    
    print("🔄 Starting database migration...")
    print(f"Source: {source_db}")
    print(f"Target: {target_db}")
    
    # Check if source database exists
    if not os.path.exists(source_db):
        print(f"❌ Source database {source_db} not found!")
        return
    
    # Backup target database if it exists
    if os.path.exists(target_db):
        backup_name = f"{target_db}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(target_db, backup_name)
        print(f"📦 Backed up existing {target_db} to {backup_name}")
    
    # Connect to both databases
    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)
    
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()
    
    try:
        # Get all tables from source database
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in source_cursor.fetchall()]
        
        print(f"📋 Found {len(tables)} tables to migrate:")
        for table in tables:
            print(f"  - {table}")
        
        # Migrate each table
        for table in tables:
            print(f"\n🔄 Migrating table: {table}")
            
            # Get table schema
            source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
            schema = source_cursor.fetchone()
            
            if schema and schema[0]:
                # Create table in target database (ignore if exists)
                try:
                    target_cursor.execute(schema[0])
                    print(f"  ✅ Created table schema")
                except sqlite3.OperationalError as e:
                    if "already exists" in str(e):
                        print(f"  ⚠️  Table already exists, skipping schema creation")
                    else:
                        raise e
            
            # Get row count
            source_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = source_cursor.fetchone()[0]
            print(f"  📊 {row_count} rows to migrate")
            
            if row_count > 0:
                # Get all data from source table
                source_cursor.execute(f"SELECT * FROM {table}")
                rows = source_cursor.fetchall()
                
                # Get column names
                source_cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in source_cursor.fetchall()]
                
                # Insert data into target table
                placeholders = ','.join(['?' for _ in columns])
                insert_sql = f"INSERT OR REPLACE INTO {table} VALUES ({placeholders})"
                
                target_cursor.executemany(insert_sql, rows)
                print(f"  ✅ Migrated {len(rows)} rows")
        
        # Commit changes
        target_conn.commit()
        print(f"\n🎉 Migration completed successfully!")
        
        # Show final statistics
        print(f"\n📊 Final database statistics:")
        target_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        final_tables = target_cursor.fetchall()
        
        for table in final_tables:
            table_name = table[0]
            target_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = target_cursor.fetchone()[0]
            print(f"  {table_name}: {count:,} rows")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        target_conn.rollback()
    finally:
        source_conn.close()
        target_conn.close()

if __name__ == "__main__":
    migrate_database()
