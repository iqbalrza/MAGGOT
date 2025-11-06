# 📊 Data Folder

Folder ini berisi semua dataset yang digunakan untuk training dan testing model.

## 📋 Files

### **Training Data**
- `dummy_data.csv` (500 samples, 125 KB)
  - Dataset augmented untuk training
  - 12 columns: id, Jumlah_telur_gram, Media_Telur, Lama_menetas_hari, Makanan_gram, Jumlah_panen_gram, temp, humidity, temp_max, weather_main, month, season
  - Delimiter: semicolon (`;`)
  - Size: 500 rows

### **Backup Data**
- `dummy_data_original_backup.csv` (100 samples, 5 KB)
  - Original dataset sebelum augmentation
  - Backup untuk referensi

### **Batch Processing**
- `input_batch.csv`
  - Template input untuk prediksi batch
  - Format sama dengan dummy_data.csv
  
- `hasil_prediksi_batch.csv`
  - Output hasil prediksi batch
  - Berisi prediksi + confidence scores

---

## 📖 Data Format

### dummy_data.csv Structure
```csv
id;Jumlah_telur_gram;Media_Telur;Lama_menetas_hari;Makanan_gram;Jumlah_panen_gram;temp;humidity;temp_max;weather_main;month;season
1;100;Dedak atau Bekatul;4;5000;4250;29;75;31;Clear;6;Kemarau
2;80;Kotoran Ternak (Fermentasi);8;4000;3100;26;90;28;Rain;12;Hujan
...
```

### Columns Description
| Column | Type | Description | Range/Values |
|--------|------|-------------|--------------|
| `id` | int | Unique identifier | 1-500 |
| `Jumlah_telur_gram` | float | Berat telur (gram) | 50-150 |
| `Media_Telur` | string | Media penetasan | 3 categories |
| `Lama_menetas_hari` | int | Target: Lama penetasan | 4-10 hari |
| `Makanan_gram` | float | Berat pakan (gram) | 3000-7000 |
| `Jumlah_panen_gram` | float | Target: Hasil panen | 2000-6000 |
| `temp` | float | Suhu rata-rata (°C) | 24-32 |
| `humidity` | float | Kelembaban (%) | 60-95 |
| `temp_max` | float | Suhu maksimal (°C) | 26-35 |
| `weather_main` | string | Kondisi cuaca | Clear/Clouds/Rain/Drizzle/Thunderstorm |
| `month` | int | Bulan (1-12) | 1-12 |
| `season` | string | Musim | Kemarau/Hujan/Pancaroba |

### Media_Telur Categories
1. Dedak atau Bekatul
2. Kotoran Ternak (Fermentasi)
3. Ampas atau Limbah Organik Basah

---

## 🔧 Usage

### Load Data
```python
import pandas as pd

# Load training data
df = pd.read_csv('data/dummy_data.csv', delimiter=';')

# Load original backup
df_original = pd.read_csv('data/dummy_data_original_backup.csv', delimiter=';')

# Load batch input
batch_input = pd.read_csv('data/input_batch.csv', delimiter=';')
```

### Create New Input for Batch Prediction
```python
import pandas as pd

# Create input
new_data = pd.DataFrame({
    'Jumlah_telur_gram': [100, 120],
    'Media_Telur': ['Dedak atau Bekatul', 'Kotoran Ternak (Fermentasi)'],
    'temp': [29, 27],
    'humidity': [75, 80],
    'temp_max': [31, 29],
    'weather_main': ['Clear', 'Clouds'],
    'season': ['Kemarau', 'Pancaroba'],
    'Makanan_gram': [5000, 6000]
})

# Save to CSV
new_data.to_csv('data/input_batch.csv', sep=';', index=False)
```

---

## 📈 Data Statistics

### Original Dataset (100 samples)
- Mean penetasan: 6.2 hari
- Mean panen: 3,850 gram
- Temp range: 24-32°C
- Humidity range: 60-95%

### Augmented Dataset (500 samples)
- Mean penetasan: 6.1 hari
- Mean panen: 3,920 gram
- Balanced across all classes
- Realistic variations maintained

---

## ⚠️ Important Notes

1. **Delimiter:** Gunakan semicolon (`;`) bukan comma (`,`)
2. **Encoding:** UTF-8
3. **Missing Values:** Tidak ada missing values
4. **Backup:** Selalu backup sebelum modify data

---

## 🔄 Update Data

Jika ingin menambah data baru:
1. Ikuti format yang sama
2. Pastikan menggunakan semicolon (`;`) sebagai delimiter
3. Validasi data terlebih dahulu
4. Re-train model jika perlu

Lihat script `../scripts/improve_model.py` untuk data augmentation.
