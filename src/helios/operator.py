"""
HELIOS Universal Operator
The Engine of the Type 3 Operating System.
Translates high-level intent into low-level phase instructions.
"""
import numpy as np
import os
from src.helios.substrate_3d import AcousticSubstrate3D
from experiments.cycle320_forward_cymatics_2d import Emitter
from src.helios.mesh_loader import MeshLoader

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
        self.mesh_loader = MeshLoader()
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

    def create_from_file(self, filepath: str, scale_mm=50.0):
        """
        Loads an OBJ file, centers/scales it, voxelizes it, and compiles it.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        # Load and Process
        verts, faces = self.mesh_loader.load_obj(filepath)
        verts = self.mesh_loader.center_and_scale(verts, target_scale_mm=scale_mm)
        targets = self.mesh_loader.voxelize_surface(verts, faces, self.resolution)
        
        if not targets:
            raise ValueError("Mesh voxelization yielded zero targets.")
            
        # Solve
        phases = self._solve_phases(targets)
        
        # Store
        obj_id = self.next_id
        self.active_objects[obj_id] = {
            "type": f"file:{os.path.basename(filepath)}",
            "location": (50.0, 50.0, 50.0), # Centered by default
            "phases": phases,
            "targets": targets
        }
        self.next_id += 1
        return obj_id, len(targets)

    def move_object(self, object_id: int, new_location: tuple):
        """
        Moves an existing object to a new location.
        """
        if object_id not in self.active_objects:
            raise ValueError(f"Object ID {object_id} not found.")
            
        obj = self.active_objects[object_id]
        shape = obj['type']
        
        # Recalculate targets
        if "file:" in shape:
             # Complex case: need to reload or shift points
             # Simple shift for now
             current_loc = obj['location']
             shift = np.array(new_location) - np.array(current_loc)
             new_targets = [t + shift for t in obj['targets']]
        elif shape == "cube":
            new_targets = self._get_cube_targets(new_location)
        else:
            raise ValueError(f"Unknown shape: {shape}")
            
        # Solve for new phases
        phases = self._solve_phases(new_targets)
        
        # Update object
        obj['location'] = new_location
        obj['phases'] = phases
        obj['targets'] = new_targets
        return True

    def delete_object(self, object_id: int):
        """
        Removes an object from the field.
        """
        if object_id in self.active_objects:
            del self.active_objects[object_id]
            return True
        return False
        
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
        Returns stability index based on Gorkov Potential.
        Stability = Potential at target (should be negative/min) / Global Min Potential.
        Or simply the value of U at the target (lower is better).
        For normalized metric 0-1:
        We want a deep potential well.
        """
        obj = self.active_objects.get(object_id)
        if not obj: return -1.0
        
        # Apply phases
        for i, e in enumerate(self.emitters):
            e.phase = obj['phases'][i]
            
        # Calculate Complex Pressure Field
        field = self.box.propagate(self.emitters)
        
        # Calculate Gorkov Potential
        potential = self.box.calculate_gorkov_potential(field)
        
        # Analyze stability at target points
        # Ideally, targets should be at local minima of U.
        # We return the average potential at target points (should be negative).
        
        total_u = 0.0
        count = 0
        
        for t in obj['targets']:
            tx = int(t[0] / self.resolution)
            ty = int(t[1] / self.resolution)
            tz = int(t[2] / self.resolution)
            
            if 0 <= tx < potential.shape[2] and 0 <= ty < potential.shape[1] and 0 <= tz < potential.shape[0]:
                u_val = potential[tz, ty, tx]
                total_u += u_val
                count += 1
                
        if count == 0: return 0.0
        
        avg_u = total_u / count
        return avg_u # Return raw potential (negative is good)