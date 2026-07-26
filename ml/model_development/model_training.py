import os
import time
import joblib
import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import optuna

# Prevent optuna from printing too much in the terminal
optuna.logging.set_verbosity(optuna.logging.WARNING)

def evaluate_model(model, X_train, y_train, X_val, y_val, name="Model"):
    start_train = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start_train
    
    start_inf = time.time()
    preds = model.predict(X_val)
    inf_time = (time.time() - start_inf) * 1000 # in ms
    
    mae = mean_absolute_error(y_val, preds)
    rmse = np.sqrt(mean_squared_error(y_val, preds))
    r2 = r2_score(y_val, preds)
    
    return {
        "Model": name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "Train_Time_s": train_time,
        "Inference_Time_ms": inf_time
    }

def train_baselines(X_train, y_train, X_val, y_val, reports_dir):
    print("--- Training Baseline Models ---")
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1),
        "XGBoost": XGBRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    }
    
    results = []
    for name, model in models.items():
        res = evaluate_model(model, X_train, y_train, X_val, y_val, name)
        results.append(res)
        
    df_results = pd.DataFrame(results).sort_values(by="R2", ascending=False)
    print("\nBaseline Results:")
    print(df_results.to_string(index=False))
    
    os.makedirs(reports_dir, exist_ok=True)
    df_results.to_csv(os.path.join(reports_dir, "baseline_comparison.csv"), index=False)
    
    return df_results

def optimize_xgboost(X_train, y_train, X_val, y_val, artifacts_dir):
    print("\n--- Starting Optuna Hyperparameter Optimization for XGBoost ---")
    
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 150),
            'max_depth': trial.suggest_int('max_depth', 3, 9),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.7, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.7, 1.0),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-3, 10.0, log=True),
            'random_state': 42,
            'n_jobs': -1
        }
        
        model = XGBRegressor(**params)
        model.fit(X_train, y_train)
        
        preds = model.predict(X_val)
        rmse = np.sqrt(mean_squared_error(y_val, preds))
        return rmse

    # Optuna tuning
    study = optuna.create_study(direction='minimize')
    print("Running 15 Trials of Bayesian Optimization...")
    study.optimize(objective, n_trials=15) 
    
    best_params = study.best_trial.params
    best_params['random_state'] = 42
    best_params['n_jobs'] = -1
    
    print(f"Optimization Complete! Best RMSE: {study.best_value}")
    
    print("\nTraining Final Optimized XGBoost Model...")
    best_model = XGBRegressor(**best_params)
    best_model.fit(X_train, y_train)
    
    # Save the model
    model_path = os.path.join(artifacts_dir, 'trained_model.joblib')
    joblib.dump(best_model, model_path)
    
    # Save hyperparams
    with open(os.path.join(artifacts_dir, 'training_config.json'), 'w') as f:
        json.dump(best_params, f, indent=4)
        
    print(f"Final Model Saved: {model_path}")
    return best_model

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    artifacts_dir = os.path.join(base_dir, 'data', 'artifacts')
    reports_dir = os.path.join(base_dir, 'data', 'reports')
    
    print("Loading serialized datasets...")
    X_train, y_train = joblib.load(os.path.join(artifacts_dir, 'train.joblib'))
    X_val, y_val = joblib.load(os.path.join(artifacts_dir, 'val.joblib'))
    
    # Step 4: Baseline
    train_baselines(X_train, y_train, X_val, y_val, reports_dir)
    
    # Step 5: Hyperparameter Optimization
    optimize_xgboost(X_train, y_train, X_val, y_val, artifacts_dir)
