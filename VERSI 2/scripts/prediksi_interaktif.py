import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import os

def load_models():
    """Load semua model dan encoders yang diperlukan"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(script_dir, '..', 'models')
        
        # Load model penetasan (dengan weather features)
        model_penetasan = joblib.load(os.path.join(models_dir, 'model_penetasan_maggot.pkl'))
        metadata = joblib.load(os.path.join(models_dir, 'model_penetasan_metadata.pkl'))
        
        # Load model panen
        model_panen = joblib.load(os.path.join(models_dir, 'model_panen_maggot.pkl'))
        
        return {
            'penetasan': model_penetasan,
            'panen': model_panen,
            'metadata': metadata
        }
    except Exception as e:
        print(f"Error loading models: {e}")
        return None

def prediksi_penetasan_weather(jumlah_telur, media, temp, humidity, temp_max, weather, season, models):
    """Prediksi lama penetasan dengan 21 features"""
    try:
        # Encode categorical variables menggunakan mapping dari metadata
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
        
        # Siapkan input features (21 features)
        X = np.array([[
            jumlah_telur, temp, humidity, temp_max,
            media_encoded, weather_encoded, season_encoded,
            temp_humidity_idx, temp_range, telur_per_temp,
            temp_squared, humidity_squared,
            temp_level, humidity_level,
            optimal_temp, optimal_humidity, optimal_condition,
            is_rainy, is_clear, is_kemarau, is_hujan
        ]])
        
        # Prediksi
        lama_menetas = models['penetasan'].predict(X)[0]
        pred_proba = models['penetasan'].predict_proba(X)[0]
        confidence = max(pred_proba) * 100
        
        return {
            'lama_menetas': lama_menetas,
            'confidence': confidence,
            'probabilities': pred_proba
        }
    except Exception as e:
        print(f"Error dalam prediksi penetasan: {e}")
        return None

def prediksi_panen(jumlah_telur, makanan, models):
    """Prediksi jumlah panen"""
    try:
        X = np.array([[jumlah_telur, makanan]])
        jumlah_panen = models['panen'].predict(X)[0]
        
        return {
            'jumlah_panen_gram': jumlah_panen,
            'jumlah_panen_kg': jumlah_panen / 1000
        }
    except Exception as e:
        print(f"Error dalam prediksi panen: {e}")
        return None

def tampilkan_hasil(hasil_penetasan, hasil_panen):
    """Tampilkan hasil prediksi dengan format yang bersih"""
    print("\n" + "="*70)
    print("HASIL PREDIKSI BUDIDAYA MAGGOT")
    print("="*70)
    
    if hasil_penetasan:
        print("\n[PENETASAN TELUR]")
        print(f"Estimasi waktu penetasan: {hasil_penetasan['lama_menetas']} hari")
        print(f"Tingkat keyakinan: {hasil_penetasan['confidence']:.1f}%")
    
    if hasil_panen:
        print("\n[HASIL PANEN]")
        print(f"Estimasi hasil panen: {hasil_panen['jumlah_panen_gram']:.0f} gram")
        print(f"                      {hasil_panen['jumlah_panen_kg']:.2f} kg")
    
    print("\n" + "="*70)

def input_data_cuaca():
    """Input data cuaca dari user"""
    print("\n=== INPUT DATA CUACA ===")
    
    print("\nPilih musim:")
    print("1. Kemarau (April-Oktober)")
    print("2. Hujan (November-Maret)")
    print("3. Pancaroba (Peralihan)")
    season_choice = input("Pilih musim (1/2/3): ").strip()
    
    season_map = {
        '1': 'Kemarau',
        '2': 'Hujan',
        '3': 'Pancaroba'
    }
    season = season_map.get(season_choice, 'Kemarau')
    
    print("\nPilih kondisi cuaca:")
    print("1. Clear (Cerah)")
    print("2. Clouds (Berawan)")
    print("3. Rain (Hujan)")
    print("4. Thunderstorm (Petir)")
    weather_choice = input("Pilih cuaca (1/2/3/4): ").strip()
    
    weather_map = {
        '1': 'Clear',
        '2': 'Clouds',
        '3': 'Rain',
        '4': 'Thunderstorm'
    }
    weather = weather_map.get(weather_choice, 'Clear')
    
    # Input suhu dan kelembaban
    temp = float(input("\nSuhu rata-rata (°C) [24-33]: ").strip() or "28")
    temp_max = float(input("Suhu maksimum (°C) [26-35]: ").strip() or str(temp + 2))
    humidity = float(input("Kelembaban (%) [65-95]: ").strip() or "80")
    
    return {
        'temp': temp,
        'humidity': humidity,
        'temp_max': temp_max,
        'weather': weather,
        'season': season
    }

def main():
    """Fungsi utama untuk prediksi interaktif"""
    print("="*70)
    print("SISTEM PREDIKSI BUDIDAYA MAGGOT (IMPROVED - 78% ACCURACY)")
    print("="*70)
    
    # Load models
    print("\nMemuat model...")
    models = load_models()
    
    if models is None:
        print("Gagal memuat model. Pastikan file model tersedia.")
        return
    
    print("Model berhasil dimuat!")
    
    while True:
        try:
            # Input data penetasan
            print("\n" + "="*70)
            print("INPUT DATA BUDIDAYA")
            print("="*70)
            
            jumlah_telur = float(input("\nJumlah telur (gram): "))
            
            print("\nMedia telur:")
            print("1. Ampas atau Limbah Organik Basah")
            print("2. Campuran Media (Kombinasi Kering & Basah)")
            print("3. Dedak atau Bekatul")
            print("4. Kotoran Ternak (Fermentasi)")
            media_choice = input("Pilih media (1/2/3/4): ").strip()
            
            media_map = {
                '1': 'Ampas atau Limbah Organik Basah',
                '2': 'Campuran Media (Kombinasi Kering & Basah)',
                '3': 'Dedak atau Bekatul',
                '4': 'Kotoran Ternak (Fermentasi)'
            }
            media = media_map.get(media_choice, 'Dedak atau Bekatul')
            
            # Input data cuaca
            cuaca = input_data_cuaca()
            
            # Input data panen
            makanan = float(input("\nJumlah makanan (gram): "))
            
            # Prediksi penetasan
            hasil_penetasan = prediksi_penetasan_weather(
                jumlah_telur=jumlah_telur,
                media=media,
                temp=cuaca['temp'],
                humidity=cuaca['humidity'],
                temp_max=cuaca['temp_max'],
                weather=cuaca['weather'],
                season=cuaca['season'],
                models=models
            )
            
            # Prediksi panen
            hasil_panen = prediksi_panen(
                jumlah_telur=jumlah_telur,
                makanan=makanan,
                models=models
            )
            
            # Tampilkan hasil
            tampilkan_hasil(hasil_penetasan, hasil_panen)
            
            # Tanya apakah ingin prediksi lagi
            lanjut = input("\nPrediksi lagi? (y/n): ").strip().lower()
            if lanjut != 'y':
                print("\nTerima kasih telah menggunakan sistem prediksi!")
                break
                
        except KeyboardInterrupt:
            print("\n\nProgram dihentikan.")
            break
        except ValueError as e:
            print(f"\nError: Input tidak valid. {e}")
            continue
        except Exception as e:
            print(f"\nError: {e}")
            continue

if __name__ == "__main__":
    main()
