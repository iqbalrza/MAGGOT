# 📱 Panduan Integrasi ke Aplikasi Mobile

## 🎯 Langkah-langkah Implementasi

### **STEP 1: Setup Backend API**

#### 1.1 Install Dependencies
```bash
pip install -r requirements_api.txt
```

#### 1.2 Jalankan API Server
```bash
python api_server.py
```

Server akan berjalan di: `http://localhost:5000`

#### 1.3 Test API
```bash
python test_api.py
```

---

### **STEP 2: Deploy ke Server (Production)**

#### Opsi A: Deploy ke Cloud (Heroku)
```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn api_server:app" > Procfile

# Create runtime.txt
echo "python-3.12" > runtime.txt

# Deploy
heroku create maggot-ml-api
git push heroku main
```

#### Opsi B: Deploy ke VPS (DigitalOcean/AWS)
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

#### Opsi C: Deploy ke Google Cloud Run (Serverless)
```bash
# Create Dockerfile
# Build and deploy
gcloud run deploy maggot-ml-api --source .
```

---

### **STEP 3: Integrasi ke Mobile App**

## 📱 ANDROID (Kotlin/Java)

### 3.1 Add Dependencies (build.gradle)
```gradle
dependencies {
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
}
```

### 3.2 Create API Interface (MaggotApiService.kt)
```kotlin
package com.example.maggotapp.api

import retrofit2.Response
import retrofit2.http.*

// Data classes untuk request/response
data class PenetasanRequest(
    val jumlah_telur_gram: Float,
    val media_telur: String,
    val temp: Float,
    val humidity: Float,
    val temp_max: Float,
    val weather_main: String,
    val season: String
)

data class PanenRequest(
    val jumlah_telur_gram: Float,
    val makanan_gram: Float
)

data class PenetasanResponse(
    val success: Boolean,
    val prediction: PenetasanPrediction,
    val probabilities: Map<String, Float>,
    val recommendations: List<String>
)

data class PenetasanPrediction(
    val lama_penetasan_hari: Int,
    val confidence: Float,
    val confidence_label: String
)

data class PanenResponse(
    val success: Boolean,
    val prediction: PanenPrediction,
    val business_metrics: BusinessMetrics,
    val recommendations: List<String>
)

data class PanenPrediction(
    val jumlah_panen_gram: Float,
    val jumlah_panen_kg: Float,
    val conversion_rate: Float,
    val conversion_label: String
)

data class BusinessMetrics(
    val roi_estimate: Float,
    val estimated_value: String,
    val feed_cost: String
)

// API Service Interface
interface MaggotApiService {
    
    @GET("api/health")
    suspend fun healthCheck(): Response<Map<String, Any>>
    
    @GET("api/info")
    suspend fun getModelInfo(): Response<Map<String, Any>>
    
    @POST("api/predict/penetasan")
    suspend fun predictPenetasan(
        @Body request: PenetasanRequest
    ): Response<PenetasanResponse>
    
    @POST("api/predict/panen")
    suspend fun predictPanen(
        @Body request: PanenRequest
    ): Response<PanenResponse>
}
```

### 3.3 Create Retrofit Client (ApiClient.kt)
```kotlin
package com.example.maggotapp.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {
    
    // Ganti dengan URL production Anda
    private const val BASE_URL = "http://your-server-ip:5000/"
    // Atau: "https://maggot-ml-api.herokuapp.com/"
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val apiService: MaggotApiService = retrofit.create(MaggotApiService::class.java)
}
```

### 3.4 Create Repository (MaggotRepository.kt)
```kotlin
package com.example.maggotapp.repository

import com.example.maggotapp.api.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class MaggotRepository {
    
    private val apiService = ApiClient.apiService
    
    suspend fun predictPenetasan(
        jumlahTelur: Float,
        mediaTelur: String,
        temp: Float,
        humidity: Float,
        tempMax: Float,
        weather: String,
        season: String
    ): Result<PenetasanResponse> = withContext(Dispatchers.IO) {
        try {
            val request = PenetasanRequest(
                jumlah_telur_gram = jumlahTelur,
                media_telur = mediaTelur,
                temp = temp,
                humidity = humidity,
                temp_max = tempMax,
                weather_main = weather,
                season = season
            )
            
            val response = apiService.predictPenetasan(request)
            
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Prediction failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun predictPanen(
        jumlahTelur: Float,
        makanan: Float
    ): Result<PanenResponse> = withContext(Dispatchers.IO) {
        try {
            val request = PanenRequest(
                jumlah_telur_gram = jumlahTelur,
                makanan_gram = makanan
            )
            
            val response = apiService.predictPanen(request)
            
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Prediction failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### 3.5 Create ViewModel (PenetasanViewModel.kt)
```kotlin
package com.example.maggotapp.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.maggotapp.api.PenetasanResponse
import com.example.maggotapp.repository.MaggotRepository
import kotlinx.coroutines.launch

