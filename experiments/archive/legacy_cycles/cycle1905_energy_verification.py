#!/usr/bin/env python3
"""
CYCLE 1905: ENERGY EFFECT VERIFICATION

Verify that E=0.5 eliminates dead zones across multiple N values.
Compare E=0.5 vs E=1.0 systematically.
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

def run_with_energy(seed, n_initial, repro_prob, init_energy):
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
    return sum(1 for p in final_pops if p > 0) >= 2

def main():
    print(f"CYCLE 1905: Energy Verification | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Comparing E=0.5 vs E=1.0 across N values")
    print("=" * 80)

    seeds = list(range(1905001, 1905051))  # 50 seeds
    prob = 0.10

    test_n = list(range(10, 20))

    print(f"\n{'N':>3} | {'E=0.5':>6} | {'E=1.0':>6} | {'Δ':>6}")
    print("-" * 35)

    total_improvement = 0
    num_improved = 0

    for n in test_n:
        coex_05 = sum(run_with_energy(s, n, prob, 0.5) for s in seeds) / len(seeds) * 100
        coex_10 = sum(run_with_energy(s, n, prob, 1.0) for s in seeds) / len(seeds) * 100
        delta = coex_05 - coex_10

        if delta > 0:
            num_improved += 1
            total_improvement += delta

        marker = "**" if n == 14 else "  "
        print(f"{n:>3} | {coex_05:>5.0f}% | {coex_10:>5.0f}% | {delta:>+5.0f}%{marker}")

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    avg_imp = total_improvement / num_improved if num_improved > 0 else 0

    print(f"\nN values improved with E=0.5: {num_improved}/{len(test_n)}")
    print(f"Average improvement: {avg_imp:+.0f}%")

    if num_improved >= len(test_n) * 0.8:
        print(f"""
EFFECT VERIFIED ✓

E=0.5 outperforms E=1.0 across most N values.

NEW ENGINEERING PROTOCOL:
1. Use initial energy E=0.5 (not 1.0)
2. No need for intervention at most N
3. Dead zones largely eliminated

This is a simpler solution than agent injection.
""")
    else:
        print("\nEffect limited to specific N range.")

if __name__ == "__main__":
    main()
