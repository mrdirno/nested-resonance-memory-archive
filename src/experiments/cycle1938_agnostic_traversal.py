#!/usr/bin/env python3
"""
CYCLE 1938: AGNOSTIC TRAVERSAL (THE VIABILITY CORRIDOR)

We have found a parameter set that yields ~60% stability at N=14 (Dead Zone).
However, enforcing N=14 static stability might be the wrong goal.
This experiment tests "Dynamic Traversal":
1. Initialize at N=1 (Seed).
2. Let the system grow.
3. Observe if it can pass through the N=10-14 bottleneck and reach
   a stable state at higher N (e.g., N=50+).

Parameters (from C1934/C1935/C1936):
- comp_thresh = 0.99
- decomp_thresh = 0.80
- repro_prob = 0.17
- recharge_base = 0.20
- effective_prob = 1.05
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/src')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 2000 # Longer run to allow growth
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
    """Run simulation starting from N=1 seed."""
    # Optimal Parameters
    n_initial = 1
    comp_thresh = 0.99
    decomp_thresh = 0.80
    recharge_base = 0.20
    repro_prob = 0.17
    effective_prob = 1.05
    
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    max_n = 0
    final_n = 0
    status = "Alive"

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        
        if total > max_n:
            max_n = total
        
        if total >= 3000:
            status = "Explosion"
            final_n = 3000
            break
        if total == 0:
            status = "Extinction"
            final_n = 0
            break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge_base / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition Logic
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

    if status == "Alive":
        final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
        final_n = sum(final_pops)
        
    return status, max_n, final_n

def main():
    print(f"CYCLE 1938: Agnostic Traversal | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    seeds = list(range(1938000, 1938100)) # 100 seeds
    print(f"Simulations: {len(seeds)}")
    print("Parameters: comp=0.99, decomp=0.80, repro=0.17, recharge=0.20")
    print("-" * 40)
    print(f"{ 'Seed':>8} | { 'Status':<10} | { 'Max N':>6} | { 'Final N':>8}")
    print("-" * 40)
    
    results = {"Extinction": 0, "Explosion": 0, "Alive": 0}
    max_reached = []
    final_counts = []
    
    for s in seeds:
        status, mx, fn = run_simulation(s)
        results[status] += 1
        max_reached.append(mx)
        final_counts.append(fn)
        
        if s % 10 == 0: # Sample output
            print(f"{s:>8} | {status:<10} | {mx:>6} | {fn:>8}")
            
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print(f"Extinction Rate: {results['Extinction']}%")
    print(f"Explosion Rate:  {results['Explosion']}%")
    print(f"Survival Rate:   {results['Alive']}%")
    
    if results['Alive'] > 0:
        avg_final = sum([x for x in final_counts if x > 0 and x < 3000]) / results['Alive']
        print(f"Average Final N (Survivors): {avg_final:.1f}")
        
    # Analyze the "Neck"
    # Did any extinctions happen AFTER reaching N=14?
    # Or did they all die early?
    bottleneck_deaths = [m for m in max_reached if m >= 10 and m < 20 and m in final_counts and m == 0] # logic check: final count is 0 if dead
    # Actually, we want max_reached for those who died
    dead_maxes = [max_reached[i] for i in range(len(seeds)) if final_counts[i] == 0]
    died_before_10 = len([m for m in dead_maxes if m < 10])
    died_in_deadzone = len([m for m in dead_maxes if 10 <= m <= 20])
    died_after_20 = len([m for m in dead_maxes if m > 20])
    
    print("\nDEATH ANALYSIS:")
    print(f"Died before N=10: {died_before_10}")
    print(f"Died in Dead Zone (10-20): {died_in_deadzone}")
    print(f"Died after N=20: {died_after_20}")
    
    # Successes
    survived_past_20 = len([f for f in final_counts if f > 20])
    print(f"Successfully traversed to N>20: {survived_past_20}%")

if __name__ == "__main__":
    main()
