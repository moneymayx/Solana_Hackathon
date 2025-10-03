#!/usr/bin/env python3
"""
Migrate data from benita_agent.db to billions.db with schema mapping
"""
import sqlite3
import os
import shutil
from datetime import datetime

def migrate_database():
    """Migrate data from benita_agent.db to billions.db with schema mapping"""
    
    source_db = "benita_agent.db"
    target_db = "billions.db"
    
    print("🔄 Starting database migration with schema mapping...")
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
            
            # Check if table exists in target
            target_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            if not target_cursor.fetchone():
                print(f"  ⚠️  Table {table} doesn't exist in target database, skipping")
                continue
            
            # Get column information for both databases
            source_cursor.execute(f"PRAGMA table_info({table})")
            source_columns = {col[1]: col[0] for col in source_cursor.fetchall()}
            
            target_cursor.execute(f"PRAGMA table_info({table})")
            target_columns = {col[1]: col[0] for col in target_cursor.fetchall()}
            
            print(f"  Source columns: {list(source_columns.keys())}")
            print(f"  Target columns: {list(target_columns.keys())}")
            
            # Find common columns
            common_columns = set(source_columns.keys()) & set(target_columns.keys())
            print(f"  Common columns: {list(common_columns)}")
            
            if not common_columns:
                print(f"  ⚠️  No common columns found, skipping table")
                continue
            
            # Get row count
            source_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = source_cursor.fetchone()[0]
            print(f"  📊 {row_count} rows to migrate")
            
            if row_count > 0:
                # Get data from source table
                common_cols_str = ', '.join(common_columns)
                source_cursor.execute(f"SELECT {common_cols_str} FROM {table}")
                rows = source_cursor.fetchall()
                
                # Insert data into target table
                placeholders = ','.join(['?' for _ in common_columns])
                insert_sql = f"INSERT OR REPLACE INTO {table} ({common_cols_str}) VALUES ({placeholders})"
                
                try:
                    target_cursor.executemany(insert_sql, rows)
                    print(f"  ✅ Migrated {len(rows)} rows")
                except Exception as e:
                    print(f"  ❌ Failed to insert data: {str(e)}")
                    # Try to insert row by row to identify problematic data
                    success_count = 0
                    for i, row in enumerate(rows):
                        try:
                            target_cursor.execute(insert_sql, row)
                            success_count += 1
                        except Exception as row_error:
                            print(f"    Row {i+1} failed: {str(row_error)[:100]}...")
                    print(f"  ⚠️  Successfully migrated {success_count}/{len(rows)} rows")
        
        # Commit changes
        target_conn.commit()
        print(f"\n🎉 Migration completed!")
        
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

