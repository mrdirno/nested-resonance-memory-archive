#!/usr/bin/env python3
"""
CYCLE 1911: SEED SENSITIVITY ANALYSIS

Why did C1904-C1907 show dramatic energy effects but C1909-C1910 show marginal effects?
Test multiple seed ranges to understand variability.
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

def run_coexistence(seed, n_initial, repro_prob, init_energy):
    """Standard coexistence test."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, init_energy, depth=0), 0)

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
    return 1 if final_pops[0] > 0 and final_pops[1] > 0 else 0

def main():
    print(f"CYCLE 1911: Seed Sensitivity | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing multiple seed ranges for N=14 with E=0.5 and E=1.0")
    print("=" * 80)

    prob = 0.10
    n = 14

    # Test different seed ranges
    seed_ranges = [
        ("C1904", list(range(1904001, 1904031))),
        ("C1905", list(range(1905001, 1905031))),
        ("C1906", list(range(1906001, 1906031))),
        ("C1907", list(range(1907001, 1907031))),
        ("C1910", list(range(1910001, 1910031))),
        ("C1911", list(range(1911001, 1911031))),
        ("Random1", list(range(1, 31))),
        ("Random2", list(range(42001, 42031))),
    ]

    print(f"\n{'Range':>10} | {'E=0.5':>6} | {'E=1.0':>6} | {'Effect':>10}")
    print("-" * 45)

    for name, seeds in seed_ranges:
        coex_05 = np.mean([run_coexistence(s, n, prob, 0.5) for s in seeds]) * 100
        coex_10 = np.mean([run_coexistence(s, n, prob, 1.0) for s in seeds]) * 100
        diff = coex_05 - coex_10
        effect = "HELPS" if diff > 10 else "HURTS" if diff < -10 else "~NEUTRAL"
        print(f"{name:>10} | {coex_05:>5.0f}% | {coex_10:>5.0f}% | {effect:>10} ({diff:+.0f}%)")

    # Statistical summary
    print("\n" + "=" * 80)
    print("STATISTICAL SUMMARY")
    print("=" * 80)

    # Pool all seeds
    all_seeds = []
    for _, seeds in seed_ranges:
        all_seeds.extend(seeds)

    coex_all_05 = np.mean([run_coexistence(s, n, prob, 0.5) for s in all_seeds]) * 100
    coex_all_10 = np.mean([run_coexistence(s, n, prob, 1.0) for s in all_seeds]) * 100

    print(f"\nPooled (n={len(all_seeds)}):")
    print(f"  E=0.5: {coex_all_05:.1f}%")
    print(f"  E=1.0: {coex_all_10:.1f}%")
    print(f"  Effect: {coex_all_05 - coex_all_10:+.1f}%")

    print(f"""
INTERPRETATION:

If results vary dramatically by seed range:
→ Effect is sensitive to initial conditions
→ 30-seed samples too small for reliable estimates
→ Need 100+ seeds or theory-based explanation

If results are consistent across seed ranges:
→ Earlier dramatic effects were anomalies
→ True effect is the pooled estimate
""")

if __name__ == "__main__":
    main()
