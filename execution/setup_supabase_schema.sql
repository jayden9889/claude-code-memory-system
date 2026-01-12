-- Supabase Memory Database Schema
-- Run this to set up the memories table in Supabase

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

-- Create full-text search index
CREATE INDEX IF NOT EXISTS idx_memories_fts ON memories USING GIN(to_tsvector('english', content::text));

-- Create function for search
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

-- Create function to get summary stats
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

-- Create view for recent memories
CREATE OR REPLACE VIEW recent_memories AS
SELECT id, created_at, category, tags,
       content->'insights'->>'summary' AS summary,
       array_length(tags, 1) AS tag_count
FROM memories
ORDER BY created_at DESC
LIMIT 50;

-- Enable Row Level Security (RLS)
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users (full access)
CREATE POLICY "Enable full access for authenticated users"
ON memories
FOR ALL
USING (auth.role() = 'authenticated')
WITH CHECK (auth.role() = 'authenticated');

-- Create policy for service role (full access for background agents)
CREATE POLICY "Enable full access for service role"
ON memories
FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- Grant permissions
GRANT ALL ON memories TO authenticated;
GRANT ALL ON memories TO service_role;
GRANT SELECT ON recent_memories TO authenticated;
GRANT SELECT ON recent_memories TO service_role;

-- Comments for documentation
COMMENT ON TABLE memories IS 'Stores all persistent memories from Claude Code conversations';
COMMENT ON COLUMN memories.id IS 'Unique identifier in format YYYYMMDD_HHMMSS';
COMMENT ON COLUMN memories.category IS 'Type of memory: insights, learnings, patterns, or context_history';
COMMENT ON COLUMN memories.tags IS 'Array of tags for categorization and search';
COMMENT ON COLUMN memories.content IS 'Full memory content including insights, learnings, decisions, etc.';
COMMENT ON COLUMN memories.transcript_length IS 'Length of original conversation transcript in characters';
COMMENT ON COLUMN memories.metadata IS 'Additional metadata (source, agent used, etc.)';
