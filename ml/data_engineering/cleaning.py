import pandas as pd
import numpy as np

class DataCleaner:
    def __init__(self):
        self.fragility_map = {"Low": 1, "Medium": 2, "High": 3}
        
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Starting Data Cleaning...")
        
        # 1. Remove duplicates
        initial_len = len(df)
        df = df.drop_duplicates().copy()
        print(f"   - Removed {initial_len - len(df)} duplicate rows.")
        
        # 2. Handle missing values
        df = df.dropna(subset=['length_cm', 'width_cm', 'height_cm', 'weight_kg'])
        
        # 3. Drop negative weights (invalid records)
        invalid_mask = df['weight_kg'] <= 0
        if invalid_mask.sum() > 0:
            print(f"   - Dropped {invalid_mask.sum()} invalid rows (negative weight).")
            df = df[~invalid_mask]
            
        # 4. Ordinal Encoding
        df['fragility_encoded'] = df['fragility'].map(self.fragility_map)
        
        # 5. Winsorization (Cap Outliers)
        upper_limit = df['weight_kg'].quantile(0.99)
        df.loc[df['weight_kg'] > upper_limit, 'weight_kg'] = upper_limit
        print("   - Winsorization applied to weight_kg at 99th percentile.")
        
        return df
