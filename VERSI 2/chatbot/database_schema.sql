-- ============================================
-- MAGGOT CHATBOT DATABASE SCHEMA
-- PostgreSQL with pgvector Extension
-- ============================================
-- Created: November 2025
-- Description: Database schema untuk chatbot RAG system
-- ============================================

-- ============================================
-- 1. CREATE DATABASE
-- ============================================
-- Jalankan sebagai postgres superuser
-- Atau skip jika database sudah dibuat

-- Connect ke postgres default database terlebih dahulu
-- psql -U postgres

-- Create database
CREATE DATABASE maggot_chatbot
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Connect ke database yang baru dibuat
-- \c maggot_chatbot

-- ============================================
-- 2. CREATE EXTENSION - pgvector
-- ============================================
-- Harus dijalankan setelah connect ke database maggot_chatbot

CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check pgvector version
SELECT extversion FROM pg_extension WHERE extname = 'vector';

-- ============================================
-- 3. CREATE TABLE - documents
-- ============================================
-- Table untuk menyimpan metadata dokumen

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath TEXT,
    file_size INTEGER,
    total_chunks INTEGER,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    full_text TEXT
);

-- Add comments
COMMENT ON TABLE documents IS 'Menyimpan metadata dokumen PDF yang diupload';
COMMENT ON COLUMN documents.id IS 'Primary key, auto-increment';
COMMENT ON COLUMN documents.filename IS 'Nama file asli (contoh: jurnal_bsf.pdf)';
COMMENT ON COLUMN documents.filepath IS 'Path lengkap file di server';
COMMENT ON COLUMN documents.file_size IS 'Ukuran file dalam bytes';
COMMENT ON COLUMN documents.total_chunks IS 'Jumlah chunks yang dibuat dari dokumen ini';
COMMENT ON COLUMN documents.upload_date IS 'Timestamp saat file diupload';
COMMENT ON COLUMN documents.metadata IS 'Data tambahan dalam format JSON (author, subject, etc)';
COMMENT ON COLUMN documents.full_text IS 'Full text dokumen (optional, untuk search)';

-- ============================================
-- 4. CREATE TABLE - chunks
-- ============================================
-- Table untuk menyimpan text chunks dengan vector embeddings
-- VECTOR_DIMENSION: 3072 (Azure OpenAI text-embedding-3-large)
-- Note: Ganti 3072 dengan dimension yang Anda gunakan

CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    char_count INTEGER,
    embedding vector(3072),  -- Sesuaikan dengan VECTOR_DIMENSION Anda
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add comments
COMMENT ON TABLE chunks IS 'Menyimpan text chunks dengan vector embeddings untuk similarity search';
COMMENT ON COLUMN chunks.id IS 'Primary key, auto-increment';
COMMENT ON COLUMN chunks.document_id IS 'Foreign key ke table documents';
COMMENT ON COLUMN chunks.chunk_index IS 'Index/urutan chunk dalam dokumen (0, 1, 2, ...)';
COMMENT ON COLUMN chunks.text IS 'Text content dari chunk';
COMMENT ON COLUMN chunks.char_count IS 'Jumlah karakter dalam chunk';
COMMENT ON COLUMN chunks.embedding IS 'Vector embedding dari text (3072 dimensions)';
COMMENT ON COLUMN chunks.metadata IS 'Metadata tambahan (page_number, section, etc)';
COMMENT ON COLUMN chunks.created_at IS 'Timestamp saat chunk dibuat';

-- ============================================
-- 5. CREATE INDEXES
-- ============================================

-- Index untuk document lookup
CREATE INDEX IF NOT EXISTS chunks_document_id_idx 
ON chunks(document_id);

COMMENT ON INDEX chunks_document_id_idx IS 'Index untuk query chunks berdasarkan document_id';

-- Index untuk vector similarity search
-- HNSW index hanya efisien untuk dimension <= 2000
-- Untuk dimension > 2000 (seperti 3072), skip index ini

-- JIKA VECTOR_DIMENSION <= 2000, uncomment baris berikut:
-- CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx 
-- ON chunks USING hnsw (embedding vector_cosine_ops);
-- COMMENT ON INDEX chunks_embedding_hnsw_idx IS 'HNSW index untuk cosine similarity search';

