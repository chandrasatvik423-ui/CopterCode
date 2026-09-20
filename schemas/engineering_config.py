from pydantic import BaseModel, Field

class SolverLimits(BaseModel):
    max_arm_width_mm: float = Field(default=40.0, description="Absolute maximum allowable arm width.")
    min_arm_width_mm: float = Field(default=12.0, description="Starting arm width for solver.")
    width_iteration_step_mm: float = Field(default=1.0, description="Iteration step for solver.")
    height_multiplier_limit: float = Field(default=2.0, description="Arm height max = start_height * this factor.")
    auto_correction_step_mm: float = Field(default=5.0, description="Diagonal expansion step for clearance.")
    max_diagonal_limit_mm: float = Field(default=2000.0, description="Absolute maximum frame size limit.")

class SafetyPolicy(BaseModel):
    min_structural_safety_factor: float = Field(default=1.5, description="Minimum acceptable SF for screening.")
    min_thrust_to_weight_ratio: float = Field(default=1.5, description="Minimum acceptable TWR for liftoff.")
    body_clearance_buffer_mm: float = Field(default=15.0, description="Added to PCB dims for propeller clearance check.")

class AppConfig(BaseModel):
    llm_endpoint: str = Field(default="http://localhost:11434/api/generate")
    llm_model: str = Field(default="phi3")
    openscad_path: str = Field(default="openscad", description="Path or command for OpenSCAD executable.")
    slicer_path: str = Field(default="prusa-slicer-console", description="Path or command for Slicer CLI.")
    default_material: str = Field(default="PLA", description="Default frame material for physics and manufacturing.")

class EngineeringProfile(BaseModel):
    solver: SolverLimits = SolverLimits()
    safety: SafetyPolicy = SafetyPolicy()
    app: AppConfig = AppConfig()

# Global Configuration Singleton
CONFIG = EngineeringProfile()