#!/usr/bin/env python3
"""
CYCLE 1700: PHASE ALIGNMENT ANALYSIS
Why does n=25 produce lower mean creation energy?
Investigate phase resonance matching rates.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1700"
CYCLES = 50  # First 50 cycles
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
DECOMP_THRESHOLD = 1.3
RESONANCE_THRESHOLD = 0.5

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

def run_phase_analysis(seed, n_initial=25):
    """Track phase resonance matching."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track phase matching
    matched_resonances = []
    unmatched_resonances = []
    matched_energies = []

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Track resonance matching
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                combined_e = agents[i].energy + agents[i+1].energy

                if sim >= RESONANCE_THRESHOLD:
                    matched_resonances.append(sim)
                    new_e = combined_e * 0.85
                    if d == 0:
                        matched_energies.append((combined_e, new_e))
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    if d == 0:
                        unmatched_resonances.append(sim)
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

    # Compute statistics
    if matched_resonances:
        match_rate = len(matched_resonances) / (len(matched_resonances) + len(unmatched_resonances)) if unmatched_resonances else 1.0
        mean_matched = np.mean(matched_resonances)
        mean_combined = np.mean([e[0] for e in matched_energies]) if matched_energies else 0
        low_combined = sum(1 for e in matched_energies if e[1] < DECOMP_THRESHOLD)
        low_combined_ratio = low_combined / len(matched_energies) if matched_energies else 0
    else:
        match_rate = 0
        mean_matched = 0
        mean_combined = 0
        low_combined_ratio = 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "total_attempts": len(matched_resonances) + len(unmatched_resonances),
        "total_matched": len(matched_resonances),
        "match_rate": match_rate,
        "mean_resonance": mean_matched,
        "mean_combined_e": mean_combined,
        "low_combined_ratio": low_combined_ratio
    }

def main():
    print(f"CYCLE 1700: Phase Alignment | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Why does n=25 produce lower mean creation energy?")
    print("=" * 70)

    seeds = list(range(1700001, 1700021))

    population_sizes = [15, 20, 25, 30, 35, 50]
    all_results = []

    for n_init in population_sizes:
        results = [run_phase_analysis(seed, n_init) for seed in seeds]
        avg_rate = np.mean([r["match_rate"] for r in results])
        avg_combined = np.mean([r["mean_combined_e"] for r in results])
        avg_low = np.mean([r["low_combined_ratio"] for r in results])
        print(f"\nn={n_init}: match_rate={avg_rate:.1%}, combined_E={avg_combined:.3f}, low_ratio={avg_low:.1%}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("PHASE RESONANCE BY POPULATION SIZE")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Attempts':>9} | {'Matched':>8} | {'Rate':>6} | {'Combined E':>10} | {'Low%':>6}")
    print("-" * 60)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_att = np.mean([r["total_attempts"] for r in subset])
        avg_mat = np.mean([r["total_matched"] for r in subset])
        avg_rate = np.mean([r["match_rate"] for r in subset])
        avg_comb = np.mean([r["mean_combined_e"] for r in subset])
        avg_low = np.mean([r["low_combined_ratio"] for r in subset])
        print(f"{n_init:4d} | {avg_att:9.1f} | {avg_mat:8.1f} | {avg_rate:5.1%} | {avg_comb:10.3f} | {avg_low:5.1%}")

    # Success correlation
    print("\n" + "=" * 70)
    print("LOW-COMBINED RATIO vs SUCCESS")
    print("=" * 70)
    success_rates = {15: 32, 20: 56, 25: 96, 30: 38, 35: 52, 50: 66}
    print(f"\n{'N':>4} | {'Combined E':>10} | {'Low%':>6} | {'Success':>8}")
    print("-" * 40)
    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_comb = np.mean([r["mean_combined_e"] for r in subset])
        avg_low = np.mean([r["low_combined_ratio"] for r in subset])
        success = success_rates.get(n_init, 0)
        print(f"{n_init:4d} | {avg_comb:10.3f} | {avg_low:5.1%} | {success:7d}%")

if __name__ == "__main__":
    main()