-- JIKA VECTOR_DIMENSION > 2000 (seperti 3072):
-- Tidak perlu buat index, akan menggunakan sequential scan
-- Sequential scan lebih lambat tapi works untuk any dimension

-- Alternatif: IVFFlat index (works untuk dimension > 2000)
-- CREATE INDEX IF NOT EXISTS chunks_embedding_ivfflat_idx 
-- ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
-- COMMENT ON INDEX chunks_embedding_ivfflat_idx IS 'IVFFlat index untuk cosine similarity search';

-- ============================================
-- 6. CREATE VIEWS (Optional)
-- ============================================

-- View untuk summary dokumen dengan jumlah chunks
CREATE OR REPLACE VIEW documents_summary AS
SELECT 
    d.id,
    d.filename,
    d.file_size,
    d.total_chunks,
    d.upload_date,
    COUNT(c.id) as actual_chunks,
    ROUND(AVG(c.char_count)::numeric, 2) as avg_chunk_size
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.filename, d.file_size, d.total_chunks, d.upload_date
ORDER BY d.upload_date DESC;

COMMENT ON VIEW documents_summary IS 'Summary dokumen dengan statistik chunks';

-- ============================================
-- 7. GRANT PERMISSIONS (Optional)
-- ============================================
-- Jika menggunakan user selain postgres

-- CREATE USER maggot_user WITH PASSWORD 'your_password';
-- GRANT CONNECT ON DATABASE maggot_chatbot TO maggot_user;
-- GRANT USAGE ON SCHEMA public TO maggot_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO maggot_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO maggot_user;

-- ============================================
-- 8. SAMPLE QUERIES
-- ============================================

-- Check database statistics
SELECT 
    (SELECT COUNT(*) FROM documents) as total_documents,
    (SELECT COUNT(*) FROM chunks) as total_chunks,
    (SELECT SUM(file_size) FROM documents) as total_size_bytes,
    (SELECT ROUND(AVG(char_count)::numeric, 2) FROM chunks) as avg_chunk_size;

-- List all documents
SELECT id, filename, total_chunks, upload_date 
FROM documents 
ORDER BY upload_date DESC;

-- Get chunks for specific document
SELECT chunk_index, LEFT(text, 100) as text_preview, char_count
FROM chunks 
WHERE document_id = 1
ORDER BY chunk_index;

-- Similarity search example (requires actual embedding vector)
-- SELECT 
--     c.id,
--     c.text,
--     d.filename,
--     1 - (c.embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
-- FROM chunks c
-- JOIN documents d ON c.document_id = d.id
-- ORDER BY c.embedding <=> '[0.1, 0.2, ...]'::vector
-- LIMIT 5;

-- Delete document and all its chunks (cascade)
-- DELETE FROM documents WHERE id = 1;

-- ============================================
-- 9. MAINTENANCE QUERIES
-- ============================================

-- Vacuum analyze untuk optimize performance
VACUUM ANALYZE documents;
VACUUM ANALYZE chunks;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- ============================================
-- 10. BACKUP & RESTORE
-- ============================================

-- Backup database (run in command line, not psql)
-- pg_dump -U postgres -d maggot_chatbot -F c -b -v -f maggot_chatbot_backup.dump

-- Restore database (run in command line)
-- pg_restore -U postgres -d maggot_chatbot -v maggot_chatbot_backup.dump

-- Backup only schema
-- pg_dump -U postgres -d maggot_chatbot --schema-only -f schema_only.sql

-- Backup only data
-- pg_dump -U postgres -d maggot_chatbot --data-only -f data_only.sql

-- ============================================
-- NOTES:
-- ============================================
-- 1. Jalankan query ini secara berurutan dari atas ke bawah
-- 2. Untuk dimension > 2000, skip HNSW index creation
-- 3. Pastikan pgvector extension sudah terinstall di system
-- 4. Sesuaikan vector dimension dengan model embedding Anda:
--    - text-embedding-3-large: 3072
--    - text-embedding-3-small: 1536
--    - all-MiniLM-L6-v2: 384
-- 5. Untuk production, pertimbangkan:
--    - Connection pooling (pgBouncer)
--    - Regular VACUUM ANALYZE
--    - Monitor query performance
--    - Backup schedule

-- ============================================
-- END OF SCHEMA
-- ============================================
