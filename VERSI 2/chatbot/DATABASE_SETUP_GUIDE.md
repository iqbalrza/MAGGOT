# 🗄️ Database Setup Guide - PostgreSQL with pgvector

Panduan lengkap untuk setup PostgreSQL dan pgvector extension untuk sistem chatbot RAG.

## 📋 Daftar Isi

- [Persyaratan Sistem](#persyaratan-sistem)
- [Instalasi PostgreSQL](#instalasi-postgresql)
- [Instalasi pgvector Extension](#instalasi-pgvector-extension)
- [Konfigurasi Database](#konfigurasi-database)
- [Setup Otomatis](#setup-otomatis)
- [Verifikasi Instalasi](#verifikasi-instalasi)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Persyaratan Sistem

- **PostgreSQL**: Version 12 atau lebih baru (Rekomendasi: PostgreSQL 15+)
- **Python**: Version 3.8+
- **Disk Space**: Minimal 500MB untuk PostgreSQL + data
- **RAM**: Minimal 2GB

---

## 📦 Instalasi PostgreSQL

### Windows

#### Metode 1: PostgreSQL Installer (Recommended)

1. **Download PostgreSQL Installer**
   - Kunjungi: https://www.postgresql.org/download/windows/
   - Download versi terbaru (PostgreSQL 15 atau 16)

2. **Jalankan Installer**
   ```
   - Run installer sebagai Administrator
   - Pilih komponen yang akan diinstall:
     ✅ PostgreSQL Server
     ✅ pgAdmin 4 (GUI Tool)
     ✅ Command Line Tools
     ✅ Stack Builder (untuk install extensions)
   ```

3. **Konfigurasi saat Instalasi**
   - **Port**: 5432 (default)
   - **Password**: Buat password untuk user `postgres` (INGAT PASSWORD INI!)
   - **Locale**: Default locale

4. **Selesaikan Instalasi**
   - Klik Next sampai selesai
   - Catat password yang sudah dibuat

#### Metode 2: Menggunakan Chocolatey

```powershell
# Install Chocolatey dulu jika belum ada
# Lihat: https://chocolatey.org/install

# Install PostgreSQL
choco install postgresql

# Start PostgreSQL service
net start postgresql-x64-15
```

### macOS

```bash
# Menggunakan Homebrew
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15

# Create default database
initdb /usr/local/var/postgres
```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Switch to postgres user
sudo -u postgres psql
```

---

## 🔌 Instalasi pgvector Extension

pgvector adalah PostgreSQL extension untuk menyimpan dan melakukan similarity search pada vector embeddings.

### Windows

#### Metode 1: Download Pre-built Binary (Recommended)

1. **Download pgvector untuk Windows**
   - Kunjungi: https://github.com/pgvector/pgvector/releases
   - Download file untuk Windows (contoh: `pgvector-v0.5.1-windows-x64.zip`)

2. **Extract dan Install**
   ```powershell
   # Extract ZIP file
   # Copy file DLL ke folder PostgreSQL
   
   # Lokasi default PostgreSQL (sesuaikan dengan versi Anda):
   # C:\Program Files\PostgreSQL\15\lib
   # C:\Program Files\PostgreSQL\15\share\extension
   
   # Copy vector.dll ke folder lib
   Copy-Item vector.dll "C:\Program Files\PostgreSQL\15\lib\"
   
   # Copy vector.control dan vector--*.sql ke folder extension
   Copy-Item vector.control "C:\Program Files\PostgreSQL\15\share\extension\"
   Copy-Item vector--*.sql "C:\Program Files\PostgreSQL\15\share\extension\"
   ```

3. **Restart PostgreSQL**
   ```powershell
   # Restart service
   net stop postgresql-x64-15
   net start postgresql-x64-15
   ```

#### Metode 2: Compile dari Source (Advanced)

Memerlukan Visual Studio dan build tools. Lihat dokumentasi resmi pgvector untuk detail.

### macOS

```bash
# Install pgvector menggunakan Homebrew
brew install pgvector

# Atau build dari source
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install
```

### Linux (Ubuntu/Debian)

```bash
# Metode 1: Dari package repository (jika tersedia)
sudo apt install postgresql-15-pgvector

# Metode 2: Build dari source
sudo apt install postgresql-server-dev-15 git build-essential
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

---

## ⚙️ Konfigurasi Database

### 1. Buat File `.env`

Buat file `.env` di folder `chatbot/` dengan konfigurasi berikut:

```env
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=maggot_chatbot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here

# Vector Dimension (Azure OpenAI text-embedding-3-large = 3072)
VECTOR_DIMENSION=3072

# Azure OpenAI Settings (untuk embeddings)
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=text-embedding-3-large
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Catatan Penting:**
- Ganti `your_password_here` dengan password PostgreSQL yang Anda buat saat instalasi
- `VECTOR_DIMENSION` harus sesuai dengan model embedding yang digunakan:
  - Azure OpenAI `text-embedding-3-large`: 3072
  - Azure OpenAI `text-embedding-3-small`: 1536
  - `sentence-transformers/all-MiniLM-L6-v2`: 384

### 2. Install Python Dependencies

```powershell
# Masuk ke folder chatbot
cd "c:\Users\iqbal\Documents\Code Labs\MAGGOT\VERSI 2\chatbot"

# Install dependencies
pip install -r requirements_chatbot.txt
```

---

## 🚀 Setup Otomatis

### Opsi 1: Python Script (Recommended)

Setup script akan otomatis:
- ✅ Cek koneksi PostgreSQL
- ✅ Buat database `maggot_chatbot`
- ✅ Install pgvector extension
- ✅ Buat tables (documents, chunks)
- ✅ Buat indexes untuk vector similarity search

```powershell
# Jalankan setup script
python setup_database.py
```

### Opsi 2: Manual SQL Setup

Jika ingin setup manual menggunakan SQL, tersedia file-file berikut:

#### Quick Setup (Rekomendasi untuk manual setup)
```powershell
# Jalankan quick setup SQL
psql -U postgres -f quick_setup.sql
```

File: `quick_setup.sql` - Setup cepat database, extension, dan tables

#### Complete Schema (Untuk referensi lengkap)
```powershell
# Jalankan complete schema
psql -U postgres -f database_schema.sql
```

File: `database_schema.sql` - Schema lengkap dengan comments, views, dan maintenance queries

#### Testing & Sample Queries
File: `sample_queries.sql` - Query untuk testing, monitoring, dan maintenance

**Catatan:**
- File SQL tersedia di folder `chatbot/`
- Gunakan `quick_setup.sql` untuk setup cepat
- Gunakan `database_schema.sql` untuk referensi lengkap
- Gunakan `sample_queries.sql` untuk testing dan monitoring

**Output yang diharapkan:**

```
================================================================================
🚀 DATABASE SETUP FOR CHATBOT SYSTEM
================================================================================
🔍 Checking PostgreSQL connection...
✅ PostgreSQL is running!

📦 Creating database 'maggot_chatbot'...
✅ Database 'maggot_chatbot' created!

🔌 Installing pgvector extension...
✅ pgvector extension installed!

📋 Setting up tables...
✅ Connected to PostgreSQL database: maggot_chatbot
✅ pgvector extension enabled
⚠️  Skipping vector index (dimension 3072 > 2000)
   Queries will use sequential scan (slower but works)
✅ Tables created successfully

📊 Database Statistics:
   Total documents: 0
   Total chunks: 0

================================================================================
✅ DATABASE SETUP COMPLETE!
================================================================================

📋 Next steps:
   1. Start the server: python chatbot_api.py
   2. Test with Postman (see POSTMAN_TESTING_GUIDE.md)
```

---

## ✅ Verifikasi Instalasi

### 1. Cek PostgreSQL Running

```powershell
# Cek service status (Windows)
sc query postgresql-x64-15

# Atau via pgAdmin
# Buka pgAdmin 4 dan connect ke server
```

### 2. Cek pgvector Extension

```sql
-- Connect ke database menggunakan psql atau pgAdmin
-- Windows PowerShell:
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot

-- Jalankan query:
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Output yang diharapkan:
--  oid  | extname | extowner | extnamespace | extrelocatable | extversion | extconfig | extcondition
-- ------+---------+----------+--------------+----------------+------------+-----------+--------------
-- 16384 | vector  |       10 |         2200 | f              | 0.5.1      |           |
```

### 3. Cek Tables

```sql
-- List tables
\dt

-- Output:
--            List of relations
--  Schema |   Name    | Type  |  Owner
-- --------+-----------+-------+----------
--  public | chunks    | table | postgres
--  public | documents | table | postgres

-- Cek struktur table chunks
\d chunks
```

### 4. Test Python Connection

```python
# test_db_connection.py
from models.vector_db import VectorDatabase
import os
from dotenv import load_dotenv

load_dotenv()

db = VectorDatabase(vector_dimension=3072)
if db.connect():
    print("✅ Database connection successful!")
    stats = db.get_stats()
    print(f"📊 Stats: {stats}")
    db.close()
else:
    print("❌ Connection failed!")
```

```powershell
python test_db_connection.py
```

---

## 🔧 Troubleshooting

### ❌ Error: "Could not connect to PostgreSQL"

**Penyebab:**
- PostgreSQL service tidak berjalan
- Password salah di `.env`
- Port tidak sesuai

**Solusi:**

```powershell
# Cek service status
sc query postgresql-x64-15

# Start service jika tidak berjalan
net start postgresql-x64-15

# Cek port yang digunakan
netstat -ano | findstr :5432

# Test connection manual
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -h localhost -p 5432
```

### ❌ Error: "extension 'vector' does not exist"

**Penyebab:**
- pgvector belum terinstall dengan benar

**Solusi:**

```powershell
# Verifikasi file pgvector ada di folder yang benar:
# - vector.dll harus ada di: C:\Program Files\PostgreSQL\15\lib\
# - vector.control harus ada di: C:\Program Files\PostgreSQL\15\share\extension\
# - vector--*.sql harus ada di: C:\Program Files\PostgreSQL\15\share\extension\

# Restart PostgreSQL setelah copy file
net stop postgresql-x64-15
net start postgresql-x64-15

# Coba install extension manual via psql
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d maggot_chatbot
CREATE EXTENSION vector;
```

### ❌ Error: "dimension cannot be greater than 16000"

**Penyebab:**
- Versi pgvector terlalu lama (< 0.5.0)

**Solusi:**
- Update pgvector ke versi 0.5.0 atau lebih baru
- Download dari: https://github.com/pgvector/pgvector/releases

### ❌ Error: "permission denied to create extension"

**Penyebab:**
- User tidak punya privilege untuk create extension

**Solusi:**

```sql
-- Login sebagai superuser (postgres)
-- Grant privilege ke user Anda
ALTER USER your_username WITH SUPERUSER;

-- Atau install extension sebagai postgres user
psql -U postgres -d maggot_chatbot -c "CREATE EXTENSION vector;"
```

### ⚠️ Warning: "Skipping vector index (dimension > 2000)"

**Penjelasan:**
- pgvector 0.5.0+ mendukung dimension sampai 16000
- Namun HNSW index hanya efisien untuk dimension <= 2000
- Untuk dimension > 2000, sistem akan menggunakan sequential scan
- Search tetap berfungsi, tapi lebih lambat untuk dataset besar

**Optimasi:**
- Untuk production dengan banyak dokumen, pertimbangkan:
  - Gunakan embedding model dengan dimension lebih kecil
  - Atau gunakan IVFFlat index sebagai alternatif
  - Atau upgrade hardware untuk mempercepat sequential scan

### 🔍 Cek Logs PostgreSQL

**Windows:**
```powershell
# Lokasi default log
Get-Content "C:\Program Files\PostgreSQL\15\data\log\*.log" -Tail 50
```

**Linux/macOS:**
```bash
# Cek log menggunakan journalctl
sudo journalctl -u postgresql -n 50

# Atau langsung dari file log
tail -f /var/log/postgresql/postgresql-15-main.log
```

---

## 📊 Schema Database

### Table: `documents`

Menyimpan metadata dokumen yang diupload.

| Column       | Type         | Description                    |
|-------------|--------------|--------------------------------|
| id          | SERIAL       | Primary key                    |
| filename    | VARCHAR(255) | Nama file                      |
| filepath    | TEXT         | Path file                      |
| file_size   | INTEGER      | Ukuran file (bytes)           |
| total_chunks| INTEGER      | Jumlah chunks                  |
| upload_date | TIMESTAMP    | Tanggal upload                 |
| metadata    | JSONB        | Metadata tambahan             |
| full_text   | TEXT         | Full text dokumen (optional)   |

### Table: `chunks`

Menyimpan text chunks dengan vector embeddings.

| Column      | Type       | Description                    |
|------------|------------|--------------------------------|
| id         | SERIAL     | Primary key                    |
| document_id| INTEGER    | Foreign key ke documents       |
| chunk_index| INTEGER    | Index chunk di dokumen         |
| text       | TEXT       | Text content chunk             |
| char_count | INTEGER    | Jumlah karakter                |
| embedding  | VECTOR(n)  | Vector embedding (dimensi n)   |
| metadata   | JSONB      | Metadata chunk                 |
| created_at | TIMESTAMP  | Tanggal dibuat                 |

**Indexes:**
- `chunks_embedding_idx`: HNSW index untuk similarity search (jika dimension <= 2000)
- `chunks_document_id_idx`: Index untuk lookup berdasarkan document_id

---

## 🎯 Next Steps

Setelah database setup berhasil:

1. ✅ **Start Chatbot API**: `python chatbot_api.py`
2. ✅ **Upload Dokumen**: Gunakan endpoint `/upload` untuk upload PDF
3. ✅ **Test Chat**: Gunakan endpoint `/chat` untuk bertanya
4. ✅ **Monitor**: Lihat logs dan database stats

**Referensi:**
- [QUICK_START.md](./QUICK_START.md) - Quick start guide
- [POSTMAN_TESTING_GUIDE.md](./POSTMAN_TESTING_GUIDE.md) - Test dengan Postman
- [README.md](./README.md) - Dokumentasi lengkap sistem

---

## 📚 Resources

- **PostgreSQL Official**: https://www.postgresql.org/
- **pgvector GitHub**: https://github.com/pgvector/pgvector
- **pgvector Documentation**: https://github.com/pgvector/pgvector#installation
- **Azure OpenAI Embeddings**: https://learn.microsoft.com/en-us/azure/ai-services/openai/

**Additional Guides:**
- **[SQL_FILES_README.md](SQL_FILES_README.md)** - Panduan file SQL (quick_setup.sql, database_schema.sql, sample_queries.sql)
- **[WINDOWS_COMMANDS.md](WINDOWS_COMMANDS.md)** - PowerShell commands untuk PostgreSQL di Windows

---

**Dibuat oleh**: Chatbot RAG System Team  
**Last Updated**: November 2025
