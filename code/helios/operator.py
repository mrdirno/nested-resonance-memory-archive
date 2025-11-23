"""
HELIOS Universal Operator
The Engine of the Type 3 Operating System.
Translates high-level intent into low-level phase instructions.
"""
import numpy as np
from code.helios.substrate_3d import AcousticSubstrate3D
from experiments.cycle320_forward_cymatics_2d import Emitter

class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z

class UniversalOperator:
    """
    The Interface for Reality Compilation.
    """
    def __init__(self, resolution_mm=2.0):
        self.resolution = resolution_mm
        self.box_dim = 100.0
        self.box = AcousticSubstrate3D(
            width_mm=self.box_dim, 
            height_mm=self.box_dim, 
            depth_mm=self.box_dim, 
            resolution_mm=self.resolution
        )
        self.emitters = self._create_hardware_layer()
        self.active_objects = {} # ID -> {type, phases, location}
        self.next_id = 1
        
    def _create_hardware_layer(self):
        # Initialize 384-emitter array (6 sides, 8x8)
        # Reusing logic from Cycle 348
        emitters = []
        spacing = 10.0
        num = 8
        
        def add_face(fixed, orientation):
            center_offset = (num - 1) * spacing / 2.0
            center = self.box_dim / 2.0
            for i in range(num):
                for j in range(num):
                    c1 = center - center_offset + i * spacing
                    c2 = center - center_offset + j * spacing
                    if orientation == 'z': emitters.append(Emitter3D(c1, c2, fixed, 1.0, 0.0))
                    elif orientation == 'x': emitters.append(Emitter3D(fixed, c1, c2, 1.0, 0.0))
                    elif orientation == 'y': emitters.append(Emitter3D(c1, fixed, c2, 1.0, 0.0))
                    
        add_face(0.0, 'z'); add_face(self.box_dim, 'z')
        add_face(0.0, 'x'); add_face(self.box_dim, 'x')
        add_face(0.0, 'y'); add_face(self.box_dim, 'y')
        return emitters

    def create_object(self, shape: str, location: tuple):
        """
        Instantiates a static object.
        """
        if shape == "cube":
            targets = self._get_cube_targets(location)
        else:
            raise ValueError(f"Unknown shape: {shape}")
            
        # Solve for phases
        phases = self._solve_phases(targets)
        
        # Store object
        obj_id = self.next_id
        self.active_objects[obj_id] = {
            "type": shape,
            "location": location,
            "phases": phases,
            "targets": targets
        }
        self.next_id += 1
        return obj_id
        
    def _get_cube_targets(self, center):
        offset = 25.0
        cx, cy, cz = center
        return [
            np.array([cx-offset, cy-offset, cz-offset]),
            np.array([cx+offset, cy-offset, cz-offset]),
            np.array([cx-offset, cy+offset, cz-offset]),
            np.array([cx-offset, cy-offset, cz+offset]),
            np.array([cx+offset, cy+offset, cz-offset]),
            np.array([cx+offset, cy-offset, cz+offset]),
            np.array([cx-offset, cy+offset, cz+offset]),
            np.array([cx+offset, cy+offset, cz+offset])
        ]

    def _solve_phases(self, targets):
        # Simplified GA for production use (fast convergence)
        # In a real system, this would be GPU-accelerated or pre-computed.
        # For now, we use the CPU implementation from Cycle 348.
        
        # Import local GA to avoid circular dependencies if possible, 
        # or re-implement efficiently.
        from experiments.cycle348_volumetric_printing import genetic_algorithm_multi_target
        
        # Reduce generations for unit test speed, but keep high enough for success
        best_phases = genetic_algorithm_multi_target(targets, self.box, self.emitters, generations=20, pop_size=20)
        return best_phases

    def get_stability(self, object_id: int) -> float:
        """
        Returns worst-case pressure ratio (Target/Max).
        Lower is better.
        """
        obj = self.active_objects.get(object_id)
        if not obj: return -1.0
        
        # Apply phases
        for i, e in enumerate(self.emitters):
            e.phase = obj['phases'][i]
            
        field = self.box.propagate(self.emitters)
        potential = field**2
        p_max = np.max(potential)
        
        max_ratio = 0.0
        for t in obj['targets']:
            tx = int(t[0] / self.resolution)
            ty = int(t[1] / self.resolution)
            tz = int(t[2] / self.resolution)
            
            if 0 <= tx < field.shape[2] and 0 <= ty < field.shape[1] and 0 <= tz < field.shape[0]:
                p_val = potential[tz, ty, tx]
                ratio = p_val / p_max if p_max > 0 else 1.0
                if ratio > max_ratio: max_ratio = ratio
                
        return max_ratio