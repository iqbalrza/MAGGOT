import joblib
import numpy as np
import pandas as pd
import os

def load_models():
    """Load semua model dan encoders"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, '..', 'models')
    
    model_penetasan = joblib.load(os.path.join(models_dir, 'model_penetasan_maggot.pkl'))
    model_panen = joblib.load(os.path.join(models_dir, 'model_panen_maggot.pkl'))
    metadata = joblib.load(os.path.join(models_dir, 'model_penetasan_metadata.pkl'))
    
    return {
        'penetasan': model_penetasan,
        'panen': model_panen,
        'metadata': metadata
    }

def prediksi(jumlah_telur, media, temp, humidity, temp_max, weather, season, makanan, models):
    """Fungsi prediksi lengkap dengan 21 features"""
    # Encode categorical menggunakan mapping dari metadata
    metadata = models['metadata']
    media_encoded = metadata['media_mapping'].get(media, 0)
    weather_encoded = metadata['weather_mapping'].get(weather, 0)
    season_encoded = metadata['season_mapping'].get(season, 0)
    
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
    
    # Prediksi penetasan (21 features)
    X_penetasan = np.array([[
        jumlah_telur, temp, humidity, temp_max,
        media_encoded, weather_encoded, season_encoded,
        temp_humidity_idx, temp_range, telur_per_temp,
        temp_squared, humidity_squared,
        temp_level, humidity_level,
        optimal_temp, optimal_humidity, optimal_condition,
        is_rainy, is_clear, is_kemarau, is_hujan
    ]])
    
    lama_menetas = models['penetasan'].predict(X_penetasan)[0]
    pred_proba = models['penetasan'].predict_proba(X_penetasan)[0]
    confidence = max(pred_proba) * 100
    
    # Prediksi panen
    X_panen = np.array([[jumlah_telur, makanan]])
    jumlah_panen = models['panen'].predict(X_panen)[0]
    
    return {
        'lama_menetas': lama_menetas,
        'confidence': confidence,
        'jumlah_panen_gram': jumlah_panen,
        'jumlah_panen_kg': jumlah_panen / 1000
    }

def main():
    print("="*70)
    print("DEMO PREDIKSI BUDIDAYA MAGGOT (IMPROVED - 78% ACCURACY)")
    print("="*70)
    
    # Load models
    print("\nMemuat model...")
    models = load_models()
    print("Model berhasil dimuat!")
    
    # Contoh prediksi dengan berbagai kondisi cuaca
    contoh_data = [
        {
            'nama': 'Kondisi Optimal - Musim Kemarau Cerah',
            'jumlah_telur': 100,
            'media': 'Dedak atau Bekatul',
            'temp': 29,
            'humidity': 75,
            'temp_max': 31,
            'weather': 'Clear',
            'season': 'Kemarau',
            'makanan': 5000
        },
        {
            'nama': 'Kondisi Hujan - Kelembaban Tinggi',
            'jumlah_telur': 80,
            'media': 'Kotoran Ternak (Fermentasi)',
            'temp': 26,
            'humidity': 90,
            'temp_max': 28,
            'weather': 'Rain',
            'season': 'Hujan',
            'makanan': 4000
        },
        {
            'nama': 'Kondisi Pancaroba - Berawan',
            'jumlah_telur': 120,
            'media': 'Ampas atau Limbah Organik Basah',
            'temp': 28,
            'humidity': 80,
            'temp_max': 30,
            'weather': 'Clouds',
            'season': 'Pancaroba',
            'makanan': 6000
        },
        {
            'nama': 'Kondisi Ekstrem - Petir',
            'jumlah_telur': 90,
            'media': 'Campuran Media (Kombinasi Kering & Basah)',
            'temp': 25,
            'humidity': 95,
            'temp_max': 27,
            'weather': 'Thunderstorm',
            'season': 'Hujan',
            'makanan': 4500
        }
    ]
    
    for i, data in enumerate(contoh_data, 1):
        print(f"\n{'='*70}")
        print(f"CONTOH {i}: {data['nama']}")
        print('='*70)
        
        print("\nInput Data:")
        print(f"  Jumlah telur: {data['jumlah_telur']} gram")
        print(f"  Media telur: {data['media']}")
        print(f"  Suhu: {data['temp']}°C (max: {data['temp_max']}°C)")
        print(f"  Kelembaban: {data['humidity']}%")
        print(f"  Cuaca: {data['weather']}")
        print(f"  Musim: {data['season']}")
        print(f"  Jumlah makanan: {data['makanan']} gram")
        
        hasil = prediksi(
            jumlah_telur=data['jumlah_telur'],
            media=data['media'],
            temp=data['temp'],
            humidity=data['humidity'],
            temp_max=data['temp_max'],
            weather=data['weather'],
            season=data['season'],
            makanan=data['makanan'],
            models=models
        )
        
        print("\nHasil Prediksi:")
        print(f"  Lama penetasan: {hasil['lama_menetas']} hari")
        print(f"  Confidence: {hasil['confidence']:.1f}%")
        print(f"  Hasil panen: {hasil['jumlah_panen_gram']:.0f} gram ({hasil['jumlah_panen_kg']:.2f} kg)")
    
    print(f"\n{'='*70}")
    print("DEMO SELESAI")
    print('='*70)

if __name__ == "__main__":
    main()
