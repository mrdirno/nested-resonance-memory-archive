
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nrm_core.helios.compiler import MatterCompiler
from nrm_core.helios.types import Material
from nrm_core.helios.substrate_3d_gpu import AcousticSubstrate3DGPU

def run_experiment():
    print("Cycle 566: Matter Compiler Prototype Test")
    
    # 1. Define Material
    # Styrofoam
    styrofoam = Material(name="Styrofoam", density=25.0, sound_speed=2350.0)
    
    # 2. Define Geometry (Triangle)
    # Center is 50, 50, 50
    p1 = np.array([50.0, 50.0, 50.0])
    p2 = np.array([50.0 + 10, 50.0, 50.0])
    p3 = np.array([50.0 + 5, 50.0 + 8.66, 50.0])
    
    geometry = [p1, p2, p3]
    
    # 3. Initialize Compiler
    compiler = MatterCompiler(width_mm=100, height_mm=100, depth_mm=100)
    
    # 4. Compile
    emitters = compiler.compile(geometry, styrofoam)
    
    # 5. Verify
    print("Verifying Compilation...")
    # Re-init substrate to check field
    config = compiler._build_standard_array() # Wait, need config
    # Accessing internal for verification is hacky but fine for exp
    
    from nrm_core.helios.types import PhysicsConfig
    config = PhysicsConfig(rho_particle=styrofoam.density, c_particle=styrofoam.sound_speed)
    substrate = AcousticSubstrate3DGPU(100, 100, 100, 1, config=config)
    
    field = substrate.propagate(emitters)
    U = substrate.calculate_gorkov_potential(field)
    
    # Check potentials at targets
    print("Target Potentials:")
    for i, p in enumerate(geometry):
        ix, iy, iz = int(p[0]), int(p[1]), int(p[2])
        val = U[iz, iy, ix]
        print(f"Point {i} {p}: {val}")
        
        # Check neighborhood
        # Simple check: is it lower than above/below?
        val_up = U[iz+2, iy, ix]
        print(f"  Neighbor (Z+2mm): {val_up}")
        
        if val < val_up:
            print("  -> Local Minimum (Stable in Z)")
        else:
            print("  -> Unstable")

    # Visualize Slice
    z_idx = 50
    slice_u = U[z_idx, :, :]
    
    plt.figure(figsize=(10, 8))
    plt.imshow(slice_u, origin='lower', extent=[0, 100, 0, 100], cmap='viridis_r')
    plt.colorbar(label='Gorkov Potential')
    
    # Plot targets
    tx = [p[0] for p in geometry]
    ty = [p[1] for p in geometry]
    plt.scatter(tx, ty, c='red', marker='x', label='Target')
    
    plt.title(f"Compiled Geometry: Triangle ({styrofoam.name})")
    plt.savefig(os.path.join(os.path.dirname(__file__), 'cycle566_triangle.png'))
    print("Plot saved.")

if __name__ == "__main__":
    run_experiment()
