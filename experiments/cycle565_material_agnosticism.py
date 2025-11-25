
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nrm_core.helios.substrate_3d_gpu import AcousticSubstrate3DGPU
from nrm_core.helios.types import PhysicsConfig, Emitter3D

def run_experiment():
    print("Testing Material Agnosticism...")
    
    # Default Config (Styrofoam)
    config_default = PhysicsConfig()
    
    # Heavy Config (Lead)
    # rho = 11340 kg/m3
    config_heavy = PhysicsConfig(rho_particle=11340.0)
    
    print(f"Default Rho: {config_default.rho_particle}")
    print(f"Heavy Rho: {config_heavy.rho_particle}")
    
    # Create Substrates
    sub_def = AcousticSubstrate3DGPU(50, 50, 50, 1, config=config_default)
    sub_heavy = AcousticSubstrate3DGPU(50, 50, 50, 1, config=config_heavy)
    
    # Emitters
    emitters = [Emitter3D(25, 25, 0, 1.0, 1.0, 0.0), Emitter3D(25, 25, 50, 1.0, 1.0, 0.0)]
    
    # Propagate (Field should be same, Gorkov differs)
    field_def = sub_def.propagate(emitters)
    field_heavy = sub_heavy.propagate(emitters)
    
    # Check Field Identity
    diff_field = np.max(np.abs(field_def - field_heavy))
    print(f"Field Difference (Should be 0): {diff_field}")
    
    # Gorkov
    U_def = sub_def.calculate_gorkov_potential(field_def)
    U_heavy = sub_heavy.calculate_gorkov_potential(field_heavy)
    
    max_U = np.max(np.abs(U_def))
    diff_U = np.max(np.abs(U_def - U_heavy))
    
    print(f"Max U: {max_U}")
    print(f"Potential Difference: {diff_U}")
    
    if max_U > 0:
        rel_diff = diff_U / max_U
        print(f"Relative Difference: {rel_diff}")
        
        if rel_diff > 1e-5: # Expect at least 0.001% change
            print("SUCCESS: Material properties affect the Trap Potential.")
        else:
            print("FAILURE: Change is too small.")
    else:
        print("FAILURE: Max U is zero.")

if __name__ == "__main__":
    run_experiment()
