#!/usr/bin/env python3
"""
Automatically set up Supabase database schema.
No manual SQL needed!
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Supabase credentials not found in .env")
    sys.exit(1)

print("🔧 Setting up Supabase database schema...")
print(f"📍 URL: {SUPABASE_URL}")

try:
    import psycopg2
    from psycopg2 import sql

    print("✓ psycopg2 library found")

except ImportError:
    print("\n📦 Installing psycopg2-binary...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary"], check=True)
    import psycopg2
    from psycopg2 import sql
    print("✓ psycopg2 installed")

try:
    # Extract project ref from URL
    # Format: https://PROJECT_REF.supabase.co
    project_ref = SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')

    # Supabase connection string using service_role key as password
    # This uses the connection pooler in transaction mode
    conn_string = f"postgresql://postgres.{project_ref}:{SUPABASE_KEY}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

    print(f"🔌 Connecting to Supabase PostgreSQL...")

    # Connect to database
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True  # Important for DDL statements
    cursor = conn.cursor()

    print("✓ Connected to Supabase PostgreSQL")

    # Read SQL schema
    with open('execution/setup_supabase_schema.sql', 'r') as f:
        schema_sql = f.read()

    print("\n📊 Creating database tables...")

    # Execute the entire SQL script
    cursor.execute(schema_sql)

    print("✅ Database schema created successfully!")
    print("\n📋 Tables created:")
    print("   - memories (main table)")
    print("   - recent_memories (view)")
    print("\n🔍 Indexes created:")
    print("   - idx_memories_category")
    print("   - idx_memories_tags")
    print("   - idx_memories_created_at")
    print("   - idx_memories_content (JSONB)")
    print("   - idx_memories_fts (full-text search)")
    print("\n🔧 Functions created:")
    print("   - search_memories(text, integer)")
    print("   - get_memory_stats()")
    print("\n🔒 Security:")
    print("   - Row Level Security enabled")
    print("   - Service role policy created")

    # Test the setup
    print("\n🧪 Testing database...")
    cursor.execute("SELECT * FROM get_memory_stats();")
    stats = cursor.fetchone()[0]
    print(f"✓ Stats function works: {stats}")

    cursor.close()
    conn.close()

    print("\n✅ Supabase is ready to store memories!")
    print("🚀 You can now run: python3 execution/test_memory_system.py")

except psycopg2.Error as e:
    print(f"\n❌ PostgreSQL Error: {e}")
    print(f"Error Code: {e.pgcode}")
    print(f"Error Message: {e.pgerror}")
    print("\n⚠️ Automatic setup failed. Please run SQL manually:")
    print("\n1. Go to: https://supabase.com/dashboard/project/uzniuvsjhejfcspeoais/sql/new")
    print("2. Copy SQL from: execution/setup_supabase_schema.sql")
    print("3. Paste and click RUN")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n⚠️ Automatic setup failed. Please run SQL manually:")
    print("\n1. Go to: https://supabase.com/dashboard/project/uzniuvsjhejfcspeoais/sql/new")
    print("2. Copy SQL from: execution/setup_supabase_schema.sql")
    print("3. Paste and click RUN")
    sys.exit(1)
