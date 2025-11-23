#!/usr/bin/env python3
"""
CYCLE 1878: SEED SENSITIVITY ANALYSIS

How much variance is due to random seed vs. structural N effects?
Compare variance within N vs. variance across N.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

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

def run_test(seed, n_initial, repro_prob):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

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
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
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
    return 1 if sum(1 for p in final_pops if p > 0) >= 2 else 0

def main():
    print(f"CYCLE 1878: Seed Sensitivity | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("How much variance from random seed vs. structural N effects?")
    print("=" * 80)

    seeds = list(range(1878001, 1878101))  # 100 seeds for statistics
    prob = 0.10

    # Test multiple N values
    test_n = list(range(10, 25))

    # Collect all results
    all_coex = []  # For across-N variance
    within_n_var = []  # For within-N variance

    print(f"\n{'N':>3} | {'Coex %':>6} | {'Within Var':>10}")
    print("-" * 30)

    for n in test_n:
        coex_results = [run_test(s, n, prob) for s in seeds]
        coex_pct = sum(coex_results) / len(seeds) * 100
        var = np.var(coex_results)

        all_coex.append(coex_pct)
        within_n_var.append(var)

        print(f"{n:>3} | {coex_pct:>5.0f}% | {var:>10.3f}")

    # Analysis
    print("\n" + "=" * 80)
    print("VARIANCE ANALYSIS")
    print("=" * 80)

    # Across-N variance
    across_var = np.var(all_coex)
    print(f"\nAcross-N variance: {across_var:.1f}")
    print(f"(Variance in coexistence % across different N values)")

    # Average within-N variance
    avg_within = np.mean(within_n_var)
    print(f"\nAverage within-N variance: {avg_within:.3f}")
    print(f"(Average variance due to random seed at fixed N)")

    # Ratio
    if avg_within > 0:
        ratio = across_var / (avg_within * 100)  # Scale appropriately
        print(f"\nStructural effect / Seed effect: {ratio:.1f}x")

    # Signal to noise
    print("\n" + "=" * 80)
    print("SIGNAL TO NOISE RATIO")
    print("=" * 80)

    # Calculate effect sizes
    max_coex = max(all_coex)
    min_coex = min(all_coex)
    range_coex = max_coex - min_coex
    avg_std = np.sqrt(avg_within) * 100  # Convert to %

    print(f"\nStructural range: {min_coex:.0f}% - {max_coex:.0f}% ({range_coex:.0f}%)")
    print(f"Seed noise (avg std): {avg_std:.1f}%")

    snr = range_coex / avg_std if avg_std > 0 else float('inf')
    print(f"Signal/Noise ratio: {snr:.1f}")

    if snr > 3:
        print("""
CONCLUSION: High signal-to-noise ratio

Structural N effects dominate over random seed variance.
Statistical significance is reliable with 20+ seeds.
""")
    else:
        print("""
CONCLUSION: Low signal-to-noise ratio

Random seed variance is significant relative to N effects.
Need more seeds (50+) for reliable statistics.
""")

if __name__ == "__main__":
    main()
