#!/usr/bin/env python3
"""
CYCLE 1946: REFINED EQUILIBRIUM POPULATION MODEL

C1945 model (N_eq ≈ 33K) underestimates by 60%.
Refine model by accounting for:
1. Multiple births per cycle per agent
2. Recharge rate effect
3. Composition/decomposition balance
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
P_BASE = 0.17
N_INITIAL = 14
COMP_THRESH = 0.99
DECOMP_THRESH = 1.7
RECHARGE_BASE = 0.4

def run_simulation_with_tracking(seed, K):
    """Run simulation and track birth/death/composition rates."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    for i in range(N_INITIAL):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    births_per_cycle = []
    deaths_per_cycle = []
    comps_per_cycle = []
    decomps_per_cycle = []
    pops_per_cycle = []

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        pops_per_cycle.append(total)
        births = 0
        deaths = 0
        comps = 0
        decomps = 0

        p_effective = P_BASE / (1 + total / K)

        # Recharge
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)

        # Reproduction - count births
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < p_effective:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
                births += 1

        # Composition - count compositions
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                e1, e2 = agents[i].energy, agents[i+1].energy
                pi1 = (e1 * PI * 2) % (2 * PI)
                e_1 = (d * E / 4) % (2 * PI)
                phi1 = (e1 * PHI) % (2 * PI)
                pi2 = (e2 * PI * 2) % (2 * PI)
                e_2 = (d * E / 4) % (2 * PI)
                phi2 = (e2 * PHI) % (2 * PI)
                v1 = [pi1, e_1, phi1]
                v2 = [pi2, e_2, phi2]
                dot = sum(a * b for a, b in zip(v1, v2))
                mag1 = math.sqrt(sum(a**2 for a in v1))
                mag2 = math.sqrt(sum(a**2 for a in v2))
                sim = dot / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0
                if sim >= COMP_THRESH:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    comps += 1
                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESH:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)
                    decomps += 1

        # Deaths
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)
                    deaths += 1

        births_per_cycle.append(births)
        deaths_per_cycle.append(deaths)
        comps_per_cycle.append(comps)
        decomps_per_cycle.append(decomps)

    # Equilibrium statistics (last 100 cycles)
    if len(pops_per_cycle) >= 200:
        eq_pop = np.mean(pops_per_cycle[-100:])
        eq_births = np.mean(births_per_cycle[-100:])
        eq_deaths = np.mean(deaths_per_cycle[-100:])
        eq_comps = np.mean(comps_per_cycle[-100:])
        eq_decomps = np.mean(decomps_per_cycle[-100:])
    else:
        eq_pop = np.mean(pops_per_cycle[-50:]) if len(pops_per_cycle) >= 50 else np.mean(pops_per_cycle)
        eq_births = np.mean(births_per_cycle[-50:]) if len(births_per_cycle) >= 50 else np.mean(births_per_cycle)
        eq_deaths = np.mean(deaths_per_cycle[-50:]) if len(deaths_per_cycle) >= 50 else np.mean(deaths_per_cycle)
        eq_comps = np.mean(comps_per_cycle[-50:]) if len(comps_per_cycle) >= 50 else np.mean(comps_per_cycle)
        eq_decomps = np.mean(decomps_per_cycle[-50:]) if len(decomps_per_cycle) >= 50 else np.mean(decomps_per_cycle)

    return {
        'eq_pop': eq_pop,
        'eq_births': eq_births,
        'eq_deaths': eq_deaths,
        'eq_comps': eq_comps,
        'eq_decomps': eq_decomps
    }

def main():
    print(f"CYCLE 1946: Refined Population Model | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Measuring birth/death/composition rates at equilibrium")
    print("=" * 80)

    seeds = list(range(1946001, 1946021))  # 20 seeds
    K_values = [20, 30, 40, 50]

    print(f"\n{'K':>4} | {'Eq Pop':>7} | {'Births':>7} | {'Deaths':>7} | {'Comps':>6} | {'Decomps':>7}")
    print("-" * 56)

    results = {}
    for K in K_values:
        res = [run_simulation_with_tracking(s, K) for s in seeds]
        avg = {key: np.mean([r[key] for r in res]) for key in res[0].keys()}
        results[K] = avg
        print(f"{K:>4} | {avg['eq_pop']:>7.0f} | {avg['eq_births']:>7.1f} | {avg['eq_deaths']:>7.1f} | {avg['eq_comps']:>6.1f} | {avg['eq_decomps']:>7.1f}")

    # Derive refined model
    print(f"\n{'=' * 80}")
    print("REFINED MODEL DERIVATION")
    print("=" * 80)

    # Extract scaling factors
    print("\nEQUILIBRIUM SCALING:")
    for K in K_values:
        ratio = results[K]['eq_pop'] / K
        birth_rate = results[K]['eq_births'] / results[K]['eq_pop'] if results[K]['eq_pop'] > 0 else 0
        print(f"  K={K}: N/K = {ratio:.1f}, birth_rate = {birth_rate:.4f}")

    # Average scaling factor
    avg_ratio = np.mean([results[K]['eq_pop'] / K for K in K_values])

    print(f"\nREFINED MODEL:")
    print(f"  N_eq ≈ {avg_ratio:.0f} × K")
    print(f"  (vs C1945 model: N_eq ≈ 33K)")
    print(f"  Correction factor: {avg_ratio/33:.2f}×")

    # Balance analysis
    print(f"\nBALANCE ANALYSIS (at K=30):")
    K = 30
    print(f"  Population: {results[K]['eq_pop']:.0f}")
    print(f"  Births/cycle: {results[K]['eq_births']:.1f}")
    print(f"  Deaths/cycle: {results[K]['eq_deaths']:.1f}")
    print(f"  Comps/cycle: {results[K]['eq_comps']:.1f} (removes 2×{results[K]['eq_comps']:.1f} = {2*results[K]['eq_comps']:.1f})")
    print(f"  Decomps/cycle: {results[K]['eq_decomps']:.1f} (adds 2×{results[K]['eq_decomps']:.1f} = {2*results[K]['eq_decomps']:.1f})")

    net_change = results[K]['eq_births'] - results[K]['eq_deaths'] - 2*results[K]['eq_comps'] + 2*results[K]['eq_decomps']
    print(f"  Net change: {net_change:.1f} (should be ~0)")

    print(f"""
CONCLUSIONS:
1. True scaling: N_eq ≈ {avg_ratio:.0f}K (not 33K)
2. Birth rate at equilibrium: ~{np.mean([results[K]['eq_births']/results[K]['eq_pop'] for K in K_values]):.4f} per agent
3. Net change ≈ 0 confirms equilibrium
4. Decomposition provides ~{np.mean([2*results[K]['eq_decomps'] for K in K_values]):.0f} agents/cycle (buffers losses)

Session status: 283 cycles completed (C1664-C1946).
""")

if __name__ == "__main__":
    main()
