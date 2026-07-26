import pandas as pd

class FeatureEngineer:
    def engineer_product_features(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Engineering Product Features...")
        df = df.copy()
        # Volume
        df['volume_cm3'] = df['length_cm'] * df['width_cm'] * df['height_cm']
        # Density (kg per liter)
        df['density_index'] = df['product_weight_kg'] / (df['volume_cm3'] / 1000)
        return df
        
    def engineer_material_features(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Engineering Material Features...")
        df = df.copy()
        # Material Efficiency: Strength relative to CO2 cost
        # Add 0.01 to avoid division by zero
        df['material_efficiency'] = df['strength_score'] / (df['co2_emission_kg'] + 0.01)
        return df
