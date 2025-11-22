import sys
import os
import numpy as np

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# --- MULTI-PHASE MICRO-SYSTEM ---
class MultiPhaseSwarm:
    def __init__(self, n_agents=200, size=10.0):
        self.n = n_agents
        self.size = size
        self.pos = np.random.rand(n_agents, 2) * size
        self.vel = np.random.randn(n_agents, 2)
        # Normalize velocity
        norms = np.linalg.norm(self.vel, axis=1, keepdims=True)
        self.vel = self.vel / norms
        
        self.phase = "FLOCKING" # Start in Phase A
        
    def step(self):
        # 1. Physics Update (Vicsek-like)
        
        if self.phase == "FLOCKING":
            # Alignment Rule
            mean_vel = np.mean(self.vel, axis=0)
            target = mean_vel / (np.linalg.norm(mean_vel) + 1e-6)
            self.vel += 0.1 * target + np.random.normal(0, 0.05, (self.n, 2))
            
            # Move
            norms = np.linalg.norm(self.vel, axis=1, keepdims=True)
            self.vel = self.vel / norms
            self.pos += self.vel * 0.1
            self.pos = self.pos % self.size
            
        elif self.phase == "AGGREGATION":
            # Cohesion Rule (Move towards center of mass)
            com = np.mean(self.pos, axis=0)
            to_com = com - self.pos
            # Normalize
            dists = np.linalg.norm(to_com, axis=1, keepdims=True)
            target = to_com / (dists + 1e-6)
            
            # Strong Cohesion, High Randomness (to kill Polarization)
            self.vel += 0.5 * target + np.random.normal(0, 0.5, (self.n, 2))
            
            # Move
            norms = np.linalg.norm(self.vel, axis=1, keepdims=True)
            self.vel = self.vel / norms
            self.pos += self.vel * 0.1
            # No periodic BC in aggregation to allow clumping

    def get_metrics(self):
        # Polarization
        mean_v = np.mean(self.vel, axis=0)
        pol = np.linalg.norm(mean_v)
        
        # Density (Proxy: Inverse of mean distance to COM)
        com = np.mean(self.pos, axis=0)
        dists = np.linalg.norm(self.pos - com, axis=1)
        # Scale density to be roughly comparable to polarization (0-1 range)
        # Tighter clumping -> Higher density
        density = 2.0 / (np.mean(dists) + 1e-6)
        # Clip for stability
        density = min(density, 1.0) 
        
        return {"polarization": pol, "density": density}

# --- EXPERIMENT ---
def run_adaptive_linker():
    print("\n--- PAPER 22: THE ADAPTIVE LINKER (DYNAMIC ABSTRACTION) ---")
    
    STEPS = 200
    PHASE_SWITCH = 100
    
    swarm = MultiPhaseSwarm()
    
    # Controller State
    active_linker = "POLARIZATION" # Default
    fitness_adaptive = 0.0
    fitness_fixed = 0.0
    
    print(f"Phase A: FLOCKING (Steps 0-{PHASE_SWITCH})")
    print(f"Phase B: AGGREGATION (Steps {PHASE_SWITCH}-{STEPS})")
    
    for t in range(STEPS):
        # Switch Phase
        if t == PHASE_SWITCH:
            print("\n*** ENVIRONMENT CHANGE: SWITCHING TO AGGREGATION PHASE ***")
            swarm.phase = "AGGREGATION"
            
        # Step Physics
        swarm.step()
        metrics = swarm.get_metrics()
        
        # --- CONTROL LOGIC ---
        
        # 1. Fixed Controller (Always optimizes Polarization)
        # In Flocking, Polarization is the survival metric.
        # In Aggregation, Density is the survival metric.
        if swarm.phase == "FLOCKING":
            fitness_fixed += metrics["polarization"]
        else:
            # In Aggregation, Polarization is USELESS. Zero fitness gain.
            fitness_fixed += 0.0
            
        # 2. Adaptive Controller (Switches Linker)
        
        signal_pol = metrics["polarization"]
        signal_den = metrics["density"]
        
        # Hysteresis / Switching Logic
        if signal_den > signal_pol + 0.1 and active_linker == "POLARIZATION":
            print(f"[Meta-Controller] t={t}: Switching Linker POLARIZATION -> DENSITY (Pol={signal_pol:.2f}, Den={signal_den:.2f})")
            active_linker = "DENSITY"
        elif signal_pol > signal_den + 0.1 and active_linker == "DENSITY":
            print(f"[Meta-Controller] t={t}: Switching Linker DENSITY -> POLARIZATION (Pol={signal_pol:.2f}, Den={signal_den:.2f})")
            active_linker = "POLARIZATION"
            
        # Calculate Fitness based on Active Linker matching the Environment
        if swarm.phase == "FLOCKING":
            if active_linker == "POLARIZATION":
                fitness_adaptive += metrics["polarization"]
            else:
                fitness_adaptive += 0.0 # Wrong abstraction = Death
        else: # AGGREGATION
            if active_linker == "DENSITY":
                fitness_adaptive += metrics["density"]
            else:
                fitness_adaptive += 0.0 # Wrong abstraction = Death
                
    print("\n--- RESULTS ---")
    print(f"Fixed Linker Fitness:    {fitness_fixed:.2f}")
    print(f"Adaptive Linker Fitness: {fitness_adaptive:.2f}")
    
    if fitness_adaptive > fitness_fixed * 1.2:
        print("SUCCESS: Adaptive Linker significantly outperformed Fixed Linker.")
    else:
        print("FAILURE: No significant advantage found.")

if __name__ == "__main__":
    run_adaptive_linker()
