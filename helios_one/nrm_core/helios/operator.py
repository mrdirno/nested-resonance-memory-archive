"""
HELIOS Universal Operator
The Engine of the Type 3 Operating System.
Translates high-level intent into low-level phase instructions.
"""
import numpy as np
import os
from .substrate_3d import AcousticSubstrate3D
from .types import Emitter, Emitter3D, Material
from .mesh_loader import MeshLoader
from .compiler import MatterCompiler

# GPU acceleration (optional)
try:
    from .substrate_3d_gpu import AcousticSubstrate3DGPU
    from .ga_gpu import GeneticAlgorithmGPU
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

class UniversalOperator:
    """
    The Interface for Reality Compilation.
    """
    def __init__(self, resolution_mm=2.0, use_gpu=True, solver_config=None):
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
        
        # Initialize Matter Compiler with current hardware config
        self.compiler = MatterCompiler(
            width_mm=self.box_dim, 
            height_mm=self.box_dim, 
            depth_mm=self.box_dim,
            emitters=self.emitters,
            solver_config=solver_config
        )
        
        self.active_objects = {} # ID -> {type, phases, location}
        self.next_id = 1
        
    def _create_hardware_layer(self):
        # Initialize 384-emitter array (6 sides, 8x8)
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
                    if orientation == 'z': 
                        # Top/Bottom faces. x=c1, y=c2, z=fixed
                        emitters.append(Emitter3D(c1, c2, 1.0, 0.0, 1.0, fixed))
                    elif orientation == 'x': 
                        # Left/Right faces. x=fixed, y=c1, z=c2
                        emitters.append(Emitter3D(fixed, c1, 1.0, 0.0, 1.0, c2))
                    elif orientation == 'y': 
                        # Front/Back faces. x=c1, y=fixed, z=c2
                        emitters.append(Emitter3D(c1, fixed, 1.0, 0.0, 1.0, c2))
                    
        add_face(0.0, 'z'); add_face(self.box_dim, 'z')
        add_face(0.0, 'x'); add_face(self.box_dim, 'x')
        add_face(0.0, 'y'); add_face(self.box_dim, 'y')
        return emitters

    def _get_material(self, name: str) -> Material:
        """
        Returns a Material object by name.
        """
        name = name.lower()
        if name == "styrofoam":
            return Material(name="Styrofoam", density=25.0, sound_speed=2350.0)
        elif name == "water":
            return Material(name="Water", density=1000.0, sound_speed=1480.0)
        elif name == "lead":
            return Material(name="Lead", density=11340.0, sound_speed=1260.0) # High density, hard to trap
        else:
            # Default to Styrofoam
            return Material(name="Styrofoam", density=25.0, sound_speed=2350.0)

    def create_object(self, shape: str, location: tuple, material="Styrofoam"):
        """
        Instantiates a static object.
        """
        if shape == "cube":
            targets = self._get_cube_targets(location)
        else:
            raise ValueError(f"Unknown shape: {shape}")
            
        # Compile
        mat = self._get_material(material)
        compiled_emitters = self.compiler.compile(targets, mat)
        phases = [e.phase for e in compiled_emitters]
        
        # Store object
        obj_id = self.next_id
        self.active_objects[obj_id] = {
            "type": shape,
            "location": location,
            "phases": phases,
            "targets": targets,
            "material": mat.name
        }
        self.next_id += 1
        return obj_id

    def create_from_file(self, filepath: str, scale_mm=50.0, material="Styrofoam"):
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
            
        # Compile
        mat = self._get_material(material)
        compiled_emitters = self.compiler.compile(targets, mat)
        phases = [e.phase for e in compiled_emitters]
        
        # Store
        obj_id = self.next_id
        self.active_objects[obj_id] = {
            "type": f"file:{os.path.basename(filepath)}",
            "location": (50.0, 50.0, 50.0), # Centered by default
            "phases": phases,
            "targets": targets,
            "material": mat.name
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
        mat_name = obj.get('material', 'Styrofoam')
        mat = self._get_material(mat_name)
        
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
            
        # Re-Compile
        compiled_emitters = self.compiler.compile(new_targets, mat)
        phases = [e.phase for e in compiled_emitters]
        
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
        from .animator import Animator
        animator = Animator()
        
        obj = self.active_objects[object_id]
        current_type = obj['type']
        
        if "file:" not in current_type:
             raise ValueError("Animation only supported for file-loaded objects.")
             
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

    def apply_phase_function(self, func):
        """
        Applies a mathematical function to set the phase of all emitters.
        func: callable(x, y, z) -> float (phase in radians)
        """
        for e in self.emitters:
            e.phase = func(e.x, e.y, e.z)
            
    def get_stability(self, object_id: int) -> float:
        """
        Returns stability index based on Gorkov Potential.
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
        return avg_u 

    def get_field_slice(self, z_ratio: float = 0.5) -> list[list[float]]:
        """
        Returns a 2D slice of the pressure field (magnitude squared).
        """
        z_layer = int(z_ratio * self.box.depth)
        z_layer = max(0, min(z_layer, self.box.depth - 1))
        
        if self.use_gpu and hasattr(self.box, 'propagate_slice'):
             # GPU optimization if available
             field = self.box.propagate_slice(self.emitters, z_layer)
        elif hasattr(self.box, 'propagate_slice'):
             field = self.box.propagate_slice(self.emitters, z_layer)
        else:
             # Fallback (slow)
             full_field = self.box.propagate(self.emitters)
             field = full_field[z_layer]
             
        intensity = np.abs(field)**2
        return intensity.tolist()

    def get_volumetric_traps(self, threshold: float = -1e-6) -> list:
        """
        Returns a list of [x, y, z] coordinates (voxel indices) of active traps.
        """
        # Propagate
        if self.use_gpu:
             field = self.box.propagate(self.emitters)
             # Use GPU substrate method
             if hasattr(self.box, 'get_trap_indices'):
                 return self.box.get_trap_indices(field, threshold)
        
        # Fallback for CPU or if method missing
        # Calculate U manually
        field = self.box.propagate(self.emitters)
        U = self.box.calculate_gorkov_potential(field)
        indices = np.argwhere(U < threshold)
        return indices[:, [2, 1, 0]].tolist()

    def calculate_osd_metrics(self, field_data: np.ndarray) -> dict:
        """
        Calculates Orthogonal Sum Dynamics (OSD) metrics.
        """
        # 1. Vector Sum (Visibility)
        visibility_map = np.abs(field_data)**2
        vector_sum_total = np.sum(visibility_map)
        
        # 2. Scalar Sum (Mass)
        emitter_intensities = [e.amplitude**2 for e in self.emitters]
        mass_density = sum(emitter_intensities)
        scalar_sum_total = mass_density * field_data.size
        
        # 3. Coherence Ratio
        if scalar_sum_total > 0:
            ratio = vector_sum_total / scalar_sum_total
        else:
            ratio = 0.0
            
        return {
            "vector_sum": float(vector_sum_total),
            "scalar_sum": float(scalar_sum_total),
            "coherence_ratio": float(ratio),
            "note": "Scalar Sum is uniform due to non-decaying simulation model. Ratio indicates focusing efficiency."
        }
