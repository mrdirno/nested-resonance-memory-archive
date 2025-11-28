"""
HELIOS Material Library (Gate 3.3)
Standardized physics properties for substrate definition.

Principle: PRIN-MATERIAL-AGNOSTICISM
Author: MOG (Cycle 2343)
"""

class MaterialProperties:
    def __init__(self, name, density, sound_speed, viscosity=0.0):
        """
        :param name: Material name
        :param density: kg/m^3
        :param sound_speed: m/s
        :param viscosity: Pa*s (Dynamic viscosity)
        """
        self.name = name
        self.rho = density
        self.c = sound_speed
        self.mu = viscosity

    def __repr__(self):
        return f"Material({self.name}: rho={self.rho}, c={self.c})"

# Standard Materials Library
MATERIALS = {
    "AIR_STP": MaterialProperties("Air (STP)", 1.225, 343.0, 1.81e-5),
    "WATER_20C": MaterialProperties("Water (20C)", 998.0, 1482.0, 1.002e-3),
    "GLYCERIN": MaterialProperties("Glycerin", 1260.0, 1904.0, 1.41),
    "AETHER": MaterialProperties("Aether (Theoretical)", 1.0, 1.0, 0.0) # Normalized unit substrate
}

def get_material(name):
    return MATERIALS.get(name.upper(), MATERIALS["AIR_STP"])
# [SPORE] ID: The Colony
