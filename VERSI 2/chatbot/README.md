# Chatbot RAG System - Maggot BSF

Sistem chatbot berbasis RAG (Retrieval Augmented Generation) dengan Tesseract OCR untuk ekstraksi teks dari PDF.

## 🎯 Fitur Utama

- **Upload PDF** dan ekstraksi otomatis
- **OCR dengan Tesseract** untuk membaca teks dari gambar/tabel
- **Text Chunking** dan vector embedding
- **Semantic Search** dengan pgvector
- **Azure OpenAI** untuk chatbot responses
- **REST API** untuk integrasi mobile

## 📋 Arsitektur

```
Upload PDF → OCR Tesseract → Text Chunking → Vector Embedding → PostgreSQL + pgvector
```

## 🚀 Quick Start

### 1. Install Dependencies

**Install Tesseract OCR:**
- Windows: Download dari [tesseract-ocr](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux: `sudo apt install tesseract-ocr tesseract-ocr-ind`
- macOS: `brew install tesseract tesseract-lang`

**Install Python packages:**
```bash
pip install -r requirements_chatbot.txt
```

**Install PostgreSQL dengan pgvector:**
- PostgreSQL 12+
- pgvector extension

### 2. Configure Environment

Copy `.env.example` ke `.env` dan isi:

```env
# OCR
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
OCR_LANG=eng+ind
SKIP_OCR=false

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=maggot_chatbot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Azure OpenAI
USE_AZURE_OPENAI=True
AZURE_EMBEDDING_API_KEY=your_key
AZURE_EMBEDDING_ENDPOINT=your_endpoint
AZURE_CHATBOT_API_KEY=your_key
AZURE_CHATBOT_ENDPOINT=your_endpoint

# Vector Config
VECTOR_DIMENSION=3072
CHUNK_SIZE=800
CHUNK_OVERLAP=100
```

### 3. Setup Database

```bash
python setup_database.py
```

### 4. Start Server

```bash
python chatbot_api.py
```

Server berjalan di: `http://localhost:5001`

## 📡 API Endpoints

### Upload PDF
```http
POST /api/upload
Content-Type: multipart/form-data

file: <PDF file>
```

### Query Chatbot
```http
POST /api/query
Content-Type: application/json

{
  "question": "Your question here",
  "document_id": 1,
  "top_k": 5
}
```

### List Documents
```http
GET /api/documents
```

### Delete Document
```http
DELETE /api/documents/{id}
```

## 📚 Dokumentasi Lengkap

- **[Database Setup Guide](DATABASE_SETUP_GUIDE.md)** - Panduan install PostgreSQL & pgvector
- **[OCR Setup Guide](OCR_SETUP_GUIDE.md)** - Panduan install Tesseract
- **[Postman Testing Guide](POSTMAN_TESTING_GUIDE.md)** - Testing dengan Postman
- **[Quick Start Guide](QUICK_START.md)** - Panduan cepat

## 🔧 Tech Stack

- **OCR:** Tesseract OCR + OpenCV
- **Backend:** Flask + Python 3.12
- **Database:** PostgreSQL + pgvector
- **Embedding:** Azure OpenAI (text-embedding-3-large, 3072 dim)
- **LLM:** Azure OpenAI (gpt-4o-mini)
- **Vector Search:** pgvector (sequential scan untuk 3072 dim)

## 📁 Project Structure

```
chatbot/
├── chatbot_api.py           # Main API server
├── setup_database.py        # Database setup script
├── requirements_chatbot.txt # Python dependencies
├── .env                     # Configuration (gitignored)
├── .env.example            # Configuration template
│
├── models/
│   ├── rag_system.py       # RAG implementation
│   └── vector_db.py        # PostgreSQL + pgvector
│
├── utils/
│   ├── pdf_processor.py    # OCR with Tesseract
│   ├── text_processor.py   # Chunking & embedding
│   └── azure_embeddings.py # Azure OpenAI embeddings
│
└── storage/
    └── uploads/            # Uploaded PDFs
```

## ⚙️ Configuration

### OCR Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `TESSERACT_CMD` | Auto-detect | Path to tesseract.exe |
| `OCR_LANG` | `eng+ind` | OCR languages |
| `SKIP_OCR` | `false` | Skip OCR (faster, less accurate) |

### Vector Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTOR_DIMENSION` | `3072` | Embedding dimension |
| `CHUNK_SIZE` | `800` | Characters per chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |

## 🐛 Troubleshooting

### Error: tesseract is not installed
Install Tesseract OCR dan set path di `.env`

### Error: Failed to connect to database
1. Check PostgreSQL is running
2. Verify credentials in `.env`
3. Run `python setup_database.py`

### Error: Vector dimension mismatch
Database dimension harus match dengan embedding dimension (3072)

## 📝 Notes

- **pgvector limitation:** Index tidak digunakan untuk dimension > 2000
- **Performance:** Sequential scan lebih lambat tapi works untuk 3072 dim
- **OCR:** Skip OCR (`SKIP_OCR=true`) untuk PDF digital (lebih cepat)

## 📄 License

MIT License
