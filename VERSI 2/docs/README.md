# Sistem Prediksi Budidaya Maggot (Improved - 78% Accuracy)

Model machine learning untuk memprediksi lama penetasan dan hasil panen maggot dengan akurasi tinggi.

## 📊 Model yang Digunakan

### 1. Model Prediksi Penetasan Telur (Improved)
- **Model**: Gradient Boosting Classifier
- **Akurasi**: 78% (peningkatan 95% dari versi sebelumnya 40%)
- **Algorithm**: Gradient Boosting dengan 300 estimators
- **Input Features** (21 fitur): 
  - **Original (7)**: Jumlah telur, Media telur, Suhu, Kelembaban, Suhu max, Cuaca, Musim
  - **Engineered (14)**: 
    - Interaction: temp × humidity, telur/temp, temp range
    - Polynomial: temp², humidity²
    - Categorical: temp_level, humidity_level
    - Indicators: optimal_condition, is_rainy, is_clear, is_kemarau, is_hujan, dll
- **Output**: Lama penetasan (hari)
- **Performance**:
  - Test Accuracy: 78%
  - Cross-Validation: 76% ± 3.3%
  - Training Samples: 500 (augmented)
  
- **Feature Importance**:
  - Media Telur: 34.4% (paling penting)
  - Jumlah Telur: 17.2%
  - Weather: 9.6%
  - Temp × Humidity: 7.1%
  - Telur/Temp ratio: 5.4%

### 2. Model Prediksi Hasil Panen
- **Model**: Gradient Boosting Regressor
- **Akurasi**: R² Score 0.8856 (88.6%)
- **Input**: 
  - Jumlah telur (gram)
  - Jumlah makanan (gram)
- **Output**: Jumlah panen (gram)
- **Performance**:
  - MAE: 396.56 gram
  - RMSE: 491.73 gram
  - MAPE: 10.71%

## 🚀 Cara Menggunakan

### 1. Install Dependencies
```bash
pip install pandas numpy scikit-learn matplotlib seaborn joblib
```

### 2. Training Model
```bash
# Training model penetasan (improved - 78% accuracy)
python model_penetasan.py

# Training model panen
python model_panen_maggot.py

# Or improve existing model further
python improve_model.py
```

### 3. Demo Prediksi (Recommended)
```bash
python demo_prediksi.py
```
Menampilkan 4 contoh prediksi dengan berbagai kondisi cuaca.

### 4. Prediksi Interaktif
```bash
python prediksi_interaktif.py
```
Program akan memandu input data cuaca dan budidaya.

### 5. Prediksi Batch
```bash
python prediksi_batch.py
```

## 🌤️ Input Data Cuaca

### Musim
- **Kemarau**: April-Oktober (suhu tinggi, kelembaban rendah)
- **Hujan**: November-Maret (kelembaban tinggi)
- **Pancaroba**: Masa peralihan

### Kondisi Cuaca
- **Clear**: Cerah (optimal untuk penetasan)
- **Clouds**: Berawan
- **Rain**: Hujan (kelembaban tinggi)
- **Thunderstorm**: Hujan petir (ekstrem)

### Parameter Cuaca
- **Suhu**: 24-33°C (rata-rata Indonesia: 28°C)
- **Kelembaban**: 65-95% (rata-rata: 79%)
- **Suhu Max**: Biasanya +2°C dari suhu rata-rata

## 📁 File Output

### Model Files
- `model_penetasan_maggot.pkl` - Model penetasan dengan weather features
- `model_panen_maggot.pkl` - Model untuk prediksi panen
- `label_encoder_media.pkl` - Encoder untuk media telur
- `label_encoder_weather.pkl` - Encoder untuk kondisi cuaca
- `label_encoder_season.pkl` - Encoder untuk musim
- `model_penetasan_metadata.pkl` - Metadata model penetasan
- `model_panen_metadata.pkl` - Metadata model panen

### Visualisasi
- `evaluasi_model_penetasan.png` - Grafik evaluasi model penetasan
- `evaluasi_model_panen.png` - Grafik evaluasi model panen

## 🎯 Metrik Evaluasi

### Model Penetasan (Improved)
- **Accuracy**: 78% (peningkatan 95% dari 40%)
- **Algorithm**: Gradient Boosting Classifier
- **Cross-Validation Score**: 76% ± 3.3%
- **Features**: 21 (7 original + 14 engineered)
- **Training Data**: 500 samples (augmented)
- **Best Performance**:
  - Class 8 hari: 86% accuracy
  - Class 5 hari: 85% accuracy
  - Class 4 hari: 84% accuracy
- Confusion Matrix & Feature Importance Analysis

### Model Panen
- **R² Score**: 0.8856 (88.6%)
- **MAE**: 396.56 gram
- **RMSE**: 491.73 gram
- **MAPE**: 10.71%
- Cross-Validation MAE

## 💡 Contoh Penggunaan Programmatik

