# Postman Testing Guide - Chatbot API

Panduan lengkap testing API chatbot menggunakan Postman.

## 🚀 Quick Start

### 1. Start Server
```powershell
cd "VERSI 2\chatbot"
python chatbot_api.py
```

Server akan berjalan di: `http://localhost:5001`

### 2. Open Postman

Download Postman: https://www.postman.com/downloads/

## 📡 API Endpoints Testing

### 1️⃣ Health Check

**Method:** `GET`  
**URL:** `http://localhost:5001/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Maggot BSF Chatbot API",
  "version": "1.0.0"
}
```

---

### 2️⃣ Upload PDF

**Method:** `POST`  
**URL:** `http://localhost:5001/api/upload`

#### Setup di Postman:

1. **Method:** Pilih `POST`

2. **URL:** `http://localhost:5001/api/upload`

3. **Headers:** (Auto-detected, tidak perlu set manual)
   - Content-Type: `multipart/form-data` (otomatis)

4. **Body:**
   - Pilih tab **"Body"**
   - Pilih **"form-data"** (bukan raw!)
   - Tambah field:
     - **Key:** `file` (ketik manual)
     - **Type:** Ubah dari "Text" ke **"File"** (dropdown di sebelah kanan key)
     - **Value:** Klik "Select Files" dan pilih PDF Anda

5. **Click "Send"**

#### Screenshots Guide:

```
┌─────────────────────────────────────────────────┐
│ POST  http://localhost:5001/api/upload    Send │
├─────────────────────────────────────────────────┤
│ Params  Authorization  Headers  Body  ...      │
│                                                  │
│ ● none  ○ form-data  ○ x-www-form-urlencoded   │
│ ○ raw   ○ binary     ○ GraphQL                 │
│                                                  │
│ ┌─────────────────────────────────────────┐    │
│ │ KEY      │ VALUE              │ TYPE    │    │
│ │ file     │ [Select Files]     │ File ▼  │    │
│ └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

#### Expected Response (Success):

```json
{
  "success": true,
  "document_id": 1,
  "filename": "sample.pdf",
  "file_size": 245632,
  "total_chunks": 25,
  "processing_time": "32.45s",
  "metadata": {
    "num_images": 10,
    "text_length": 5234,
    "ocr_text_length": 3421
  }
}
```

#### Possible Errors:

**Error 1: No file provided**
```json
{
  "error": "No file provided"
}
```
**Fix:** Pastikan key-nya "file" dan type-nya "File"

**Error 2: Invalid file type**
```json
{
  "error": "Invalid file type. Only PDF allowed"
}
```
**Fix:** Upload file dengan extension `.pdf`

**Error 3: File too large**
```json
{
  "error": "File too large. Maximum size is 100MB"
}
```
**Fix:** Compress PDF atau gunakan file lebih kecil

**Error 4: Failed to process PDF**
```json
{
  "error": "Failed to process PDF: tesseract is not installed"
}
```
**Fix:** Install Tesseract OCR (lihat OCR_SETUP_GUIDE.md)

---

### 3️⃣ Query Chatbot

**Method:** `POST`  
**URL:** `http://localhost:5001/api/query`

#### Setup di Postman:

1. **Method:** `POST`

2. **URL:** `http://localhost:5001/api/query`

3. **Headers:**
   - Key: `Content-Type`
   - Value: `application/json`

4. **Body:**
   - Pilih **"raw"**
   - Pilih **"JSON"** (dropdown di sebelah kanan)
   - Paste JSON ini:

```json
{
  "question": "Apa faktor yang mempengaruhi penetasan telur BSF?",
  "top_k": 5,
  "document_id": 1,
  "min_similarity": 0.3
}
```

5. **Click "Send"**

#### Request Body Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | ✅ Yes | Pertanyaan ke chatbot |
| `top_k` | integer | ❌ No | Jumlah chunks yang diambil (default: 5) |
| `document_id` | integer | ❌ No | Filter by document ID (optional) |
| `min_similarity` | float | ❌ No | Minimum similarity score (default: 0.3) |

#### Expected Response:

```json
{
  "question": "Apa faktor yang mempengaruhi penetasan telur BSF?",
  "answer": "Berdasarkan dokumen yang diunggah, faktor-faktor yang mempengaruhi penetasan telur Black Soldier Fly (BSF) meliputi:\n\n1. **Suhu**: Suhu optimal berkisar 25-30°C\n2. **Kelembaban**: Kelembaban ideal 60-70%\n3. **Kualitas media penetasan**: Media yang bersih dan sesuai\n4. **Nutrisi**: Ketersediaan makanan yang cukup\n\nProses penetasan biasanya memakan waktu sekitar 4 hari pada kondisi optimal.",
  "model": "gpt-4o-mini-2",
  "tokens_used": 245,
  "num_sources": 3,
  "sources": [
    {
      "text": "Proses penetasan telur BSF memakan waktu sekitar 4 hari...",
      "filename": "sample.pdf",
      "similarity": 0.85,
      "chunk_index": 5
    },
    {
      "text": "Faktor suhu sangat penting dalam penetasan...",
      "filename": "sample.pdf",
      "similarity": 0.78,
      "chunk_index": 12
    },
    {
      "text": "Kelembaban optimal untuk penetasan adalah 60-70%...",
      "filename": "sample.pdf",
      "similarity": 0.72,
      "chunk_index": 8
    }
  ]
}
```

