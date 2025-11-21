#!/usr/bin/env python3
"""
CYCLE 1719: THRESHOLD VALIDATION
Validate D1D2 >1.3 threshold across comprehensive parameter space.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1719"
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

def run_validation(seed, n_initial, recharge, repro):
    """Validate threshold."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    d1_created = 0
    d2_created = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro:
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
                    if d == 0:
                        d1_created += 1
                    elif d == 1:
                        d2_created += 1
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

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    coexist = sum(1 for p in final_pops if len(p) > 0) >= 2
    d1d2_ratio = d2_created / d1_created if d1_created > 0 else 0

    return {
        "d1d2_ratio": d1d2_ratio,
        "coexist": coexist
    }

def main():
    print(f"CYCLE 1719: Threshold Validation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Validate D1D2 >1.3 threshold across parameter space")
    print("=" * 70)

    seeds = list(range(1719001, 1719051))  # 50 seeds

    # Comprehensive parameter grid
    recharge_vals = [0.05, 0.075, 0.1, 0.125, 0.15]
    repro_vals = [0.05, 0.1, 0.15]
    n_vals = [20, 25, 30, 35]

    correct = 0
    total = 0
    errors = []

    for recharge in recharge_vals:
        for repro in repro_vals:
            for n in n_vals:
                results = [run_validation(seed, n, recharge, repro) for seed in seeds]
                avg_d1d2 = np.mean([r["d1d2_ratio"] for r in results])
                coexist = sum(1 for r in results if r["coexist"]) / len(results) * 100

                # Test threshold
                predicted_success = avg_d1d2 > 1.3
                actual_success = coexist >= 90

                total += 1
                if predicted_success == actual_success:
                    correct += 1
                else:
                    errors.append((n, recharge, repro, avg_d1d2, coexist))

    accuracy = correct / total * 100

    print(f"\n{'='*70}")
    print(f"VALIDATION RESULTS")
    print(f"{'='*70}")
    print(f"\nAccuracy: {correct}/{total} ({accuracy:.1f}%)")
    print(f"\nThreshold: D1D2 > 1.3 predicts coexist >= 90%")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        print(f"{'N':>4} | {'Rech':>5} | {'Repr':>5} | {'D1D2':>6} | {'Coex':>6}")
        print("-" * 40)
        for n, rech, repr, d1d2, coex in errors[:10]:  # Show first 10
            pred = "✓" if d1d2 > 1.3 else "✗"
            act = "✓" if coex >= 90 else "✗"
            print(f"{n:4d} | {rech:5.3f} | {repr:5.2f} | {d1d2:6.2f} | {coex:5.0f}% (pred={pred}, act={act})")

if __name__ == "__main__":
    main()
