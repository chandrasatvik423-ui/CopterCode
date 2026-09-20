"""
schemas/geometry.py
--------------------
Pydantic model representing the solved frame geometry.

This model serves as the single source of truth for all geometry
values flowing between the pipeline, CAD generator, and screening engines.
"""

from pydantic import BaseModel, Field, field_validator


class GeometryModel(BaseModel):
    """Fully-resolved drone frame geometry after the propeller clearance solver."""

    motor_to_motor_diagonal_mm: float = Field(
        ..., description="Motor-to-motor diagonal distance (mm). Primary frame size metric."
    )
    arm_length_mm: float = Field(
        ..., description="Distance from hub center to motor centre (mm). = diagonal / 2."
    )
    arm_width_mm: float = Field(
        ..., description="Arm cross-section width (mm). Set by structural solver."
    )
    arm_height_mm: float = Field(
        ..., description="Arm cross-section height (mm). Set by structural solver."
    )
    cutout_width_ratio: float = Field(
        default=0.6, description="Inner cutout width as a fraction of arm_width_mm."
    )
    cutout_height_ratio: float = Field(
        default=0.7, description="Inner cutout height as a fraction of arm_height_mm."
    )
    pcb_width: float = Field(
        ..., description="Central body (PCB stack) width after component placement (mm)."
    )
    pcb_length: float = Field(
        ..., description="Central body (PCB stack) length after component placement (mm)."
    )
    motor_count: int = Field(
        ..., description="Number of motors / arms."
    )
    auto_corrected: bool = Field(
        default=False,
        description="True if diagonal was expanded by the propeller clearance auto-correction loop."
    )
    original_diagonal_mm: float = Field(
        default=0.0,
        description="Diagonal requested by topology before auto-correction. 0 if no correction was needed."
    )

    @field_validator("motor_to_motor_diagonal_mm", "arm_length_mm")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Diagonal and arm_length must be positive.")
        return v
