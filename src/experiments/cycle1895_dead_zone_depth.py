#!/usr/bin/env python3
"""
CYCLE 1895: DEAD ZONE DEPTH HARMONIC DECAY

Characterize harmonic weakening by dead zone depth (minimum coexistence).
This may be more robust than scaling exponents.
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
    return sum(1 for p in final_pops if p > 0) >= 2

def find_minimum(prob, seeds, nc, scan_range=5):
    """Find minimum coexistence near critical point."""
    test_range = range(nc - scan_range, nc + scan_range + 1)
    min_coex = 100
    min_n = nc

    for n in test_range:
        coex = sum(run_test(s, n, prob) for s in seeds) / len(seeds) * 100
        if coex < min_coex:
            min_coex = coex
            min_n = n

    return min_n, min_coex

def main():
    print(f"CYCLE 1895: Dead Zone Depth | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Measuring harmonic weakening by minimum coexistence")
    print("=" * 80)

    seeds = list(range(1895001, 1895051))  # 50 seeds
    prob = 0.10
    lam = 16 - 13 * prob

    harmonics = [1, 2, 3]

    print(f"\n{'k':>3} | {'Nc':>4} | {'N_min':>5} | {'Min Coex':>8} | {'Depth':>6}")
    print("-" * 45)

    depths = []
    k_vals = []

    for k in harmonics:
        nc = int(round(k * lam))

        # Find minimum
        min_n, min_coex = find_minimum(prob, seeds, nc)

        # Depth = 100 - minimum coex (how far down the well goes)
        depth = 100 - min_coex
        depths.append(depth)
        k_vals.append(k)

        print(f"{k:>3} | {nc:>4} | {min_n:>5} | {min_coex:>7.0f}% | {depth:>5.0f}%")

    # Analysis
    print("\n" + "=" * 80)
    print("HARMONIC DECAY ANALYSIS")
    print("=" * 80)

    # Fit decay: depth(k) = depth(1) × k^(-γ)
    if len(depths) >= 2:
        ln_k = [math.log(k) for k in k_vals]
        ln_d = [math.log(d) if d > 0 else 0 for d in depths]

        slope, intercept = np.polyfit(ln_k, ln_d, 1)
        gamma = -slope
        depth_1 = math.exp(intercept)

        print(f"\nPower law fit: depth(k) = {depth_1:.1f} × k^(-{gamma:.2f})")

        print(f"\n{'k':>3} | {'Measured':>8} | {'Predicted':>9}")
        print("-" * 30)
        for k, d in zip(k_vals, depths):
            pred = depth_1 * k**(-gamma)
            print(f"{k:>3} | {d:>7.0f}% | {pred:>8.0f}%")

        print(f"""
HARMONIC WEAKENING LAW:

depth(k) = {depth_1:.0f}% × k^(-{gamma:.1f})

This means:
  k=1: depth = {depth_1:.0f}% (severe)
  k=2: depth = {depth_1 * 2**(-gamma):.0f}% (moderate)
  k=3: depth = {depth_1 * 3**(-gamma):.0f}% (mild)

Higher harmonics have progressively shallower dead zones.
Decay exponent γ = {gamma:.2f}
""")

if __name__ == "__main__":
    main()
