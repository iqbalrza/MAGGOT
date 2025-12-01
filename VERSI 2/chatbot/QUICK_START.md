# Quick Start Guide - Chatbot RAG

## 🚀 Instalasi Cepat (5 Menit)

### Step 1: Install Dependencies
```bash
cd chatbot
pip install -r requirements_chatbot.txt
```

### Step 2: Setup PostgreSQL & pgvector

#### Option A: Docker (Termudah)
```bash
docker run --name maggot-postgres \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=maggot_chatbot \
  -p 5432:5432 \
  -d pgvector/pgvector:pg15
```

#### Option B: Manual Install
Lihat: [DATABASE_SETUP_GUIDE.md](DATABASE_SETUP_GUIDE.md) untuk panduan lengkap install PostgreSQL & pgvector

### Step 3: Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env dan isi:
# - OPENAI_API_KEY=your_key_here
# - POSTGRES_PASSWORD=yourpassword
```

### Step 4: Initialize Database
```bash
python setup_db.py
```

### Step 5: Start Server
```bash
python chatbot_api.py
```

Server berjalan di: http://localhost:5001

### Step 6: Test API
```bash
# Terminal baru
python test_chatbot.py
```

## 📝 Test Manual dengan cURL

### 1. Health Check
```bash
curl http://localhost:5001/health
```

### 2. Upload PDF
```bash
curl -X POST http://localhost:5001/api/upload \
  -F "file=@path/to/your/document.pdf"
```

### 3. Query Chatbot
```bash
curl -X POST http://localhost:5001/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Apa faktor yang mempengaruhi penetasan telur maggot BSF?",
    "top_k": 5
  }'
```

## ❓ Troubleshooting

### Error: Could not connect to database
```bash
# Pastikan PostgreSQL berjalan
docker ps  # Cek container
docker start maggot-postgres  # Start jika belum running
```

### Error: OpenAI API key
```bash
# Cek .env file
cat .env | grep OPENAI_API_KEY

# Pastikan key valid di https://platform.openai.com/api-keys
```

### Error: Module not found
```bash
# Install ulang dependencies
pip install -r requirements_chatbot.txt --upgrade
```

## 📱 Integrasi Mobile

Lihat: [MOBILE_INTEGRATION.md](MOBILE_INTEGRATION.md)

## 📖 Dokumentasi Lengkap

Lihat: [README.md](README.md)

---

**Setup berhasil! 🎉**

Sekarang Anda bisa:
1. Upload PDF jurnal via API
2. Chat dengan AI tentang isi jurnal
3. Integrasikan dengan mobile app