---

### 4️⃣ Multi-turn Chat

**Method:** `POST`  
**URL:** `http://localhost:5001/api/chat`

#### Request Body:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Apa itu maggot BSF?"
    },
    {
      "role": "assistant",
      "content": "Maggot BSF adalah larva dari lalat Black Soldier Fly (Hermetia illucens)..."
    },
    {
      "role": "user",
      "content": "Berapa lama waktu penetasannya?"
    }
  ],
  "top_k": 5,
  "document_id": 1
}
```

#### Expected Response:

```json
{
  "question": "Berapa lama waktu penetasannya?",
  "answer": "Waktu penetasan telur BSF adalah sekitar 4 hari pada kondisi optimal (suhu 25-30°C dan kelembaban 60-70%).",
  "model": "gpt-4o-mini-2",
  "tokens_used": 180,
  "num_sources": 2
}
```

---

### 5️⃣ List Documents

**Method:** `GET`  
**URL:** `http://localhost:5001/api/documents`

**Optional Query Params:**
- `limit`: Jumlah maksimum dokumen (default: 100)

**Example:** `http://localhost:5001/api/documents?limit=10`

#### Expected Response:

```json
{
  "documents": [
    {
      "id": 1,
      "filename": "sample.pdf",
      "file_size": 245632,
      "total_chunks": 25,
      "upload_date": "2025-11-07T10:30:45",
      "metadata": {
        "num_images": 10,
        "text_length": 5234,
        "ocr_text_length": 3421
      }
    },
    {
      "id": 2,
      "filename": "document2.pdf",
      "file_size": 512000,
      "total_chunks": 45,
      "upload_date": "2025-11-07T11:15:22",
      "metadata": {
        "num_images": 15,
        "text_length": 8900,
        "ocr_text_length": 5200
      }
    }
  ],
  "count": 2
}
```

---

### 6️⃣ Get Document by ID

**Method:** `GET`  
**URL:** `http://localhost:5001/api/documents/{document_id}`

**Example:** `http://localhost:5001/api/documents/1`

#### Expected Response:

```json
{
  "id": 1,
  "filename": "sample.pdf",
  "filepath": "./storage/uploads/sample.pdf",
  "file_size": 245632,
  "total_chunks": 25,
  "upload_date": "2025-11-07T10:30:45",
  "metadata": {
    "num_images": 10,
    "text_length": 5234,
    "ocr_text_length": 3421
  },
  "full_text": "--- Page 1 ---\n..."
}
```

---

### 7️⃣ Delete Document

**Method:** `DELETE`  
**URL:** `http://localhost:5001/api/documents/{document_id}`

**Example:** `http://localhost:5001/api/documents/1`

#### Expected Response:

```json
{
  "success": true,
  "message": "Document 1 deleted"
}
```

---

### 8️⃣ Database Statistics

**Method:** `GET`  
**URL:** `http://localhost:5001/api/stats`

#### Expected Response:

```json
{
  "total_documents": 5,
  "total_chunks": 125,
  "total_size": 1245632
}
```

---

## 📋 Postman Collection

### Import ke Postman

Buat file `chatbot_api_collection.json`:

```json
{
  "info": {
    "name": "Maggot BSF Chatbot API",
    "description": "API for PDF upload and RAG chatbot",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:5001/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5001",
          "path": ["health"]
        }
      }
    },
    {
      "name": "Upload PDF",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": []
            }
          ]
        },
        "url": {
          "raw": "http://localhost:5001/api/upload",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5001",
          "path": ["api", "upload"]
        }
      }
    },
    {
      "name": "Query Chatbot",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"question\": \"Apa faktor yang mempengaruhi penetasan telur BSF?\",\n  \"top_k\": 5,\n  \"min_similarity\": 0.3\n}"
        },
        "url": {
          "raw": "http://localhost:5001/api/query",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5001",
          "path": ["api", "query"]
        }
      }
    },
    {
      "name": "List Documents",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:5001/api/documents?limit=10",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5001",
          "path": ["api", "documents"],
          "query": [
            {
              "key": "limit",
              "value": "10"
            }
          ]
        }
      }
    },
    {
      "name": "Get Document by ID",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:5001/api/documents/1",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5001",
          "path": ["api", "documents", "1"]
        }
      }
    },
    {
      "name": "Delete Document",
      "request": {
        "method": "DELETE",
        "header": [],
        "url": {
          "raw": "http://localhost:5001/api/documents/1",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5001",
          "path": ["api", "documents", "1"]
        }
      }
    },
    {
      "name": "Database Stats",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:5001/api/stats",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5001",
          "path": ["api", "stats"]
        }
      }
    }
  ]
}
```

