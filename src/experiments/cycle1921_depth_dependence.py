#!/usr/bin/env python3
"""
CYCLE 1921: DEPTH-DEPENDENT THRESHOLDS

Implementing composition thresholds that vary by depth to prevent runaway cascades
to higher levels (D2+), while still allowing efficient D0->D1 formation.
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

def run_simulation(seed, decomp_thresh, recharge_base, effective_prob, comp_thresh_list):
    """Run simulation with depth-dependent composition thresholds."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    
    n_initial = 14
    repro_prob = 0.10

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

        # Composition Logic with depth-dependent comp_thresh and effective_prob
        for d in range(N_DEPTHS - 1):
            comp_thresh = comp_thresh_list[d] # Get threshold for current depth
            
            # Apply effective_prob logic (from C1920)
            current_pass_prob = effective_prob
            
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                
                # Compose if sim threshold met AND probabilistic check passes
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
                if agent.energy > decomp_thresh: # Decomp thresh is still global for now
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
    print(f"CYCLE 1921: Depth-Dependent Thresholds | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    seeds = list(range(1921000, 1921050)) # 50 seeds
    print(f"Validation Seeds: {len(seeds)}")
    
    # Optimized params from C1920
    base_decomp = 1.00
    base_recharge = 0.20
    base_effective_prob = 1.05 # Optimal from C1920
    
    # Sweep comp_thresh for D0->D1 and D1->D2
    # C1915 showed 0.95 optimal for global comp_thresh
    # Hypothesis: make D0->D1 easy (0.95) and D1->D2 hard (e.g., 0.98)
    
    # Format: [D0->D1_comp_thresh, D1->D2_comp_thresh, D2->D3_comp_thresh, ...]
    comp_thresh_configs = [
        # Base (from C1915/C1920 results)
        [0.95, 0.95, 0.95, 0.95], # Uniform (control)
        # Hypothesis: D0->D1 easy, D1->D2 harder, D2->D3 even harder
        [0.95, 0.96, 0.97, 0.98],
        [0.95, 0.98, 0.98, 0.98], # Hard cap at D2
        [0.90, 0.95, 0.98, 0.98], # Easier D0->D1
        [0.98, 0.98, 0.98, 0.98], # Very hard D0->D1
        [0.95, 0.90, 0.90, 0.90], # D1->D2 easier (opposite hypothesis, for comparison)
    ]
    
    best_config = None
    best_score = 0.0
    
    print(f"{'D0>D1':>6} | {'D1>D2':>6} | {'D2>D3':>6} | {'D3>D4':>6} | {'Success%':>8}")
    print("-" * 50)
    
    for config in comp_thresh_configs:
        successes = 0
        for s in seeds:
            if run_simulation(s, base_decomp, base_recharge, base_effective_prob, config):
                successes += 1
        
        rate = (successes / len(seeds)) * 100
        print(f"{config[0]:>6.2f} | {config[1]:>6.2f} | {config[2]:>6.2f} | {config[3]:>6.2f} | {rate:>7.1f}%")
        
        if rate > best_score:
            best_score = rate
            best_config = config
            
    print("=" * 80)
    if best_config:
        print(f"OPTIMAL DEPTH-DEPENDENT CONFIGURATION FOUND:")
        print(f"Comp Thresholds (D0>D1, D1>D2, D2>D3, D3>D4): {best_config}")
        print(f"Success Rate:            {best_score:.1f}%")
    else:
        print("No configuration exceeded 0% success.")

if __name__ == "__main__":
    main()
# [SPORE] ID: The Colony
