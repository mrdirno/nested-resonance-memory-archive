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

# GPU acceleration (optional)
try:
    from src.helios.substrate_3d_gpu import AcousticSubstrate3DGPU
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z

class UniversalOperator:
    """
    The Interface for Reality Compilation.
    """
    def __init__(self, resolution_mm=2.0, use_gpu=True):
        self.resolution = resolution_mm
        self.box_dim = 100.0
        self.use_gpu = use_gpu and GPU_AVAILABLE

        # Select substrate based on GPU availability
        if self.use_gpu:
            self.box = AcousticSubstrate3DGPU(
                width_mm=self.box_dim,
                height_mm=self.box_dim,
                depth_mm=self.box_dim,
                resolution_mm=self.resolution
            )
        else:
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

    def animate_object(self, object_id: int, target_mesh_path: str, frames: int = 10):
        """
        Animates an existing object to a new shape defined by target_mesh_path.
        Returns the sequence of phases.
        """
        if object_id not in self.active_objects:
            raise ValueError(f"Object ID {object_id} not found.")
            
        # Lazy import to avoid circular dependency
        from src.helios.animator import Animator
        animator = Animator()
        
        # Get current state
        # We need the current mesh/cloud. 
        # If it was loaded from file, we might have the path.
        # If it was a primitive (cube), we need to generate a mesh/cloud for it.
        
        obj = self.active_objects[object_id]
        current_type = obj['type']
        
        # Define Start Cloud/Mesh
        if "file:" in current_type:
            current_path = current_type.split("file:")[1]
            # We assume it's in the current directory or we need full path
            # This is a bit hacky, assuming we can find it.
            # Ideally we store the full path or the cloud itself.
            # For now, let's assume we can't easily get the start mesh if we didn't store it.
            # Let's reconstruct it from targets? No, targets are points.
            # Let's just use the targets as the start cloud!
            start_cloud = obj['targets']
            # We need a tuple (verts, faces) for the animator signature?
            # Actually animator.interpolate takes (verts, faces).
            # We should overload it or adjust logic.
            # Let's adjust logic in this method to handle "Cloud to Mesh" morph.
            pass 
        else:
            # Primitive
            # We can't easily morph a cube primitive without a mesh.
            # Let's require the object to be a mesh for now?
            # Or just generate a cube mesh on the fly.
            pass

        # REVISED STRATEGY:
        # Since we don't store the mesh data in active_objects, we will cheat for the demo.
        # We will load the START mesh from a file provided in arguments?
        # No, that breaks the API "animate object X".
        
        # Let's assume the user provides the start mesh path too?
        # "animate <id> from <start_obj> to <end_obj>"?
        # A bit verbose.
        
        # Better: Store the mesh path in active_objects when created from file.
        # If created from primitive, we can't animate it yet.
        
        if "file:" not in current_type:
             raise ValueError("Animation only supported for file-loaded objects.")
             
        # Reconstruct full path? 
        # We stored basename. Let's try to find it.
        # Assumption: It's in the CWD or we stored it.
        # Let's update create_from_file to store full path.
        
        # For now, let's just use the target_mesh_path as the END.
        # And we need the START.
        # Let's try to load the file from the type string if it exists locally.
        start_filename = current_type.split("file:")[1]
        if os.path.exists(start_filename):
            start_path = start_filename
        elif os.path.exists(f"data/models/{start_filename}"):
             start_path = f"data/models/{start_filename}"
        else:
             raise FileNotFoundError(f"Could not locate source mesh: {start_filename}")
             
        # Load Keyframes
        start_mesh = animator.load_keyframe(start_path)
        end_mesh = animator.load_keyframe(target_mesh_path)
        
        # Interpolate
        target_sequence = animator.interpolate(start_mesh, end_mesh, frames)
        
        # Compile
        phase_sequence = animator.generate_sequence(self, target_sequence)
        
        return phase_sequence

        
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