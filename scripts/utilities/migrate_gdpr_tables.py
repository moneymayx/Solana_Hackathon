#!/usr/bin/env python3
"""
GDPR Database Migration Script

Adds GDPR compliance tables to the database:
- consent_records: Stores user consent for data processing
- Updates existing tables for GDPR compliance
"""

import asyncio
import sqlite3
from datetime import datetime
from pathlib import Path

async def migrate_gdpr_tables():
    """Add GDPR compliance tables to the database"""
    
    db_path = Path("billions.db")
    
    if not db_path.exists():
        print("❌ Database not found. Please run the main application first to create the database.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔧 Starting GDPR database migration...")
        
        # Create consent_records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                consent_type TEXT NOT NULL,
                granted BOOLEAN NOT NULL,
                timestamp DATETIME NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                consent_text TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create index for consent_records
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_consent_records_user_id 
            ON consent_records (user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_consent_records_type 
            ON consent_records (consent_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_consent_records_timestamp 
            ON consent_records (timestamp)
        """)
        
        # Add GDPR-related columns to existing tables if they don't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN gdpr_consent_essential BOOLEAN DEFAULT 1")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN gdpr_consent_analytics BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN gdpr_consent_marketing BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN gdpr_consent_research BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN data_deletion_requested BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN data_deletion_timestamp DATETIME")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Add GDPR-related event types to security_events
        gdpr_event_types = [
            "GDPR_DATA_DELETION_REQUEST",
            "GDPR_DATA_EXPORT_REQUEST", 
            "GDPR_CONSENT_UPDATE",
            "GDPR_CONSENT_CHANGE",
            "GDPR_RETENTION_CHECK",
            "GDPR_COMPLIANCE_AUDIT"
        ]
        
        for event_type in gdpr_event_types:
            cursor.execute("""
                INSERT OR IGNORE INTO security_events 
                (event_type, description, timestamp)
                VALUES (?, ?, ?)
            """, (event_type, f"GDPR event type: {event_type}", datetime.utcnow()))
        
        # Commit changes
        conn.commit()
        
        print("✅ GDPR database migration completed successfully!")
        print("   📋 Added consent_records table")
        print("   📋 Added GDPR columns to users table")
        print("   📋 Added GDPR event types to security_events")
        print("   📋 Created necessary indexes")
        
        # Verify migration
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='consent_records'")
        if cursor.fetchone():
            print("   ✅ consent_records table created")
        else:
            print("   ❌ consent_records table creation failed")
        
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        gdpr_columns = [col for col in columns if col.startswith('gdpr_') or col.startswith('data_')]
        print(f"   ✅ Added {len(gdpr_columns)} GDPR columns to users table: {gdpr_columns}")
        
        return True
        
    except Exception as e:
        print(f"❌ GDPR database migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_gdpr_tables())
