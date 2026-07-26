import pandas as pd

class DataCleaner:
    def clean_products(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Cleaning Products...")
        df = df.copy()
        
        # Parse dimensions
        dims = df['dimensions_cm'].str.split('x', expand=True).astype(float)
        df['length_cm'] = dims[0]
        df['width_cm'] = dims[1]
        df['height_cm'] = dims[2]
        
        # Drop duplicates
        df = df.drop_duplicates(subset=['product_id'])
        
        return df

    def clean_materials(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Cleaning Materials...")
        df = df.copy()
        df = df.drop_duplicates(subset=['material_id'])
        return df
