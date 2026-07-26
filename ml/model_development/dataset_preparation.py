import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib
import os

def generate_ground_truth(products_path, materials_path):
    print("Generating Ground Truth Dataset via Cross Join & Heuristics...")
    df_p = pd.read_csv(products_path)
    df_m = pd.read_csv(materials_path)
    
    # Cross join (Cartesian product)
    df_p['key'] = 1
    df_m['key'] = 1
    df_pairs = pd.merge(df_p, df_m, on='key').drop('key', axis=1)
    
    # 1. Hard Filtering (Physics & Compliance)
    weight_mask = df_pairs['product_weight_kg'] <= df_pairs['weight_capacity_kg']
    food_mask = ~(df_pairs['food_grade_required'] & ~df_pairs['food_safe'])
    
    valid_pairs = df_pairs[weight_mask & food_mask].copy()
    print(f"Filtered {len(df_pairs)} theoretical pairs down to {len(valid_pairs)} physically valid pairs.")
    
    # 2. Score Generation (Heuristic Label for ML)
    co2_penalty = valid_pairs['co2_emission_kg'] / valid_pairs['co2_emission_kg'].max()
    efficiency_bonus = valid_pairs['material_efficiency'] / valid_pairs['material_efficiency'].max()
    
    # Cost penalty (Exceeding max cost heavily penalized)
    cost_ratio = valid_pairs['cost_per_kg'] / valid_pairs['max_packaging_cost'].replace(0, 0.01)
    cost_penalty = np.where(cost_ratio > 1, 0.5 + cost_ratio * 0.1, cost_ratio * 0.2)
    
    base_score = 100 * (0.5 * efficiency_bonus - 0.3 * co2_penalty - 0.2 * cost_penalty)
    
    # Normalize 0-100
    min_s = base_score.min()
    max_s = base_score.max()
    valid_pairs['suitability_score'] = 100 * (base_score - min_s) / (max_s - min_s)
    
    return valid_pairs

def build_pipeline_and_split(df, artifacts_dir):
    print("Building Scikit-Learn Preprocessing Pipeline...")
    
    # FEATURE SELECTION: Drop redundant physical dimensions and IDs to prevent data leakage
    drop_cols = [
        'product_id', 'product_name', 'material_id', 'material_name', 
        'length_cm', 'width_cm', 'height_cm', # Replaced by volume_cm3
        'suitability_score' # Target
    ]
    
    target = 'suitability_score'
    X = df.drop(columns=drop_cols)
    y = df[target]
    
    numeric_features = [
        'product_weight_kg', 'volume_cm3', 'density_index', 
        'max_packaging_cost', 'strength_score', 'weight_capacity_kg', 
        'co2_emission_kg', 'cost_per_kg', 'material_efficiency'
    ]
    
    categorical_features = [
        'category', 'sub_category', 'preferred_material_type', 'sustainability_priority', 
        'material_type', 'water_resistance', 'industry_usage', 'sustainability_rating'
    ]
    
    boolean_features = [
        'fragile', 'food_grade_required', 'moisture_sensitive', 'temperature_sensitive', 'food_safe'
    ]
    
    # Column Transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('bool', 'passthrough', boolean_features)
        ],
        remainder='drop'
    )
    
    # Splitting (60/20/20)
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42) # 0.25 * 0.8 = 0.2
    
    print(f"Dataset split successfully: Train({len(X_train)}), Val({len(X_val)}), Test({len(X_test)})")
    
    # Fit strictly on train to avoid data leakage
    print("Fitting preprocessor on training data...")
    X_train_proc = preprocessor.fit_transform(X_train)
    X_val_proc = preprocessor.transform(X_val)
    X_test_proc = preprocessor.transform(X_test)
    
    # Save artifacts
    os.makedirs(artifacts_dir, exist_ok=True)
    joblib.dump(preprocessor, os.path.join(artifacts_dir, 'preprocessor.joblib'))
    joblib.dump((X_train_proc, y_train), os.path.join(artifacts_dir, 'train.joblib'))
    joblib.dump((X_val_proc, y_val), os.path.join(artifacts_dir, 'val.joblib'))
    joblib.dump((X_test_proc, y_test), os.path.join(artifacts_dir, 'test.joblib'))
    
    print(f"Artifacts serialized and saved to {artifacts_dir}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    p_path = os.path.join(base_dir, 'data', 'processed', 'processed_products.csv')
    m_path = os.path.join(base_dir, 'data', 'processed', 'processed_materials.csv')
    artifacts_dir = os.path.join(base_dir, 'data', 'artifacts')
    
    df_combined = generate_ground_truth(p_path, m_path)
    
    combined_path = os.path.join(base_dir, 'data', 'processed', 'combined_training_data.csv')
    df_combined.to_csv(combined_path, index=False)
    
    build_pipeline_and_split(df_combined, artifacts_dir)
