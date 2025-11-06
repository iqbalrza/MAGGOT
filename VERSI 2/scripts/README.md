# 🐍 Scripts Folder

Folder ini berisi semua Python scripts dan Jupyter Notebook untuk training, prediction, dan analysis.

## 📋 Files

### **Training Scripts**
1. **`model_penetasan.py`** (11 KB)
   - Train Gradient Boosting Classifier untuk penetasan
   - Features: 21 features (7 input + 14 engineered)
   - Output: Model + metadata + encoders + visualization
   - Runtime: ~30 seconds

2. **`model_panen_maggot.py`** (13 KB)
   - Train Gradient Boosting Regressor untuk panen
   - Features: 2 features (Jumlah telur, Makanan)
   - Output: Model + metadata + visualization
   - Runtime: ~10 seconds

3. **`improve_model.py`** (16 KB)
   - Comprehensive model improvement script
   - Data augmentation: 100 → 500 samples
   - Feature engineering: 7 → 21 features
   - Algorithm comparison: RF, GB, Ensemble
   - Output: Best model + comparison plots

### **Prediction Scripts**
4. **`prediksi_interaktif.py`** (8.4 KB)
   - Interactive CLI untuk prediksi
   - Input manual dari user
   - Output dengan rekomendasi
   - Usage: `python prediksi_interaktif.py`

5. **`demo_prediksi.py`** (5.6 KB)
   - Demo dengan 4 skenario contoh
   - Output: Prediksi + confidence + rekomendasi
   - Usage: `python demo_prediksi.py`

6. **`prediksi_batch.py`** (2.4 KB)
   - Batch prediction dari CSV
   - Input: `../data/input_batch.csv`
   - Output: `../data/hasil_prediksi_batch.csv`
   - Usage: `python prediksi_batch.py`

### **Utility Scripts**
7. **`lihat_hasil.py`** (1.2 KB)
   - View hasil prediksi batch
   - Pretty print results
   - Usage: `python lihat_hasil.py`

### **Jupyter Notebook**
8. **`model_training.ipynb`** (32 KB)
   - Complete training workflow
   - 12 sections: Data loading, EDA, Feature engineering, Training (both models), Evaluation, Testing
   - Interactive visualization
   - Usage: `jupyter notebook model_training.ipynb`

---

## 🚀 Usage Guide

### 1. Training Models

#### Train Penetasan Model
```bash
cd scripts
python model_penetasan.py
```
Output:
- `../models/model_penetasan_maggot.pkl`
- `../models/model_penetasan_metadata.pkl`
- `../models/label_encoder_*.pkl`
- `../docs/evaluasi_model_penetasan.png`

#### Train Panen Model
```bash
cd scripts
python model_panen_maggot.py
```
Output:
- `../models/model_panen_maggot.pkl`
- `../models/model_panen_metadata.pkl`
- `../docs/evaluasi_model_panen.png`

#### Improve Model (Full Pipeline)
```bash
cd scripts
python improve_model.py
```
Output:
- All model files + augmented data + comparison visualization

---

### 2. Making Predictions

#### Interactive Prediction
```bash
cd scripts
python prediksi_interaktif.py
```
Menu:
```
1. Prediksi Penetasan
2. Prediksi Panen
3. Keluar
```

#### Demo Prediction
```bash
cd scripts
python demo_prediksi.py
```
Shows 4 example scenarios with predictions.

#### Batch Prediction
```bash
cd scripts

# 1. Prepare input CSV
# Edit: ../data/input_batch.csv

# 2. Run batch prediction
python prediksi_batch.py

# 3. View results
python lihat_hasil.py
```

---

### 3. Jupyter Notebook

```bash
cd scripts
jupyter notebook model_training.ipynb
```

Or open in VS Code with Jupyter extension.

Notebook contains:
1. Import Libraries
2. Load Data
3. EDA with visualizations
4. Feature Engineering
5. Data Preparation
6. Train Penetasan Model
7. Visualize Penetasan Results
8. Train Panen Model
9. Visualize Panen Results
10. Save Models
11. Test Predictions
12. Summary

---

## 📊 Script Features

### model_penetasan.py
```python
# Key functions
def create_features(df):
    """Create 21 features from 7 inputs"""
    
def predict_penetasan(input_dict):
    """Predict with all 21 features"""
```

### model_panen_maggot.py
```python
# Key functions
def train_model():
    """Train Gradient Boosting Regressor"""
    
def predict_panen(jumlah_telur, makanan):
    """Predict harvest amount"""
```

### prediksi_interaktif.py
```python
# Key functions
def prediksi_penetasan_weather():
    """Interactive penetasan prediction"""
    
def prediksi_panen_interaktif():
    """Interactive panen prediction"""
    
def main_menu():
    """Main menu loop"""
```

### improve_model.py
```python
# Key functions
def augment_data(df, num_samples):
    """Generate synthetic data"""
    
def create_features(df):
    """Feature engineering"""
    
def compare_algorithms():
    """Compare RF, GB, Ensemble"""
```

---

## 🔧 Dependencies

Install required packages:
```bash
pip install pandas numpy scikit-learn matplotlib seaborn joblib
```

For Jupyter:
```bash
pip install jupyter ipykernel
```

For API:
```bash
cd ../api
pip install -r requirements_api.txt
```

---

## 📈 Performance

| Script | Runtime | Output |
|--------|---------|--------|
| model_penetasan.py | ~30s | Model (8.8MB) + metadata |
| model_panen_maggot.py | ~10s | Model (212KB) + metadata |
| improve_model.py | ~4min | Best model + plots |
| prediksi_interaktif.py | Interactive | Console output |
| demo_prediksi.py | ~1s | 4 predictions |
| prediksi_batch.py | ~1s | CSV output |

---

## 🎯 Best Practices

1. **Training:**
   - Jalankan `improve_model.py` untuk hasil terbaik
   - Backup model sebelum re-train
   - Validasi performa di test set

2. **Prediction:**
   - Gunakan `prediksi_interaktif.py` untuk testing
   - Gunakan `prediksi_batch.py` untuk production
   - Gunakan API untuk mobile integration

3. **Development:**
   - Gunakan `model_training.ipynb` untuk eksperimen
   - Update scripts setelah model improvement
   - Document changes di README

---

## 🐛 Troubleshooting

### Import Error
```bash
pip install -r ../api/requirements_api.txt
```

### Model Not Found
```bash
# Check path
ls ../models/*.pkl

# Re-train if needed
python model_penetasan.py
python model_panen_maggot.py
```

### CSV Delimiter Error
Make sure CSV uses semicolon (`;`):
```python
df = pd.read_csv('file.csv', delimiter=';')
```

---

## 📚 More Info

Lihat dokumentasi lengkap di folder `../docs/`.
