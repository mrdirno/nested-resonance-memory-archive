#!/usr/bin/env python3
"""
CYCLE 1921: DEPTH DEPENDENCE ANALYSIS

Test how N_DEPTHS affects Nc at optimal reproduction probability.
C1918-C1920 established p ~0.17 as optimal.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 500
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

# OPTIMAL PARAMETERS
DECOMP_THRESH = 0.8
COMP_THRESH = 0.99
RECHARGE_BASE = 0.2
REPRO_PROB = 0.17  # Optimal from C1918-C1920

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

def run_with_depth(seed, n_initial, n_depths):
    """Run with variable depth."""
    reality = RealityInterface(n_populations=n_depths, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(n_depths)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(n_depths):
            for agent in pops[d]:
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_PROB:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(n_depths - 1):
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

        for d in range(1, n_depths):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESH:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(n_depths):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [len(reality.get_population_agents(d)) for d in range(n_depths)]
    return final_pops[0] > 0 and final_pops[1] > 0

def find_nc(n_depths, seeds):
    """Find critical N for given depth."""
    n_range = range(3, 15)
    results = {}

    for n in n_range:
        coex = np.mean([run_with_depth(s, n, n_depths) for s in seeds]) * 100
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
    print(f"CYCLE 1921: Depth Dependence | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"Testing Nc vs N_DEPTHS at p = {REPRO_PROB}")
    print("=" * 80)

    seeds = list(range(1921001, 1921031))  # 30 seeds

    # Test different depths
    depths = [3, 4, 5, 6, 7]

    print(f"\n{'N_DEPTHS':>10} | {'Nc':>6}")
    print("-" * 22)

    nc_results = {}
    for d in depths:
        nc, _ = find_nc(d, seeds)
        nc_results[d] = nc
        print(f"{d:>10} | {nc:>6.2f}")

    # Analysis
    print("\n" + "=" * 80)
    print("REGRESSION ANALYSIS")
    print("=" * 80)

    depth_vals = list(nc_results.keys())
    nc_vals = list(nc_results.values())

    # Linear fit
    slope, intercept = np.polyfit(depth_vals, nc_vals, 1)

    print(f"\nLinear fit: Nc = {intercept:.2f} + {slope:.2f}*D")

    # R² calculation
    predicted = [intercept + slope * d for d in depth_vals]
    ss_res = sum((nc - pred)**2 for nc, pred in zip(nc_vals, predicted))
    ss_tot = sum((nc - np.mean(nc_vals))**2 for nc in nc_vals)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    print(f"R²: {r_squared:.3f}")

    # Characterize relationship
    if slope > 0.1:
        relationship = "Positive: deeper hierarchies → higher Nc"
    elif slope < -0.1:
        relationship = "Negative: deeper hierarchies → lower Nc"
    else:
        relationship = "Flat: depth has minimal effect on Nc"

    print(f"""
CONCLUSION:

Depth dependence analysis reveals:

1. Relationship: {relationship}
2. Slope: {slope:+.3f} Nc per depth level
3. R² = {r_squared:.3f}

Physical interpretation:
- More depth levels → {'more composition pathways' if slope > 0 else 'more cascade stabilization' if slope < 0 else 'balanced dynamics'}
- Nc varies from {min(nc_vals):.1f} (D={depth_vals[nc_vals.index(min(nc_vals))]}) to {max(nc_vals):.1f} (D={depth_vals[nc_vals.index(max(nc_vals))]})

Session status: 258 cycles completed (C1664-C1921).
""")

if __name__ == "__main__":
    main()
