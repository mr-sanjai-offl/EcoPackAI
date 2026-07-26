import pandas as pd
import os
import json
from validation import validate_data
from cleaning import DataCleaner
from feature_engineering import FeatureEngineer

def run_pipeline(input_path: str, processed_path: str, metadata_path: str):
    print("Running EcoPackAI Data Pipeline...")
    
    # Extract
    df = pd.read_csv(input_path)
    
    # Transform (Clean -> Validate -> Engineer)
    cleaner = DataCleaner()
    df_cleaned = cleaner.clean(df)
    
    df_valid = validate_data(df_cleaned)
    
    engineer = FeatureEngineer()
    df_processed = engineer.engineer_features(df_valid)
    
    # Load (Save Artifacts)
    df_processed.to_csv(processed_path, index=False)
    
    metadata = {
        "num_rows": len(df_processed),
        "num_columns": len(df_processed.columns),
        "features": list(df_processed.columns),
        "pipeline_version": "1.0.0"
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Pipeline complete. Processed data saved to {processed_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    input_path = os.path.join(base_dir, 'data', 'raw', 'raw_packaging_data.csv')
    processed_path = os.path.join(base_dir, 'data', 'processed', 'processed_dataset.csv')
    metadata_path = os.path.join(base_dir, 'data', 'metadata', 'metadata.json')
    
    run_pipeline(input_path, processed_path, metadata_path)
