import joblib
import os
from pathlib import Path

# Get the script's directory and construct absolute paths
script_dir = Path(__file__).parent
models_dir = script_dir.parent / 'models'

# Load metadata
m = joblib.load(models_dir / 'model_penetasan_metadata.pkl')
m2 = joblib.load(models_dir / 'model_panen_metadata.pkl')

print("=" * 60)
print("HASIL TRAINING MODEL")
print("=" * 60)

print("\nMODEL PENETASAN TELUR")
print("-" * 60)
print(f"- Model: {m['model_name']}")
print(f"- Test Accuracy: {m['test_accuracy']*100:.2f}%")
print(f"- CV Score: {m['cv_mean']:.4f} +/- {m['cv_std']:.4f}")
print(f"- Training Samples: {m['num_training_samples']}")
print(f"- Features: {m['num_features']}")

print("\nMODEL HASIL PANEN")
print("-" * 60)
print(f"- Model Type: {m2['model_type']}")
print(f"- MAE: {m2['mae']:.2f} gram")
print(f"- RMSE: {m2['rmse']:.2f} gram")
print(f"- R2 Score: {m2['r2_score']:.4f}")
print(f"- MAPE: {m2['mape']:.2f}%")
print(f"- CV MAE: {m2['cv_score_mean']:.2f} +/- {m2['cv_score_std']:.2f} gram")
print(f"- Best Params: {m2['best_params']}")

print("\n" + "=" * 60)
print("INTERPRETASI:")
print("=" * 60)
print(f"- Model Penetasan memiliki akurasi {m['test_accuracy']*100:.1f}%")
print(f"- Model Panen rata-rata error hanya {m2['mae']:.0f} gram")
print(f"- R2 Score {m2['r2_score']:.4f} = model menjelaskan {m2['r2_score']*100:.1f}% variasi data")
print(f"- MAPE {m2['mape']:.1f}% = error rata-rata {m2['mape']:.1f}% dari nilai aktual")
print("\nKedua model SIAP DIGUNAKAN!")
