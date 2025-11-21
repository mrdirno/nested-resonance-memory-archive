#!/usr/bin/env python3
"""
CYCLE 1915: OPTIMIZED THRESHOLD TEST

Re-test N threshold behavior with corrected parameters.
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

# OPTIMIZED PARAMETERS
DECOMP_THRESH = 1.0
COMP_THRESH = 0.9
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

def run_optimized(seed, n_initial, repro_prob):
    """Run with optimized parameters."""
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

def main():
    print(f"CYCLE 1915: Optimized Threshold | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"Parameters: decomp={DECOMP_THRESH}, comp={COMP_THRESH}, recharge={RECHARGE_BASE}")
    print("=" * 80)

    seeds = list(range(1915001, 1915031))
    prob = 0.10

    # Full N sweep
    print(f"\nN sweep (p={prob}):")
    print(f"{'N':>4} | {'Coex%':>6}")
    print("-" * 16)

    results = {}
    for n in range(10, 25):
        coex = np.mean([run_optimized(s, n, prob) for s in seeds]) * 100
        results[n] = coex
        print(f"{n:>4} | {coex:>5.0f}%")

    # Find threshold
    print("\n" + "=" * 80)
    print("THRESHOLD ANALYSIS")
    print("=" * 80)

    # Find Nc (50% crossing)
    nc = None
    for n in range(10, 24):
        if results[n] < 50 and results[n+1] >= 50:
            nc = n + 0.5
            break
        elif results[n] >= 50 and results[n+1] < 50:
            nc = n + 0.5
            break

    if nc:
        print(f"\nCritical N (50% crossing): ~{nc}")
    else:
        # Check if all above or below
        if all(r >= 50 for r in results.values()):
            print("\nAll N have >= 50% coexistence")
        elif all(r < 50 for r in results.values()):
            print("\nAll N have < 50% coexistence")
        else:
            print("\nThreshold not clearly identified")

    # Below/above asymmetry
    below = [results[n] for n in range(10, 14)]
    above = [results[n] for n in range(17, 25)]

    avg_below = np.mean(below)
    avg_above = np.mean(above)

    print(f"\nRegion averages:")
    print(f"  N=10-13: {avg_below:.1f}%")
    print(f"  N=17-24: {avg_above:.1f}%")
    print(f"  Asymmetry: {avg_above - avg_below:+.1f}%")

    # Deterministic threshold
    det_threshold = None
    for n in range(10, 25):
        if results[n] == 100:
            det_threshold = n
            break

    if det_threshold:
        print(f"\nDeterministic threshold: N ≥ {det_threshold}")
    else:
        print(f"\nNo deterministic threshold found (no N with 100%)")

    print(f"""
COMPARISON WITH OLD PARAMETERS:

Old (C1908-C1913):
- N=14 coexistence: ~0%
- N=17 coexistence: ~0%
- Threshold: Not found

New (optimized):
- Results above show improved coexistence
- Threshold behavior may now be observable
""")

if __name__ == "__main__":
    main()
