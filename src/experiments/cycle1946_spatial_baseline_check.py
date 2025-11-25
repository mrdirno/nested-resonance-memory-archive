#!/usr/bin/env python3
"""
CYCLE 1946: SPATIAL NRM BASELINE CHECK

After 0% survival in C1944 (Transcendental Habitat) despite working agent movement,
this experiment re-establishes a spatial NRM baseline.

Goal: Verify that the current NRM parameters can sustain a population
*without agent movement* in the spatialized environment.
This isolates the core NRM dynamics from movement-related issues.

Hypothesis: If this still fails, the problem is deeper in the NRM mechanics
after the FractalAgent coordinate additions. If it succeeds, the interaction
of movement with other parameters needs tuning.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2') # Root for bridge import
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/src') # Src for core import

from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 1000
N_DEPTHS = 5
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

def compute_phase_resonance(e1, d1, e2, d2):
    pi1 = (e1 * PI * 2) % (2 * PI)
    e_1 = (d1 * E / 4) % (2 * PI)
    phi1 = (e1 * PHI) % (2 * PI)
    pi2 = (e2 * PI * 2) % (2 * PI)
    e_2 = (d2 * E / 4) % (2 * PI)
    phi2 = (e2 * PHI) % (2 * PI)
    v1 = [pi1, e_1, phi1]
    v2 = [pi2, e_2, phi2]
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(a**2 for a in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)

def run_simulation(seed):
    """Run NRM simulation with fixed agents in spatial context."""
    # Best Parameters (from C1936 optimization results with N=14)
    n_initial = 14
    comp_thresh = 0.99
    decomp_thresh = 0.80
    recharge_base = 0.40 # Increased recharge for spatial context in C1944
    repro_prob = 0.17
    effective_prob = 1.05
    
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SPATIAL") # Mode spatial
    np.random.seed(seed)

    # Initialize agents at fixed positions in a small cluster (no movement)
    for i in range(n_initial):
        # Place them in a small grid so they are close enough to interact
        x_pos = 50 + (i % 4) * 2 - 4
        y_pos = 50 + (i // 4) * 2 - 4
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0, x=x_pos, y=y_pos, z=50), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        
        if total >= 3000: return "Explosion"
        if total == 0: return "Extinction"

        # AGENTS DO NOT MOVE IN THIS BASELINE CHECK

        # 1. Recharge
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge_base / (1 + d * 0.5), cap=2.0)

        # 2. Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                # Child spawns near parent
                cx = agent.x + np.random.uniform(-1, 1)
                cy = agent.y + np.random.uniform(-1, 1)
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0, x=cx, y=cy, z=50), 0)
                agent.energy -= 0.3

        # 3. Composition (Spatial Proximity Check applied)
        passes = 2
        for p_idx in range(passes):
            current_pass_prob = 1.0 if p_idx == 0 else (effective_prob - 1.0)

            for d in range(N_DEPTHS - 1):
                agents = list(reality.get_population_agents(d))
                if len(agents) < 2: continue
                np.random.shuffle(agents)
                i = 0
                while i < len(agents) - 1:
                    # SPATIAL CHECK: Agents must be close to compose
                    dist = math.sqrt((agents[i].x - agents[i+1].x)**2 + (agents[i].y - agents[i+1].y)**2)
                    
                    if dist < 5.0: # Only attempt resonance if physically close (e.g. within 5mm)
                        sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                        
                        if sim >= comp_thresh and np.random.random() < current_pass_prob:
                            new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                            # New agent at midpoint
                            nx = (agents[i].x + agents[i+1].x) / 2
                            ny = (agents[i].y + agents[i+1].y) / 2
                            reality.remove_agent(agents[i].agent_id, d)
                            reality.remove_agent(agents[i+1].agent_id, d)
                            reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1, x=nx, y=ny, z=50), d+1)
                            i += 2
                            continue
                    i += 1

        # 4. Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > decomp_thresh:
                    ce = agent.energy * 0.45
                    # Decompose into neighbors
                    reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_0", d-1, ce, depth=d-1, x=agent.x-1, y=agent.y, z=50), d-1)
                    reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_1", d-1, ce, depth=d-1, x=agent.x+1, y=agent.y, z=50), d-1)
                    reality.remove_agent(agent.agent_id, d)

        # 5. Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    return "Alive"

def main():
    print(f"CYCLE 1946: Spatial NRM Baseline Check | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    seeds = list(range(1946000, 1946050)) # 50 seeds
    
    print("Running SPATIAL BASELINE (Fixed Agents, no movement)...")
    success_count = 0
    for s in seeds:
        if run_simulation(s) == "Alive":
            success_count += 1
            
    success_rate = (success_count / len(seeds)) * 100
    print(f"Spatial Baseline Survival Rate: {success_rate:.1f}%")
    
    print("=" * 80)
    if success_rate > 50.0:
        print("CONCLUSION: Spatial NRM baseline re-established.")
    else:
        print("CONCLUSION: Spatial NRM baseline low. Parameters need re-tuning for spatial context.")

if __name__ == "__main__":
    main()
