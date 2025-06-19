-- Renewable Energy RAG System Database Schema
-- Multi-tenant architecture with Row Level Security (RLS)

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (if not exists)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects table for organizing documents
CREATE TABLE IF NOT EXISTS projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  market TEXT, -- e.g., "Solar", "Wind", "Hydro", "Battery Storage"
  location TEXT,
  owner TEXT,
  status TEXT DEFAULT 'active',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT,
  file_type TEXT,
  source_type TEXT NOT NULL, -- 'dropbox', 'google_drive', 'upload'
  source_id TEXT,
  processing_status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
  chunk_count INTEGER DEFAULT 0,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  error_message TEXT
);

-- Document chunks with embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding VECTOR(1536), -- OpenAI embedding dimension
  token_count INTEGER,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversation contexts for tracking RAG usage
CREATE TABLE IF NOT EXISTS conversation_contexts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  conversation_id TEXT NOT NULL,
  query TEXT NOT NULL,
  retrieved_chunks UUID[] DEFAULT '{}',
  response TEXT,
  context_usage_score FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_documents_user_project ON documents (user_id, project_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_user_project ON document_chunks (user_id, project_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document ON document_chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects (user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_contexts_user ON conversation_contexts (user_id);

-- Enable Row Level Security
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_contexts ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can only access their own projects" ON projects;
DROP POLICY IF EXISTS "Users can only access their own documents" ON documents;
DROP POLICY IF EXISTS "Users can only access their own document chunks" ON document_chunks;
DROP POLICY IF EXISTS "Users can only access their own conversation contexts" ON conversation_contexts;

-- RLS Policies using auth.uid() for Supabase authentication
CREATE POLICY "Users can only access their own projects" ON projects
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own documents" ON documents
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own document chunks" ON document_chunks
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own conversation contexts" ON conversation_contexts
  FOR ALL USING (auth.uid() = user_id);

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Storage bucket for documents (if using Supabase Storage)
-- This would be created through Supabase dashboard or API
-- INSERT INTO storage.buckets (id, name, public) VALUES ('documents', 'documents', false);

-- Storage policies for documents bucket
-- CREATE POLICY "Users can upload their own documents" ON storage.objects
--   FOR INSERT WITH CHECK (auth.uid()::text = (storage.foldername(name))[1]);

-- CREATE POLICY "Users can view their own documents" ON storage.objects
--   FOR SELECT USING (auth.uid()::text = (storage.foldername(name))[1]);

-- CREATE POLICY "Users can delete their own documents" ON storage.objects
--   FOR DELETE USING (auth.uid()::text = (storage.foldername(name))[1]); 