class PenetasanViewModel : ViewModel() {
    
    private val repository = MaggotRepository()
    
    private val _predictionResult = MutableLiveData<PenetasanResponse>()
    val predictionResult: LiveData<PenetasanResponse> = _predictionResult
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error
    
    fun predictPenetasan(
        jumlahTelur: Float,
        mediaTelur: String,
        temp: Float,
        humidity: Float,
        tempMax: Float,
        weather: String,
        season: String
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            
            val result = repository.predictPenetasan(
                jumlahTelur, mediaTelur, temp, humidity, tempMax, weather, season
            )
            
            result.onSuccess { response ->
                _predictionResult.value = response
                _error.value = null
            }.onFailure { exception ->
                _error.value = exception.message ?: "Unknown error"
            }
            
            _isLoading.value = false
        }
    }
}
```

### 3.6 Create UI Activity (PenetasanActivity.kt)
```kotlin
package com.example.maggotapp.ui

import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.example.maggotapp.R
import com.example.maggotapp.viewmodel.PenetasanViewModel

class PenetasanActivity : AppCompatActivity() {
    
    private val viewModel: PenetasanViewModel by viewModels()
    
    // UI Components
    private lateinit var etJumlahTelur: EditText
    private lateinit var spinnerMedia: Spinner
    private lateinit var etTemp: EditText
    private lateinit var etHumidity: EditText
    private lateinit var etTempMax: EditText
    private lateinit var spinnerWeather: Spinner
    private lateinit var spinnerSeason: Spinner
    private lateinit var btnPredict: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var tvResult: TextView
    private lateinit var tvConfidence: TextView
    private lateinit var tvRecommendations: TextView
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_penetasan)
        
        initViews()
        setupSpinners()
        setupObservers()
        setupListeners()
    }
    
    private fun initViews() {
        etJumlahTelur = findViewById(R.id.et_jumlah_telur)
        spinnerMedia = findViewById(R.id.spinner_media)
        etTemp = findViewById(R.id.et_temp)
        etHumidity = findViewById(R.id.et_humidity)
        etTempMax = findViewById(R.id.et_temp_max)
        spinnerWeather = findViewById(R.id.spinner_weather)
        spinnerSeason = findViewById(R.id.spinner_season)
        btnPredict = findViewById(R.id.btn_predict)
        progressBar = findViewById(R.id.progress_bar)
        tvResult = findViewById(R.id.tv_result)
        tvConfidence = findViewById(R.id.tv_confidence)
        tvRecommendations = findViewById(R.id.tv_recommendations)
    }
    
    private fun setupSpinners() {
        // Media options
        val mediaOptions = arrayOf(
            "Dedak atau Bekatul",
            "Kotoran Ternak (Fermentasi)",
            "Ampas atau Limbah Organik Basah"
        )
        spinnerMedia.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, mediaOptions)
        
        // Weather options
        val weatherOptions = arrayOf("Clear", "Clouds", "Rain", "Drizzle", "Thunderstorm")
        spinnerWeather.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, weatherOptions)
        
        // Season options
        val seasonOptions = arrayOf("Kemarau", "Hujan", "Pancaroba")
        spinnerSeason.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, seasonOptions)
    }
    
    private fun setupObservers() {
        viewModel.isLoading.observe(this) { isLoading ->
            progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
            btnPredict.isEnabled = !isLoading
        }
        
        viewModel.predictionResult.observe(this) { response ->
            displayResult(response)
        }
        
        viewModel.error.observe(this) { error ->
            error?.let {
                Toast.makeText(this, "Error: $it", Toast.LENGTH_LONG).show()
            }
        }
    }
    
    private fun setupListeners() {
        btnPredict.setOnClickListener {
            if (validateInput()) {
                makePrediction()
            }
        }
    }
    
    private fun validateInput(): Boolean {
        val jumlahTelur = etJumlahTelur.text.toString()
        val temp = etTemp.text.toString()
        val humidity = etHumidity.text.toString()
        val tempMax = etTempMax.text.toString()
        
        when {
            jumlahTelur.isEmpty() -> {
                etJumlahTelur.error = "Masukkan jumlah telur"
                return false
            }
            temp.isEmpty() -> {
                etTemp.error = "Masukkan suhu"
                return false
            }
            humidity.isEmpty() -> {
                etHumidity.error = "Masukkan kelembaban"
                return false
            }
            tempMax.isEmpty() -> {
                etTempMax.error = "Masukkan suhu maksimal"
                return false
            }
        }
        
        return true
    }
    
    private fun makePrediction() {
        val jumlahTelur = etJumlahTelur.text.toString().toFloat()
        val media = spinnerMedia.selectedItem.toString()
        val temp = etTemp.text.toString().toFloat()
        val humidity = etHumidity.text.toString().toFloat()
        val tempMax = etTempMax.text.toString().toFloat()
        val weather = spinnerWeather.selectedItem.toString()
        val season = spinnerSeason.selectedItem.toString()
        
        viewModel.predictPenetasan(
            jumlahTelur, media, temp, humidity, tempMax, weather, season
        )
    }
    
    private fun displayResult(response: PenetasanResponse) {
        val prediction = response.prediction
        
        // Display main result
        tvResult.text = "Prediksi Penetasan: ${prediction.lama_penetasan_hari} Hari"
        tvConfidence.text = "Confidence: ${prediction.confidence}% (${prediction.confidence_label})"
        
        // Display recommendations
        val recommendations = response.recommendations.joinToString("\n") { "• $it" }
        tvRecommendations.text = "Rekomendasi:\n$recommendations"
        
        // Show result card
        findViewById<View>(R.id.card_result).visibility = View.VISIBLE
    }
}
```

---

## 📱 iOS (Swift)

### 3.1 Create API Service
```swift
import Foundation

