"""
CYCLE 342: Computational Matter (Acoustic Logic)
Objective: Implement an AND Gate using particle interactions (Scattering).
Mechanism: The presence of Input Particles (A, B) scatters the acoustic field, 
altering the potential landscape at Output C.
"""
import numpy as np
import json
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.substrate_3d import AcousticSubstrate3D
from experiments.cycle320_forward_cymatics_2d import Emitter

class Emitter3D(Emitter):
    def __init__(self, x, y, z, frequency, phase, amplitude=1.0):
        super().__init__(x, y, frequency, phase, amplitude)
        self.z = z

def calculate_field_at_point(point, emitters, wave_speed=343.0):
    """Calculates complex pressure at a point from emitters."""
    field = 0j
    for e in emitters:
        dist = np.sqrt((point[0]-e.x)**2 + (point[1]-e.y)**2 + (point[2]-e.z)**2)
        # Convert dist to meters for phase
        dist_m = dist / 1000.0
        real_freq = 30000 + (e.frequency * 20000)
        k = 2 * np.pi * real_freq / wave_speed
        
        # Phase = -k*d + phi
        phase = -k * dist_m + e.phase
        field += e.amplitude * np.exp(1j * phase)
    return field

def simulate_logic_gate(input_a_present, input_b_present):
    """
    Simulates the acoustic field with optional scatterers A and B.
    Returns the position of Output C.
    """
    # 1. Setup Space
    box = AcousticSubstrate3D(width_mm=60, height_mm=60, depth_mm=60, resolution_mm=1)
    
    # 2. Emitters (Standard 6-axis setup)
    mid = 30.0
    emitters = [
        Emitter3D(mid, mid, 0, 1.0, 0.0), Emitter3D(mid, mid, 60, 1.0, 0.0),
        Emitter3D(0, mid, mid, 1.0, 0.0), Emitter3D(60, mid, mid, 1.0, 0.0),
        Emitter3D(mid, 0, mid, 1.0, 0.0), Emitter3D(mid, 60, mid, 1.0, 0.0)
    ]
    
    # 3. Define Positions
    # Move scatterers further out (15mm from center) to reduce influence
    pos_a = np.array([15.0, 30.0, 30.0])
    pos_b = np.array([45.0, 30.0, 30.0])
    pos_c_0 = np.array([30.0, 30.0, 30.0]) # Default "0" position (Center) 
    pos_c_1 = np.array([30.0, 40.0, 30.0]) # Target "1" position (Shifted Y) 
    
    # 4. Configure Phases (The "Program")
    # We tune the emitters such that:
    # - Without scatterers, there is a trap at C_0.
    # - With BOTH scatterers, the interference shifts the trap to C_1.
    # This is hard to solve analytically. 
    # Simplified approach for simulation:
    # We assume the scatterers emit a secondary wave that is Pi-shifted relative to the trap at C_0,
    # effectively cancelling it and creating a new minimum at C_1?
    # Or simpler: The scatterers act as "Repulsors".
    # If A and B are present, they push C away from C_0 towards C_1.
    
    # Let's just focus emitters at C_0 initially.
    freq_hz = 40000
    v = 343.0
    k = 2 * np.pi * freq_hz / v
    
    for e in emitters:
        # Focus at C_0
        dist = np.sqrt((e.x - pos_c_0[0])**2 + (e.y - pos_c_0[1])**2 + (e.z - pos_c_0[2])**2)
        dist_m = dist / 1000.0
        e.phase = (k * dist_m) % (2 * np.pi) # Constructive interference (Antinode)
        # Wait, trap is Node. So we want Destructive? 
        # Actually, standard levitation uses Standing Wave.
        # Let's stick to the "Focus = Antinode, Trap = Adjacent Node" model.
        
    # 5. Calculate Field with Scattering
    # Grid
    z, y, x = np.mgrid[0:60, 0:60, 0:60]
    # Convert to meters
    x_m, y_m, z_m = x*0.001, y*0.001, z*0.001
    
    # Incident Field
    field_incident = np.zeros((60, 60, 60), dtype=complex)
    
    for e in emitters:
        ex_m, ey_m, ez_m = e.x*0.001, e.y*0.001, e.z*0.001
        dist_m = np.sqrt((x_m - ex_m)**2 + (y_m - ey_m)**2 + (z_m - ez_m)**2)
        phase = -k * dist_m + e.phase
        field_incident += e.amplitude * np.exp(1j * phase)
        
    # Scattering Field
    field_scatter = np.zeros((60, 60, 60), dtype=complex)
    
    scatterers = []
    if input_a_present: scatterers.append(pos_a)
    if input_b_present: scatterers.append(pos_b)
    
    for s_pos in scatterers:
        # 1. Calculate Incident Field at Scatterer
        p_inc = calculate_field_at_point(s_pos, emitters)
        
        # 2. Scatter Source (Monopole)
        # Amplitude proportional to incident pressure
        # Phase shift? Hard sphere scattering usually has phase shift.
        # Let's assume it re-radiates with some scattering coefficient sigma.
        sigma = 0.3 # Reduced to require constructive interference from BOTH for shift
        s_amp = p_inc * sigma
        
        sx_m, sy_m, sz_m = s_pos[0]*0.001, s_pos[1]*0.001, s_pos[2]*0.001
        dist_m = np.sqrt((x_m - sx_m)**2 + (y_m - sy_m)**2 + (z_m - sz_m)**2)
        
        # Avoid singularity at source
        dist_m[dist_m < 0.001] = 0.001
        
        # Propagate scattered wave (Spherical)
        # Green's function: exp(ikr) / r
        # We ignore 1/r decay for simplicity in this small volume? No, physics matters.
        field_scatter += s_amp * (np.exp(1j * k * dist_m) / dist_m) * 0.01 # Scale factor
        
    total_field = field_incident + field_scatter
    potential = np.abs(total_field)**2
    
    # 6. Find Output C Position
    # Search near C_0 and C_1
    # We define "Output 1" if the trap is closer to C_1 than C_0.
    
    # Find global min in the central region
    roi = potential[20:40, 20:50, 20:40] # Z, Y, X
    min_idx = np.unravel_index(np.argmin(roi), roi.shape)
    
    # Convert back to global coords
    c_z = min_idx[0] + 20
    c_y = min_idx[1] + 20
    c_x = min_idx[2] + 20
    
    trap_pos = np.array([float(c_x), float(c_y), float(c_z)])
    
    # Logic Decision (Symmetry Based)
    # Case 00: Trap is near center (or random).
    # Case 01/10: Trap is pushed Left or Right (Symmetry Broken).
    # Case 11: Trap is pushed Forward but Centered (Symmetry Restored).
    
    # Define "1" as: Y > 40 AND |X - 30| < 5
    # This captures the "Pushed Forward and Centered" state which only happens with A AND B.
    
    is_pushed = trap_pos[1] > 40
    is_centered = abs(trap_pos[0] - 30) < 5
    
    state = 1 if (is_pushed and is_centered) else 0
    
    return state, trap_pos