**Cara Import:**
1. Buka Postman
2. Click "Import" button (kiri atas)
3. Drag & drop file `chatbot_api_collection.json`
4. Collection siap digunakan!

---

## 🧪 Testing Workflow

### Scenario 1: Upload & Query

1. **Start Server**
   ```powershell
   python chatbot_api.py
   ```

2. **Health Check** - Pastikan server running
   - `GET http://localhost:5001/health`

3. **Upload PDF**
   - `POST http://localhost:5001/api/upload`
   - Attach PDF file
   - Catat `document_id` dari response

4. **Query**
   - `POST http://localhost:5001/api/query`
   - Gunakan `document_id` dari step 3
   - Tanya sesuatu tentang PDF

5. **Verify**
   - Check response answer sesuai dengan PDF

### Scenario 2: Fast Mode (Skip OCR)

1. **Edit `.env`**
   ```env
   SKIP_OCR=true
   ```

2. **Restart Server**

3. **Upload PDF** - Harusnya lebih cepat!

4. **Compare processing_time** dengan full OCR mode

### Scenario 3: Multi-Document Query

1. **Upload multiple PDFs**
   - Upload PDF 1, dapat document_id = 1
   - Upload PDF 2, dapat document_id = 2

2. **Query specific document**
   ```json
   {
     "question": "...",
     "document_id": 1
   }
   ```

3. **Query all documents** (omit document_id)
   ```json
   {
     "question": "..."
   }
   ```

---

## 🐛 Common Issues

### Issue 1: Connection Refused

**Error:** `Could not get any response`

**Fix:**
- Pastikan server running: `python chatbot_api.py`
- Check port 5001 tidak digunakan app lain
- Check firewall settings

### Issue 2: File Upload Fails

**Error:** `No file provided`

**Fix:**
- Pastikan di Body pilih **"form-data"** (bukan raw!)
- Key harus **"file"** (lowercase)
- Type harus **"File"** (bukan Text)

### Issue 3: Database Error

**Error:** `Failed to connect to database`

**Fix:**
- Pastikan PostgreSQL running
- Check credentials di `.env`
- Run: `python models/vector_db.py` untuk setup

### Issue 4: OCR Error

**Error:** `tesseract is not installed`

**Fix:**
- Install Tesseract OCR
- Set path di `.env`: `TESSERACT_CMD=...`
- Atau set `SKIP_OCR=true` untuk skip OCR

---

## 📊 Performance Tips

### Faster Testing

1. **Skip OCR** untuk PDF digital:
   ```env
   SKIP_OCR=true
   ```

2. **Use smaller PDFs** untuk testing (1-5 pages)

3. **Reduce chunk size** di `.env`:
   ```env
   CHUNK_SIZE=500
   ```

### Better Results

1. **Use OCR** untuk scanned PDFs:
   ```env
   SKIP_OCR=false
   ```

2. **Increase top_k** untuk more context:
   ```json
   {"top_k": 10}
   ```

3. **Adjust similarity threshold**:
   ```json
   {"min_similarity": 0.2}
   ```

---

## 📱 Export for Mobile Team

### Generate Code Snippets

Postman dapat generate code untuk berbagai platform:

1. Click request (e.g., "Upload PDF")
2. Click **"Code"** button (kanan atas)
3. Pilih language:
   - **JavaScript - Fetch**
   - **Python - Requests**
   - **Java - OkHttp**
   - **Swift - URLSession**
   - **Kotlin - OkHttp**
   - dll.

Example untuk Flutter:
```dart
var headers = {
  'Content-Type': 'multipart/form-data'
};
var request = http.MultipartRequest('POST', Uri.parse('http://localhost:5001/api/upload'));
request.files.add(await http.MultipartFile.fromPath('file', '/path/to/file.pdf'));
request.headers.addAll(headers);

http.StreamedResponse response = await request.send();

if (response.statusCode == 200) {
  print(await response.stream.bytesToString());
}
```

---

## ✅ Testing Checklist

- [ ] Server can start
- [ ] Health check returns OK
- [ ] PDF upload works
- [ ] OCR extracts text
- [ ] Chunks are created
- [ ] Embeddings generated
- [ ] Data stored in database
- [ ] Query returns relevant answer
- [ ] Multi-turn chat works
- [ ] List documents works
- [ ] Delete document works
- [ ] Stats endpoint works

---

**Happy Testing! 🚀**
