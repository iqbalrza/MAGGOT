# OCR Setup Guide - Tesseract

Panduan instalasi dan konfigurasi Tesseract OCR untuk sistem chatbot.

## 📋 Arsitektur Baru

Sistem chatbot sekarang menggunakan alur sederhana:

```
1. Upload PDF
   ↓
2. Ekstraksi Teks & Gambar dengan OCR Tesseract
   ↓
3. Text Chunking
   ↓
4. Vector Embedding
   ↓
5. Simpan ke PostgreSQL + pgvector
```

## 🔧 Instalasi Tesseract

### Windows

1. **Download Tesseract Installer**
   - Kunjungi: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.x.exe` (versi terbaru)

2. **Install Tesseract**
   - Jalankan installer
   - Install ke: `C:\Program Files\Tesseract-OCR`
   - ✅ Centang "Add to PATH" saat instalasi

3. **Download Language Data (Optional)**
   - English sudah terinstall default
   - Untuk Indonesian: download `ind.traineddata`
   - Simpan di: `C:\Program Files\Tesseract-OCR\tessdata\`
   - Download dari: https://github.com/tesseract-ocr/tessdata

4. **Verifikasi Instalasi**
   ```powershell
   tesseract --version
   ```
   Output harus menampilkan versi Tesseract

### Linux (Ubuntu/Debian)

```bash
# Install Tesseract
sudo apt update
sudo apt install tesseract-ocr

# Install language pack Indonesian
sudo apt install tesseract-ocr-ind

# Verifikasi
tesseract --version
```

### macOS

```bash
# Install via Homebrew
brew install tesseract

# Install Indonesian language
brew install tesseract-lang

# Verifikasi
tesseract --version
```

## ⚙️ Konfigurasi

### File `.env`

Tambahkan konfigurasi berikut di file `.env`:

```env
# OCR Settings
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe  # Windows
# TESSERACT_CMD=/usr/bin/tesseract  # Linux/Mac

OCR_LANG=eng+ind  # English + Indonesian
SKIP_OCR=false    # Set true untuk skip OCR (hanya ekstrak teks native)
```

### Penjelasan Variabel

- **TESSERACT_CMD**: Path lengkap ke executable tesseract
  - Windows: `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - Linux: `/usr/bin/tesseract`
  - macOS: `/usr/local/bin/tesseract`
  
- **OCR_LANG**: Bahasa untuk OCR (gunakan `+` untuk multiple)
  - `eng`: English only
  - `ind`: Indonesian only
  - `eng+ind`: English + Indonesian

- **SKIP_OCR**: Skip OCR processing untuk speed
  - `false`: Gunakan OCR (lebih lambat, lebih akurat)
  - `true`: Hanya native text extraction (lebih cepat)

## 🧪 Testing OCR

### Test Tesseract Command Line

```powershell
# Test OCR pada gambar
tesseract test_image.png output -l eng+ind

# Lihat hasil
cat output.txt
```

### Test Python Integration

```python
import pytesseract
from PIL import Image

# Set path (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load image
img = Image.open('test.png')

# Perform OCR
text = pytesseract.image_to_string(img, lang='eng+ind')
print(text)
```

### Test PDF Processor

```bash
cd chatbot
python utils/pdf_processor.py
```

## 📊 Performa OCR

### Tips Optimasi

1. **DPI Setting**: PDF dikonversi ke 300 DPI untuk OCR yang lebih baik
2. **Preprocessing**: Image di-preprocess (grayscale, threshold, denoise)
3. **Language**: Gunakan language yang sesuai untuk akurasi lebih baik

### Benchmark

| Mode | Speed | Akurasi |
|------|-------|---------|
| Native Text Only | Fast (2-5s) | Baik untuk PDF digital |
| OCR + Native | Slow (30-60s) | Sangat baik untuk PDF scan |
| OCR Only | Medium (20-40s) | Terbaik untuk image/scan |

## 🐛 Troubleshooting

### Error: "tesseract is not installed"

**Solusi Windows:**
```powershell
# Tambahkan ke PATH
$env:Path += ";C:\Program Files\Tesseract-OCR"

# Atau set di .env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

**Solusi Linux:**
```bash
sudo apt install tesseract-ocr
```

### Error: "Failed to load language 'ind'"

**Solusi:**
- Download `ind.traineddata` dari: https://github.com/tesseract-ocr/tessdata
- Copy ke folder `tessdata`:
  - Windows: `C:\Program Files\Tesseract-OCR\tessdata\`
  - Linux: `/usr/share/tesseract-ocr/4.00/tessdata/`

### OCR Hasil Buruk

**Solusi:**
1. Pastikan PDF quality bagus (minimal 150 DPI)
2. Gunakan DPI lebih tinggi saat konversi (300-600)
3. Coba OCR lang yang berbeda
4. Check preprocessing settings

### OCR Terlalu Lambat

**Solusi:**
1. Set `SKIP_OCR=true` untuk PDF digital
2. Reduce DPI (tapi akurasi turun)
3. Process halaman tertentu saja
4. Gunakan multi-threading (future improvement)

## 🔄 Comparison: BLIP vs Tesseract

| Feature | BLIP (Old) | Tesseract (New) |
|---------|------------|-----------------|
| **Purpose** | Image captioning | Text extraction (OCR) |
| **Model Size** | ~1GB | ~50MB |
| **Dependencies** | PyTorch, Transformers | pytesseract, OpenCV |
| **GPU Required** | Yes (untuk speed) | No |
| **Output** | Natural language captions | Extracted text |
| **Best For** | Describing images | Reading text from images/tables |
| **Speed** | Slow (5-10s/image) | Fast (1-2s/page) |

## 📝 Next Steps

1. ✅ Install Tesseract
2. ✅ Configure `.env`
3. ✅ Test OCR
4. ✅ Upload PDF dan test full pipeline
5. ✅ Monitor hasil dan adjust settings

## 🎯 Use Cases

### Cocok untuk OCR:
- PDF hasil scan
- PDF dengan tabel/chart
- PDF dengan gambar berisi text
- Dokumen campuran text + image

### Skip OCR (faster):
- PDF digital native
- PDF dengan text murni
- Testing/development cepat

