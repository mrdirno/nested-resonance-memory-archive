
"""
Helios: Material Agnosticism
============================
This module defines physical properties for various substrates (Air, Water, Metamaterials).
It enables the Reality Compiler to target different mediums without code changes.

Gate 3.3 Compliant.
"""

from dataclasses import dataclass

@dataclass
class MaterialProperties:
    name: str
    density: float          # kg/m^3
    speed_of_sound: float   # m/s
    viscosity: float        # Pa*s (Dynamic Viscosity)
    surface_tension: float  # N/m (optional, for liquids)

class Materials:
    """Standard Material Library."""
    
    AIR_STP = MaterialProperties(
        name="Air (STP)",
        density=1.225,
        speed_of_sound=343.0,
        viscosity=1.81e-5,
        surface_tension=0.0
    )
    
    WATER_20C = MaterialProperties(
        name="Water (20C)",
        density=998.0,
        speed_of_sound=1482.0,
        viscosity=1.002e-3,
        surface_tension=0.0728
    )
    
    GLYCERIN = MaterialProperties(
        name="Glycerin",
        density=1261.0,
        speed_of_sound=1904.0,
        viscosity=1.412,
        surface_tension=0.064
    )
    
    # Theoretical Metamaterial with tunable properties
    AETHER_V1 = MaterialProperties(
        name="Aether V1 (NRM Substrate)",
        density=1.0,
        speed_of_sound=1.0,  # Unit speed for simulation
        viscosity=0.1,       # Tunable damping
        surface_tension=0.0
    )

def get_material(name: str) -> MaterialProperties:
    """Factory method to retrieve material by name."""
    name_upper = name.upper().replace(" ", "_").replace("(", "").replace(")", "")
    if hasattr(Materials, name_upper):
        return getattr(Materials, name_upper)
    else:
        raise ValueError(f"Material '{name}' not found in library.")
