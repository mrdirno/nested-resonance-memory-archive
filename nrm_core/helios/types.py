from dataclasses import dataclass

@dataclass
class Material:
    name: str
    density: float      # kg/m^3
    sound_speed: float  # m/s

@dataclass
class PhysicsConfig:
    rho_air: float = 1.2      # Air density (kg/m^3)
    c_air: float = 343.0      # Sound speed (m/s)
    rho_particle: float = 25.0 # Particle density (kg/m^3)
    c_particle: float = 2350.0 # Particle sound speed (m/s)
    radius: float = 0.001     # Particle radius (m)
    frequency: float = 40000.0 # Hz

@dataclass
class Emitter:
    x: float
    y: float
    frequency: float
    phase: float
    amplitude: float = 1.0

@dataclass
class Emitter3D(Emitter):
    z: float = 0.0