### Prediksi Penetasan (21 Features)
```python
import joblib
import numpy as np

# Load model dan metadata
model = joblib.load('model_penetasan_maggot.pkl')
metadata = joblib.load('model_penetasan_metadata.pkl')

# Input
jumlah_telur = 100
media_telur = "Dedak atau Bekatul"
temp = 29
humidity = 75
temp_max = 31
weather = "Clear"
season = "Kemarau"

# Encode categorical
media_enc = metadata['media_mapping'][media_telur]
weather_enc = metadata['weather_mapping'][weather]
season_enc = metadata['season_mapping'][season]

# Calculate engineered features
temp_humidity_idx = (temp * humidity) / 1000
temp_range = temp_max - temp
telur_per_temp = jumlah_telur / temp
temp_squared = temp ** 2
humidity_squared = humidity ** 2
temp_level = 0 if temp < 26 else (1 if temp < 29 else 2)
humidity_level = 0 if humidity < 75 else (1 if humidity < 85 else 2)
optimal_temp = 1 if 27 <= temp <= 30 else 0
optimal_humidity = 1 if 70 <= humidity <= 80 else 0
optimal_condition = optimal_temp * optimal_humidity
is_rainy = 1 if weather in ['Rain', 'Thunderstorm'] else 0
is_clear = 1 if weather == 'Clear' else 0
is_kemarau = 1 if season == 'Kemarau' else 0
is_hujan = 1 if season == 'Hujan' else 0

# Prediksi (21 features)
X_input = np.array([[
    jumlah_telur, temp, humidity, temp_max,
    media_enc, weather_enc, season_enc,
    temp_humidity_idx, temp_range, telur_per_temp,
    temp_squared, humidity_squared,
    temp_level, humidity_level,
    optimal_temp, optimal_humidity, optimal_condition,
    is_rainy, is_clear, is_kemarau, is_hujan
]])

prediksi = model.predict(X_input)[0]
proba = model.predict_proba(X_input)[0]
confidence = max(proba) * 100

print(f"Prediksi: {prediksi} hari")
print(f"Confidence: {confidence:.1f}%")
```

### Prediksi Panen
```python
import joblib
import numpy as np

# Load model
model = joblib.load('model_panen_maggot.pkl')

# Input
jumlah_telur = 100
jumlah_makanan = 5000

# Prediksi
X_input = np.array([[jumlah_telur, jumlah_makanan]])
prediksi = model.predict(X_input)[0]

print(f"Prediksi panen: {prediksi:.0f} gram ({prediksi/1000:.2f} kg)")
```

## 📋 Format Data Input

### File CSV
Data training dengan augmentation (500 samples, 12+ kolom):
```csv
Jumlah_telur_gram;Media_Telur;Lama_menetas_hari;Makanan_gram;Jumlah_panen_gram;temp;humidity;temp_max;weather_main;month;season
100;Dedak atau Bekatul;4;5000;2158;29;75;31;Clear;5;Kemarau
```

### Media Telur yang Tersedia
1. Ampas atau Limbah Organik Basah
2. Campuran Media (Kombinasi Kering & Basah)
3. Dedak atau Bekatul
4. Kotoran Ternak (Fermentasi)

## 📈 Interpretasi Hasil

### Waktu Penetasan
- 3-5 hari: Cepat (kondisi optimal)
- 6-8 hari: Normal
- 9-13 hari: Lambat (perlu optimalisasi)

### Hasil Panen
Output dalam gram dan kilogram untuk kemudahan interpretasi.

### Confidence Score
- < 30%: Rendah (data di luar pola training)
- 30-50%: Normal (sesuai dengan variasi data)
- > 50%: Tinggi (sangat sesuai dengan pola training)

## 🔬 Analisis & Insight

### Feature Importance (Top 10)
1. **Media Telur (34.4%)**: Faktor paling penting untuk penetasan
2. **Jumlah Telur (17.2%)**: Berpengaruh signifikan
3. **Weather (9.6%)**: Kondisi cuaca mempengaruhi
4. **Temp × Humidity (7.1%)**: Interaksi penting!
5. **Telur/Temp Ratio (5.4%)**: Engineered feature efektif
6. **Humidity² (4.0%)**: Non-linear relationship
7. **Temp² (3.8%)**: Polynomial feature berguna

### Kondisi Optimal
- Media: Dedak atau Bekatul
- Suhu: 28-30°C
- Kelembaban: 70-80%
- Cuaca: Clear atau Clouds
- Musim: Kemarau
- **Expected: 4-5 hari penetasan dengan confidence 85-95%**

### Improvement History
- **Original Model**: 40% accuracy (7 features, 100 samples)
- **Improved Model**: 78% accuracy (21 features, 500 samples)
- **Gain**: +95% relative improvement (+38 percentage points)

## ⚙️ Hyperparameter Tuning

Model menggunakan GridSearchCV untuk menemukan hyperparameter optimal:
- Random Forest: n_estimators, max_depth, min_samples_split, min_samples_leaf
- Gradient Boosting: learning_rate, n_estimators, max_depth, min_samples_split

## 📝 Catatan

- **Model Improved**: Akurasi 78% (peningkatan 95% dari 40%)
- **Data Augmentation**: 100 → 500 samples
- **Feature Engineering**: 7 → 21 features (interaction, polynomial, indicators)
- **Algorithm**: Gradient Boosting Classifier (terbaik dari 4 model yang diuji)
- **Cross-validation**: 5 folds untuk validasi robust
- **Confidence Score**: Rata-rata 85-100% untuk prediksi akurat

## 🚀 Cara Meningkatkan Akurasi Lebih Lanjut

1. **Collect Real Data** ⭐⭐⭐⭐⭐
   - Kumpulkan data real dari lapangan
   - Target: 1000+ samples
   - Expected: 80-85% accuracy

2. **More Feature Engineering**
   - Tambah fitur domain-specific
   - Time-series features
   - Interaction terms lebih banyak

3. **Advanced Algorithms**
   - Try XGBoost, LightGBM, CatBoost
   - Neural Networks
   - Stacking ensemble

4. **Hyperparameter Tuning**
   - GridSearchCV dengan parameter space lebih luas
   - Bayesian Optimization

5. **Data Quality**
   - Remove outliers carefully
   - Balance class distribution
   - Feature selection dengan SHAP

**Script tersedia**: `improve_model.py` untuk implementasi strategi di atas
