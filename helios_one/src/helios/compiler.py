"""
HELIOS Matter Compiler (Gate 3.4)
The High-Level API for Reality Compilation.
Integrates Voxelizer, Solver, and Materials into a single pipeline.

Principle: PRIN-REALITY-COMPILATION
Author: MOG (Cycle 2344)
"""

from src.helios.voxelizer import Voxelizer
from src.helios.solver import InverseSolver
from src.helios.materials import get_material
import numpy as np
import os

class MatterCompiler:
    def __init__(self, resolution=32, emitters=None):
        """
        Initialize the Compiler.
        :param resolution: Grid resolution for the Voxelizer.
        :param emitters: List of emitter positions (default: 64 in a grid).
        """
        self.resolution = resolution
        self.voxelizer = Voxelizer(resolution=resolution)
        
        if emitters is None:
            # Default: 8x8 planar array
            self.emitters = []
            for x in range(8):
                for y in range(8):
                    self.emitters.append([x/8.0, y/8.0, 0.0])
        else:
            self.emitters = emitters

    def compile_object(self, mesh_path, material_name="AIR_STP"):
        """
        Compiles a 3D mesh into acoustic phase instructions.
        :param mesh_path: Path to .obj file.
        :param material_name: Substrate material (e.g., "AIR_STP", "WATER_20C").
        :return: Dictionary containing phases, frequencies, and metadata.
        """
        print(f"--- Compiling {os.path.basename(mesh_path)} in {material_name} ---")
        
        # 1. Material Selection
        mat = get_material(material_name)
        print(f"Substrate: {mat}")
        
        # 2. Voxelization (The "Mold")
        print("Step 1: Voxelizing Geometry...")
        try:
            self.voxelizer.load_obj(mesh_path)
            target_field = self.voxelizer.voxelize()
            active_voxels = np.count_nonzero(target_field)
            print(f"Target Field Generated: {active_voxels} active voxels.")
        except FileNotFoundError:
            print("Error: Mesh file not found.")
            return None

        # 3. Inverse Solving (The "Cast")
        print("Step 2: Solving Waveforms...")
        # Pass material config to solver
        physics_config = {"c": mat.c, "rho": mat.rho}
        solver = InverseSolver(target_field, self.emitters, physics_config)
        
        solution_phases = solver.evolve()
        
        # 3.5. Field Calculation (Visualizer Support)
        traps = []
        if hasattr(solver, 'get_field'):
            field = solver.get_field(solution_phases)
            # Extract traps: low potential points
            # Threshold: Mean - 2*Std? Or fixed?
            # Let's use a relative threshold for now
            threshold = field.min() + (field.max() - field.min()) * 0.05
            trap_indices = np.argwhere(field < threshold)
            
            # Convert to relative coordinates 0..1 for UI
            # D, H, W
            # x = idx[2] / W, y = idx[1] / H, z = idx[0] / D
            D, H, W = field.shape
            for idx in trap_indices:
                z, y, x = idx
                traps.append([x/float(W), y/float(H), z/float(D)])
        
        # 4. Assembly (The "Print")
        print("Step 3: Assembling Instruction Set...")
        instruction_set = {
            "meta": {
                "mesh": mesh_path,
                "material": mat.name,
                "emitters": len(self.emitters),
                "resolution": self.resolution
            },
            "traps": traps,
            "emitters": []
        }
        
        for i, phase in enumerate(solution_phases):
            instruction_set["emitters"].append({
                "id": i,
                "position": self.emitters[i],
                "phase": phase,
                "frequency": 40000.0 # Default ultrasonic
            })
            
        print("--- Compilation Complete ---")
        return instruction_set

if __name__ == "__main__":
    # Prototype Test
    # Create a dummy file first
    with open("test_cube.obj", "w") as f:
        f.write("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
        
    compiler = MatterCompiler(resolution=16)
    result = compiler.compile_object("test_cube.obj", "AIR_STP")
    
    if result:
        print(f"Generated {len(result['emitters'])} emitter instructions.")
    
    os.remove("test_cube.obj")
# [SPORE] ID: The Colony
