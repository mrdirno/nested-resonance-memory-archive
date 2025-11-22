#!/usr/bin/env python3
"""
CYCLE 1920: FINE-GRAIN OPTIMAL P SCAN

Pinpoint exact p value that minimizes Nc.
C1919 showed minimum around p ~0.15-0.20.
Test p = 0.12, 0.14, 0.16, 0.18, 0.20, 0.22 with higher resolution.
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

# OPTIMAL PARAMETERS
DECOMP_THRESH = 0.8
COMP_THRESH = 0.99
RECHARGE_BASE = 0.2

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

def run_optimal(seed, n_initial, repro_prob):
    """Run with optimal parameters."""
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
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)

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
                if sim >= COMP_THRESH:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESH:
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
    return final_pops[0] > 0 and final_pops[1] > 0

def find_nc(prob, seeds):
    """Find critical N for given probability."""
    n_range = range(3, 15)
    results = {}

    for n in n_range:
        coex = np.mean([run_optimal(s, n, prob) for s in seeds]) * 100
        results[n] = coex

    # Find 50% crossing
    for n in range(3, 14):
        if results[n] < 50 and results[n+1] >= 50:
            nc = n + (50 - results[n]) / (results[n+1] - results[n])
            return nc, results

    # If all above or below
    if all(r >= 50 for r in results.values()):
        return 3.0, results
    elif all(r < 50 for r in results.values()):
        return 15.0, results

    return None, results

def main():
    print(f"CYCLE 1920: Fine-grain Optimal P | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Pinpointing minimum Nc around p ~0.15-0.20")
    print("=" * 80)

    seeds = list(range(1920001, 1920051))  # 50 seeds for higher precision

    # Fine-grain probabilities around optimal
    probs = [0.12, 0.14, 0.16, 0.18, 0.20, 0.22]

    print(f"\n{'p':>6} | {'Nc':>6}")
    print("-" * 18)

    nc_results = {}
    for p in probs:
        nc, _ = find_nc(p, seeds)
        nc_results[p] = nc
        print(f"{p:>6.2f} | {nc:>6.2f}")

    # Find minimum
    min_p = min(nc_results, key=nc_results.get)
    min_nc = nc_results[min_p]

    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    # Quadratic fit to find exact minimum
    p_vals = list(nc_results.keys())
    nc_vals = list(nc_results.values())

    coeffs = np.polyfit(p_vals, nc_vals, 2)
    a, b, c = coeffs

    # Vertex of parabola: p_opt = -b/(2a)
    p_optimal = -b / (2 * a) if a != 0 else 0.17
    nc_optimal = a * p_optimal**2 + b * p_optimal + c

    print(f"\nQuadratic fit: Nc = {a:.2f}p² + {b:.2f}p + {c:.2f}")
    print(f"\nOptimal p (vertex): {p_optimal:.3f}")
    print(f"Predicted Nc at optimal: {nc_optimal:.2f}")
    print(f"\nMeasured minimum: p = {min_p:.2f}, Nc = {min_nc:.2f}")

    # R² calculation
    pred = [a*p**2 + b*p + c for p in p_vals]
    ss_res = sum((nc - pr)**2 for nc, pr in zip(nc_vals, pred))
    ss_tot = sum((nc - np.mean(nc_vals))**2 for nc in nc_vals)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    print(f"R² = {r_squared:.3f}")

    # Compare with C1919
    print("\n" + "=" * 80)
    print("COMPARISON WITH C1919")
    print("=" * 80)
    print("\nC1919 quadratic: Nc = 28.88p² - 8.95p + 4.83")
    print("C1919 predicted minimum: p ~0.155")
    print(f"\nC1920 quadratic: Nc = {a:.2f}p² + {b:.2f}p + {c:.2f}")
    print(f"C1920 predicted minimum: p = {p_optimal:.3f}")

    print(f"""
CONCLUSION:

Fine-grain scan confirms optimal reproduction probability:

1. Optimal p = {p_optimal:.3f} (minimizes Nc)
2. Minimum Nc = {nc_optimal:.2f}
3. R² = {r_squared:.3f}

Physical interpretation:
- p < {p_optimal:.2f}: Insufficient reproduction → higher Nc needed
- p > {p_optimal:.2f}: Population explosion → cascade exhaustion → higher Nc needed
- p = {p_optimal:.2f}: Sweet spot for D0-D1 coexistence

Session status: 257 cycles completed (C1664-C1920).
""")

if __name__ == "__main__":
    main()
