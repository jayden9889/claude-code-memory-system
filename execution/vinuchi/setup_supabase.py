#!/usr/bin/env python3
"""
Supabase Setup for Vinuchi Blog Writer
Creates all required tables for the blog writer system.
"""

import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
import requests

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    sys.exit(1)


def execute_sql(sql: str, description: str = ""):
    """Execute SQL against Supabase via REST API."""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    # Use the REST API to execute SQL via RPC
    # First, let's try creating via the postgres REST endpoint
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"

    print(f"\n{description}...")

    response = requests.post(
        url,
        headers=headers,
        json={"query": sql}
    )

    if response.status_code in [200, 201, 204]:
        print(f"  OK")
        return True
    elif response.status_code == 404:
        print(f"  Note: exec_sql function not found, tables may need manual creation")
        return False
    else:
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        return False


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in Supabase."""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }

    url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1"
    response = requests.get(url, headers=headers)

    return response.status_code == 200


def create_table_via_rest(table_name: str, sample_data: dict) -> bool:
    """Create a table by inserting sample data (Supabase auto-creates in some configs)."""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    response = requests.post(url, headers=headers, json=sample_data)

    return response.status_code in [200, 201]


def main():
    """Main setup routine."""
    print("=" * 60)
    print("VINUCHI BLOG WRITER - SUPABASE SETUP")
    print("=" * 60)
    print(f"Supabase URL: {SUPABASE_URL}")

    # Check which tables already exist
    tables_to_check = [
        "vinuchi_blogs",
        "vinuchi_style_profile",
        "vinuchi_preferences",
        "vinuchi_generated_blogs"
    ]

    print("\nChecking existing tables...")
    existing = []
    missing = []

    for table in tables_to_check:
        if check_table_exists(table):
            print(f"  {table}: EXISTS")
            existing.append(table)
        else:
            print(f"  {table}: MISSING")
            missing.append(table)

    if not missing:
        print("\nAll tables exist! Setup complete.")
        return

    print(f"\n{len(missing)} tables need to be created.")
    print("\nPlease run the following SQL in your Supabase SQL Editor:")
    print("-" * 60)

    sql_statements = """
-- Enable the vector extension (for embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- Table: vinuchi_blogs (stores all scraped blog content)
CREATE TABLE IF NOT EXISTS vinuchi_blogs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    published_date DATE,
    word_count INTEGER,
    keywords_extracted TEXT[],
    embedding vector(1536),
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: vinuchi_style_profile (stores learned style patterns)
CREATE TABLE IF NOT EXISTS vinuchi_style_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL,
    value JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: vinuchi_preferences (user rules and preferences)
CREATE TABLE IF NOT EXISTS vinuchi_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_type TEXT NOT NULL,
    rule_value TEXT NOT NULL,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE
);

-- Table: vinuchi_generated_blogs (history of generated content)
CREATE TABLE IF NOT EXISTS vinuchi_generated_blogs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    topic_requested TEXT,
    embedding vector(1536),
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_vinuchi_blogs_embedding ON vinuchi_blogs
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_vinuchi_generated_embedding ON vinuchi_generated_blogs
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_vinuchi_blogs_date ON vinuchi_blogs (published_date DESC);
CREATE INDEX IF NOT EXISTS idx_vinuchi_preferences_type ON vinuchi_preferences (rule_type);
"""

    print(sql_statements)
    print("-" * 60)
    print("\nAfter running the SQL, run this script again to verify.")


if __name__ == "__main__":
    main()
