-- ============================================
-- QUICK SETUP - MAGGOT CHATBOT DATABASE
-- ============================================
-- Versi cepat untuk setup database
-- Run ini jika Anda ingin setup manual tanpa Python script
-- ============================================

-- STEP 1: Connect ke PostgreSQL
-- psql -U postgres

-- STEP 2: Create Database
CREATE DATABASE maggot_chatbot;

-- STEP 3: Connect ke database baru
\c maggot_chatbot

-- STEP 4: Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- STEP 5: Create documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath TEXT,
    file_size INTEGER,
    total_chunks INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    full_text TEXT
);

-- STEP 6: Create chunks table
-- NOTE: Ganti 3072 dengan dimension embedding Anda
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    char_count INTEGER,
    embedding vector(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- STEP 7: Create indexes
CREATE INDEX chunks_document_id_idx ON chunks(document_id);

-- STEP 8: Verify setup
SELECT 
    'Database' as component, 
    current_database() as name,
    'OK' as status
UNION ALL
SELECT 
    'pgvector' as component,
    extversion as name,
    'OK' as status
FROM pg_extension 
WHERE extname = 'vector'
UNION ALL
SELECT 
    'documents table' as component,
    tablename as name,
    'OK' as status
FROM pg_tables 
WHERE tablename = 'documents'
UNION ALL
SELECT 
    'chunks table' as component,
    tablename as name,
    'OK' as status
FROM pg_tables 
WHERE tablename = 'chunks';

-- Setup complete! ✅
-- Next: Configure .env file dan start Python server
