# SQL Files - Database Setup

Kumpulan file SQL untuk setup dan maintenance database PostgreSQL dengan pgvector.

## 📄 File yang Tersedia

### 1. `quick_setup.sql` ⚡
**Untuk**: Setup cepat database  
**Isi**: Query minimal untuk membuat database, extension, dan tables

**Cara pakai:**
```powershell
# Connect ke PostgreSQL dan jalankan file
psql -U postgres -f quick_setup.sql
```

**Atau secara manual:**
```powershell
# 1. Connect ke PostgreSQL
psql -U postgres

# 2. Copy-paste query dari quick_setup.sql
# 3. Jalankan satu per satu
```

---

### 2. `database_schema.sql` 📚
**Untuk**: Referensi lengkap schema database  
**Isi**: 
- Complete table definitions dengan comments
- Indexes (HNSW & IVFFlat)
- Views untuk reporting
- Sample queries
- Backup/restore commands
- Maintenance queries

**Cara pakai:**
```powershell
# Jalankan seluruh file
psql -U postgres -d maggot_chatbot -f database_schema.sql

# Atau buka di editor dan copy yang diperlukan
```

---

### 3. `sample_queries.sql` 🔍
**Untuk**: Testing, monitoring, dan troubleshooting  
**Isi**:
- Database statistics
- Data validation queries
- Performance monitoring
- Maintenance operations
- Testing queries
- Troubleshooting queries

**Cara pakai:**
```powershell
# Connect ke database
psql -U postgres -d maggot_chatbot

# Copy-paste query yang diperlukan
# Atau jalankan dari file
\i sample_queries.sql
```

---

## 🎯 Use Cases

### Setup Baru (Pertama Kali)

**Opsi A - Otomatis (Recommended):**
```powershell
python setup_database.py
```

**Opsi B - Manual SQL:**
```powershell
psql -U postgres -f quick_setup.sql
```

---

### Check Database Statistics

```powershell
psql -U postgres -d maggot_chatbot

# Lalu jalankan query dari sample_queries.sql
# Section 2: DATABASE STATISTICS
```

---

### Monitoring & Troubleshooting

```powershell
# Connect ke database
psql -U postgres -d maggot_chatbot

# Copy query dari sample_queries.sql:
# - Section 6: Performance Monitoring
# - Section 12: Troubleshooting
```

---

### Backup & Restore

```powershell
# Backup (Windows PowerShell)
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -d maggot_chatbot -F c -f backup.dump

# Restore
& "C:\Program Files\PostgreSQL\15\bin\pg_restore.exe" -U postgres -d maggot_chatbot -c -v backup.dump
```

---

## 📝 Notes

### Vector Dimensions

File SQL menggunakan **dimension 3072** (Azure OpenAI text-embedding-3-large).

**Jika menggunakan model lain**, edit dimension di:
- `quick_setup.sql` line 30: `embedding vector(3072)`
- `database_schema.sql` line 69: `embedding vector(3072)`

Contoh dimensi untuk model lain:
- `text-embedding-3-small`: 1536
- `all-MiniLM-L6-v2`: 384
- `text-embedding-ada-002`: 1536

### Indexes

**HNSW Index** (fast, tapi limited dimension <= 2000):
```sql
CREATE INDEX chunks_embedding_hnsw_idx 
ON chunks USING hnsw (embedding vector_cosine_ops);
```

**IVFFlat Index** (works untuk dimension > 2000):
```sql
CREATE INDEX chunks_embedding_ivfflat_idx 
ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

**No Index** (dimension > 2000, sequential scan):
- Lebih lambat tapi works untuk any dimension
- File setup default menggunakan ini untuk 3072 dim

---

## 🔧 Customization

### Ganti Vector Dimension

1. Edit file SQL yang diperlukan
2. Cari `vector(3072)` 
3. Ganti dengan dimension yang sesuai
4. Jalankan ulang setup

### Tambah Columns

Edit `database_schema.sql` dan tambahkan columns:

```sql
-- Contoh: tambah column language di documents
ALTER TABLE documents 
ADD COLUMN language VARCHAR(10) DEFAULT 'id';

-- Contoh: tambah column confidence_score di chunks
ALTER TABLE chunks 
ADD COLUMN confidence_score FLOAT;
```

### Tambah Indexes

```sql
-- Index untuk full text search
CREATE INDEX documents_fulltext_idx 
ON documents USING gin(to_tsvector('indonesian', full_text));

-- Index untuk filename search
CREATE INDEX documents_filename_idx 
ON documents(filename);
```

---

## 📚 Resources

**PostgreSQL Documentation:**
- https://www.postgresql.org/docs/

**pgvector Documentation:**
- https://github.com/pgvector/pgvector

**SQL Tutorial:**
- https://www.postgresql.org/docs/current/tutorial.html

---

## ⚠️ Important

1. **Backup sebelum menjalankan maintenance queries**
2. **Test di development environment dulu**
3. **Jangan jalankan DELETE/TRUNCATE di production tanpa backup**
4. **Monitor disk space saat VACUUM**
5. **REINDEX bisa memakan waktu untuk table besar**

---

**Created**: November 2025  
**For**: MAGGOT Chatbot RAG System
