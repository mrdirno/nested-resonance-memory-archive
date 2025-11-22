#!/usr/bin/env python3
"""
CYCLE 1876: HIGHER HARMONIC CRITICALITY

Does the variance peak occur at λ₂=28 and λ₃=43 too?
Test: fine-grained scan around each harmonic
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

    pop_history = []

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        pop_history.append(total)

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
    coex = sum(1 for p in final_pops if p > 0) >= 2
    final_total = sum(final_pops)

    return {'coex': coex, 'final_total': final_total}

def main():
    print(f"CYCLE 1876: Higher Harmonic Criticality | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing variance peaks at λ₂=28 and λ₃=43")
    print("=" * 80)

    seeds = list(range(1876001, 1876041))  # 40 seeds
    prob = 0.10

    # Test around each harmonic
    harmonics = [
        (14, "λ₁", range(10, 19)),
        (28, "λ₂", range(24, 33)),
        (43, "λ₃", range(39, 48))
    ]

    all_results = []

    for center, label, n_range in harmonics:
        print(f"\n{'='*60}")
        print(f"{label} = {center}")
        print("=" * 60)
        print(f"{'N':>3} | {'Coex':>5} | {'Mean Pop':>8} | {'Variance':>8}")
        print("-" * 40)

        harmonic_results = []
        for n in n_range:
            finals = []
            coex_count = 0
            for seed in seeds:
                r = run_test(seed, n, prob)
                finals.append(r['final_total'])
                if r['coex']:
                    coex_count += 1

            coex_pct = coex_count / len(seeds) * 100
            mean_final = np.mean(finals)
            var_final = np.var(finals)

            harmonic_results.append({
                'n': n, 'coex': coex_pct, 'mean': mean_final, 'var': var_final
            })
            print(f"{n:>3} | {coex_pct:>4.0f}% | {mean_final:>8.1f} | {var_final:>8.1f}")

        # Find peak
        max_var = max(r['var'] for r in harmonic_results)
        peak_n = [r['n'] for r in harmonic_results if r['var'] == max_var][0]
        print(f"\nVariance peak at N = {peak_n}")

        all_results.append({
            'label': label,
            'center': center,
            'peak': peak_n,
            'results': harmonic_results
        })

    # Summary
    print("\n" + "=" * 80)
    print("CRITICAL SUMMARY")
    print("=" * 80)
    print(f"{'Harmonic':>8} | {'Expected':>8} | {'Variance Peak':>13}")
    print("-" * 35)

    for hr in all_results:
        print(f"{hr['label']:>8} | {hr['center']:>8} | {hr['peak']:>13}")

    # Analysis
    matches = sum(1 for hr in all_results if abs(hr['peak'] - hr['center']) <= 1)

    print(f"\nMatches: {matches}/3 peaks within ±1 of expected")

    if matches == 3:
        print("""
All harmonics show variance peaks near expected positions.
This confirms universal critical behavior across the harmonic series.
""")
    else:
        print("""
Not all harmonics show variance peaks at expected positions.
Higher harmonics may have different critical behavior.
""")

if __name__ == "__main__":
    main()
