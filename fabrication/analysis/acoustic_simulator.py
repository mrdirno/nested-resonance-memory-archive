import numpy as np
import matplotlib.pyplot as plt
import math

# --- INPUT PARAMETERS ---
# Dimensions of Artifact 03 (Optimized) - 60x60x120mm prism
HEIGHT = 120.0 # mm
RESOLUTION = 120 # From generator, for Z axis. (Actual grid z res = 2 * res)
LAYERS = 100 # Number of discrete layers for simulation
FREQ_RANGE = np.linspace(100, 10000, 100) # 100 Hz to 10 kHz

# --- MEDIUM PROPERTIES (Air at STP) ---
RHO_AIR = 1.225 # kg/m^3
C_AIR = 343.0 # m/s
Z_AIR = RHO_AIR * C_AIR # Acoustic impedance of air

# --- MATERIAL PROPERTIES (PLA) ---
RHO_PLA = 1240 # kg/m^3 (Approx for PLA)

# --- GYROID GEOMETRY PARAMETERS (from artifact 03 generator) ---
SIZE_Z = 120.0 # Total height of artifact
BASE_SCALE = 2.0 * math.pi / 15.0 # Roughly 15mm unit cell at base
# The generator's freq_mod for Z-axis scaling: 1.0 + (z_norm * 2.0)
# This means effective wavelength scales from 1x to 3x from bottom to top.

def calculate_effective_properties(z_mm, z_max_mm):
    """
    Calculates effective porosity and related properties at a given height z for Artifact 03.
    z_mm: Current height in mm (from -z_max_mm/2 to z_max_mm/2)
    """
    # Normalized height (0 at bottom, 1 at top)
    z_norm = (z_mm + z_max_mm/2) / z_max_mm
    
    # Inverse of freq_mod for density gradient (lower frequency -> more open/porous)
    # The generator has: freq_mod = 1.0 + (z_norm * 2.0)
    # This means the density decreases as Z increases.
    
    # Porosity (phi) is what we need. Lower freq_mod means higher porosity.
    # Let's map 1/freq_mod to porosity.
    
    # The generator uses abs(gyroid) < 0.5 for fill (i.e. thickness 1.0)
    # And freq_mod is applied to z (z_prime = z / freq_mod).
    # This means cells are "stretched" at the top (freq_mod high).
    # If cells stretch, the same 'fill' value results in *lower density* over volume.
    
    # Let's derive porosity based on the volume fraction for a Gyroid.
    # It's roughly (1 - Volume_Fraction).
    # Volume_Fraction ~ 0.32 for the optimized version (thick walls).
    # This is not directly a simple porosity.
    
    # For simulation, let's simplify.
    # Porosity is higher at the top (stretched gyroid) and lower at the bottom.
    # Let's assume porosity scales with (1 / freq_mod)
    
    # Effective frequency scale at this height
    effective_z_scale_factor = 1.0 + (z_norm * 2.0) 
    
    # Lower scale factor means denser material
    # Let's assume porosity (phi) goes from ~0.6 at bottom to ~0.9 at top
    # This is a simplification and would be derived more rigorously from the STL's volume fraction per slice.
    phi = 0.6 + (z_norm * 0.3) # 0.6 at bottom, 0.9 at top
    phi = np.clip(phi, 0.1, 0.9) # Ensure reasonable bounds
    
    # Effective density of the porous medium (Bruggeman model or simple average)
    rho_eff = (phi * RHO_AIR) + ((1 - phi) * RHO_PLA)
    
    # Effective speed of sound (Simplification for porous media)
    # Often, c_eff is lower in porous media and depends on many factors.
    # For a simple model, let's assume c_eff ~ c_air * sqrt(phi) or similar, but with damping.
    c_eff = C_AIR * math.sqrt(phi) # Basic model: speed decreases with density
    
    # Effective acoustic impedance
    z_eff = rho_eff * c_eff
    
    return phi, rho_eff, c_eff, z_eff

def simulate_absorption(freq_range, layers=LAYERS, height_mm=HEIGHT):
    """
    Simulates acoustic absorption coefficient using a 1D Transfer Matrix Method.
    """
    height_m = height_mm / 1000.0
    layer_thickness_m = height_m / layers
    
    absorption_coeffs = []
    
    for freq in freq_range:
        omega = 2 * math.pi * freq # Angular frequency
        
        # Calculate effective properties for each layer
        z_eff_layers = []
        for i in range(layers):
            z_mid_mm = (i + 0.5) * (height_mm / layers) - (height_mm / 2.0)
            _, _, _, z_eff = calculate_effective_properties(z_mid_mm, height_mm)
            z_eff_layers.append(z_eff)
            
        z_eff_layers = np.array(z_eff_layers)
        
        # --- TRANSFER MATRIX METHOD ---
        # Initialize T matrix for the entire medium (identity matrix)
        T_total = np.array([[1.0, 0.0], [0.0, 1.0]])
        
        for i in range(layers):
            Z_layer = z_eff_layers[i]
            k_layer = omega / (C_AIR * math.sqrt(calculate_effective_properties((i + 0.5) * (height_mm / layers) - (height_mm / 2.0), height_mm)[0])) # Use effective speed of sound
            
            # Impedance matrix for this layer
            A_layer = np.array([
                [math.cos(k_layer * layer_thickness_m), 1j * Z_layer * math.sin(k_layer * layer_thickness_m)],
                [(1j / Z_layer) * math.sin(k_layer * layer_thickness_m), math.cos(k_layer * layer_thickness_m)]
            ])
            
            T_total = np.matmul(T_total, A_layer) # Accumulate transfer matrices
        
        # Calculate Reflection Coefficient (R) for the whole stack
        # Interface between air (Z_AIR) and the stack (represented by T_total)
        
        # For a stack terminated by air (or any impedance Z_LOAD)
        Z_LOAD = Z_AIR # Assumed backing medium is air
        
        # Input impedance of the stack
        Z_in = (T_total[0,0] * Z_LOAD + T_total[0,1]) / (T_total[1,0] * Z_LOAD + T_total[1,1])
        
        # Reflection coefficient
        reflection_coeff = (Z_in - Z_AIR) / (Z_in + Z_AIR)
        
        # Absorption coefficient (alpha)
        alpha = 1 - abs(reflection_coeff)**2
        absorption_coeffs.append(alpha)
        
    return np.array(absorption_coeffs)

if __name__ == "__main__":
    print("Running Acoustic Absorption Simulation for Artifact 03...")
    
    # Simulation
    absorption_spectrum = simulate_absorption(FREQ_RANGE)
    
    # Plotting results
    plt.figure(figsize=(10, 6))
    plt.plot(FREQ_RANGE, absorption_spectrum)
    plt.title('Acoustic Absorption Spectrum for Artifact 03 (The Directional Current)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Absorption Coefficient (α)')
    plt.grid(True)
    plt.ylim(0, 1)
    plt.xlim(FREQ_RANGE.min(), FREQ_RANGE.max())
    
    # Save plot
    output_plot_path = "fabrication/analysis/acoustic_absorption_spectrum.png"
    plt.savefig(output_plot_path)
    print(f"Absorption spectrum plot saved to {output_plot_path}")
    plt.show()

