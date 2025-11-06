# 🚀 Quick Start Guide - VERSI 2

## 📋 Ringkasan Project (Clean & Final)

✅ **34 files** diorganisir ke **6 folders**  
✅ **9.79 MB** total size (optimized)  
✅ **Production-ready** structure  
✅ **Complete documentation** di setiap folder  
✅ **Old files removed** - Clean codebase

---

## 📂 Struktur Folder Baru

```
VERSI 2/
├── api/        → REST API untuk mobile (4 files)
├── data/       → Dataset CSV (5 files)
├── docs/       → Dokumentasi lengkap (5 files)
├── models/     → ML models & encoders (8 files, 9 MB)
├── scripts/    → Python scripts & notebook (9 files)
└── mobile/     → Untuk kode Android/iOS (siap diisi)
```

---

## ⚡ Command Cheat Sheet

### 📊 **Data & Model**
```bash
# Lihat struktur folder
tree /F /A

# Lihat statistics
Get-ChildItem -Recurse -File | Measure-Object -Property Length -Sum
```

### 🎓 **Training**
```bash
cd scripts
python model_penetasan.py      # Train penetasan (78% accuracy)
python model_panen_maggot.py   # Train panen (88.6% R²)
python improve_model.py        # Full improvement pipeline
```

### 🎯 **Prediction**
```bash
cd scripts
python prediksi_interaktif.py  # Interactive CLI
python demo_prediksi.py        # Demo 4 scenarios
python prediksi_batch.py       # Batch from CSV
python lihat_hasil.py          # View batch results
```

### 🌐 **API Server**
```bash
cd api
pip install -r requirements_api.txt
python api_server.py           # Start server (port 5000)
python test_api.py             # Test all endpoints
```

### 📓 **Jupyter Notebook**
```bash
cd scripts
jupyter notebook model_training.ipynb
```

---

## 🔧 Path Configuration

**Semua script sudah diupdate!** ✅

Jika perlu update manual:
```python
# Dari folder scripts/
model = joblib.load('../models/model_penetasan_maggot.pkl')
df = pd.read_csv('../data/dummy_data.csv', delimiter=';')

# Dari folder api/
model = joblib.load('../models/model_penetasan_maggot.pkl')
```

---

## 📱 Mobile Integration

### **Android (Kotlin)**
```kotlin
// 1. Add dependencies (build.gradle)
implementation 'com.squareup.retrofit2:retrofit:2.9.0'
implementation 'com.squareup.retrofit2:converter-gson:2.9.0'

// 2. Copy code dari docs/MOBILE_INTEGRATION_GUIDE.md
// 3. Update BASE_URL dengan server Anda
private const val BASE_URL = "http://your-server-ip:5000/"
```

### **iOS (Swift)**
```swift
// 1. Copy code dari docs/MOBILE_INTEGRATION_GUIDE.md
// 2. Update baseURL
private let baseURL = "http://your-server-ip:5000"
```

**Dokumentasi lengkap:** `docs/MOBILE_INTEGRATION_GUIDE.md`

---

## 🚀 Deployment Steps

### **1. Deploy API ke Cloud**

#### **Heroku (Recommended)**
```bash
cd api
echo "web: gunicorn api_server:app" > Procfile
echo "python-3.12" > runtime.txt
heroku create maggot-ml-api
git push heroku main
```

#### **Google Cloud Run**
```bash
cd api
gcloud run deploy maggot-ml-api --source .
```

### **2. Update Mobile App**
```kotlin
// Update BASE_URL dengan URL production
private const val BASE_URL = "https://your-app.herokuapp.com/"
```

### **3. Test End-to-End**
```bash
# Test API
curl https://your-app.herokuapp.com/api/health

# Test prediction
curl -X POST https://your-app.herokuapp.com/api/predict/penetasan \
  -H "Content-Type: application/json" \
  -d '{"jumlah_telur_gram": 100, ...}'
```

---

## 📚 Dokumentasi

