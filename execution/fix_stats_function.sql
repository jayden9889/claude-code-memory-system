-- Fix for get_memory_stats() function
-- Run this in Supabase SQL editor to fix the stats function

CREATE OR REPLACE FUNCTION get_memory_stats()
RETURNS JSON AS $$
DECLARE
  result JSON;
  unique_tags_count INTEGER;
BEGIN
  -- Count unique tags separately to avoid aggregate/set-returning function conflict
  SELECT COUNT(DISTINCT tag) INTO unique_tags_count
  FROM memories, unnest(tags) AS tag;

  -- Build the stats object
  SELECT json_build_object(
    'total_memories', COUNT(*),
    'insights', COUNT(*) FILTER (WHERE category = 'insights'),
    'learnings', COUNT(*) FILTER (WHERE category = 'learnings'),
    'patterns', COUNT(*) FILTER (WHERE category = 'patterns'),
    'context_history', COUNT(*) FILTER (WHERE category = 'context_history'),
    'total_tags', COALESCE(unique_tags_count, 0),
    'last_updated', MAX(created_at)
  )
  INTO result
  FROM memories;

  RETURN result;
END;
$$ LANGUAGE plpgsql;
