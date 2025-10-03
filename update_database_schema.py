"""
Update database schema to add new columns to existing tables
"""
import sqlite3
import os
from datetime import datetime

def update_database_schema():
    """Add new columns to the existing database schema"""
    
    # Database file path
    db_path = "billions.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    # Backup the database
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"📦 Creating backup: {backup_path}")
    
    # Read the original database
    with open(db_path, 'rb') as original:
        with open(backup_path, 'wb') as backup:
            backup.write(original.read())
    
    print("✅ Backup created successfully")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get current table schema
        cursor.execute("PRAGMA table_info(users)")
        current_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Current users table columns: {current_columns}")
        
        # Define new columns to add
        new_columns = [
            ("password_hash", "TEXT"),
            ("is_verified", "BOOLEAN DEFAULT FALSE"),
            ("anonymous_free_questions_used", "INTEGER DEFAULT 0"),
            ("has_used_anonymous_questions", "BOOLEAN DEFAULT FALSE"),
            ("full_name", "TEXT"),
            ("date_of_birth", "DATETIME"),
            ("phone_number", "TEXT"),
            ("address", "TEXT"),
            ("kyc_status", "TEXT DEFAULT 'not_submitted'"),
            ("kyc_provider", "TEXT"),
            ("kyc_reference_id", "TEXT")
        ]
        
        # Add new columns that don't exist
        for column_name, column_type in new_columns:
            if column_name not in current_columns:
                try:
                    alter_sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                    print(f"🔧 Adding column: {column_name} {column_type}")
                    cursor.execute(alter_sql)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"⚠️  Could not add column {column_name}: {e}")
            else:
                print(f"ℹ️  Column {column_name} already exists")
        
        # Create EmailVerification table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("✅ EmailVerification table created/verified")
        
        # Update FreeQuestions table to add missing columns
        cursor.execute("PRAGMA table_info(free_questions)")
        free_questions_columns = [row[1] for row in cursor.fetchall()]
        
        free_questions_new_columns = [
            ("last_used", "DATETIME"),
            ("expires_at", "DATETIME")
        ]
        
        for column_name, column_type in free_questions_new_columns:
            if column_name not in free_questions_columns:
                try:
                    alter_sql = f"ALTER TABLE free_questions ADD COLUMN {column_name} {column_type}"
                    print(f"🔧 Adding column to free_questions: {column_name} {column_type}")
                    cursor.execute(alter_sql)
                    print(f"✅ Added column to free_questions: {column_name}")
                except sqlite3.Error as e:
                    print(f"⚠️  Could not add column {column_name} to free_questions: {e}")
            else:
                print(f"ℹ️  Column {column_name} already exists in free_questions")
        
        # Commit all changes
        conn.commit()
        print("✅ Database schema updated successfully!")
        
        # Verify the updated schema
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Updated users table columns: {updated_columns}")
        
        # Check if all required columns exist
        required_columns = [col[0] for col in new_columns]
        missing_columns = [col for col in required_columns if col not in updated_columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        else:
            print("✅ All required columns are present")
            return True
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Updating database schema...")
    success = update_database_schema()
    if success:
        print("🎉 Database schema update completed successfully!")
    else:
        print("❌ Database schema update failed!")
