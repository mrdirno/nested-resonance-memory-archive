#!/usr/bin/env python3
"""
CYCLE 1881: SCALING ANALYSIS

Does NRM show statistical mechanics scaling behavior near the critical point?
Test: order parameter scaling, correlation length, susceptibility
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
    return 1 if sum(1 for p in final_pops if p > 0) >= 2 else 0

def main():
    print(f"CYCLE 1881: Scaling Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Does NRM show statistical mechanics scaling?")
    print("=" * 80)

    seeds = list(range(1881001, 1881101))  # 100 seeds
    prob = 0.10
    n_c = 14  # Critical point

    # Test scaling near critical point
    # In Ising model: m ~ |T - Tc|^β
    # Here: coex ~ |N - Nc|^β

    test_n = list(range(10, 19))
    results = []

    print(f"\n{'N':>3} | {'|N-Nc|':>6} | {'Coex':>5} | {'ln|N-Nc|':>9} | {'ln(Coex)':>9}")
    print("-" * 50)

    for n in test_n:
        coex = sum(run_test(s, n, prob) for s in seeds) / len(seeds)
        delta = abs(n - n_c)

        results.append({'n': n, 'delta': delta, 'coex': coex})

        if delta > 0 and coex > 0:
            ln_delta = np.log(delta)
            ln_coex = np.log(coex)
            print(f"{n:>3} | {delta:>6} | {coex:>5.2f} | {ln_delta:>9.3f} | {ln_coex:>9.3f}")
        else:
            print(f"{n:>3} | {delta:>6} | {coex:>5.2f} | {'N/A':>9} | {'N/A':>9}")

    # Fit scaling exponent
    print("\n" + "=" * 80)
    print("SCALING ANALYSIS")
    print("=" * 80)

    # Below critical (N < 14)
    below = [(r['delta'], r['coex']) for r in results if r['n'] < n_c and r['delta'] > 0]
    # Above critical (N > 14)
    above = [(r['delta'], r['coex']) for r in results if r['n'] > n_c and r['delta'] > 0]

    for label, data in [("Below Nc", below), ("Above Nc", above)]:
        if len(data) >= 2:
            ln_deltas = [np.log(d) for d, c in data if c > 0]
            ln_coex = [np.log(c) for d, c in data if c > 0]

            if len(ln_deltas) >= 2:
                # Linear regression for scaling exponent
                slope, intercept = np.polyfit(ln_deltas, ln_coex, 1)
                print(f"\n{label}:")
                print(f"  Scaling exponent β ≈ {slope:.2f}")
                print(f"  (coex ~ |N - Nc|^{slope:.2f})")

    # Susceptibility (variance)
    print("\n" + "=" * 80)
    print("SUSCEPTIBILITY (VARIANCE)")
    print("=" * 80)

    for n in [12, 13, 14, 15, 16]:
        results_n = [run_test(s, n, prob) for s in seeds]
        var = np.var(results_n)
        print(f"N = {n}: variance = {var:.3f}")

    # Conclusion
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print("""
Statistical mechanics analogy:

1. Order parameter: Coexistence probability
2. Control parameter: N (population size)
3. Critical point: Nc = 14

If scaling holds, the system belongs to a universality class
defined by the exponent β.
""")

if __name__ == "__main__":
    main()
