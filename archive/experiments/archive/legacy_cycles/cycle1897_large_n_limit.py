#!/usr/bin/env python3
"""
CYCLE 1897: LARGE N BEHAVIOR

What happens at very large N?
- Does the system always coexist?
- Are there N-independent failure modes?
- Is there a mean-field limit?
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

def main():
    print(f"CYCLE 1897: Large N Behavior | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Exploring behavior at large N values")
    print("=" * 80)

    seeds = list(range(1897001, 1897031))  # 30 seeds
    prob = 0.10
    lam = 16 - 13 * prob

    # Test large N values
    # Note: λ₃ ≈ 44, λ₄ ≈ 59
    test_n = [20, 30, 40, 50, 60, 70, 80, 90, 100]

    print(f"\n{'N':>4} | {'Coex':>5} | {'Note':>20}")
    print("-" * 40)

    results = []

    for n in test_n:
        coex = sum(run_test(s, n, prob) for s in seeds) / len(seeds) * 100

        # Note harmonics
        k = n / lam
        if abs(k - round(k)) < 0.1:
            note = f"≈ λ_{int(round(k))}"
        else:
            note = ""

        results.append((n, coex))
        print(f"{n:>4} | {coex:>4.0f}% | {note:>20}")

    # Analysis
    print("\n" + "=" * 80)
    print("LARGE N ANALYSIS")
    print("=" * 80)

    # Check for asymptotic behavior
    high_n_coex = [c for n, c in results if n >= 60]
    avg_high = np.mean(high_n_coex)
    std_high = np.std(high_n_coex)

    print(f"\nHigh N (≥60) statistics:")
    print(f"  Mean coexistence: {avg_high:.1f}%")
    print(f"  Std deviation: {std_high:.1f}%")

    if avg_high > 95:
        print(f"""
MEAN-FIELD BEHAVIOR:

At large N (≥60), system approaches mean-field limit:
  - Coexistence → 100%
  - Higher harmonics (k≥4) barely visible
  - System becomes deterministic

This confirms the theoretical prediction:
  - For N >> λ, system always coexists
  - Finite-size effects dominate at small N
""")
    elif std_high < 10 and avg_high > 80:
        print(f"""
QUASI-DETERMINISTIC REGIME:

At large N (≥60), system shows stable behavior:
  - Coexistence ≈ {avg_high:.0f}% ± {std_high:.0f}%
  - Harmonic effects present but weak
  - Near mean-field limit
""")
    else:
        print(f"\nComplex behavior persists at large N.")
        print("Higher harmonics still significant.")

if __name__ == "__main__":
    main()
