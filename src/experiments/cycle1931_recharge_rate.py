#!/usr/bin/env python3
"""
CYCLE 1931: RECHARGE RATE STUDY

Test how recharge_base affects coexistence.
Current: recharge_base = 0.2. Test range 0.1-0.5.
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
REPRO_PROB = 0.17
N_INITIAL = 5  # Mid-range for sensitivity
COMP_THRESH = 0.99
DECOMP_THRESH = 1.7

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

def run_simulation(seed, recharge_base):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    for i in range(N_INITIAL):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)
    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge_base / (1 + d * 0.5), cap=2.0)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_PROB:
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
    print(f"CYCLE 1931: Recharge Rate Study | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"Testing recharge_base effect at N={N_INITIAL}")
    print("=" * 80)

    seeds = list(range(1931001, 1931051))  # 50 seeds
    recharge_values = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]

    print(f"\n{'recharge':>10} | {'Coex %':>7}")
    print("-" * 24)

    results = {}
    for rb in recharge_values:
        coex = np.mean([run_simulation(s, rb) for s in seeds]) * 100
        results[rb] = coex
        print(f"{rb:>10.2f} | {coex:>6.1f}%")

    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    best_rb = max(results, key=results.get)
    baseline = results[0.2]

    print(f"\nBaseline (0.2): {baseline:.1f}%")
    print(f"Best recharge: {best_rb} ({results[best_rb]:.1f}%)")

    # Characterize trend
    low_avg = np.mean([results[rb] for rb in [0.1, 0.15]])
    high_avg = np.mean([results[rb] for rb in [0.4, 0.5]])

    print(f"""
RECHARGE RATE EFFECT:

1. Low recharge (0.1-0.15): {low_avg:.1f}%
2. Baseline (0.2): {baseline:.1f}%
3. High recharge (0.4-0.5): {high_avg:.1f}%

Physical interpretation:
- Low recharge: Slow energy gain → less reproduction → low coexistence
- High recharge: Fast energy gain → rapid composition → {'stability' if high_avg > baseline else 'instability'}

Optimal recharge_base: {best_rb}

Session status: 268 cycles completed (C1664-C1931).
""")

if __name__ == "__main__":
    main()
