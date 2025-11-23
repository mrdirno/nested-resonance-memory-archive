#!/usr/bin/env python3
"""
CYCLE 1707: MECHANISM VERIFICATION
Does offspring ratio predict optimal N at different reproduction rates?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1707"
CYCLES = 1000
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

def run_verification(seed, n_initial, repro_rate):
    """Test offspring ratio at different reproduction rates."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1

    # Track original IDs
    original_ids = set()
    for i in range(n_initial):
        agent_id = f"D0_{i}"
        reality.add_agent(FractalAgent(agent_id, 0, 1.0, depth=0), 0)
        original_ids.add(agent_id)

    both_original = 0
    both_offspring = 0
    one_original = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction at specified rate
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_rate:
                offspring_id = f"D0_{cycle}_{agent.agent_id[-6:]}"
                reality.add_agent(FractalAgent(offspring_id, 0, 0.5, depth=0), 0)
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

                    if d == 0:
                        a1_orig = agents[i].agent_id in original_ids
                        a2_orig = agents[i+1].agent_id in original_ids
                        if a1_orig and a2_orig:
                            both_original += 1
                        elif a1_orig or a2_orig:
                            one_original += 1
                        else:
                            both_offspring += 1

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

    # Final state
    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    coexist = sum(1 for p in final_pops if len(p) > 0) >= 2

    total_comps = both_original + one_original + both_offspring
    offspring_ratio = (one_original + 2*both_offspring) / (2*total_comps) if total_comps > 0 else 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "repro_rate": repro_rate,
        "offspring_ratio": offspring_ratio,
        "coexist": coexist
    }

def main():
    print(f"CYCLE 1707: Mechanism Verification | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Does offspring ratio predict optimal N across parameters?")
    print("=" * 70)

    seeds = list(range(1707001, 1707021))  # 20 seeds
    population_sizes = [20, 25, 30, 35]
    repro_rates = [0.05, 0.1, 0.15, 0.2]

    for rate in repro_rates:
        print(f"\n{'='*70}")
        print(f"REPRODUCTION RATE = {rate}")
        print(f"{'='*70}")
        print(f"\n{'N':>4} | {'Off%':>6} | {'Coexist':>8}")
        print("-" * 25)

        results_at_rate = []
        for n_init in population_sizes:
            results = [run_verification(seed, n_init, rate) for seed in seeds]
            avg_off = np.mean([r["offspring_ratio"] for r in results])
            coexist = sum(1 for r in results if r["coexist"]) / len(results) * 100
            results_at_rate.append((n_init, avg_off, coexist))
            print(f"{n_init:4d} | {avg_off:5.1%} | {coexist:7.0f}%")

        # Find optimal by offspring ratio and by coexistence
        best_off = max(results_at_rate, key=lambda x: x[1])
        best_coex = max(results_at_rate, key=lambda x: x[2])
        print(f"\nHighest offspring ratio: n={best_off[0]} ({best_off[1]:.1%})")
        print(f"Highest coexistence: n={best_coex[0]} ({best_coex[2]:.0f}%)")
        print(f"Match: {'YES' if best_off[0] == best_coex[0] else 'NO'}")

if __name__ == "__main__":
    main()
