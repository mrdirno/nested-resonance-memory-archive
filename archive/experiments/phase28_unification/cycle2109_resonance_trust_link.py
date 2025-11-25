
import sys
import os
import random
import numpy as np
from typing import List, Dict, Tuple

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

# --- UNIFIED AGENT ---
# Inherits physics (FractalAgent) and adds social memory (Ledger)
class UnifiedAgent(FractalAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.memory: Dict[str, float] = {} # Social Ledger
        self.strategy = "Cooperator"

    def record_interaction(self, partner_id: str, outcome: float):
        current = self.memory.get(partner_id, 0.0)
        self.memory[partner_id] = current + outcome

    def check_reputation(self, agent_id: str) -> float:
        return self.memory.get(agent_id, 0.0)

    def calculate_unified_affinity(self, other: 'UnifiedAgent', alpha: float = 0.5) -> float:
        """
        Combine Physical Resonance (Micro) with Social Trust (Macro).
        Affinity = alpha * Resonance + (1-alpha) * Trust
        """
        # 1. Physical Resonance (Cos(delta_phase)) -> Range [-1, 1]
        resonance = self.calculate_resonance(other)
        
        # 2. Social Trust (Reputation) -> Range [-5, 5] typically
        # Normalize trust to [-1, 1] for combination
        raw_trust = self.check_reputation(other.state.agent_id)
        trust = np.tanh(raw_trust) # Sigmoid squash
        
        # 3. Unified Affinity
        affinity = (alpha * resonance) + ((1 - alpha) * trust)
        return affinity

# --- SIMULATION ---
def run_unified_simulation(alpha: float) -> float:
    """
    Run a simulation where agents cluster based on Unified Affinity.
    alpha: Weight of Physics (1.0 = Pure Physics, 0.0 = Pure Social)
    """
    print(f"\n--- Simulation: Alpha {alpha:.2f} (Physics vs Social) ---", flush=True)
    
    N_AGENTS = 50
    CYCLES = 100
    
    # Setup Agents: Half Good (Phase 0, Coop), Half Bad (Phase Pi, Defect)
    # BUT we mix them up physically.
    # Group A: Phase 0, Coop.
    # Group B: Phase 0, Defect. (Physically identical to A, Socially different)
    # Group C: Phase Pi, Coop.
    # Group D: Phase Pi, Defect.
    
    agents = []
    for i in range(N_AGENTS):
        group = i % 4
        if group == 0: # A: 0, Coop
            phase, strat = 0.0, "Cooperator"
        elif group == 1: # B: 0, Defect
            phase, strat = 0.0, "Defector"
        elif group == 2: # C: Pi, Coop
            phase, strat = np.pi, "Cooperator"
        else: # D: Pi, Defect
            phase, strat = np.pi, "Defector"
            
        agent = UnifiedAgent(
            agent_id=f"u_{i}",
            energy=1.0,
            phase=phase,
            position=np.random.rand(3) * 10.0
        )
        agent.strategy = strat
        # Pre-load memory: Everyone knows everyone's strategy (Perfect Reputation for test)
        # If Strat=Defector, Trust=-1. If Strat=Coop, Trust=1.
        # We inject this "Memory" to simulate a mature society.
        for j in range(N_AGENTS): # Self and others
            # Determine j's strategy
            j_group = j % 4
            j_strat = "Cooperator" if j_group in [0, 2] else "Defector"
            score = 1.0 if j_strat == "Cooperator" else -1.0
            agent.memory[f"u_{j}"] = score * 5.0 # Strong memory
            
        agents.append(agent)

    # Clustering Logic using Unified Affinity
    # We manually cluster for the test
    clusters = []
    visited = set()
    
    for i, agent_i in enumerate(agents):
        if i in visited: continue
        
        cluster = [agent_i]
        visited.add(i)
        
        for j, agent_j in enumerate(agents):
            if j in visited: continue
            
            affinity = agent_i.calculate_unified_affinity(agent_j, alpha)
            
            # Threshold for clustering
            if affinity > 0.5:
                cluster.append(agent_j)
                visited.add(j)
        
        if len(cluster) > 1:
            clusters.append(cluster)
            
    # Analyze Clusters
    # Ideally, Cooperators cluster with Cooperators (Social), OR Phase 0 with Phase 0 (Physical).
    # Metric: Purity of Cooperators in clusters.
    
    total_clustered = sum(len(c) for c in clusters)
    coop_in_clusters = 0
    for c in clusters:
        for a in c:
            if a.strategy == "Cooperator": coop_in_clusters += 1
            
    fraction_coop = coop_in_clusters / total_clustered if total_clustered > 0 else 0.0
    print(f"Clustered Population: {total_clustered}")
    print(f"Cooperator Fraction in Clusters: {fraction_coop:.2f}")
    
    return fraction_coop

def run_experiment():
    print("MOG ONLINE: Cycle 2109 - The Recursive Link", flush=True)
    
    # Scenario 1: Pure Physics (Alpha 1.0)
    # Should cluster by Phase. Group A+B (Coop+Defect), Group C+D (Coop+Defect).
    # Coop Fraction should be ~0.5 (Random mixing of strategies)
    res_phys = run_unified_simulation(1.0)
    
    # Scenario 2: Pure Social (Alpha 0.0)
    # Should cluster by Strategy. Group A+C (Coop), Group B+D (Defect).
    # Note: Defectors usually don't cluster well or we filter them?
    # Here, Defectors have Trust=-1.
    # Affinity(Defect, Defect) = tanh(-1) = -0.76. They repel.
    # Affinity(Coop, Coop) = tanh(1) = 0.76. They attract.
    # So only Cooperators should cluster.
    # Coop Fraction should be 1.0.
    res_soc = run_unified_simulation(0.0)
    
    # Scenario 3: Unified (Alpha 0.5)
    # Trade-off.
    res_uni = run_unified_simulation(0.5)
    
    print("\n--- ANALYSIS ---")
    print(f"Pure Physics (Expected 0.50): {res_phys:.2f}")
    print(f"Pure Social (Expected 1.00): {res_soc:.2f}")
    print(f"Unified (Mixed): {res_uni:.2f}")

if __name__ == "__main__":
    run_experiment()
