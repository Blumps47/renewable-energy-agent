"""Database initialization script for Supabase."""

import asyncio
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SQL statements to create tables
CREATE_TABLES_SQL = """
-- Enable the pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    capabilities TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'active',
    model_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    type TEXT NOT NULL,
    size INTEGER NOT NULL,
    checksum TEXT NOT NULL,
    dropbox_path TEXT NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create embeddings table with vector column
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(384), -- Adjust dimension based on your embedding model
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID DEFAULT NULL,
    session_id TEXT NOT NULL UNIQUE,
    messages JSONB DEFAULT '[]',
    context JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    location JSONB DEFAULT '{}',
    capacity NUMERIC DEFAULT NULL,
    estimated_cost NUMERIC DEFAULT NULL,
    timeline JSONB DEFAULT '{}',
    documents TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create knowledge_base table
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    source TEXT DEFAULT NULL,
    confidence NUMERIC DEFAULT 1.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create agent_interactions table
CREATE TABLE IF NOT EXISTS agent_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    message_type TEXT NOT NULL,
    content JSONB NOT NULL,
    response JSONB DEFAULT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_processed ON documents(processed);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(type);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_type ON projects(type);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_status ON agent_interactions(status);

-- Create vector similarity search function
CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE(
    id uuid,
    document_id uuid,
    chunk_text text,
    chunk_index int,
    similarity float,
    metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        embeddings.id,
        embeddings.document_id,
        embeddings.chunk_text,
        embeddings.chunk_index,
        1 - (embeddings.embedding <=> query_embedding) AS similarity,
        embeddings.metadata
    FROM embeddings
    WHERE 1 - (embeddings.embedding <=> query_embedding) > match_threshold
    ORDER BY embeddings.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""

# Sample data insertion
INSERT_SAMPLE_DATA_SQL = """
-- Insert sample knowledge base entries
INSERT INTO knowledge_base (title, content, category, tags) VALUES
('Solar Panel Efficiency Basics', 
 'Solar panel efficiency refers to the percentage of sunlight that can be converted into usable electricity by the solar cell. Most residential solar panels have an efficiency rating between 15% and 22%. Higher efficiency panels produce more electricity per square foot of installation space.',
 'Solar Energy',
 ARRAY['solar', 'efficiency', 'panels', 'basics']
),
('Wind Turbine Site Assessment', 
 'Proper wind resource assessment is crucial for wind energy projects. Key factors include average wind speed, wind direction patterns, turbulence, and seasonal variations. A minimum average wind speed of 6-7 m/s is typically required for commercial viability.',
 'Wind Energy',
 ARRAY['wind', 'turbine', 'assessment', 'site selection']
),
('Energy Storage Technologies', 
 'Battery energy storage systems (BESS) are becoming increasingly important for renewable energy integration. Lithium-ion batteries are the most common technology, with costs declining rapidly. Other technologies include pumped hydro, compressed air, and emerging technologies like flow batteries.',
 'Energy Storage',
 ARRAY['storage', 'battery', 'grid', 'integration']
),
('Renewable Energy Incentives', 
 'Various financial incentives support renewable energy deployment including federal tax credits (ITC/PTC), state rebates, net metering programs, and renewable energy certificates (RECs). The Investment Tax Credit (ITC) provides a 30% tax credit for solar installations.',
 'Policy & Finance',
 ARRAY['incentives', 'tax credits', 'financing', 'policy']
);
"""


async def init_database():
    """Initialize the Supabase database with required tables and sample data."""
    
    # Get environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_service_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")
        return False
    
    try:
        # Create Supabase client with service key for admin operations
        supabase = create_client(supabase_url, supabase_service_key)
        
        print("🔄 Creating database tables...")
        
        # Execute table creation SQL
        # Note: Supabase doesn't support direct SQL execution via Python client
        # This would typically be run through the Supabase dashboard SQL editor
        # or using a direct PostgreSQL connection
        
        print("""
⚠️  MANUAL STEP REQUIRED:
Please run the following SQL in your Supabase SQL editor:

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy and paste the SQL from the generated file 'database_schema.sql'
4. Execute the SQL to create tables and functions

Alternatively, you can use a direct PostgreSQL connection with psycopg2.
        """)
        
        # Write SQL to file for manual execution
        with open('database_schema.sql', 'w') as f:
            f.write(CREATE_TABLES_SQL)
            f.write('\n\n-- Sample Data\n')
            f.write(INSERT_SAMPLE_DATA_SQL)
        
        print("✅ Database schema saved to 'database_schema.sql'")
        print("✅ Please execute this file in your Supabase SQL editor")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False


if __name__ == "__main__":
    print("🌱 Renewable Energy AI Agent Ecosystem - Database Initialization")
    print("=" * 60)
    
    success = asyncio.run(init_database())
    
    if success:
        print("\n✅ Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Execute 'database_schema.sql' in your Supabase SQL editor")
        print("2. Set up your .env file with the required API keys")
        print("3. Run 'python -m src.main' to start the agent")
    else:
        print("\n❌ Database initialization failed!")
        exit(1) 