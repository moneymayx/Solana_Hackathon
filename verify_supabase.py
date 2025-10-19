#!/usr/bin/env python3
"""
Supabase Connection Verification Tool
Helps diagnose connection issues step by step
"""
import os
import asyncio
import socket
from dotenv import load_dotenv

load_dotenv()

def test_dns_resolution(hostname):
    """Test if hostname can be resolved"""
    print(f"🔍 Testing DNS resolution for: {hostname}")
    try:
        ip_address = socket.gethostbyname(hostname)
        print(f"✅ DNS resolved: {hostname} → {ip_address}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        print(f"   This means the hostname '{hostname}' doesn't exist or can't be found")
        return False

def parse_database_url(url):
    """Parse database URL to extract components"""
    if not url:
        return None
    
    # Remove postgresql+asyncpg:// or postgresql://
    url = url.replace("postgresql+asyncpg://", "").replace("postgresql://", "")
    
    # Split into user:pass@host:port/db
    parts = url.split("@")
    if len(parts) != 2:
        return None
    
    credentials = parts[0]
    rest = parts[1]
    
    # Extract host and port
    host_port_db = rest.split("/")
    host_port = host_port_db[0]
    
    host_parts = host_port.split(":")
    hostname = host_parts[0]
    port = host_parts[1] if len(host_parts) > 1 else "5432"
    
    return {
        "hostname": hostname,
        "port": port,
        "full_url": url
    }

async def test_postgresql_connection():
    """Test PostgreSQL connection"""
    database_url = os.getenv("DATABASE_URL")
    
    print("=" * 70)
    print("  SUPABASE CONNECTION DIAGNOSTIC")
    print("=" * 70)
    print()
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file!")
        print()
        print("Please add to .env:")
        print("DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@HOST:5432/postgres")
        return False
    
    print(f"📋 DATABASE_URL found")
    print(f"   {database_url[:60]}...")
    print()
    
    # Parse URL
    parsed = parse_database_url(database_url)
    if not parsed:
        print("❌ Failed to parse DATABASE_URL")
        print("   Expected format: postgresql+asyncpg://user:pass@host:port/db")
        return False
    
    print(f"🔧 Parsed connection details:")
    print(f"   Hostname: {parsed['hostname']}")
    print(f"   Port: {parsed['port']}")
    print()
    
    # Test DNS
    if not test_dns_resolution(parsed['hostname']):
        print()
        print("💡 TROUBLESHOOTING STEPS:")
        print()
        print("1. Go to https://app.supabase.com/projects")
        print("2. Find your project and click on it")
        print("3. Go to: Settings → Database")
        print("4. Look for 'Connection string' section")
        print("5. Copy the 'URI' connection string")
        print("6. Make sure you:")
        print("   - Replace [YOUR-PASSWORD] with your actual password")
        print("   - Add '+asyncpg' after 'postgresql'")
        print("   - URL-encode special characters in password")
        print()
        print("Example:")
        print("  From Supabase: postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres")
        print("  In .env file:  postgresql+asyncpg://postgres:MyPass%21@db.xxx.supabase.co:5432/postgres")
        print()
        return False
    
    print()
    print("✅ DNS resolution successful!")
    print()
    print("Now testing actual database connection...")
    print()
    
    # Test actual connection
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        engine = create_async_engine(database_url, echo=False)
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"   PostgreSQL version: {version[:80]}...")
            print()
            
            # Check pgvector
            result = await conn.execute(text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'"))
            has_vector = result.fetchone()[0] > 0
            
            if has_vector:
                print(f"✅ pgvector extension is installed")
            else:
                print(f"⚠️  pgvector extension NOT installed")
                print(f"   Run in Supabase SQL Editor:")
                print(f"   CREATE EXTENSION vector;")
            print()
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed!")
        print(f"   Error: {e}")
        print()
        print("💡 Common issues:")
        print("   1. Password is incorrect")
        print("   2. Special characters in password need URL encoding")
        print("   3. Project is paused or deleted")
        print("   4. IP address not allowed (check Supabase firewall)")
        print()
        return False

async def main():
    success = await test_postgresql_connection()
    
    print("=" * 70)
    if success:
        print("  🎉 ALL CHECKS PASSED!")
        print("  Your Supabase connection is ready to use.")
    else:
        print("  ⚠️  CONNECTION ISSUES DETECTED")
        print("  Please follow the troubleshooting steps above.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())

