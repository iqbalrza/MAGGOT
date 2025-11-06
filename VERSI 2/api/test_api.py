"""
Test script untuk REST API
Jalankan setelah api_server.py running
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_health():
    """Test health check"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    response = requests.get(f"{API_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_info():
    """Test model info"""
    print("\n" + "="*70)
    print("TEST 2: Model Info")
    print("="*70)
    
    response = requests.get(f"{API_URL}/api/info")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_penetasan():
    """Test penetasan prediction"""
    print("\n" + "="*70)
    print("TEST 3: Prediksi Penetasan")
    print("="*70)
    
    # Test case 1: Kondisi optimal
    data = {
        "jumlah_telur_gram": 100,
        "media_telur": "Dedak atau Bekatul",
        "temp": 29,
        "humidity": 75,
        "temp_max": 31,
        "weather_main": "Clear",
        "season": "Kemarau"
    }
    
    print("\nInput:")
    print(json.dumps(data, indent=2))
    
    response = requests.post(
        f"{API_URL}/api/predict/penetasan",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\nStatus: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))


def test_panen():
    """Test panen prediction"""
    print("\n" + "="*70)
    print("TEST 4: Prediksi Panen")
    print("="*70)
    
    # Test case 1: Normal feeding
    data = {
        "jumlah_telur_gram": 100,
        "makanan_gram": 5000
    }
    
    print("\nInput:")
    print(json.dumps(data, indent=2))
    
    response = requests.post(
        f"{API_URL}/api/predict/panen",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\nStatus: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))


def test_multiple_scenarios():
    """Test multiple scenarios"""
    print("\n" + "="*70)
    print("TEST 5: Multiple Scenarios")
    print("="*70)
    
    scenarios = [
        {
            "name": "Kondisi Hujan",
            "data": {
                "jumlah_telur_gram": 80,
                "media_telur": "Kotoran Ternak (Fermentasi)",
                "temp": 26,
                "humidity": 90,
                "temp_max": 28,
                "weather_main": "Rain",
                "season": "Hujan"
            }
        },
        {
            "name": "Kondisi Panas",
            "data": {
                "jumlah_telur_gram": 120,
                "media_telur": "Ampas atau Limbah Organik Basah",
                "temp": 32,
                "humidity": 65,
                "temp_max": 35,
                "weather_main": "Clear",
                "season": "Kemarau"
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        response = requests.post(
            f"{API_URL}/api/predict/penetasan",
            json=scenario['data']
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Prediksi: {result['prediction']['lama_penetasan_hari']} hari")
            print(f"Confidence: {result['prediction']['confidence']:.1f}%")
            print(f"Rekomendasi:")
            for rec in result['recommendations']:
                print(f"  • {rec}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TESTING MAGGOT ML API")
    print("="*70)
    print("\nPastikan api_server.py sudah running di http://localhost:5000")
    print("\n" + "="*70)
    
    try:
        # Run all tests
        test_health()
        test_info()
        test_penetasan()
        test_panen()
        test_multiple_scenarios()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED!")
        print("="*70 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Please start the server first: python api_server.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
