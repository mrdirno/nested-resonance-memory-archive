"""
HELIOS Matter Compiler
The High-Level API for Inverse Cymatics.
Converts Geometric Intent + Material Properties -> Acoustic Phase Instructions.

Cycle 566: Prototype Implementation.
"""
import numpy as np
from typing import List, Tuple
from .types import Material, PhysicsConfig, Emitter3D
from .substrate_3d_gpu import AcousticSubstrate3DGPU
from .ga_gpu import genetic_algorithm_gpu

class MatterCompiler:
    def __init__(self, width_mm=100, height_mm=100, depth_mm=100, emitters: List[Emitter3D] = None):
        self.width = width_mm
        self.height = height_mm
        self.depth = depth_mm
        # Standard Array Configuration (can be overridden)
        if emitters is None:
            self.emitters = self._build_standard_array()
        else:
            self.emitters = emitters
        
    def _build_standard_array(self) -> List[Emitter3D]:
        """
        Builds a standard 8x8 dual-sided array (Top/Bottom).
        """
        emitters = []
        spacing = 10.0
        num = 8
        center_offset = (num - 1) * spacing / 2.0
        center_w = self.width / 2.0
        center_h = self.height / 2.0
        
        for i in range(num):
            for j in range(num):
                x = center_w - center_offset + i * spacing
                y = center_h - center_offset + j * spacing
                
                # Bottom firing up
                emitters.append(Emitter3D(x, y, 0.0, 1.0, 1.0, 0.0))
                # Top firing down
                emitters.append(Emitter3D(x, y, self.depth, 1.0, 1.0, 0.0))
                
        return emitters

    def compile(self, geometry: List[np.ndarray], material: Material) -> List[Emitter3D]:
        """
        Compiles the target geometry into emitter phases.
        
        Args:
            geometry: List of target points (x,y,z) in mm.
            material: Material properties for the target matter.
            
        Returns:
            List of configured Emitters.
        """
        print(f"[Compiler] Initializing for {material.name}...")
        
        # 1. Configure Physics
        config = PhysicsConfig(
            rho_particle=material.density,
            c_particle=material.sound_speed
        )
        
        # 2. Initialize Substrate (GPU)
        substrate = AcousticSubstrate3DGPU(
            width_mm=self.width,
            height_mm=self.height,
            depth_mm=self.depth,
            resolution_mm=1.0, # High res for solving
            config=config
        )
        print(f"[Compiler] Substrate initialized on {substrate.device}.")
        
        # 3. Run Solver
        print(f"[Compiler] Solving for {len(geometry)} target points...")
        best_phases = genetic_algorithm_gpu(
            geometry, 
            substrate, 
            self.emitters, 
            generations=100, # Increased for stability
            pop_size=100
        )
        
        # 4. Apply Phases
        compiled_emitters = []
        for i, e in enumerate(self.emitters):
            # Create copy with new phase
            new_e = Emitter3D(e.x, e.y, e.z, e.frequency, best_phases[i], e.amplitude)
            compiled_emitters.append(new_e)
            
        print("[Compiler] Compilation Complete.")
        return compiled_emitters

