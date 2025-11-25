#!/usr/bin/env python3
"""
CYCLE 1931: RECHARGE RATE OPTIMIZATION

Investigating why the "Golden Parameter Set" failed (0% success) with recharge=0.20.
Sweeping recharge_base from 0.20 to 0.50 to find the survival threshold for N=14.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/src')
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

def run_simulation(seed, recharge_val):
    """Run simulation with variable recharge rate."""
    # Golden Parameters (except recharge)
    n_initial = 14
    repro_prob = 0.17
    comp_thresh = 0.99
    decomp_thresh = 1.7
    effective_prob = 1.05 
    
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        
        if total >= 3000: return False
        if total == 0: return False

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge_val / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition Logic with P=1.05
        passes = 2
        for p_idx in range(passes):
            current_pass_prob = 1.0 if p_idx == 0 else (effective_prob - 1.0)

            for d in range(N_DEPTHS - 1):
                agents = list(reality.get_population_agents(d))
                if len(agents) < 2: continue
                np.random.shuffle(agents)
                i = 0
                while i < len(agents) - 1:
                    sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                    
                    if sim >= comp_thresh and np.random.random() < current_pass_prob:
                        new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                        reality.remove_agent(agents[i].agent_id, d)
                        reality.remove_agent(agents[i+1].agent_id, d)
                        reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                        i += 2
                    else:
                        i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > decomp_thresh:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    d0_alive = final_pops[0] > 0
    d1_alive = final_pops[1] > 0
    controlled = sum(final_pops[2:]) < sum(final_pops[:2])
    
    return d0_alive and d1_alive and controlled

def main():
    print(f"CYCLE 1931: Recharge Rate Optimization | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    seeds = list(range(1931000, 1931050)) # 50 seeds
    print(f"Validation Seeds: {len(seeds)}")
    
    # Sweep recharge
    recharge_range = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    
    best_rech = 0.0
    best_score = 0.0
    
    print(f"{'Recharge':>8} | {'Success%':>8}")
    print("-" * 20)
    
    for rech in recharge_range:
        successes = 0
        for s in seeds:
            if run_simulation(s, rech):
                successes += 1
        
        rate = (successes / len(seeds)) * 100
        print(f"{rech:>8.2f} | {rate:>7.1f}%")
        
        if rate > best_score:
            best_score = rate
            best_rech = rech
            
    print("=" * 80)
    if best_rech > 0:
        print(f"OPTIMAL RECHARGE RATE FOUND: {best_rech}")
        print(f"Success Rate:              {best_score:.1f}%")
    else:
        print("No configuration exceeded 0% success.")

if __name__ == "__main__":
    main()
