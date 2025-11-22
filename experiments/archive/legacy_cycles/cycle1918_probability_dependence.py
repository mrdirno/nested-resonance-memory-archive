#!/usr/bin/env python3
"""
CYCLE 1918: PROBABILITY DEPENDENCE WITH OPTIMAL PARAMETERS

Test Nc dependence on reproduction probability p.
Does λ(p) = 16 - 13p still hold?
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
    # Scan N to find 50% crossing
    n_range = range(4, 20)
    results = {}

    for n in n_range:
        coex = np.mean([run_optimal(s, n, prob) for s in seeds]) * 100
        results[n] = coex

    # Find 50% crossing
    for n in range(4, 19):
        if results[n] < 50 and results[n+1] >= 50:
            nc = n + (50 - results[n]) / (results[n+1] - results[n])
            return nc, results

    # If all above or below
    if all(r >= 50 for r in results.values()):
        return 4.0, results  # All above
    elif all(r < 50 for r in results.values()):
        return 20.0, results  # All below

    return None, results

def main():
    print(f"CYCLE 1918: Probability Dependence | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing Nc dependence on p with optimal parameters")
    print("=" * 80)

    seeds = list(range(1918001, 1918031))  # 30 seeds

    # Test multiple probabilities
    probs = [0.05, 0.08, 0.10, 0.12, 0.15]

    print(f"\n{'p':>6} | {'Nc':>5} | {'λ(p)=16-13p':>10}")
    print("-" * 28)

    nc_results = {}
    for p in probs:
        nc, _ = find_nc(p, seeds)
        predicted = 16 - 13 * p
        nc_results[p] = nc
        print(f"{p:>6.2f} | {nc:>5.1f} | {predicted:>10.1f}")

    # Analysis
    print("\n" + "=" * 80)
    print("λ(p) ANALYSIS")
    print("=" * 80)

    # Fit linear model to Nc vs p
    p_vals = list(nc_results.keys())
    nc_vals = list(nc_results.values())

    slope, intercept = np.polyfit(p_vals, nc_vals, 1)

    print(f"\nLinear fit: Nc = {intercept:.1f} + {slope:.1f}p")
    print(f"Expected:   Nc = 16 - 13p")
    print(f"\nIntercept: {intercept:.1f} (expected 16)")
    print(f"Slope: {slope:.1f} (expected -13)")

    # R² calculation
    predicted_nc = [intercept + slope * p for p in p_vals]
    ss_res = sum((nc - pred)**2 for nc, pred in zip(nc_vals, predicted_nc))
    ss_tot = sum((nc - np.mean(nc_vals))**2 for nc in nc_vals)
    r_squared = 1 - ss_res / ss_tot

    print(f"R²: {r_squared:.3f}")

    print(f"""
CONCLUSION:

With optimal parameters, the λ(p) relationship {'HOLDS' if abs(slope + 13) < 3 else 'DIFFERS'}.

Measured: Nc = {intercept:.1f} {slope:+.1f}p
Expected: Nc = 16 - 13p

The {'' if abs(intercept - 16) < 3 else 'difference in '} intercept and
{'' if abs(slope + 13) < 3 else 'difference in '} slope suggest the
parameters affect the absolute scale but may preserve the p-dependence.
""")

if __name__ == "__main__":
    main()
