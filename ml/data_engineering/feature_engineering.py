import pandas as pd

class FeatureEngineer:
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Starting Feature Engineering...")
        
        # Volume (cm^3)
        df['volume_cm3'] = df['length_cm'] * df['width_cm'] * df['height_cm']
        
        # Material Density Index
        df['density_index'] = df['weight_kg'] / (df['volume_cm3'] / 1000)
        
        # Fragility Index
        df['fragility_index'] = df['weight_kg'] * df['fragility_encoded']
        
        print("   - Features engineered: volume_cm3, density_index, fragility_index.")
        return df
