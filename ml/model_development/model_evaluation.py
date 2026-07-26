"""
Step 8: Model Evaluation on Held-Out Test Set

This module evaluates the final tuned model on the TEST set (which was never
seen during training or hyperparameter tuning). This is the only honest
measure of how the model will perform in production.

Step 9: Model Serialization - saves all production artifacts.
Step 10: Model Registry - creates a lightweight version tracking system.
"""
import os
import json
import hashlib
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def evaluate_on_test_set(model, X_test, y_test, reports_dir: str) -> dict:
    """Run final evaluation on the held-out test set.
    
    Args:
        model: Trained XGBoost model.
        X_test: Preprocessed test features.
        y_test: True test labels.
        reports_dir: Directory to save evaluation plots.
        
    Returns:
        Dictionary of evaluation metrics.
    """
    print("--- Step 8: Final Model Evaluation on TEST Set ---")
    os.makedirs(reports_dir, exist_ok=True)
    
    preds = model.predict(X_test)
    
    metrics = {
        "mae": round(float(mean_absolute_error(y_test, preds)), 6),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test, preds))), 6),
        "r2": round(float(r2_score(y_test, preds)), 6),
        "test_samples": int(len(y_test))
    }
    
    print(f"  MAE:  {metrics['mae']}")
    print(f"  RMSE: {metrics['rmse']}")
    print(f"  R2:   {metrics['r2']}")
    
    # 1. Residual Plot
    residuals = y_test.values - preds
    plt.figure(figsize=(10, 6))
    plt.scatter(preds, residuals, alpha=0.4, s=10)
    plt.axhline(y=0, color='red', linestyle='--')
    plt.xlabel("Predicted Score")
    plt.ylabel("Residual (Actual - Predicted)")
    plt.title("Residual Analysis")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "residual_plot.png"), dpi=150)
    plt.close()
    
    # 2. Prediction Error Plot (Actual vs Predicted)
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, preds, alpha=0.4, s=10)
    min_val = min(y_test.min(), preds.min())
    max_val = max(y_test.max(), preds.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')
    plt.xlabel("Actual Score")
    plt.ylabel("Predicted Score")
    plt.title("Prediction Error Plot")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "prediction_error.png"), dpi=150)
    plt.close()
    
    # 3. Residual Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(residuals, bins=50, edgecolor='black', alpha=0.7)
    plt.xlabel("Residual Value")
    plt.ylabel("Frequency")
    plt.title("Residual Distribution (Should be ~Normal around 0)")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "residual_distribution.png"), dpi=150)
    plt.close()
    
    print(f"  Evaluation plots saved to {reports_dir}")
    return metrics


def save_model_metrics(metrics: dict, artifacts_dir: str):
    """Step 9: Save model metrics JSON for production monitoring."""
    path = os.path.join(artifacts_dir, 'model_metrics.json')
    with open(path, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"  Model metrics saved to {path}")


def save_feature_metadata(preprocessor, artifacts_dir: str):
    """Step 9: Save feature metadata for production inference validation."""
    feature_names = []
    for name, transformer, columns in preprocessor.transformers_:
        if name == 'num':
            feature_names.extend(columns)
        elif name == 'cat':
            feature_names.extend(transformer.get_feature_names_out(columns).tolist())
        elif name == 'bool':
            feature_names.extend(columns)
    
    metadata = {
        "total_features": len(feature_names),
        "feature_names": feature_names,
        "numeric_count": len(preprocessor.transformers_[0][2]),
        "categorical_count": len(preprocessor.transformers_[1][2]),
        "boolean_count": len(preprocessor.transformers_[2][2])
    }
    
    path = os.path.join(artifacts_dir, 'feature_metadata.json')
    with open(path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"  Feature metadata saved to {path}")
    return metadata


def create_model_registry(model, metrics: dict, artifacts_dir: str):
    """Step 10: Create a lightweight model registry entry.
    
    In production (MLflow, Weights & Biases, Vertex AI), this would be
    stored in a database. For our portfolio, we use a JSON registry.
    """
    print("\n--- Step 10: Creating Model Registry Entry ---")
    
    # Generate model hash for integrity verification
    model_path = os.path.join(artifacts_dir, 'trained_model.joblib')
    with open(model_path, 'rb') as f:
        model_hash = hashlib.sha256(f.read()).hexdigest()[:16]
    
    # Load training config
    config_path = os.path.join(artifacts_dir, 'training_config.json')
    with open(config_path, 'r') as f:
        hyperparams = json.load(f)
    
    registry_entry = {
        "model_name": "EcoPackAI-XGBoost-v1",
        "model_version": "1.0.0",
        "algorithm": "XGBRegressor",
        "training_date": datetime.now().isoformat(),
        "dataset_version": "real_data_v1",
        "metrics": metrics,
        "hyperparameters": hyperparams,
        "model_hash": model_hash,
        "author": "EcoPackAI Team",
        "environment": {
            "python": "3.11+",
            "xgboost": "3.3.0",
            "scikit-learn": "1.9.0"
        },
        "artifacts": [
            "trained_model.joblib",
            "preprocessor.joblib",
            "feature_metadata.json",
            "model_metrics.json",
            "training_config.json"
        ],
        "status": "production"
    }
    
    registry_path = os.path.join(artifacts_dir, 'model_registry.json')
    with open(registry_path, 'w') as f:
        json.dump(registry_entry, f, indent=4)
    
    print(f"  Registry: {registry_entry['model_name']} v{registry_entry['model_version']}")
    print(f"  Hash:     {model_hash}")
    print(f"  Status:   {registry_entry['status']}")
    print(f"  Saved to: {registry_path}")
    
    return registry_entry


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    artifacts_dir = os.path.join(base_dir, 'data', 'artifacts')
    reports_dir = os.path.join(base_dir, 'data', 'reports')
    
    model = joblib.load(os.path.join(artifacts_dir, 'trained_model.joblib'))
    preprocessor = joblib.load(os.path.join(artifacts_dir, 'preprocessor.joblib'))
    X_test, y_test = joblib.load(os.path.join(artifacts_dir, 'test.joblib'))
    
    # Step 8
    metrics = evaluate_on_test_set(model, X_test, y_test, reports_dir)
    
    # Step 9
    save_model_metrics(metrics, artifacts_dir)
    save_feature_metadata(preprocessor, artifacts_dir)
    
    # Step 10
    create_model_registry(model, metrics, artifacts_dir)
