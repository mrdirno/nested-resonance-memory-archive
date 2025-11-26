
"""
Helios: The Matter Compiler (Prototype)
=======================================
High-level API for the Reality Compiler.
Integrates Voxelizer (Gate 3.1), Solver (Gate 3.2), and Materials (Gate 3.3).

Function:
    compile_matter(mesh_path, material_name, resolution) -> emitter_phases

Gate 3.4 Compliant.
"""

import numpy as np
import os
from typing import Optional, List

# Import Gates
from nrm_core.helios.voxelizer import Voxelizer
from nrm_core.helios.solver import InverseSolver, SolverConfig
from nrm_core.helios.materials import Materials, get_material
from nrm_core.helios.substrate import SubstrateInterface, AcousticLevitation

# Re-export for easy access
__all__ = ['compile_matter', 'Materials']

def compile_matter(
    mesh_path: str, 
    material_name: str = "Air (STP)",
    resolution: int = 32,
    emitter_config: Optional[dict] = None
) -> np.ndarray:
    """
    Compiles a 3D mesh into acoustic phase instructions.
    
    Args:
        mesh_path: Path to the .obj file.
        material_name: Name of the target medium (e.g., "Air (STP)", "Water (20C)").
        resolution: Voxel grid resolution (N x N x N).
        emitter_config: Optional configuration for the emitter array.
        
    Returns:
        numpy.ndarray: Array of phase delays [phi_1, ..., phi_N].
    """
    print(f"\n--- Reality Compiler v1.0 ---")
    print(f"Input: {mesh_path}")
    print(f"Target Material: {material_name}")
    
    # 1. Load & Voxelize (Gate 3.1)
    print(f"[1/3] Voxelizing Mesh...")
    voxelizer = Voxelizer(resolution=resolution)
    target_field = voxelizer.process(mesh_path)
    
    if target_field is None:
        raise ValueError("Voxelization failed.")
        
    print(f"      Target Field Shape: {target_field.shape}")
    print(f"      Active Voxels: {np.sum(target_field > 0.5)}")

    # 2. Configure Physics (Gate 3.3)
    print(f"[2/3] Configuring Physics...")
    material_props = get_material(material_name)
    print(f"      Medium: {material_props.name} (c={material_props.speed_of_sound} m/s)")
    
    # Initialize Substrate (Simulation Engine)
    # Using default emitter config if none provided (8x8 array)
    if emitter_config is None:
        emitter_config = {"rows": 8, "cols": 8, "spacing": 0.01} # 10mm spacing
        
    substrate = AcousticLevitation(
        material=material_props,
        grid_resolution=resolution,
        emitters=emitter_config
    )
    
    # 3. Solve for Phases (Gate 3.2)
    print(f"[3/3] Solving Inverse Physics...")
    solver_config = SolverConfig(
        population_size=50, 
        generations=20, # Fast compile for prototype
        mutation_rate=0.1
    )
    
    solver = InverseSolver(substrate, target_field, config=solver_config)
    phases, fitness = solver.solve()
    
    print(f"\nCompilation Complete.")
    print(f"Final Fitness: {fitness:.6f}")
    
    return phases

if __name__ == "__main__":
    # Simple Test
    # Create a dummy OBJ file for testing if it doesn't exist
    test_obj = "data/test_cube.obj"
    if not os.path.exists(test_obj):
        os.makedirs("data", exist_ok=True)
        with open(test_obj, "w") as f:
            # Simple Cube
            f.write("v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\nv 0 0 1\nv 1 0 1\nv 1 1 1\nv 0 1 1\nf 1 2 6 5\nf 2 3 7 6\nf 3 4 8 7\nf 4 1 5 8\nf 1 2 3 4\nf 5 6 7 8\n")
            
    phases = compile_matter(test_obj, "Air (STP)", resolution=16)
    print(f"Generated {len(phases)} phase instructions.")
