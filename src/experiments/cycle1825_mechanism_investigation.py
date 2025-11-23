#!/usr/bin/env python3
"""
CYCLE 1825: MECHANISM INVESTIGATION
Why do patterns cycle through probability space?

Hypothesis: Balance between growth rate and composition rate
determines which N values become dead zones.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1825"
CYCLES = 500
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

def run_test_with_dynamics(seed, n_initial, repro_prob):
    """Track growth, composition, decomposition rates"""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track dynamics
    total_births = 0
    total_compositions = 0
    total_decompositions = 0
    pop_history = []

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        pop_history.append(total)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction - track births
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
                total_births += 1

        # Composition - track compositions
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    total_compositions += 1
                    i += 2
                else:
                    i += 1

        # Decomposition - track decompositions
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)
                    total_decompositions += 1

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    coexistence = sum(1 for p in final_pops if len(p) > 0) >= 2

    return {
        'coexistence': coexistence,
        'births': total_births,
        'compositions': total_compositions,
        'decompositions': total_decompositions,
        'final_cycle': len(pop_history),
        'avg_pop': np.mean(pop_history) if pop_history else 0
    }

def main():
    print(f"CYCLE 1825: Mechanism Investigation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Why do patterns cycle through probability space?")
    print("=" * 80)

    seeds = list(range(1825001, 1825021))  # 20 seeds

    # Test key N values across probability spectrum
    test_cases = [
        (29, 0.10),  # Original dead zone
        (29, 0.35),  # Safe in inverted
        (24, 0.10),  # Safe in original
        (24, 0.35),  # Inverted dead zone
        (35, 0.50),  # Safe in flat
        (35, 0.80),  # Isolated peak
        (24, 0.95),  # Return at high prob
    ]

    print(f"\n{'N':<5} | {'Prob':<6} | {'Coex':>6} | {'Births':>8} | {'Comp':>8} | {'Decomp':>8} | {'B/C Ratio':>10}")
    print("-" * 80)

    for n, prob in test_cases:
        results = [run_test_with_dynamics(seed, n, prob) for seed in seeds]

        coex = sum(r['coexistence'] for r in results) / len(results) * 100
        births = np.mean([r['births'] for r in results])
        comps = np.mean([r['compositions'] for r in results])
        decomps = np.mean([r['decompositions'] for r in results])
        ratio = births / comps if comps > 0 else float('inf')

        print(f"{n:<5} | {prob:<6} | {coex:>5.0f}% | {births:>8.0f} | {comps:>8.0f} | {decomps:>8.0f} | {ratio:>10.2f}")

    # Analysis: Compare dynamics at same N, different prob
    print("\n" + "=" * 80)
    print("MECHANISM ANALYSIS: N=29 across probability range")
    print("=" * 80)

    probs = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]

    print(f"\n{'Prob':<6} | {'Coex':>6} | {'Births':>8} | {'Comp':>8} | {'B/C':>8} | {'Avg Pop':>8}")
    print("-" * 60)

    for prob in probs:
        results = [run_test_with_dynamics(seed, 29, prob) for seed in seeds]

        coex = sum(r['coexistence'] for r in results) / len(results) * 100
        births = np.mean([r['births'] for r in results])
        comps = np.mean([r['compositions'] for r in results])
        ratio = births / comps if comps > 0 else float('inf')
        avg_pop = np.mean([r['avg_pop'] for r in results])

        print(f"{prob:<6} | {coex:>5.0f}% | {births:>8.0f} | {comps:>8.0f} | {ratio:>8.2f} | {avg_pop:>8.0f}")

if __name__ == "__main__":
    main()
