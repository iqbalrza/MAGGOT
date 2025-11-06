# 📦 Models Folder

Folder ini berisi semua file model machine learning dan encoders.

## 📋 Files

### **ML Models**
- `model_penetasan_maggot.pkl` (8.8 MB)
  - Gradient Boosting Classifier
  - 78% accuracy
  - 21 features
  - 500 training samples

- `model_panen_maggot.pkl` (212 KB)
  - Gradient Boosting Regressor
  - R² score: 88.6%
  - 2 features
  - 500 training samples

### **Metadata**
- `model_penetasan_metadata.pkl`
  - Feature columns list (21 features)
  - Accuracy metrics
  - Categorical mappings
  
- `model_panen_metadata.pkl`
  - Feature columns list (2 features)
  - Performance metrics (MAE, RMSE, R², MAPE)

### **Label Encoders**
- `label_encoder_media.pkl`
  - Encodes: Media Telur (3 categories)
  
- `label_encoder_weather.pkl`
  - Encodes: Weather conditions (5 categories)
  
- `label_encoder_season.pkl`
  - Encodes: Seasons (3 categories)

---

## 🔧 Usage

### Load Models
```python
import joblib

# Load models
model_penetasan = joblib.load('models/model_penetasan_maggot.pkl')
model_panen = joblib.load('models/model_panen_maggot.pkl')

# Load encoders
le_media = joblib.load('models/label_encoder_media.pkl')
le_weather = joblib.load('models/label_encoder_weather.pkl')
le_season = joblib.load('models/label_encoder_season.pkl')

# Load metadata
metadata_pen = joblib.load('models/model_penetasan_metadata.pkl')
metadata_pan = joblib.load('models/model_panen_metadata.pkl')
```

### Make Predictions
Lihat script di folder `../scripts/` untuk contoh penggunaan lengkap.

---

## 📊 Model Specifications

### Penetasan Model
- **Algorithm:** Gradient Boosting Classifier
- **Features:** 21 (7 input + 14 engineered)
- **Classes:** 4-10 hari
- **Performance:** 78% test accuracy, 76% CV score

### Panen Model
- **Algorithm:** Gradient Boosting Regressor
- **Features:** 2 (Jumlah telur, Makanan)
- **Target:** Jumlah panen (gram)
- **Performance:** R² 0.8856, MAE 396.56g

---

⚠️ **Note:** Jangan hapus atau modifikasi file-file di folder ini. Model yang sudah di-train adalah production-ready.
