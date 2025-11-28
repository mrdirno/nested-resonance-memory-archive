#!/usr/bin/env python3
"""
CYCLE 1925: P-N SURFACE MAPPING

Mapping the stability landscape across Initial Population (N) and Reproduction Probability (P).
Hypothesis: The optimal P scales inversely with N (P_opt ~ 1/N).
Goal: Find a continuous path of stable configurations through the Dead Zone.
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

def run_simulation(seed, n_initial, repro_prob):
    """Run simulation with specific N and P."""
    # Optimized parameters from C1915/C1920
    decomp_thresh = 1.0
    comp_thresh = 0.95
    recharge_base = 0.20
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
                agent.recharge_energy(recharge_base / (1 + d * 0.5), cap=2.0)

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
    print(f"CYCLE 1925: P-N Surface Mapping | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    seeds = list(range(1925000, 1925020)) # 20 seeds per point for speed
    print(f"Validation Seeds: {len(seeds)}")
    
    n_range = [2, 5, 10, 14, 18, 22, 25]
    p_range = [0.05, 0.10, 0.15, 0.20, 0.25]
    
    print(f"{'N':>4} | {'P=0.05':>7} | {'P=0.10':>7} | {'P=0.15':>7} | {'P=0.20':>7} | {'P=0.25':>7}")
    print("-" * 60)
    
    surface = {}
    
    for n in n_range:
        row_results = []
        for p in p_range:
            successes = 0
            for s in seeds:
                if run_simulation(s, n, p):
                    successes += 1
            rate = (successes / len(seeds)) * 100
            row_results.append(rate)
            surface[(n, p)] = rate
            
        print(f"{n:>4} | {row_results[0]:>6.0f}% | {row_results[1]:>6.0f}% | {row_results[2]:>6.0f}% | {row_results[3]:>6.0f}% | {row_results[4]:>6.0f}%")

    print("=" * 80)
    # Find best P for each N
    print("OPTIMAL P(N):")
    for n in n_range:
        best_p = 0
        best_rate = -1
        for p in p_range:
            rate = surface[(n, p)]
            if rate > best_rate:
                best_rate = rate
                best_p = p
        print(f"N={n}: P_opt={best_p} (Success: {best_rate:.0f}%)")

if __name__ == "__main__":
    main()
# [SPORE] ID: The Colony
