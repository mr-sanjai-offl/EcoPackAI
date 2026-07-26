import pandera as pa
from pandera import Column, Check
import pandas as pd

ProductSchema = pa.DataFrameSchema({
    "product_id": Column(int),
    "product_name": Column(str),
    "category": Column(str),
    "product_weight_kg": Column(float, Check.greater_than_or_equal_to(0.0)),
    "dimensions_cm": Column(str, Check.str_matches(r"^\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?$")),
    "fragile": Column(bool),
    "food_grade_required": Column(bool),
    "moisture_sensitive": Column(bool),
    "temperature_sensitive": Column(bool)
}, coerce=True, strict=False)

MaterialSchema = pa.DataFrameSchema({
    "material_id": Column(int),
    "material_name": Column(str),
    "material_type": Column(str),
    "weight_capacity_kg": Column(float, Check.greater_than_or_equal_to(0.0)),
    "co2_emission_kg": Column(float, Check.greater_than_or_equal_to(0.0)),
    "food_safe": Column(bool)
}, coerce=True, strict=False)

def validate_products(df: pd.DataFrame) -> pd.DataFrame:
    print("Validating Products...")
    return ProductSchema.validate(df)

def validate_materials(df: pd.DataFrame) -> pd.DataFrame:
    print("Validating Materials...")
    return MaterialSchema.validate(df)
