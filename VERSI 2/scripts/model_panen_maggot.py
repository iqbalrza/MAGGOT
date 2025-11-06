"""
Model Prediksi Hasil Panen Maggot
==================================
Model: Gradient Boosting Regressor (XGBoost)
Input: Jumlah Telur (gram) + Jumlah Makanan (gram)
Output: Jumlah Panen (gram)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, '..', 'models')
data_dir = os.path.join(script_dir, '..', 'data')
docs_dir = os.path.join(script_dir, '..', 'docs')

# ==================== LOAD DATA ====================
print("=" * 60)
print("MODEL PREDIKSI HASIL PANEN MAGGOT")
print("=" * 60)

df = pd.read_csv(os.path.join(data_dir, 'dummy_data.csv'), delimiter=';')
print(f"\n✓ Data berhasil dimuat: {df.shape[0]} baris, {df.shape[1]} kolom")

# ==================== EKSPLORASI DATA ====================
print("\n" + "=" * 60)
print("EKSPLORASI DATA")
print("=" * 60)

print("\nStatistik Jumlah Telur:")
print(df['Jumlah_telur_gram'].describe())

print("\nStatistik Makanan:")
print(df['Makanan_gram'].describe())

print("\nStatistik Hasil Panen:")
print(df['Jumlah_panen_gram'].describe())

# Korelasi
print("\nKorelasi dengan Hasil Panen:")
correlation = df[['Jumlah_telur_gram', 'Makanan_gram', 'Jumlah_panen_gram']].corr()
print(correlation['Jumlah_panen_gram'].sort_values(ascending=False))

# ==================== PREPROCESSING ====================
print("\n" + "=" * 60)
print("PREPROCESSING DATA")
print("=" * 60)

# Siapkan fitur (X) dan target (y)
X = df[['Jumlah_telur_gram', 'Makanan_gram']].copy()
y = df['Jumlah_panen_gram'].copy()

# Split data: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n✓ Data training: {X_train.shape[0]} samples")
print(f"✓ Data testing: {X_test.shape[0]} samples")

# ==================== TRAINING MODEL ====================
print("\n" + "=" * 60)
print("TRAINING MODEL - GRADIENT BOOSTING REGRESSOR")
print("=" * 60)

# Model Gradient Boosting dengan hyperparameter tuning
print("\n⏳ Melakukan Grid Search untuk hyperparameter terbaik...")
param_grid = {
    'n_estimators': [100, 200, 300],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [3, 5, 7],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

gb_model = GradientBoostingRegressor(random_state=42)
grid_search = GridSearchCV(
    gb_model, 
    param_grid, 
    cv=5, 
    scoring='neg_mean_absolute_error',
    n_jobs=-1,
    verbose=0
)

grid_search.fit(X_train, y_train)

print(f"✓ Best Parameters: {grid_search.best_params_}")
print(f"✓ Best Cross-Validation MAE: {-grid_search.best_score_:.2f} gram")

# Model terbaik
best_model = grid_search.best_estimator_

# ==================== TRAINING RANDOM FOREST (PEMBANDING) ====================
print("\n⏳ Training Random Forest sebagai pembanding...")
rf_model = RandomForestRegressor(
    n_estimators=200, 
    max_depth=20, 
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
print("✓ Random Forest training selesai")

# ==================== EVALUASI MODEL ====================
print("\n" + "=" * 60)
print("EVALUASI MODEL")
print("=" * 60)

# Prediksi dengan Gradient Boosting
y_pred_gb = best_model.predict(X_test)

# Prediksi dengan Random Forest
y_pred_rf = rf_model.predict(X_test)

# Metrik Gradient Boosting
mae_gb = mean_absolute_error(y_test, y_pred_gb)
mse_gb = mean_squared_error(y_test, y_pred_gb)
rmse_gb = np.sqrt(mse_gb)
r2_gb = r2_score(y_test, y_pred_gb)
mape_gb = np.mean(np.abs((y_test - y_pred_gb) / y_test)) * 100

print("\n🔷 GRADIENT BOOSTING:")
print(f"  MAE (Mean Absolute Error): {mae_gb:.2f} gram")
print(f"  RMSE (Root Mean Squared Error): {rmse_gb:.2f} gram")
print(f"  R² Score: {r2_gb:.4f}")
print(f"  MAPE (Mean Absolute % Error): {mape_gb:.2f}%")

# Metrik Random Forest
mae_rf = mean_absolute_error(y_test, y_pred_rf)
mse_rf = mean_squared_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mse_rf)
r2_rf = r2_score(y_test, y_pred_rf)
mape_rf = np.mean(np.abs((y_test - y_pred_rf) / y_test)) * 100

print("\n🔶 RANDOM FOREST:")
print(f"  MAE (Mean Absolute Error): {mae_rf:.2f} gram")
print(f"  RMSE (Root Mean Squared Error): {rmse_rf:.2f} gram")
print(f"  R² Score: {r2_rf:.4f}")
print(f"  MAPE (Mean Absolute % Error): {mape_rf:.2f}%")

# Pilih model terbaik
if mae_gb < mae_rf:
    final_model = best_model
    model_name = "Gradient Boosting"
    y_pred_final = y_pred_gb
    mae_final = mae_gb
    rmse_final = rmse_gb
    r2_final = r2_gb
    mape_final = mape_gb
    print(f"\n✓ Model terbaik: {model_name}")
else:
    final_model = rf_model
    model_name = "Random Forest"
    y_pred_final = y_pred_rf
    mae_final = mae_rf
    rmse_final = rmse_rf
    r2_final = r2_rf
    mape_final = mape_rf
    print(f"\n✓ Model terbaik: {model_name}")

# Cross-validation score
cv_scores = cross_val_score(final_model, X, y, cv=5, scoring='neg_mean_absolute_error')
print(f"✓ Cross-Validation MAE (mean ± std): {-cv_scores.mean():.2f} ± {cv_scores.std():.2f} gram")

# Feature Importance
feature_importance = pd.DataFrame({
    'Feature': ['Jumlah Telur (gram)', 'Jumlah Makanan (gram)'],
    'Importance': final_model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\nFeature Importance:")
print(feature_importance)

# ==================== VISUALISASI ====================
print("\n" + "=" * 60)
print("VISUALISASI")
print("=" * 60)

fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# 1. Prediksi vs Aktual (Gradient Boosting)
ax1 = fig.add_subplot(gs[0, 0])
ax1.scatter(y_test, y_pred_gb, alpha=0.6, color='blue', label='Gradient Boosting')
ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
ax1.set_xlabel('Aktual (gram)')
ax1.set_ylabel('Prediksi (gram)')
ax1.set_title('Gradient Boosting: Prediksi vs Aktual')
ax1.legend()

# 2. Prediksi vs Aktual (Random Forest)
ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(y_test, y_pred_rf, alpha=0.6, color='orange', label='Random Forest')
ax2.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
ax2.set_xlabel('Aktual (gram)')
ax2.set_ylabel('Prediksi (gram)')
ax2.set_title('Random Forest: Prediksi vs Aktual')
ax2.legend()

# 3. Feature Importance
ax3 = fig.add_subplot(gs[0, 2])
ax3.barh(feature_importance['Feature'], feature_importance['Importance'], color='steelblue')
ax3.set_xlabel('Importance')
ax3.set_title(f'Feature Importance ({model_name})')
ax3.invert_yaxis()

# 4. Distribusi Error (Gradient Boosting)
ax4 = fig.add_subplot(gs[1, 0])
errors_gb = y_test - y_pred_gb
ax4.hist(errors_gb, bins=20, color='blue', alpha=0.7, edgecolor='black')
ax4.set_xlabel('Error (Aktual - Prediksi)')
ax4.set_ylabel('Frequency')
ax4.set_title('Gradient Boosting: Distribusi Error')
ax4.axvline(x=0, color='red', linestyle='--', linewidth=2)

# 5. Distribusi Error (Random Forest)
ax5 = fig.add_subplot(gs[1, 1])
errors_rf = y_test - y_pred_rf
ax5.hist(errors_rf, bins=20, color='orange', alpha=0.7, edgecolor='black')
ax5.set_xlabel('Error (Aktual - Prediksi)')
ax5.set_ylabel('Frequency')
ax5.set_title('Random Forest: Distribusi Error')
ax5.axvline(x=0, color='red', linestyle='--', linewidth=2)

# 6. Perbandingan Metrik
ax6 = fig.add_subplot(gs[1, 2])
metrics = ['MAE', 'RMSE', 'R²', 'MAPE']
gb_values = [mae_gb, rmse_gb, r2_gb*1000, mape_gb]  # Scale R² untuk visualisasi
rf_values = [mae_rf, rmse_rf, r2_rf*1000, mape_rf]
x = np.arange(len(metrics))
width = 0.35
ax6.bar(x - width/2, gb_values, width, label='Gradient Boosting', color='blue', alpha=0.7)
ax6.bar(x + width/2, rf_values, width, label='Random Forest', color='orange', alpha=0.7)
ax6.set_ylabel('Nilai')
ax6.set_title('Perbandingan Metrik Model')
ax6.set_xticks(x)
ax6.set_xticklabels(metrics)
ax6.legend()
ax6.grid(axis='y', alpha=0.3)

# 7. Korelasi Heatmap
ax7 = fig.add_subplot(gs[2, 0])
sns.heatmap(correlation, annot=True, fmt='.3f', cmap='coolwarm', center=0, 
            square=True, ax=ax7, cbar_kws={"shrink": 0.8})
ax7.set_title('Correlation Matrix')

# 8. Residual Plot
ax8 = fig.add_subplot(gs[2, 1])
residuals = y_test - y_pred_final
ax8.scatter(y_pred_final, residuals, alpha=0.6, color='green')
ax8.axhline(y=0, color='red', linestyle='--', linewidth=2)
ax8.set_xlabel('Prediksi (gram)')
ax8.set_ylabel('Residual (Aktual - Prediksi)')
ax8.set_title(f'{model_name}: Residual Plot')
ax8.grid(alpha=0.3)

# 9. Box Plot Error
ax9 = fig.add_subplot(gs[2, 2])
box_data = [errors_gb, errors_rf]
ax9.boxplot(box_data, labels=['Gradient\nBoosting', 'Random\nForest'])
ax9.set_ylabel('Error (gram)')
ax9.set_title('Distribusi Error: Perbandingan Model')
ax9.axhline(y=0, color='red', linestyle='--', linewidth=1)
ax9.grid(axis='y', alpha=0.3)

plt.savefig(os.path.join(docs_dir, 'evaluasi_model_panen.png'), dpi=300, bbox_inches='tight')
print("✓ Grafik evaluasi disimpan: evaluasi_model_panen.png")

# ==================== SIMPAN MODEL ====================
print("\n" + "=" * 60)
print("SIMPAN MODEL")
print("=" * 60)

# Simpan model terbaik
joblib.dump(final_model, os.path.join(models_dir, 'model_panen_maggot.pkl'))
print(f"✓ Model disimpan: model_panen_maggot.pkl ({model_name})")

# Simpan metadata
metadata = {
    'model_type': model_name,
    'feature_names': ['Jumlah_telur_gram', 'Makanan_gram'],
    'mae': mae_final,
    'rmse': rmse_final,
    'r2_score': r2_final,
    'mape': mape_final,
    'cv_score_mean': -cv_scores.mean(),
    'cv_score_std': cv_scores.std(),
    'best_params': grid_search.best_params_ if model_name == "Gradient Boosting" else {}
}
joblib.dump(metadata, os.path.join(models_dir, 'model_panen_metadata.pkl'))
print("✓ Metadata disimpan: model_panen_metadata.pkl")

# ==================== CONTOH PREDIKSI ====================
print("\n" + "=" * 60)
print("CONTOH PREDIKSI")
print("=" * 60)

def prediksi_panen(jumlah_telur, jumlah_makanan):
    """
    Prediksi hasil panen berdasarkan jumlah telur dan makanan
    
    Parameters:
    -----------
    jumlah_telur : float
        Jumlah telur dalam gram
    jumlah_makanan : float
        Jumlah makanan dalam gram
    
    Returns:
    --------
    float : Prediksi hasil panen dalam gram
    """
    # Buat input features
    X_input = np.array([[jumlah_telur, jumlah_makanan]])
    
    # Prediksi
    prediksi = final_model.predict(X_input)[0]
    
    # Hitung conversion rate (efisiensi)
    conversion_rate = (prediksi / jumlah_makanan) * 100
    
    return prediksi, conversion_rate

# Contoh penggunaan
print("\nContoh 1:")
telur1 = 250
makanan1 = 30000
pred1, conv1 = prediksi_panen(telur1, makanan1)
print(f"  Input: {telur1}g telur, {makanan1}g makanan")
print(f"  Prediksi Panen: {pred1:.0f} gram")
print(f"  Conversion Rate: {conv1:.2f}%")

print("\nContoh 2:")
telur2 = 150
makanan2 = 25000
pred2, conv2 = prediksi_panen(telur2, makanan2)
print(f"  Input: {telur2}g telur, {makanan2}g makanan")
print(f"  Prediksi Panen: {pred2:.0f} gram")
print(f"  Conversion Rate: {conv2:.2f}%")

print("\nContoh 3:")
telur3 = 100
makanan3 = 20000
pred3, conv3 = prediksi_panen(telur3, makanan3)
print(f"  Input: {telur3}g telur, {makanan3}g makanan")
print(f"  Prediksi Panen: {pred3:.0f} gram")
print(f"  Conversion Rate: {conv3:.2f}%")

print("\nContoh 4:")
telur4 = 300
makanan4 = 32000
pred4, conv4 = prediksi_panen(telur4, makanan4)
print(f"  Input: {telur4}g telur, {makanan4}g makanan")
print(f"  Prediksi Panen: {pred4:.0f} gram")
print(f"  Conversion Rate: {conv4:.2f}%")

# ==================== ANALISIS SENSITIVITAS ====================
print("\n" + "=" * 60)
print("ANALISIS SENSITIVITAS")
print("=" * 60)

# Variasi Jumlah Telur (fix makanan)
print("\n📊 Pengaruh Jumlah Telur (Makanan tetap: 25000g):")
for telur in [50, 100, 150, 200, 250, 300]:
    pred, conv = prediksi_panen(telur, 25000)
    print(f"  {telur}g telur → {pred:.0f}g panen (Conversion: {conv:.2f}%)")

# Variasi Jumlah Makanan (fix telur)
print("\n📊 Pengaruh Jumlah Makanan (Telur tetap: 200g):")
for makanan in [18000, 20000, 23000, 26000, 29000, 32000]:
    pred, conv = prediksi_panen(200, makanan)
    print(f"  {makanan}g makanan → {pred:.0f}g panen (Conversion: {conv:.2f}%)")

print("\n" + "=" * 60)
print("SELESAI!")
print("=" * 60)
