from pydantic import BaseModel, Field
from typing import List, Literal, Tuple

class MountPattern(BaseModel):
    type: str
    spacing_mm: float
    hole_diameter_mm: float
    coordinates_mm: List[Tuple[float, float]]

class Component(BaseModel):
    id: str
    manufacturer: str
    part_number: str
    name: str
    data_status: Literal["VERIFIED_DATASHEET", "ASSUMED_GENERIC"] = "ASSUMED_GENERIC"

class Motor(Component):
    count: int = 4
    unit_mass_g: float
    total_mass_g: float
    max_thrust_n: float
    prop_diam_mm: float
    mount_pattern: MountPattern

class FlightController(Component):
    mass_g: float
    mount_pattern: MountPattern

class BatteryRetention(BaseModel):
    strap_width_mm: float
    slot_thickness_mm: float
    slot_separation_mm: float

class Battery(Component):
    mass_g: float
    retention: BatteryRetention

class Wiring(BaseModel):
    name: str
    mass_g: float

class HardwareManifest(BaseModel):
    profile: str
    motor: Motor
    flight_controller: FlightController
    battery: Battery
    wiring: Wiring