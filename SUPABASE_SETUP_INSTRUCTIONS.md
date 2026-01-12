# Supabase Database Setup Instructions

## ⚠️ Important: Run This SQL in Supabase Dashboard

I need you to create the database schema in Supabase. Here's how:

---

## Step 1: Open Supabase SQL Editor

**Click here**: 👉 https://supabase.com/dashboard/project/uzniuvsjhejfcspeoais/sql/new

---

## Step 2: Copy This SQL

```sql
-- Create memories table
CREATE TABLE IF NOT EXISTS memories (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  category TEXT NOT NULL CHECK (category IN ('insights', 'learnings', 'patterns', 'context_history')),
  tags TEXT[] DEFAULT '{}',
  content JSONB NOT NULL,
  transcript_length INTEGER DEFAULT 0,
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memories_content ON memories USING GIN(content);
CREATE INDEX IF NOT EXISTS idx_memories_fts ON memories USING GIN(to_tsvector('english', content::text));

-- Create search function
CREATE OR REPLACE FUNCTION search_memories(search_query TEXT, result_limit INTEGER DEFAULT 10)
RETURNS SETOF memories AS $$
BEGIN
  RETURN QUERY
  SELECT *
  FROM memories
  WHERE to_tsvector('english', content::text) @@ plainto_tsquery('english', search_query)
  ORDER BY created_at DESC
  LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Create stats function
CREATE OR REPLACE FUNCTION get_memory_stats()
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'total_memories', COUNT(*),
    'insights', COUNT(*) FILTER (WHERE category = 'insights'),
    'learnings', COUNT(*) FILTER (WHERE category = 'learnings'),
    'patterns', COUNT(*) FILTER (WHERE category = 'patterns'),
    'context_history', COUNT(*) FILTER (WHERE category = 'context_history'),
    'total_tags', COUNT(DISTINCT unnest(tags)),
    'last_updated', MAX(created_at)
  )
  INTO result
  FROM memories;
  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create recent memories view
CREATE OR REPLACE VIEW recent_memories AS
SELECT id, created_at, category, tags,
       content->'insights'->>'summary' AS summary,
       array_length(tags, 1) AS tag_count
FROM memories
ORDER BY created_at DESC
LIMIT 50;

-- Enable Row Level Security
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;

-- Policies for service role (full access)
DROP POLICY IF EXISTS "Enable full access for service role" ON memories;
CREATE POLICY "Enable full access for service role"
ON memories
FOR ALL
USING (true)
WITH CHECK (true);

-- Grant permissions
GRANT ALL ON memories TO service_role;
GRANT ALL ON memories TO postgres;
GRANT SELECT ON recent_memories TO service_role;
GRANT SELECT ON recent_memories TO postgres;
```

---

## Step 3: Run the SQL

1. Paste the SQL above into the SQL editor
2. Click **"RUN"** button (bottom right)
3. You should see: "Success. No rows returned"

---

## Step 4: Verify It Worked

Run this query to verify:

```sql
SELECT * FROM get_memory_stats();
```

Should return:
```json
{
  "total_memories": 0,
  "insights": 0,
  "learnings": 0,
  "patterns": 0,
  "context_history": 0,
  "total_tags": 0,
  "last_updated": null
}
```

---

## Once Complete

Tell me: "Supabase schema is set up"

And I'll migrate your 12 existing memories from local JSON to the cloud database!

---

**Quick Link**: https://supabase.com/dashboard/project/uzniuvsjhejfcspeoais/sql/new
