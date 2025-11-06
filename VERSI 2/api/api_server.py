"""
🚀 REST API Server untuk Aplikasi Mobile Maggot BSF
   
Endpoints:
- POST /api/predict/penetasan - Prediksi lama penetasan
- POST /api/predict/panen - Prediksi hasil panen
- GET /api/health - Health check
- GET /api/info - Model info

Author: Maggot ML Team
Date: 2025-11-05
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS untuk akses dari mobile app

# ==================== LOAD MODELS ====================
try:
    logger.info("Loading models...")
    
    # Load Penetasan model
    model_penetasan = joblib.load('../models/../models/model_penetasan_maggot.pkl')
    metadata_penetasan = joblib.load('../models/../models/model_penetasan_metadata.pkl')
    le_media = joblib.load('../models/../models/label_encoder_media.pkl')
    le_weather = joblib.load('../models/../models/label_encoder_weather.pkl')
    le_season = joblib.load('../models/../models/label_encoder_season.pkl')
    
    # Load Panen model
    model_panen = joblib.load('../models/../models/model_panen_maggot.pkl')
    metadata_panen = joblib.load('../models/../models/model_panen_metadata.pkl')
    
    logger.info("✓ All models loaded successfully!")
    
except Exception as e:
    logger.error(f"❌ Error loading models: {e}")
    raise


# ==================== HELPER FUNCTIONS ====================

def calculate_engineered_features(jumlah_telur, temp, humidity, temp_max):
    """Calculate all 14 engineered features"""
    features = {}
    
    # Interaction features
    features['temp_humidity_idx'] = (temp * humidity) / 1000
    features['temp_range'] = temp_max - temp
    features['telur_per_temp'] = jumlah_telur / temp
    
    # Polynomial features
    features['temp_squared'] = temp ** 2
    features['humidity_squared'] = humidity ** 2
    
    # Categorical binning
    features['temp_level'] = 0 if temp < 26 else (1 if temp < 29 else 2)
    features['humidity_level'] = 0 if humidity < 75 else (1 if humidity < 85 else 2)
    
    # Condition indicators
    features['optimal_temp'] = 1 if 27 <= temp <= 30 else 0
    features['optimal_humidity'] = 1 if 70 <= humidity <= 80 else 0
    features['optimal_condition'] = features['optimal_temp'] * features['optimal_humidity']
    
    return features


def validate_penetasan_input(data):
    """Validate input for penetasan prediction"""
    required_fields = ['jumlah_telur_gram', 'media_telur', 'temp', 
                      'humidity', 'temp_max', 'weather_main', 'season']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate numeric values
    try:
        jumlah_telur = float(data['jumlah_telur_gram'])
        temp = float(data['temp'])
        humidity = float(data['humidity'])
        temp_max = float(data['temp_max'])
        
        if jumlah_telur <= 0:
            return False, "jumlah_telur_gram must be positive"
        if temp < 15 or temp > 45:
            return False, "temp must be between 15-45°C"
        if humidity < 30 or humidity > 100:
            return False, "humidity must be between 30-100%"
        if temp_max <= temp:
            return False, "temp_max must be greater than temp"
            
    except ValueError:
        return False, "Invalid numeric value"
    
    # Validate categorical values
    media = data['media_telur']
    weather = data['weather_main']
    season = data['season']
    
    if media not in le_media.classes_:
        return False, f"Invalid media_telur. Valid options: {list(le_media.classes_)}"
    if weather not in le_weather.classes_:
        return False, f"Invalid weather_main. Valid options: {list(le_weather.classes_)}"
    if season not in le_season.classes_:
        return False, f"Invalid season. Valid options: {list(le_season.classes_)}"
    
    return True, "Valid"


def validate_panen_input(data):
    """Validate input for panen prediction"""
    required_fields = ['jumlah_telur_gram', 'makanan_gram']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate numeric values
    try:
        jumlah_telur = float(data['jumlah_telur_gram'])
        makanan = float(data['makanan_gram'])
        
        if jumlah_telur <= 0:
            return False, "jumlah_telur_gram must be positive"
        if makanan <= 0:
            return False, "makanan_gram must be positive"
            
    except ValueError:
        return False, "Invalid numeric value"
    
    return True, "Valid"


# ==================== API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Maggot ML API',
        'version': '1.0.0'
    })


@app.route('/api/info', methods=['GET'])
def model_info():
    """Get model information"""
    return jsonify({
        'penetasan_model': {
            'name': metadata_penetasan['model_name'],
            'accuracy': f"{metadata_penetasan['test_accuracy']:.2%}",
            'cv_score': f"{metadata_penetasan['cv_mean']:.2%}",
            'num_features': metadata_penetasan['num_features'],
            'media_options': list(le_media.classes_),
            'weather_options': list(le_weather.classes_),
            'season_options': list(le_season.classes_)
        },
        'panen_model': {
            'name': metadata_panen['model_name'],
            'r2_score': f"{metadata_panen['r2_score']:.4f}",
            'mae': f"{metadata_panen['mae']:.2f} gram",
            'mape': f"{metadata_panen['mape']:.2f}%"
        }
    })


@app.route('/api/predict/penetasan', methods=['POST'])
def predict_penetasan():
    """
    Predict hatching time (penetasan)
    
    Request body (JSON):
    {
        "jumlah_telur_gram": 100,
        "media_telur": "Dedak atau Bekatul",
        "temp": 29,
        "humidity": 75,
        "temp_max": 31,
        "weather_main": "Clear",
        "season": "Kemarau"
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate input
        is_valid, message = validate_penetasan_input(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Extract values
        jumlah_telur = float(data['jumlah_telur_gram'])
        media = data['media_telur']
        temp = float(data['temp'])
        humidity = float(data['humidity'])
        temp_max = float(data['temp_max'])
        weather = data['weather_main']
        season = data['season']
        
        # Encode categorical variables
        media_enc = metadata_penetasan['media_mapping'][media]
        weather_enc = metadata_penetasan['weather_mapping'][weather]
        season_enc = metadata_penetasan['season_mapping'][season]
        
        # Calculate engineered features
        eng_features = calculate_engineered_features(jumlah_telur, temp, humidity, temp_max)
        
        # Weather-based features
        is_rainy = 1 if weather in ['Rain', 'Thunderstorm'] else 0
        is_clear = 1 if weather == 'Clear' else 0
        
        # Season features
        is_kemarau = 1 if season == 'Kemarau' else 0
        is_hujan = 1 if season == 'Hujan' else 0
        
        # Create feature array (21 features in correct order)
        X_input = np.array([[
            jumlah_telur, temp, humidity, temp_max,
            media_enc, weather_enc, season_enc,
            eng_features['temp_humidity_idx'],
            eng_features['temp_range'],
            eng_features['telur_per_temp'],
            eng_features['temp_squared'],
            eng_features['humidity_squared'],
            eng_features['temp_level'],
            eng_features['humidity_level'],
            eng_features['optimal_temp'],
            eng_features['optimal_humidity'],
            eng_features['optimal_condition'],
            is_rainy, is_clear, is_kemarau, is_hujan
        ]])
        
        # Make prediction
        prediction = int(model_penetasan.predict(X_input)[0])
        probabilities = model_penetasan.predict_proba(X_input)[0]
        confidence = float(max(probabilities) * 100)
        
        # Get all class probabilities
        all_probs = {
            f"{int(cls)}_hari": float(prob * 100)
            for cls, prob in zip(model_penetasan.classes_, probabilities)
        }
        
        # Prepare response
        response = {
            'success': True,
            'prediction': {
                'lama_penetasan_hari': prediction,
                'confidence': round(confidence, 2),
                'confidence_label': 'Tinggi' if confidence >= 80 else ('Sedang' if confidence >= 60 else 'Rendah')
            },
            'probabilities': all_probs,
            'input_summary': {
                'jumlah_telur': f"{jumlah_telur}g",
                'media': media,
                'suhu': f"{temp}°C",
                'kelembaban': f"{humidity}%",
                'cuaca': weather,
                'musim': season
            },
            'recommendations': get_penetasan_recommendations(prediction, temp, humidity, weather),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Penetasan prediction: {prediction} hari (confidence: {confidence:.1f}%)")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in predict_penetasan: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/predict/panen', methods=['POST'])
def predict_panen():
    """
    Predict harvest amount (panen)
    
    Request body (JSON):
    {
        "jumlah_telur_gram": 100,
        "makanan_gram": 5000
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate input
        is_valid, message = validate_panen_input(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Extract values
        jumlah_telur = float(data['jumlah_telur_gram'])
        makanan = float(data['makanan_gram'])
        
        # Create feature array
        X_input = np.array([[jumlah_telur, makanan]])
        
        # Make prediction
        prediction = float(model_panen.predict(X_input)[0])
        
        # Calculate metrics
        conversion_rate = (prediction / makanan) * 100
        roi = ((prediction * 15) - (makanan * 2)) / (makanan * 2) * 100  # Asumsi harga
        
        # Prepare response
        response = {
            'success': True,
            'prediction': {
                'jumlah_panen_gram': round(prediction, 2),
                'jumlah_panen_kg': round(prediction / 1000, 3),
                'conversion_rate': round(conversion_rate, 2),
                'conversion_label': get_conversion_label(conversion_rate)
            },
            'input_summary': {
                'jumlah_telur': f"{jumlah_telur}g",
                'makanan': f"{makanan}g ({makanan/1000:.1f} kg)"
            },
            'business_metrics': {
                'roi_estimate': round(roi, 2),
                'estimated_value': f"Rp {int(prediction * 15):,}",  # Asumsi Rp 15/gram
                'feed_cost': f"Rp {int(makanan * 2):,}"  # Asumsi Rp 2/gram
            },
            'recommendations': get_panen_recommendations(prediction, makanan, conversion_rate),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Panen prediction: {prediction:.0f}g from {makanan}g feed")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in predict_panen: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== RECOMMENDATION FUNCTIONS ====================

def get_penetasan_recommendations(days, temp, humidity, weather):
    """Get recommendations based on prediction"""
    recommendations = []
    
    if days >= 7:
        recommendations.append("Penetasan cukup lama. Pertimbangkan untuk meningkatkan suhu dan kelembaban.")
    elif days <= 4:
        recommendations.append("Penetasan cepat! Kondisi sudah optimal.")
    
    if temp < 27:
        recommendations.append("Suhu terlalu rendah. Optimalkan ke 27-30°C.")
    elif temp > 30:
        recommendations.append("Suhu terlalu tinggi. Turunkan ke 27-30°C.")
    
    if humidity < 70:
        recommendations.append("Kelembaban terlalu rendah. Tingkatkan ke 70-80%.")
    elif humidity > 85:
        recommendations.append("Kelembaban terlalu tinggi. Turunkan ke 70-80%.")
    
    if weather in ['Rain', 'Thunderstorm']:
        recommendations.append("Cuaca hujan dapat memperlambat penetasan. Jaga suhu tetap stabil.")
    
    if not recommendations:
        recommendations.append("Kondisi sudah optimal! Pertahankan kondisi ini.")
    
    return recommendations


def get_panen_recommendations(panen, makanan, conversion):
    """Get recommendations based on harvest prediction"""
    recommendations = []
    
    if conversion < 15:
        recommendations.append("Conversion rate rendah. Periksa kualitas pakan dan kondisi lingkungan.")
    elif conversion > 25:
        recommendations.append("Conversion rate sangat baik! Pertahankan kondisi ini.")
    
    if panen < 3000:
        recommendations.append("Hasil panen rendah. Pertimbangkan menambah jumlah telur atau pakan.")
    elif panen > 8000:
        recommendations.append("Hasil panen sangat baik! Kondisi budidaya optimal.")
    
    optimal_feed = panen / 0.20  # Target 20% conversion
    if makanan < optimal_feed * 0.8:
        recommendations.append(f"Pakan kurang optimal. Pertimbangkan menambah ke {optimal_feed:.0f}g untuk hasil maksimal.")
    
    return recommendations


def get_conversion_label(rate):
    """Get conversion rate label"""
    if rate >= 25:
        return "Sangat Baik"
    elif rate >= 20:
        return "Baik"
    elif rate >= 15:
        return "Cukup"
    else:
        return "Perlu Perbaikan"


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 MAGGOT ML API SERVER")
    print("="*70)
    print("\nAvailable endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/info                - Model information")
    print("  POST /api/predict/penetasan   - Predict hatching time")
    print("  POST /api/predict/panen       - Predict harvest amount")
    print("\n" + "="*70)
    print("Server starting on http://0.0.0.0:5000")
    print("="*70 + "\n")
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=True)
