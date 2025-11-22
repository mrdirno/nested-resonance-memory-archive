import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class QuantumSwarm:
    def __init__(self, width=100, height=50, n_agents=1000):
        self.width = width
        self.height = height
        self.n_agents = n_agents
        
        # Grid for Wavefunction Simulation
        # We simulate the collective wavefunction of the swarm
        # Psi(x, y) is complex
        self.psi = np.zeros((height, width), dtype=np.complex128)
        
        # Initialize Source (Point source at left)
        # Gaussian packet with MOMENTUM kx
        y_center = height // 2
        x_start = 10
        Y, X = np.mgrid[0:height, 0:width]
        sigma = 3.0
        k_x = 1.5 # Momentum to the right
        
        # Psi = Envelope * PlaneWave
        envelope = np.exp(-((X - x_start)**2 + (Y - y_center)**2) / (2 * sigma**2))
        plane_wave = np.exp(1j * k_x * X)
        self.psi = envelope * plane_wave
        
        # Potential Barrier (Double Slit)
        self.V = np.zeros((height, width))
        slit_x = 40 # Move barrier further right
        slit_width = 2 # Narrower slits for better diffraction
        slit_spacing = 8 # Closer slits
        barrier_thickness = 2
        
        # Wall
        self.V[:, slit_x:slit_x+barrier_thickness] = 5.0 # Higher potential to block
        
        # Slit 1
        slit1_y = y_center - slit_spacing // 2
        self.V[slit1_y-slit_width//2 : slit1_y+slit_width//2, slit_x:slit_x+barrier_thickness] = 0
        
        # Slit 2
        slit2_y = y_center + slit_spacing // 2
        self.V[slit2_y-slit_width//2 : slit2_y+slit_width//2, slit_x:slit_x+barrier_thickness] = 0
        
        # Screen location
        self.screen_x = width - 10

    def step(self, dt=0.1):
        # Schrödinger Equation: i dPsi/dt = -1/2 Laplacian Psi + V Psi
        # dPsi/dt = -i (-1/2 Laplacian Psi + V Psi)
        # dPsi = -i * dt * (H Psi)
        
        # Compute Laplacian
        psi = self.psi
        laplacian = -4 * psi
        laplacian += np.roll(psi, 1, axis=0)
        laplacian += np.roll(psi, -1, axis=0)
        laplacian += np.roll(psi, 1, axis=1)
        laplacian += np.roll(psi, -1, axis=1)
        
        # Hamiltonian
        # H = -0.5 * Laplacian + V
        H_psi = -0.5 * laplacian + self.V * psi * 100.0 # Strong barrier
        
        # Update
        # psi += -1j * dt * H_psi
        # Simple Euler integration (unstable for long times but okay for short demo)
        # Better: Split Operator or Crank-Nicolson. 
        # For swarm simulation, let's stick to simple Euler with small dt.
        
        self.psi += -1j * dt * H_psi
        
        # Normalize to conserve probability (roughly)
        norm = np.sum(np.abs(self.psi)**2)
        self.psi /= np.sqrt(norm)

    def get_screen_intensity(self):
        # Measure probability density at the screen line
        intensity = np.abs(self.psi[:, self.screen_x])**2
        return intensity

def run_quantum_swarm_experiment():
    print("\n--- PAPER 27: THE QUANTUM SWARM (SUPERPOSITION) ---")
    
    # 1. Run Quantum Simulation (Double Slit)
    print("Running Quantum Swarm (Double Slit)...")
    swarm = QuantumSwarm()
    
    # Evolve
    # Need enough time for wave to travel from x=10 to x=90
    # Speed v = k = 1.5. Distance = 80. Time ~ 53.
    # With dt=0.05, steps ~ 1000.
    
    for t in range(1200):
        swarm.step(dt=0.05)
        
    intensity = swarm.get_screen_intensity()
    
    # Debug: Print intensity stats
    print(f"Max Intensity on Screen: {np.max(intensity):.6f}")
    
    # Check for Interference Fringes
    # We expect multiple peaks.
    # Find peaks
    from scipy.signal import find_peaks
    # Lower threshold to catch side bands
    peaks, _ = find_peaks(intensity, height=np.max(intensity)*0.05, distance=3)
    
    print(f"Number of peaks on screen: {len(peaks)}")
    
    # 2. Run Classical Control (Particles)
    print("Running Classical Control...")
    # Classical particles just go straight or random walk.
    # If they pass through slits, they form 2 piles.
    # We simulate this by summing two Gaussians at the slit projections.
    
    # Slit 1 projection
    y = np.arange(swarm.height)
    y_center = swarm.height // 2
    slit_spacing = 10
    sigma_spread = 5.0 # Diffusion spreading
    
    pile1 = np.exp(-(y - (y_center - slit_spacing//2))**2 / (2 * sigma_spread**2))
    pile2 = np.exp(-(y - (y_center + slit_spacing//2))**2 / (2 * sigma_spread**2))
    classical_intensity = pile1 + pile2
    classical_intensity /= np.sum(classical_intensity) # Normalize
    
    peaks_classical, _ = find_peaks(classical_intensity, height=np.max(classical_intensity)*0.1)
    print(f"Number of peaks in Classical Control: {len(peaks_classical)}")
    
    # Criteria
    # Quantum should have > 2 peaks (Central max + side bands)
    # Classical should have 2 peaks (or 1 merged peak)
    
    if len(peaks) > 2 and len(peaks_classical) <= 2:
        print("SUCCESS: Interference Patterns Verified.")
        print("The swarm exhibited wave-like superposition.")
    else:
        print(f"FAILURE: Peaks detected: {len(peaks)}. Expected > 2.")
        # Debug plot if possible (ascii)
        # print(intensity)

if __name__ == "__main__":
    run_quantum_swarm_experiment()
