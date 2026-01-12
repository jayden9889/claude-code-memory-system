#!/usr/bin/env python3
"""
Fix the get_memory_stats() function in Supabase.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

print("🔧 Fixing Supabase get_memory_stats() function...")

try:
    from supabase import create_client

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Read the fixed SQL
    with open('execution/fix_stats_function.sql', 'r') as f:
        fix_sql = f.read()

    # Execute using raw SQL via PostgREST
    import requests

    # Use Supabase SQL via REST API
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        },
        json={"query": fix_sql}
    )

    if response.status_code in [200, 201, 204]:
        print("✅ Function fixed successfully!")
    else:
        print(f"⚠️ API response: {response.status_code}")
        print("Please run this SQL manually in Supabase:")
        print("\n" + fix_sql)

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPlease run this SQL manually in Supabase SQL editor:")
    print("(File: execution/fix_stats_function.sql)")
    with open('execution/fix_stats_function.sql', 'r') as f:
        print("\n" + f.read())
