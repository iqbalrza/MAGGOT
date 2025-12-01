# PostgreSQL + pgvector Cheat Sheet

Quick reference untuk operasi database yang sering digunakan.

## 🚀 Quick Start

```powershell
# 1. Start PostgreSQL
net start postgresql-x64-15

# 2. Run setup
python setup_database.py

# 3. Test connection
python test_db_connection.py

# 4. Start API
python chatbot_api.py
```

## 🔌 Connection

```powershell
# Connect via psql
psql -U postgres -d maggot_chatbot

# Via PowerShell (full path)
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot
```

## 📊 Quick Stats

```sql
-- Database stats
SELECT 
    (SELECT COUNT(*) FROM documents) as docs,
    (SELECT COUNT(*) FROM chunks) as chunks;

-- List documents
SELECT id, filename, total_chunks FROM documents;

-- Recent uploads
SELECT filename, upload_date FROM documents ORDER BY upload_date DESC LIMIT 5;
```

## 🔍 Common Queries

```sql
-- Find document by name
SELECT * FROM documents WHERE filename LIKE '%keyword%';

-- Get chunks for document
SELECT chunk_index, LEFT(text, 100) FROM chunks WHERE document_id = 1;

-- Search text in chunks
SELECT d.filename, c.text 
FROM chunks c 
JOIN documents d ON c.document_id = d.id 
WHERE c.text ILIKE '%maggot%';

-- Count chunks per document
SELECT d.filename, COUNT(c.id) 
FROM documents d 
LEFT JOIN chunks c ON d.id = c.document_id 
GROUP BY d.filename;
```

## 🗑️ Delete Operations

```sql
-- Delete document (cascade deletes chunks)
DELETE FROM documents WHERE id = 1;

-- Delete by filename
DELETE FROM documents WHERE filename = 'test.pdf';

-- Delete old documents (30+ days)
DELETE FROM documents WHERE upload_date < NOW() - INTERVAL '30 days';
```

## 💾 Backup & Restore

```powershell
# Quick backup
pg_dump -U postgres -d maggot_chatbot -F c -f backup.dump

# Quick restore
pg_restore -U postgres -d maggot_chatbot -c backup.dump
```

## 🔧 Maintenance

```sql
-- Analyze tables
ANALYZE documents;
ANALYZE chunks;

-- Vacuum
VACUUM ANALYZE documents;
VACUUM ANALYZE chunks;

-- Reindex
REINDEX TABLE chunks;
```

```powershell
# Via command line
vacuumdb -U postgres -d maggot_chatbot -z -v
reindexdb -U postgres -d maggot_chatbot
```

## 📈 Performance

```sql
-- Table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename))
FROM pg_tables 
WHERE schemaname = 'public';

-- Index usage
SELECT 
    indexname,
    idx_scan as times_used,
    pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes 
WHERE schemaname = 'public';

-- Cache hit ratio (should be > 90%)
SELECT 
    sum(heap_blks_hit)::float / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 
FROM pg_statio_user_tables;
```

## 🐛 Troubleshooting

```powershell
# Service not starting
sc query postgresql-x64-15
net start postgresql-x64-15

# Check logs
Get-Content "C:\Program Files\PostgreSQL\15\data\log\*.log" -Tail 50

# Check port
netstat -ano | findstr :5432

# Test connection
psql -U postgres -c "SELECT 1"
```

```sql
-- Check pgvector
SELECT extversion FROM pg_extension WHERE extname = 'vector';

-- Check tables
\dt

-- Check connections
SELECT * FROM pg_stat_activity WHERE datname = 'maggot_chatbot';

-- Kill connection
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'maggot_chatbot' AND pid <> pg_backend_pid();
```

## 🎯 Vector Operations

```sql
-- Check embedding dimension
SELECT vector_dims(embedding) FROM chunks LIMIT 1;

-- Count embeddings
SELECT 
    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embedding,
    COUNT(CASE WHEN embedding IS NULL THEN 1 END) as without_embedding
FROM chunks;

-- Similarity search (example)
-- SELECT text, 1 - (embedding <=> '[...]'::vector) as similarity
-- FROM chunks 
-- ORDER BY embedding <=> '[...]'::vector 
-- LIMIT 5;
```

## 🔐 User Management

```sql
-- Create user
CREATE USER maggot_user WITH PASSWORD 'password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE maggot_chatbot TO maggot_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO maggot_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO maggot_user;

-- Change password
ALTER USER postgres WITH PASSWORD 'new_password';
```

## 📝 psql Commands

```
\l              List databases
\c dbname       Connect to database
\dt             List tables
\d tablename    Describe table
\di             List indexes
\du             List users
\dx             List extensions
\q              Quit
\?              Help
\h SQL_COMMAND  SQL command help
\timing         Toggle timing
```

## 🚨 Emergency

```powershell
# Force stop service
taskkill /F /IM postgres.exe

# Restart PostgreSQL
net stop postgresql-x64-15
net start postgresql-x64-15

# Check if running
Get-Process postgres -ErrorAction SilentlyContinue
```

```sql
-- Reset database (DANGER!)
DROP DATABASE maggot_chatbot;
CREATE DATABASE maggot_chatbot;
-- Then run setup again
```

## 📌 Environment Variables

```env
# .env file
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=maggot_chatbot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
VECTOR_DIMENSION=3072
```

## 🔢 Useful Numbers

- **Vector Dimensions:**
  - text-embedding-3-large: 3072
  - text-embedding-3-small: 1536
  - all-MiniLM-L6-v2: 384

- **Index Types:**
  - HNSW: Best for dim <= 2000
  - IVFFlat: Works for dim > 2000
  - None: Sequential scan (slower)

- **Chunk Settings:**
  - CHUNK_SIZE: 800 characters
  - CHUNK_OVERLAP: 100 characters
  - TOP_K_RESULTS: 5

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `quick_setup.sql` | Quick database setup |
| `database_schema.sql` | Complete schema with docs |
| `sample_queries.sql` | Testing & monitoring queries |
| `setup_database.py` | Python setup script |
| `test_db_connection.py` | Test database connection |
| `DATABASE_SETUP_GUIDE.md` | Full setup guide |
| `WINDOWS_COMMANDS.md` | PowerShell commands |
| `SQL_FILES_README.md` | SQL files documentation |

---

**💡 Tip**: Bookmark this file untuk quick reference!

**Platform**: Windows + PostgreSQL 15 + pgvector  
**Last Updated**: November 2025
