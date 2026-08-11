-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables for the application

-- Workflows table (state persistence)
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_subject VARCHAR(255) NOT NULL,
    email_body TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Agent capability embeddings (for semantic routing)
CREATE TABLE IF NOT EXISTS agent_capabilities (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(255) NOT NULL UNIQUE,
    capability_description TEXT NOT NULL,
    capability_tags TEXT[] DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on embeddings for fast similarity search
CREATE INDEX IF NOT EXISTS agent_capabilities_embedding_idx
ON agent_capabilities USING ivfflat (embedding vector_cosine_ops);

-- Workflow execution logs (audit trail)
CREATE TABLE IF NOT EXISTS workflow_logs (
    id SERIAL PRIMARY KEY,
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    node_name VARCHAR(255) NOT NULL,
    input JSONB,
    output JSONB,
    status VARCHAR(50),
    latency_ms INTEGER,
    cost_usd DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback collection (for continuous improvement)
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    user_correction JSONB,
    original_prediction JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
