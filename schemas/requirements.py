from pydantic import BaseModel, Field, field_validator
from typing import Optional

class MissionRequirements(BaseModel):
    mission: str = Field(..., description="The natural language mission intent.")
    drone_type: str = Field(..., description="The categorized type of drone requested.")
    diagonal_mm: float = Field(300.0, description="Target or starting diagonal motor-to-motor distance.")
    payload_mass_g: float = Field(0.0, description="Mass of the intended payload in grams.")
    
    @field_validator('payload_mass_g')
    def validate_physics(cls, v):
        if v < 0:
            raise ValueError("Payload mass cannot be negative.")
        if v > 250000:  # 250kg absolute physical ceiling for this screening tool
            raise ValueError("Payload exceeds computational limits of screening tool (250kg).")
        return v
        
    @field_validator('diagonal_mm')
    def validate_geometry(cls, v):
        if v <= 0.0:
            raise ValueError("Diagonal must be greater than 0mm.")
        return v