// MARK: - Models
struct PenetasanRequest: Codable {
    let jumlah_telur_gram: Float
    let media_telur: String
    let temp: Float
    let humidity: Float
    let temp_max: Float
    let weather_main: String
    let season: String
}

struct PenetasanResponse: Codable {
    let success: Bool
    let prediction: PenetasanPrediction
    let probabilities: [String: Float]
    let recommendations: [String]
}

struct PenetasanPrediction: Codable {
    let lama_penetasan_hari: Int
    let confidence: Float
    let confidence_label: String
}

// MARK: - API Service
class MaggotAPIService {
    
    static let shared = MaggotAPIService()
    private let baseURL = "http://your-server-ip:5000"
    
    private init() {}
    
    func predictPenetasan(
        request: PenetasanRequest,
        completion: @escaping (Result<PenetasanResponse, Error>) -> Void
    ) {
        guard let url = URL(string: "\(baseURL)/api/predict/penetasan") else {
            completion(.failure(NSError(domain: "Invalid URL", code: -1)))
            return
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            completion(.failure(error))
            return
        }
        
        URLSession.shared.dataTask(with: urlRequest) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -1)))
                return
            }
            
            do {
                let response = try JSONDecoder().decode(PenetasanResponse.self, from: data)
                completion(.success(response))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}
```

---

## 🔧 Tips Production

### 1. **Security**
```python
# Tambahkan authentication di api_server.py
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'YOUR_SECRET_KEY':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/predict/penetasan', methods=['POST'])
@require_api_key
def predict_penetasan():
    # ... existing code
```

### 2. **Rate Limiting**
```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### 3. **Caching**
```bash
pip install flask-caching
```

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/info')
@cache.cached(timeout=3600)
def model_info():
    # ... existing code
```

### 4. **Logging**
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('api.log', maxBytes=10000000, backupCount=5)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

---

## 📊 Testing Endpoints

### Gunakan Postman atau cURL:

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

**Predict Penetasan:**
```bash
curl -X POST http://localhost:5000/api/predict/penetasan \
  -H "Content-Type: application/json" \
  -d '{
    "jumlah_telur_gram": 100,
    "media_telur": "Dedak atau Bekatul",
    "temp": 29,
    "humidity": 75,
    "temp_max": 31,
    "weather_main": "Clear",
    "season": "Kemarau"
  }'
```

**Predict Panen:**
```bash
curl -X POST http://localhost:5000/api/predict/panen \
  -H "Content-Type: application/json" \
  -d '{
    "jumlah_telur_gram": 100,
    "makanan_gram": 5000
  }'
```

---

## 🎉 Summary

✅ **Backend:** Flask REST API dengan 2 endpoints terpisah  
✅ **Mobile:** Retrofit (Android) & URLSession (iOS)  
✅ **Features:** Input validation, recommendations, confidence scores  
✅ **Production Ready:** Error handling, logging, CORS support  

**Next Steps:**
1. Deploy API ke server cloud
2. Update BASE_URL di mobile app
3. Tambah authentication untuk security
4. Implement offline caching (optional)
