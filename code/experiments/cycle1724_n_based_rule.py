#!/usr/bin/env python3
"""
CYCLE 1724: N-BASED RULE
Test simple rule: avoid N=27-31 (dead zone)
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1724"
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

def run_test(seed, n_initial, recharge, repro):
    """Simple coexistence test."""
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
    return coexist

def main():
    print(f"CYCLE 1724: N-Based Rule | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Test simple rule: avoid N=27-31")
    print("=" * 70)

    seeds = list(range(1724001, 1724041))  # 40 seeds

    # Comprehensive parameter grid
    recharge_vals = [0.05, 0.075, 0.1, 0.125, 0.15]
    repro_vals = [0.05, 0.1, 0.15]
    n_vals = [20, 25, 28, 30, 32, 35, 40]

    # Test N-based rule
    dead_zone = {27, 28, 29, 30, 31}

    correct = 0
    total = 0
    errors = []

    for recharge in recharge_vals:
        for repro in repro_vals:
            for n in n_vals:
                results = [run_test(seed, n, recharge, repro) for seed in seeds]
                coexist = sum(results) / len(results) * 100

                # Rule: not in dead zone predicts success
                predicted_success = n not in dead_zone
                actual_success = coexist >= 90

                total += 1
                if predicted_success == actual_success:
                    correct += 1
                else:
                    errors.append((n, recharge, repro, coexist))

    accuracy = correct / total * 100

    print(f"\n{'='*70}")
    print(f"N-BASED RULE: Avoid N ∈ {{27-31}}")
    print(f"{'='*70}")
    print(f"\nAccuracy: {correct}/{total} ({accuracy:.1f}%)")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        print(f"{'N':>4} | {'Rech':>5} | {'Repr':>5} | {'Coex':>6}")
        print("-" * 35)
        for n, rech, repr, coex in errors:
            inzone = "dead" if n in dead_zone else "safe"
            act = "✓" if coex >= 90 else "✗"
            print(f"{n:4d} | {rech:5.3f} | {repr:5.2f} | {coex:5.0f}% ({inzone}→{act})")

    # Model comparison
    print("\n" + "=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)
    print(f"\n{'Model':<30} | {'Accuracy':>10}")
    print("-" * 45)
    print(f"{'D1Dec <45':30} | {'55%':>10}")
    print(f"{'D1D2 >1.3 (fixed)':30} | {'68%':>10}")
    print(f"{'D1D2 > 0.5+10*repro':30} | {'85%':>10}")
    print(f"{'N ∉ {27-31}':30} | {accuracy:>9.0f}%")

if __name__ == "__main__":
    main()
