#!/usr/bin/env python3
"""
CYCLE 1697: ENERGY VARIANCE ANALYSIS
Why does n=25 create optimal energy distribution?
Track energy variance at different N.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1697"
CYCLES = 1000  # First 1000 cycles
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

def run_variance_analysis(seed, n_initial=25):
    """Track energy variance over time."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track variance
    d0_var_history = []
    d0_mean_history = []
    d0_pop_history = []

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Record D0 energy statistics
        d0_agents = pops[0]
        if len(d0_agents) > 1:
            energies = [a.energy for a in d0_agents]
            d0_var = np.var(energies)
            d0_mean = np.mean(energies)
        else:
            d0_var = 0
            d0_mean = d0_agents[0].energy if d0_agents else 0

        if cycle % 10 == 0:  # Sample every 10 cycles
            d0_var_history.append(d0_var)
            d0_mean_history.append(d0_mean)
            d0_pop_history.append(len(d0_agents))

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= RESONANCE_THRESHOLD:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    # Compute early-phase variance (first 10 samples = cycles 0-90)
    early_var = np.mean(d0_var_history[:10]) if len(d0_var_history) >= 10 else 0
    early_mean = np.mean(d0_mean_history[:10]) if len(d0_mean_history) >= 10 else 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "early_var": float(early_var),
        "early_mean": float(early_mean),
        "var_history": d0_var_history[:20]
    }

def main():
    print(f"CYCLE 1697: Energy Variance | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Why does n=25 create optimal energy distribution?")
    print("=" * 70)

    seeds = list(range(1697001, 1697021))  # 20 seeds

    population_sizes = [15, 20, 25, 30, 35, 50]
    all_results = []

    for n_init in population_sizes:
        results = [run_variance_analysis(seed, n_init) for seed in seeds]
        avg_var = np.mean([r["early_var"] for r in results])
        avg_mean = np.mean([r["early_mean"] for r in results])
        print(f"\nn={n_init}: early_var={avg_var:.4f}, early_mean={avg_mean:.2f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("ENERGY VARIANCE BY POPULATION SIZE")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Early Var':>12} | {'Early Mean':>12}")
    print("-" * 35)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_var = np.mean([r["early_var"] for r in subset])
        avg_mean = np.mean([r["early_mean"] for r in subset])
        print(f"{n_init:4d} | {avg_var:12.4f} | {avg_mean:12.2f}")

    # Correlation with success
    print("\n" + "=" * 70)
    print("VARIANCE-SUCCESS CORRELATION")
    print("=" * 70)

    # Known success rates from C1680
    success_rates = {15: 32, 20: 56, 25: 96, 30: 38, 35: 52, 50: 66}

    print(f"\n{'N':>4} | {'Variance':>10} | {'Success':>8}")
    print("-" * 30)
    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_var = np.mean([r["early_var"] for r in subset])
        success = success_rates.get(n_init, 0)
        print(f"{n_init:4d} | {avg_var:10.4f} | {success:7d}%")

if __name__ == "__main__":
    main()
