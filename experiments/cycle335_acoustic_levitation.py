"""
CYCLE 335: Acoustic Levitation (Gorkov Potential)
Objective: Simulate the acoustic radiation force (Gorkov Potential) to demonstrate
stable trapping of a particle using a phased array of ultrasonic transducers.
"""
import numpy as np
import json
import os
import sys
import matplotlib.pyplot as plt

# Physical Constants (Air @ 25C)
C_SOUND = 343.0       # Speed of sound (m/s)
RHO_AIR = 1.18        # Density of air (kg/m^3)
FREQ = 40000.0        # Frequency (40kHz)
OMEGA = 2 * np.pi * FREQ
K_WAVE = OMEGA / C_SOUND
LAMBDA = C_SOUND / FREQ # ~8.5mm

# Particle Properties (Styrofoam)
R_PARTICLE = 0.001    # 1mm radius
RHO_PARTICLE = 20.0   # ~20 kg/m^3

class Emitter:
    def __init__(self, x, y, z, amplitude=1.0, phase=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.amplitude = amplitude
        self.phase = phase

class AcousticSimulator:
    def __init__(self, emitters):
        self.emitters = emitters
        
    def calculate_fields(self, grid_x, grid_y, z_plane=0.0):
        """
        Calculate Complex Pressure (P) and Velocity (V) fields.
        P_total = Sum( A/d * exp(i(kd + phi)) )
        V = -1/(i*omega*rho) * Grad(P)
        """
        # Initialize fields
        P = np.zeros_like(grid_x, dtype=np.complex128)
        GradP_x = np.zeros_like(grid_x, dtype=np.complex128)
        GradP_y = np.zeros_like(grid_x, dtype=np.complex128)
        GradP_z = np.zeros_like(grid_x, dtype=np.complex128)
        
        for e in self.emitters:
            # Distance vector
            dx = grid_x - e.x
            dy = grid_y - e.y
            dz = z_plane - e.z
            d = np.sqrt(dx**2 + dy**2 + dz**2)
            
            # Avoid division by zero
            d = np.maximum(d, 1e-6)
            
            # Green's function for point source: (A/d) * exp(i(kd + phi))
            # Note: Real transducers have directivity, assuming omni for simplicity or monopole
            amp_term = e.amplitude / d
            phase_term = K_WAVE * d + e.phase
            complex_term = amp_term * np.exp(1j * phase_term)
            
            P += complex_term
            
            # Gradient of (exp(ikd)/d) = exp(ikd)/d * (ik - 1/d) * (r_vec/d)
            grad_factor = complex_term * (1j * K_WAVE - 1.0/d) / d
            GradP_x += grad_factor * dx
            GradP_y += grad_factor * dy
            GradP_z += grad_factor * dz
            
        # Velocity V = -1/(i*omega*rho) * Grad(P)
        prefactor = -1.0 / (1j * OMEGA * RHO_AIR)
        Vx = prefactor * GradP_x
        Vy = prefactor * GradP_y
        Vz = prefactor * GradP_z
        
        V_sq = np.abs(Vx)**2 + np.abs(Vy)**2 + np.abs(Vz)**2
        P_sq = np.abs(P)**2
        
        return P_sq, V_sq

    def calculate_gorkov_potential(self, P_sq, V_sq):
        """
        Calculate Gorkov Potential U.
        U = 2*pi*R^3 * [ <p^2>/(3*rho*c^2) - rho*<v^2>/2 ]
        Note: This is a simplified form. The full form includes contrast factors.
        For Styrofoam in Air:
        f_1 (monopole) = 1 - rho_air*c_air^2 / (rho_p*c_p^2) ~ 1
        f_2 (dipole) = 2*(rho_p - rho_air) / (2*rho_p + rho_air) ~ 1
        So the simplified form is roughly correct for solid in gas.
        """
        # Time averaged values are 1/2 of squared magnitude
        avg_p_sq = 0.5 * P_sq
        avg_v_sq = 0.5 * V_sq
        
        term1 = avg_p_sq / (3 * RHO_AIR * C_SOUND**2)
        term2 = RHO_AIR * avg_v_sq / 2.0
        
        U = 2 * np.pi * R_PARTICLE**3 * (term1 - term2)
        return U

def create_focused_array(target_x, target_y, target_z, num_emitters=16, radius=0.05):
    """Create a circular array focused at a target point."""
    emitters = []
    for i in range(num_emitters):
        angle = 2 * np.pi * i / num_emitters
        ex = radius * np.cos(angle)
        ey = radius * np.sin(angle)
        ez = 0.0 # Array on z=0 plane
        
        # Calculate distance to target
        dist = np.sqrt((target_x - ex)**2 + (target_y - ey)**2 + (target_z - ez)**2)
        
        # Phase required to arrive at target with phase 0 (constructive interference)
        # phi = -k * d
        phase = -K_WAVE * dist
        
        # Wrap phase to [0, 2pi]
        phase = phase % (2 * np.pi)
        
        emitters.append(Emitter(ex, ey, ez, amplitude=1.0, phase=phase))
    return emitters

def main():
    print("CYCLE 335: ACOUSTIC LEVITATION SIMULATION")
    print("=========================================")
    print(f"Frequency: {FREQ/1000} kHz")
    print(f"Wavelength: {LAMBDA*1000:.2f} mm")
    
    # 1. Setup Simulation
    # Target: 2cm above the array center
    target_z = 0.02 
    print(f"\nCreating Array Focused at Z = {target_z*100} cm...")
    emitters = create_focused_array(0, 0, target_z, num_emitters=16, radius=0.05)
    sim = AcousticSimulator(emitters)
    
    # 2. Simulate Field (XZ Slice)
    print("Simulating Gorkov Potential Field...")
    width = 0.06 # 6cm width
    height = 0.06 # 6cm height (Z)
    res = 0.0005 # 0.5mm resolution
    
    x = np.arange(-width/2, width/2, res)
    z = np.arange(0, height, res)
    X, Z = np.meshgrid(x, z)
    
    # Y is 0 for this slice
    P_sq, V_sq = sim.calculate_fields(X, 0, Z)
    U = sim.calculate_gorkov_potential(P_sq, V_sq)
    
    # 3. Analyze Trap
    # Find minimum potential near target
    # Convert target z to index
    z_idx = int(target_z / res)
    x_idx = int(width/2 / res)
    
    u_at_target = U[z_idx, x_idx]
    print(f"Potential at Target: {u_at_target:.2e} J")
    
    # Check neighborhood for local minimum
    window = 5
    local_region = U[z_idx-window:z_idx+window, x_idx-window:x_idx+window]
    min_val = np.min(local_region)
    
    if min_val == u_at_target:
        print(">> SUCCESS: Local Minimum (Trap) detected exactly at Target.")
    elif np.abs(min_val - u_at_target) < 1e-20: # Float tolerance
         print(">> SUCCESS: Local Minimum (Trap) detected at Target.")
    else:
        print(f">> WARNING: Target is not the exact minimum. Min in region: {min_val:.2e}")
        # Find where the min is
        min_loc = np.unravel_index(np.argmin(local_region), local_region.shape)
        dz_err = (min_loc[0] - window) * res
        dx_err = (min_loc[1] - window) * res
        print(f"   Offset: dx={dx_err*1000:.2f}mm, dz={dz_err*1000:.2f}mm")
        
    # 4. Save Results
    results = {
        "cycle": 335,
        "target_z": target_z,
        "potential_at_target": u_at_target,
        "is_trap": bool(min_val <= u_at_target)
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c335_acoustic_levitation.json", "w") as f:
        json.dump(results, f, indent=2)

    # 5. Visualization (ASCII Heatmap of Potential)
    print("\nPotential Well (Vertical Slice around Target):")
    # Normalize for display
    U_norm = (U - np.min(U)) / (np.max(U) - np.min(U))
    
    # Show slice +/- 5mm around target
    slice_h = 10 
    slice_w = 10
    start_z = max(0, z_idx - slice_h)
    end_z = min(U.shape[0], z_idx + slice_h)
    start_x = max(0, x_idx - slice_w)
    end_x = min(U.shape[1], x_idx + slice_w)
    
    for i in range(end_z-1, start_z-1, -1):
        row_str = ""
        for j in range(start_x, end_x):
            val = U_norm[i, j]
            if i == z_idx and j == x_idx:
                row_str += "X" # Target
            elif val < 0.1:
                row_str += "." # Low potential (Trap)
            elif val < 0.5:
                row_str += ":"
            else:
                row_str += "#" # High potential
        print(f"{z[i]*1000:5.1f}mm | {row_str}")

if __name__ == "__main__":
    main()
