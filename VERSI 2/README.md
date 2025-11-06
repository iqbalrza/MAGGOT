# 📁 Struktur Folder VERSI 2 - Maggot BSF ML

## 📂 Struktur Direktori (Clean & Organized)

```
VERSI 2/  (31 files, ~10 MB)
│
├── � README.md                           # Project overview (this file)
├── 📄 QUICK_START.md                      # Quick start guide
├── 📄 PROJECT_STRUCTURE.md                # Detailed structure
│
├── �📁 models/ (8 files, ~9 MB)           # ML Models & Encoders
│   ├── model_penetasan_maggot.pkl         # Penetasan model (78% acc)
│   ├── model_panen_maggot.pkl             # Panen model (88.6% R²)
│   ├── model_penetasan_metadata.pkl       # Metadata penetasan
│   ├── model_panen_metadata.pkl           # Metadata panen
│   ├── label_encoder_media.pkl            # Media encoder
│   ├── label_encoder_weather.pkl          # Weather encoder
│   ├── label_encoder_season.pkl           # Season encoder
│   └── README.md                          # Model documentation
│
├── 📁 data/ (5 files, ~130 KB)           # Dataset & Data Files
│   ├── dummy_data.csv                     # Training data (500 samples)
│   ├── dummy_data_original_backup.csv     # Original backup (100 samples)
│   ├── input_batch.csv                    # Batch input template
│   ├── hasil_prediksi_batch.csv           # Batch results
│   └── README.md                          # Data documentation
│
├── 📁 scripts/ (9 files, ~90 KB)         # Python Scripts & Notebooks
│   ├── model_penetasan.py                 # Train penetasan model
│   ├── model_panen_maggot.py              # Train panen model
│   ├── improve_model.py                   # Model improvement pipeline
│   ├── prediksi_interaktif.py             # Interactive CLI
│   ├── demo_prediksi.py                   # Demo predictions
│   ├── prediksi_batch.py                  # Batch predictions
│   ├── lihat_hasil.py                     # View batch results
│   ├── model_training.ipynb               # Jupyter Notebook
│   └── README.md                          # Scripts documentation
│
├── 📁 api/ (4 files, ~21 KB)             # REST API untuk Mobile
│   ├── api_server.py                      # Flask REST API server
│   ├── test_api.py                        # API testing script
│   ├── requirements_api.txt               # API dependencies
│   └── README.md                          # API documentation
│
├── 📁 docs/ (5 files, ~1 MB)             # Dokumentasi & Visualisasi
│   ├── README.md                          # Main documentation
│   ├── API_MOBILE_INTEGRATION.md          # Architecture diagram
│   ├── MOBILE_INTEGRATION_GUIDE.md        # Android & iOS code
│   ├── evaluasi_model_panen.png           # Panen evaluation chart
│   └── model_improvement_results.png      # Model improvement chart
│
└── 📁 mobile/                             # Mobile App Code
    ├── 📁 android/                        # Android (Kotlin) - Ready
    └── 📁 ios/                            # iOS (Swift) - Ready

```

---

## 🚀 Quick Start

### 1. **Training Model**
```bash
cd scripts
python model_penetasan.py
python model_panen_maggot.py
```

### 2. **Prediksi Interaktif**
```bash
cd scripts
python prediksi_interaktif.py
```

### 3. **Run API Server**
```bash
cd api
pip install -r requirements_api.txt
python api_server.py
```

### 4. **Jupyter Notebook**
```bash
cd scripts
jupyter notebook model_training.ipynb
```

---

## 📊 Model Performance

| Model | Metric | Score |
|-------|--------|-------|
| **Penetasan** | Accuracy | **78%** |
| **Penetasan** | CV Score | 76% ± 3.3% |
| **Panen** | R² Score | **88.6%** |
| **Panen** | MAPE | 10.71% |

---

## 📖 Dokumentasi

Lihat folder `docs/` untuk dokumentasi lengkap:
- **README.md** - Dokumentasi model dan penggunaan
- **API_MOBILE_INTEGRATION.md** - Arsitektur integrasi mobile
- **MOBILE_INTEGRATION_GUIDE.md** - Panduan lengkap Android & iOS

---

## 🎯 Features

✅ **2 Model ML Terpisah:**
- Model Penetasan (78% accuracy)
- Model Panen (88.6% R² score)

✅ **REST API untuk Mobile:**
- `/api/predict/penetasan`
- `/api/predict/panen`

✅ **Scripts Lengkap:**
- Training, prediction, batch processing
- Interactive UI
- Jupyter Notebook

✅ **Production Ready:**
- Input validation
- Error handling
- Recommendations engine
- Business metrics

---

## 📱 Mobile Integration

Untuk integrasi ke aplikasi mobile (Android/iOS), lihat:
- **Dokumentasi:** `docs/MOBILE_INTEGRATION_GUIDE.md`
- **API Server:** `api/api_server.py`
- **Test API:** `api/test_api.py`

---

## 🔄 Update Log

**v2.1 (2025-11-05):**
- ✅ **Cleanup completed** - Removed VERSI 1 & temporary files
- ✅ Final structure: 31 files (~10 MB)
- ✅ Clean, production-ready codebase

**v2.0 (2025-11-05):**
- ✅ Restructure folder system (6 organized folders)
- ✅ Added mobile integration guide (Android & iOS)
- ✅ REST API implementation with Flask
- ✅ Complete documentation in each folder

**v1.0 (2025-11-05):**
- ✅ Improved model accuracy to 78% (from 40%)
- ✅ Feature engineering (7 → 21 features)
- ✅ Data augmentation (100 → 500 samples)
- ✅ Gradient Boosting optimization

---

## 📧 Support

Untuk pertanyaan dan support, lihat dokumentasi di folder `docs/`.

**Happy Farming! 🐛**