def main():
    print("CYCLE 342: ACOUSTIC LOGIC (AND GATE)")
    print("====================================")
    
    truth_table = []
    
    # Case 00
    s00, p00 = simulate_logic_gate(False, False)
    print(f"Input: 0 0 | Trap: {p00} | Output: {s00}")
    truth_table.append((0, 0, s00))
    
    # Case 01
    s01, p01 = simulate_logic_gate(False, True)
    print(f"Input: 0 1 | Trap: {p01} | Output: {s01}")
    truth_table.append((0, 1, s01))
    
    # Case 10
    s10, p10 = simulate_logic_gate(True, False)
    print(f"Input: 1 0 | Trap: {p10} | Output: {s10}")
    truth_table.append((1, 0, s10))
    
    # Case 11
    s11, p11 = simulate_logic_gate(True, True)
    print(f"Input: 1 1 | Trap: {p11} | Output: {s11}")
    truth_table.append((1, 1, s11))
    
    # Verification
    expected = [(0,0,0), (0,1,0), (1,0,0), (1,1,1)]
    success = (truth_table == expected)
    
    if success:
        print("\n>> SUCCESS: AND Gate Logic Verified.")
        print(">> Matter is computing.")
    else:
        print("\n>> FAILURE: Logic mismatch.")
        print(f"Expected: {expected}")
        print(f"Actual:   {truth_table}")
        
    # Save Results
    results = {
        "cycle": 342,
        "truth_table": truth_table,
        "success": success
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c342_acoustic_logic.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()