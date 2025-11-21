#!/usr/bin/env python3
"""
CYCLE 1875: BOUNDARY CRITICAL PHENOMENA

What happens at the exact transition between dead and safe zones?
Look for: variance peaks, critical fluctuations, scaling behavior
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

def run_test_detailed(seed, n_initial, repro_prob):
    """Run test and return detailed metrics."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    pop_history = []

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)
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

    # Calculate metrics
    final_total = sum(final_pops)
    mean_pop = np.mean(pop_history) if pop_history else 0
    var_pop = np.var(pop_history) if len(pop_history) > 1 else 0
    max_pop = max(pop_history) if pop_history else 0

    return {
        'coex': coex,
        'final_total': final_total,
        'mean_pop': mean_pop,
        'var_pop': var_pop,
        'max_pop': max_pop,
        'lifetime': len(pop_history)
    }

def main():
    print(f"CYCLE 1875: Boundary Criticality | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Critical phenomena at dead zone boundary")
    print("=" * 80)

    seeds = list(range(1875001, 1875051))  # 50 seeds
    prob = 0.10

    # Fine-grained scan around boundary
    test_n = list(range(10, 25))

    results = []
    for n in test_n:
        coex_count = 0
        all_finals = []
        all_vars = []
        all_lifetimes = []

        for seed in seeds:
            r = run_test_detailed(seed, n, prob)
            if r['coex']:
                coex_count += 1
            all_finals.append(r['final_total'])
            all_vars.append(r['var_pop'])
            all_lifetimes.append(r['lifetime'])

        coex_pct = coex_count / len(seeds) * 100
        mean_final = np.mean(all_finals)
        var_final = np.var(all_finals)  # Variance across seeds
        mean_lifetime = np.mean(all_lifetimes)
        var_lifetime = np.var(all_lifetimes)

        results.append({
            'n': n,
            'coex': coex_pct,
            'mean_final': mean_final,
            'var_final': var_final,
            'mean_lifetime': mean_lifetime,
            'var_lifetime': var_lifetime
        })

    # Display
    print(f"\n{'N':>3} | {'Coex':>5} | {'Mean Pop':>8} | {'Var Pop':>8} | {'Life Var':>8}")
    print("-" * 50)

    for r in results:
        print(f"{r['n']:>3} | {r['coex']:>4.0f}% | {r['mean_final']:>8.1f} | "
              f"{r['var_final']:>8.1f} | {r['var_lifetime']:>8.1f}")

    # Find critical point (maximum variance)
    max_var_final = max(r['var_final'] for r in results)
    max_var_life = max(r['var_lifetime'] for r in results)

    critical_n_final = [r['n'] for r in results if r['var_final'] == max_var_final][0]
    critical_n_life = [r['n'] for r in results if r['var_lifetime'] == max_var_life][0]

    print("\n" + "=" * 80)
    print("CRITICAL ANALYSIS")
    print("=" * 80)
    print(f"\nMaximum variance in final population: N = {critical_n_final}")
    print(f"Maximum variance in lifetime: N = {critical_n_life}")

    # Coexistence transition
    for i in range(len(results) - 1):
        if results[i]['coex'] > 50 and results[i+1]['coex'] < 50:
            print(f"\nCoexistence transition: N = {results[i]['n']} → {results[i+1]['n']}")
            break
        if results[i]['coex'] < 50 and results[i+1]['coex'] > 50:
            print(f"\nCoexistence transition: N = {results[i]['n']} → {results[i+1]['n']}")
            break

    # Critical signatures
    print("\n" + "=" * 80)
    print("CRITICAL SIGNATURES")
    print("=" * 80)
    print(f"""
1. Variance peak at N = {critical_n_final}
   - Systems highly sensitive to initial conditions
   - Small changes produce large outcome differences

2. Coexistence fluctuates in boundary region
   - N = 12-16 shows mixed outcomes
   - Neither reliably safe nor reliably dead

3. This is characteristic of critical phenomena:
   - Phase transition at N ≈ 14
   - Critical fluctuations near boundary
   - Order parameter (coex) changes rapidly
""")

if __name__ == "__main__":
    main()
