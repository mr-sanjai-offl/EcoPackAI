import pandera as pa
from pandera import Column, Check
import pandas as pd

# Production-grade Schema
RawPackagingSchema = pa.DataFrameSchema(
    {
        "length_cm": Column(float, Check.greater_than_or_equal_to(0.1), nullable=False),
        "width_cm": Column(float, Check.greater_than_or_equal_to(0.1), nullable=False),
        "height_cm": Column(float, Check.greater_than_or_equal_to(0.1), nullable=False),
        "weight_kg": Column(float, Check.greater_than_or_equal_to(0.01), nullable=False),
        "fragility": Column(str, Check.isin(["Low", "Medium", "High"]), nullable=False),
        "packaging_type": Column(str, nullable=True) # Target can be null during inference
    },
    coerce=True
)

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates raw data against the strict schema.
    """
    try:
        validated_df = RawPackagingSchema.validate(df)
        print("Data Validation Passed.")
        return validated_df
    except pa.errors.SchemaError as err:
        print(f"Schema Validation Error: {err}")
        raise
