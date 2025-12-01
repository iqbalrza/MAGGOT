-- ============================================
-- SAMPLE QUERIES & TESTING
-- MAGGOT CHATBOT DATABASE
-- ============================================
-- Query untuk testing dan development
-- ============================================

-- ============================================
-- 1. DATABASE INFO
-- ============================================

-- Check current database
SELECT current_database();

-- Check PostgreSQL version
SELECT version();

-- Check pgvector version
SELECT extversion FROM pg_extension WHERE extname = 'vector';

-- List all tables
\dt

-- List all indexes
\di

-- ============================================
-- 2. DATABASE STATISTICS
-- ============================================

-- Overall statistics
SELECT 
    (SELECT COUNT(*) FROM documents) as total_documents,
    (SELECT COUNT(*) FROM chunks) as total_chunks,
    (SELECT SUM(file_size) FROM documents) as total_size_bytes,
    (SELECT pg_size_pretty(SUM(file_size)::bigint) FROM documents) as total_size_readable,
    (SELECT ROUND(AVG(char_count)::numeric, 2) FROM chunks) as avg_chunk_size,
    (SELECT MIN(upload_date) FROM documents) as first_upload,
    (SELECT MAX(upload_date) FROM documents) as last_upload;

-- Documents summary
SELECT 
    id,
    filename,
    total_chunks,
    pg_size_pretty(file_size::bigint) as file_size,
    upload_date,
    (SELECT COUNT(*) FROM chunks WHERE document_id = documents.id) as actual_chunks
FROM documents
ORDER BY upload_date DESC;

-- Top 5 largest documents
SELECT 
    filename,
    pg_size_pretty(file_size::bigint) as size,
    total_chunks
FROM documents
ORDER BY file_size DESC
LIMIT 5;

-- ============================================
-- 3. CHUNKS ANALYSIS
-- ============================================

-- Chunks distribution per document
SELECT 
    d.id,
    d.filename,
    COUNT(c.id) as chunk_count,
    ROUND(AVG(c.char_count)::numeric, 2) as avg_chars,
    MIN(c.char_count) as min_chars,
    MAX(c.char_count) as max_chars
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.filename
ORDER BY chunk_count DESC;

-- Sample chunks from each document
SELECT 
    d.filename,
    c.chunk_index,
    LEFT(c.text, 100) as text_preview,
    c.char_count
FROM chunks c
JOIN documents d ON c.document_id = d.id
WHERE c.chunk_index < 3  -- First 3 chunks
ORDER BY d.id, c.chunk_index;

-- Find chunks by text content
SELECT 
    d.filename,
    c.chunk_index,
    c.text,
    c.char_count
FROM chunks c
JOIN documents d ON c.document_id = d.id
WHERE c.text ILIKE '%maggot%'  -- Change search term
LIMIT 10;

-- ============================================
-- 4. VECTOR OPERATIONS
-- ============================================

-- Check if embeddings exist
SELECT 
    d.filename,
    COUNT(CASE WHEN c.embedding IS NOT NULL THEN 1 END) as with_embedding,
    COUNT(CASE WHEN c.embedding IS NULL THEN 1 END) as without_embedding
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.filename;

-- Get embedding dimension
SELECT 
    vector_dims(embedding) as dimension
FROM chunks
WHERE embedding IS NOT NULL
LIMIT 1;

-- Sample similarity search (cosine distance)
-- NOTE: Replace the vector values with actual embedding
/*
SELECT 
    d.filename,
    c.chunk_index,
    LEFT(c.text, 100) as text_preview,
    1 - (c.embedding <=> '[0.1, 0.2, ...]'::vector) as similarity_score
FROM chunks c
JOIN documents d ON c.document_id = d.id
WHERE c.embedding IS NOT NULL
ORDER BY c.embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
*/

-- ============================================
-- 5. DATA VALIDATION
-- ============================================

-- Check for orphaned chunks (chunks without documents)
SELECT COUNT(*) as orphaned_chunks
FROM chunks c
LEFT JOIN documents d ON c.document_id = d.id
WHERE d.id IS NULL;

-- Check for documents without chunks
SELECT 
    id,
    filename,
    total_chunks
FROM documents d
WHERE NOT EXISTS (SELECT 1 FROM chunks WHERE document_id = d.id);

-- Check for NULL embeddings
SELECT 
    d.filename,
    COUNT(*) as null_embeddings
FROM chunks c
JOIN documents d ON c.document_id = d.id
WHERE c.embedding IS NULL
GROUP BY d.filename;

-- Verify chunk indexes are sequential
SELECT 
    d.filename,
    d.total_chunks,
    MAX(c.chunk_index) + 1 as max_index
