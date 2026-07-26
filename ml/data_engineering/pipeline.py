import pandas as pd
import os
from validation import validate_products, validate_materials
from cleaning import DataCleaner
from feature_engineering import FeatureEngineer

def run_pipeline():
    print("Running EcoPackAI Data Pipeline (Real Data)...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    products_in = os.path.join(base_dir, 'data', 'external', 'product_categories.csv')
    materials_in = os.path.join(base_dir, 'data', 'external', 'eco_packaging_materials.csv')
    
    products_out = os.path.join(base_dir, 'data', 'processed', 'processed_products.csv')
    materials_out = os.path.join(base_dir, 'data', 'processed', 'processed_materials.csv')
    
    # 1. Load Data
    df_products = pd.read_csv(products_in)
    df_materials = pd.read_csv(materials_in)
    
    # 2. Validate Raw Data
    df_products = validate_products(df_products)
    df_materials = validate_materials(df_materials)
    
    # 3. Clean Data
    cleaner = DataCleaner()
    df_products = cleaner.clean_products(df_products)
    df_materials = cleaner.clean_materials(df_materials)
    
    # 4. Feature Engineering
    engineer = FeatureEngineer()
    df_products = engineer.engineer_product_features(df_products)
    df_materials = engineer.engineer_material_features(df_materials)
    
    # 5. Save Processed Data
    df_products.to_csv(products_out, index=False)
    df_materials.to_csv(materials_out, index=False)
    print("Pipeline complete. Saved processed datasets.")

if __name__ == "__main__":
    run_pipeline()
