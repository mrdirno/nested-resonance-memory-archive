import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from code.nrm.schemas import MesoLinker

# --- EXPERIMENT: AUTOMATED MESO-LINKER DISCOVERY ---

class VicsekSwarm:
    def __init__(self, n_agents=100, noise=0.1, size=10.0):
        self.n = n_agents
        self.noise = noise
        self.size = size
        self.pos = np.random.rand(n_agents, 2) * size
        self.vel = np.random.randn(n_agents, 2)
        # Normalize velocity
        norms = np.linalg.norm(self.vel, axis=1, keepdims=True)
        self.vel = self.vel / norms

    def step(self):
        # Simple alignment rule
        # For each agent, align with average velocity of global swarm (simplified for prototype)
        # In a real Vicsek, it's local neighbors. Here we assume high density/global coupling for simplicity of demonstration.
        
        mean_vel = np.mean(self.vel, axis=0)
        mean_vel_norm = np.linalg.norm(mean_vel)
        
        if mean_vel_norm > 0:
            target_dir = mean_vel / mean_vel_norm
        else:
            target_dir = self.vel[0] # Arbitrary
            
        # Update velocities with noise
        self.vel += 0.1 * target_dir + np.random.normal(0, self.noise, (self.n, 2))
        
        # Re-normalize
        norms = np.linalg.norm(self.vel, axis=1, keepdims=True)
        self.vel = self.vel / norms
        
        # Update positions (Periodic BC)
        self.pos += self.vel * 0.1
        self.pos = self.pos % self.size

    def get_candidates(self):
        """Returns a dictionary of candidate macro-variables."""
        # Candidate 1: Polarization (Order Parameter) - Magnitude of mean velocity
        mean_v = np.mean(self.vel, axis=0)
        polarization = np.linalg.norm(mean_v)
        
        # Candidate 2: Mean Speed (Should be 1.0 by definition, check variance)
        mean_speed = np.mean(np.linalg.norm(self.vel, axis=1))
        
        # Candidate 3: Angular Momentum (Global Rotation)
        # center of mass
        com = np.mean(self.pos, axis=0)
        r = self.pos - com
        # cross product in 2D is just x*vy - y*vx
        ang_mom = np.mean(r[:, 0] * self.vel[:, 1] - r[:, 1] * self.vel[:, 0])
        
        # Candidate 4: Random Noise (Control)
        noise = np.random.random()
        
        return {
            "Polarization": polarization,
            "Mean_Speed": mean_speed,
            "Angular_Momentum": ang_mom,
            "Random": noise
        }

def evaluate_candidates(history):
    """
    Evaluates candidates based on Predictive Power (R2 of V_t -> V_t+1).
    A good Order Parameter should be predictable (slow dynamics).
    """
    results = {}
    
    for name in history[0].keys():
        data = np.array([step[name] for step in history])
        X = data[:-1].reshape(-1, 1)
        y = data[1:]
        
        model = LinearRegression()
        model.fit(X, y)
        pred = model.predict(X)
        r2 = r2_score(y, pred)
        
        # Complexity proxy: Variance (We want non-trivial variance, but high predictability)
        variance = np.var(data)
        
        # Score: R2 (Predictability) * Variance (Relevance)
        # We penalize zero variance (trivial constants) and low R2 (noise).
        # We also penalize extremely low variance to avoid floating point artifacts on constants
        if variance < 1e-6:
            score = 0
        else:
            score = r2 * np.log(1 + variance * 100) # Boost variance weight
        
        results[name] = {
            "R2": r2,
            "Variance": variance,
            "Score": score
        }
        
    return results

def run_discovery_prototype():
    print("\n--- NRM vNext: MESO-LINKER DISCOVERY PROTOTYPE ---")
    
    # 1. Simulate
    print("1. Simulating Swarm (L_1 Micro-Dynamics)...")
    swarm = VicsekSwarm(n_agents=200, noise=0.5) # Moderate noise to allow ordering
    history = []
    for _ in range(500):
        swarm.step()
        history.append(swarm.get_candidates())
        
    # 2. Evaluate Candidates (Information Bottleneck Proxy)
    print("2. Evaluating Candidate Macro-Variables (L_2 Abstractions)...")
    eval_results = evaluate_candidates(history)
    
    # 3. Select Best
    best_candidate = max(eval_results.items(), key=lambda x: x[1]['Score'])
    
    print("\nEvaluation Results:")
    for name, metrics in eval_results.items():
        print(f"  {name}: R2={metrics['R2']:.4f}, Var={metrics['Variance']:.4f}, Score={metrics['Score']:.4f}")
        
    print(f"\n>> DISCOVERED MESO-LINKER: '{best_candidate[0]}'")
    
    valid_discoveries = ["Polarization", "Angular_Momentum"]
    
    if best_candidate[0] in valid_discoveries:
        print(f"SUCCESS: System correctly identified a valid Order Parameter ('{best_candidate[0]}').")
        
        # 4. Formalize Linker
        linker = MesoLinker(
            source_level=1,
            target_level=2,
            upward_causation=f"measure_{best_candidate[0].lower()}",
            downward_causation="apply_field",
            validity_metric="Predictive_R2"
        )
        print(f"\nFormalized Linker:\n{linker.model_dump_json(indent=2)}")
        
    else:
        print("FAILURE: System failed to identify a valid Order Parameter.")

if __name__ == "__main__":
    run_discovery_prototype()