FROM documents d
JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.filename, d.total_chunks
HAVING d.total_chunks != MAX(c.chunk_index) + 1;

-- ============================================
-- 6. PERFORMANCE MONITORING
-- ============================================

-- Table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Cache hit ratio (should be > 90%)
SELECT 
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_ratio
FROM pg_statio_user_tables;

-- ============================================
-- 7. MAINTENANCE OPERATIONS
-- ============================================

-- Analyze tables (update statistics)
ANALYZE documents;
ANALYZE chunks;

-- Vacuum tables (reclaim space)
VACUUM documents;
VACUUM chunks;

-- Vacuum analyze (both operations)
VACUUM ANALYZE documents;
VACUUM ANALYZE chunks;

-- Reindex (rebuild indexes)
REINDEX TABLE documents;
REINDEX TABLE chunks;

-- ============================================
-- 8. DATA CLEANUP
-- ============================================

-- Delete old documents (older than 30 days)
-- DELETE FROM documents 
-- WHERE upload_date < NOW() - INTERVAL '30 days';

-- Delete specific document (cascade deletes chunks)
-- DELETE FROM documents WHERE id = 1;

-- Delete chunks without text
-- DELETE FROM chunks WHERE text IS NULL OR text = '';

-- Delete chunks without embeddings
-- DELETE FROM chunks WHERE embedding IS NULL;

-- Truncate all data (keep schema)
-- TRUNCATE TABLE chunks;
-- TRUNCATE TABLE documents CASCADE;

-- ============================================
-- 9. BACKUP COMMANDS (Run in shell, not psql)
-- ============================================

-- Backup database
-- pg_dump -U postgres -d maggot_chatbot -F c -f backup.dump

-- Backup with timestamp
-- pg_dump -U postgres -d maggot_chatbot -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

-- Restore database
-- pg_restore -U postgres -d maggot_chatbot -c -v backup.dump

-- Export to SQL file
-- pg_dump -U postgres -d maggot_chatbot -f backup.sql

-- Export specific table
-- pg_dump -U postgres -d maggot_chatbot -t documents -f documents_backup.sql

-- ============================================
-- 10. TESTING QUERIES
-- ============================================

-- Insert test document
INSERT INTO documents (filename, filepath, file_size, total_chunks, metadata)
VALUES (
    'test_document.pdf',
    '/uploads/test_document.pdf',
    1024000,
    10,
    '{"author": "Test Author", "pages": 15}'::jsonb
)
RETURNING id;

-- Insert test chunks (use document_id from above)
-- NOTE: Replace with actual embedding vector
INSERT INTO chunks (document_id, chunk_index, text, char_count, metadata)
VALUES 
    (1, 0, 'This is the first test chunk with some text content.', 52, '{"page": 1}'::jsonb),
    (1, 1, 'This is the second test chunk with more information.', 53, '{"page": 1}'::jsonb),
    (1, 2, 'This is the third chunk about maggot BSF cultivation.', 55, '{"page": 2}'::jsonb);

-- Verify test data
SELECT 
    d.filename,
    c.chunk_index,
    c.text
FROM chunks c
JOIN documents d ON c.document_id = d.id
WHERE d.filename = 'test_document.pdf'
ORDER BY c.chunk_index;

-- Delete test data
-- DELETE FROM documents WHERE filename = 'test_document.pdf';

-- ============================================
-- 11. USEFUL VIEWS
-- ============================================

-- Create view for quick document overview
CREATE OR REPLACE VIEW v_document_overview AS
SELECT 
    d.id,
    d.filename,
    d.total_chunks,
    pg_size_pretty(d.file_size::bigint) as file_size,
    d.upload_date,
    COUNT(c.id) as actual_chunks,
    COUNT(CASE WHEN c.embedding IS NOT NULL THEN 1 END) as chunks_with_embedding,
    ROUND(AVG(c.char_count)::numeric, 2) as avg_chunk_chars
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.filename, d.total_chunks, d.file_size, d.upload_date;

-- Use the view
SELECT * FROM v_document_overview ORDER BY upload_date DESC;

-- ============================================
-- 12. TROUBLESHOOTING
-- ============================================

-- Check for locked tables
SELECT 
    t.relname,
    l.locktype,
    l.mode,
    l.granted,
    a.usename,
    a.query,
    a.state
FROM pg_locks l
JOIN pg_stat_all_tables t ON l.relation = t.relid
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE t.schemaname = 'public';

-- Kill long running queries
-- SELECT pg_terminate_backend(pid)
-- FROM pg_stat_activity
-- WHERE state = 'active' 
-- AND query_start < NOW() - INTERVAL '5 minutes';

-- Check for bloat
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    ROUND(100 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_tuple_percent
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;

-- ============================================
-- END OF TESTING QUERIES
-- ============================================