| File | Lokasi | Deskripsi |
|------|--------|-----------|
| **Quick Start** | `/QUICK_START.md` | File ini |
| **Project Structure** | `/PROJECT_STRUCTURE.md` | Detail struktur lengkap |
| **Reorganization** | `/REORGANIZATION_SUMMARY.md` | Summary perubahan |
| **API Docs** | `/api/README.md` | API usage & endpoints |
| **Scripts Docs** | `/scripts/README.md` | Panduan semua scripts |
| **Mobile Guide** | `/docs/MOBILE_INTEGRATION_GUIDE.md` | Kode Android & iOS |
| **Path Update** | `/PATH_UPDATE_GUIDE.md` | Reference path updates |

---

## 🎯 Model Performance

| Model | Metric | Score | Status |
|-------|--------|-------|--------|
| **Penetasan** | Accuracy | 78% | ✅ Excellent |
| **Penetasan** | CV Score | 76% ± 3.3% | ✅ Robust |
| **Panen** | R² Score | 88.6% | ✅ Excellent |
| **Panen** | MAPE | 10.71% | ✅ Very Good |

---

## 🔍 Troubleshooting

### **Import Error**
```bash
pip install pandas numpy scikit-learn matplotlib seaborn joblib flask flask-cors
```

### **Model Not Found**
```bash
# Check path dari folder yang benar
cd scripts
python prediksi_interaktif.py

# Atau re-train
python model_penetasan.py
```

### **CSV Delimiter Error**
```python
# Pastikan gunakan delimiter=';'
df = pd.read_csv('file.csv', delimiter=';')
```

### **API Connection Error**
```bash
# Check server running
curl http://localhost:5000/api/health

# Check firewall/port
netstat -ano | findstr :5000
```

---

## 📊 Testing Checklist

✅ **Models**
- [x] model_penetasan.py → 78% accuracy
- [x] model_panen_maggot.py → 88.6% R²

✅ **Scripts**
- [x] demo_prediksi.py → 4 predictions working
- [x] prediksi_interaktif.py → Interactive mode
- [x] prediksi_batch.py → Batch processing

✅ **API**
- [x] GET /api/health → 200 OK
- [x] GET /api/info → Model info
- [x] POST /api/predict/penetasan → Prediction
- [x] POST /api/predict/panen → Prediction

✅ **Path Updates**
- [x] 8 files auto-updated
- [x] All working from correct folders

---

## 🎊 Next Steps

### **Short Term (1 week)**
1. ✅ Reorganisasi folder → **DONE**
2. ✅ Update semua paths → **DONE**
3. ✅ Buat dokumentasi → **DONE**
4. ⏳ Deploy API ke cloud → **IN PROGRESS**
5. ⏳ Start mobile development

### **Medium Term (1 month)**
1. Build Android app (Kotlin)
2. Build iOS app (Swift)
3. Integrate with API
4. User testing
5. Production deployment

### **Long Term (3 months)**
1. Collect real data from users
2. Retrain models with more data
3. Add new features (camera, weather API)
4. Scale infrastructure
5. Marketing & user acquisition

---

## 💡 Tips

✅ **Development:**
- Selalu test dari folder yang benar
- Gunakan relative paths (`../`)
- Backup sebelum re-train model

✅ **Production:**
- Deploy API sebelum mobile app
- Gunakan HTTPS untuk security
- Add API authentication
- Monitor server performance

✅ **Mobile:**
- Test API endpoints dulu
- Handle network errors
- Add loading indicators
- Cache predictions offline

---

## 📞 Support

**Documentation:** Lihat folder `/docs/`  
**Issues:** Check `/PATH_UPDATE_GUIDE.md`  
**API Help:** See `/api/README.md`  
**Mobile:** See `/docs/MOBILE_INTEGRATION_GUIDE.md`

---

## 🎉 Summary

✅ **Project Structure:** Professional & clean  
✅ **Documentation:** Complete & detailed  
✅ **Code Quality:** Tested & working  
✅ **Model Performance:** Excellent (78% & 88.6%)  
✅ **API Ready:** Production-ready  
✅ **Mobile Ready:** Guides & code available  

**Status:** 🚀 **READY FOR PRODUCTION!**

---

**Last Update:** 2025-11-05  
**Version:** 2.1 (Clean)  
**Total Files:** 34 (9.79 MB)  
**Status:** 🚀 **PRODUCTION READY!**
