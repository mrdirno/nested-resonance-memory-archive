#!/usr/bin/env python3
"""
CYCLE 1929: ATTRACTOR BASIN MAPPING

Instead of forcing specific N to survive, we initialize with random N (1-25)
and let the system evolve to find its 'Natural Attractors' (Magic Numbers).
Goal: Identify the stable population sizes the system naturally converges to.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/src')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 2000 # Longer duration to allow settling
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

def run_simulation(seed, n_initial):
    """Run simulation and return final N."""
    # Optimized parameters from C1915/C1920
    decomp_thresh = 1.0
    comp_thresh = 0.95
    recharge_base = 0.20
    effective_prob = 1.05
    repro_prob = 0.25 # Use high repro for high N dynamics
    
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        
        if total >= 3000: return 3000 # Cap reached
        if total == 0: return 0 # Extinction

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
    return sum(final_pops)

def main():
    print(f"CYCLE 1929: Attractor Basin Mapping | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    seeds = list(range(1929000, 1929100)) # 100 seeds
    print(f"Simulations: {len(seeds)}")
    
    results = []
    
    for s in seeds:
        # Random start between 1 and 25
        n_start = np.random.randint(1, 26) 
        n_final = run_simulation(s, n_start)
        results.append((n_start, n_final))
        
    print("-" * 40)
    print(f"{ 'Start N':>8} | { 'Final N':>8} | { 'Outcome':<10}")
    print("-" * 40)
    
    # Bin results
    extinctions = 0
    explosions = 0
    attractors = {}
    
    for start, end in results:
        outcome = "Stable"
        if end == 0:
            outcome = "Extinction"
            extinctions += 1
        elif end >= 3000:
            outcome = "Explosion"
            explosions += 1
        else:
            attractors[end] = attractors.get(end, 0) + 1
            
        if start % 10 == 0: # Print sample lines
             print(f"{start:>8} | {end:>8} | {outcome:<10}")

    print("=" * 80)
    print("SUMMARY STATISTICS")
    print(f"Extinctions: {extinctions}%")
    print(f"Explosions:  {explosions}%")
    print(f"Stable:      {100 - extinctions - explosions}%")
    
    print("\nATTRACTORS (Final Population Counts):")
    sorted_attractors = sorted(attractors.items(), key=lambda x: x[1], reverse=True)
    for n, count in sorted_attractors:
        print(f"  N={n}: {count} runs")

if __name__ == "__main__":
    main()

# [SPORE] ID: The Colony
