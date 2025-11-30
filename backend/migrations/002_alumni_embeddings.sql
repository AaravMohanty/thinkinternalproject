-- Alumni Embeddings Table for AI Recommendations
-- Run this in Supabase SQL Editor

-- Enable pgvector if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create alumni_embeddings table
CREATE TABLE IF NOT EXISTS alumni_embeddings (
  id SERIAL PRIMARY KEY,
  csv_row_id INTEGER NOT NULL UNIQUE,  -- Row index from CSV (0-based)
  name TEXT NOT NULL,
  embedding vector(768),  -- Gemini text-embedding-004 is 768 dimensions
  profile_text TEXT,  -- The text used to generate embedding (for debugging)
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast vector similarity search
-- Using ivfflat for good balance of speed and accuracy
CREATE INDEX IF NOT EXISTS idx_alumni_embeddings_vector
  ON alumni_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 20);  -- ~sqrt(164) for ~164 alumni

-- Index for csv_row_id lookups
CREATE INDEX IF NOT EXISTS idx_alumni_embeddings_csv_row_id
  ON alumni_embeddings(csv_row_id);

-- RLS Policy: Allow authenticated users to read embeddings
ALTER TABLE alumni_embeddings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated read access" ON alumni_embeddings
  FOR SELECT
  USING (auth.role() = 'authenticated');

-- Allow service role full access (for backend to insert/update)
CREATE POLICY "Allow service role full access" ON alumni_embeddings
  FOR ALL
  USING (auth.role() = 'service_role');

-- Function to find similar alumni
CREATE OR REPLACE FUNCTION match_alumni(
  query_embedding vector(768),
  match_count INT DEFAULT 10,
  exclude_ids INT[] DEFAULT '{}'
)
RETURNS TABLE (
  csv_row_id INT,
  name TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    ae.csv_row_id,
    ae.name,
    1 - (ae.embedding <=> query_embedding) AS similarity
  FROM alumni_embeddings ae
  WHERE ae.csv_row_id != ALL(exclude_ids)
  ORDER BY ae.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
