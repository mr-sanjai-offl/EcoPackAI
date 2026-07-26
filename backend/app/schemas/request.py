"""
Request Schemas (Step 4)

Pydantic v2 models that validate incoming API requests.
Every field has constraints (min, max, allowed values) so that
invalid data is rejected BEFORE it reaches the ML model.

Why strict validation matters:
- A negative weight would crash the density calculation (division by zero)
- An unknown category would cause OneHotEncoder to produce all zeros
- Missing fields would cause pandas to throw cryptic errors deep in the pipeline
"""
from pydantic import BaseModel, Field
from typing import Optional


class ProductRequest(BaseModel):
    """Request schema for packaging recommendation."""
    
    product_weight_kg: float = Field(
        ..., gt=0, le=500,
        description="Product weight in kilograms. Must be positive.",
        examples=[0.19]
    )
    dimensions_cm: str = Field(
        ..., pattern=r"^\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?$",
        description="Product dimensions as LxWxH in cm.",
        examples=["15x7x1"]
    )
    category: str = Field(
        ..., min_length=1,
        description="Product category.",
        examples=["Electronics"]
    )
    sub_category: str = Field(
        ..., min_length=1,
        description="Product sub-category.",
        examples=["Mobile Devices"]
    )
    fragile: bool = Field(
        default=False,
        description="Whether the product is fragile."
    )
    food_grade_required: bool = Field(
        default=False,
        description="Whether food-safe packaging is required."
    )
    moisture_sensitive: bool = Field(
        default=False,
        description="Whether the product is moisture sensitive."
    )
    temperature_sensitive: bool = Field(
        default=False,
        description="Whether the product is temperature sensitive."
    )
    preferred_material_type: str = Field(
        default="Any",
        description="Preferred packaging material type.",
        examples=["Paper-Based"]
    )
    sustainability_priority: str = Field(
        default="Medium",
        description="Sustainability priority level.",
        examples=["High"]
    )
    max_packaging_cost: float = Field(
        default=5.0, ge=0,
        description="Maximum acceptable packaging cost per kg.",
        examples=[2.5]
    )
    top_n: Optional[int] = Field(
        default=5, ge=1, le=20,
        description="Number of recommendations to return."
    )
