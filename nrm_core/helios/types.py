from dataclasses import dataclass

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
