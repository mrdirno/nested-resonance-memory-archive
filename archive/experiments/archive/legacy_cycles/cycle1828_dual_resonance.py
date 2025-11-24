#!/usr/bin/env python3
"""
CYCLE 1828: DUAL RESONANCE INVESTIGATION
Why does N=29 have two dead zones (low B/C and B/C≈0.06)?

Hypothesis: Different dynamical modes dominate at different B/C.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1828"
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

def run_detailed_analysis(seed, n_initial, repro_prob):
    """Track detailed dynamics for mechanism analysis"""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track dynamics
    births = 0
    comps_by_depth = [0] * (N_DEPTHS - 1)  # Compositions at each depth
    decomps = 0
    depth_time = [0] * N_DEPTHS  # Cycles with agents at each depth
    energy_sum = [0.0] * N_DEPTHS  # Total energy by depth
    energy_count = [0] * N_DEPTHS

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Track depth occupancy and energy
        for d in range(N_DEPTHS):
            if len(pops[d]) > 0:
                depth_time[d] += 1
                for agent in pops[d]:
                    energy_sum[d] += agent.energy
                    energy_count[d] += 1

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
                births += 1

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
                    comps_by_depth[d] += 1
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
                    decomps += 1

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    coex = sum(1 for p in final_pops if len(p) > 0) >= 2
    total_comps = sum(comps_by_depth)
    bc = births / total_comps if total_comps > 0 else 0

    # Calculate average energy by depth
    avg_energy = [energy_sum[d] / energy_count[d] if energy_count[d] > 0 else 0 for d in range(N_DEPTHS)]

    return {
        'coex': coex,
        'bc': bc,
        'births': births,
        'comps': comps_by_depth,
        'decomps': decomps,
        'depth_time': depth_time,
        'avg_energy': avg_energy
    }

def main():
    print(f"CYCLE 1828: Dual Resonance Investigation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Why does N=29 have two dead zones?")
    print("=" * 80)

    seeds = list(range(1828001, 1828031))  # 30 seeds

    # Compare the three regimes for N=29
    # Dead zone 1: prob=0.05 (B/C≈0.01)
    # Safe zone: prob=0.20 (B/C≈0.02)
    # Dead zone 2: prob=0.60 (B/C≈0.06)

    test_cases = [
        ("Dead Zone 1", 0.05),
        ("Safe Zone", 0.20),
        ("Dead Zone 2", 0.60),
    ]

    print("\n" + "=" * 80)
    print("N=29 DYNAMICS COMPARISON")
    print("=" * 80)

    for name, prob in test_cases:
        results = [run_detailed_analysis(seed, 29, prob) for seed in seeds]

        coex = sum(r['coex'] for r in results) / len(results) * 100
        bc = np.mean([r['bc'] for r in results])
        births = np.mean([r['births'] for r in results])
        total_comps = np.mean([sum(r['comps']) for r in results])
        decomps = np.mean([r['decomps'] for r in results])

        # Average composition by depth
        avg_comps = [np.mean([r['comps'][d] for r in results]) for d in range(N_DEPTHS-1)]

        # Average depth occupancy
        avg_depth_time = [np.mean([r['depth_time'][d] for r in results]) for d in range(N_DEPTHS)]

        # Average energy by depth
        avg_energy = [np.mean([r['avg_energy'][d] for r in results]) for d in range(N_DEPTHS)]

        print(f"\n{name} (prob={prob})")
        print("-" * 60)
        print(f"Coexistence: {coex:.0f}%")
        print(f"B/C Ratio: {bc:.4f}")
        print(f"Births: {births:.0f}, Decomps: {decomps:.0f}")
        print(f"\nCompositions by depth (D0→D1, D1→D2, ...):")
        print(f"  {' | '.join([f'{c:.0f}' for c in avg_comps])}")
        print(f"\nDepth occupancy (cycles with agents):")
        print(f"  {' | '.join([f'{t:.0f}' for t in avg_depth_time])}")
        print(f"\nAvg energy by depth:")
        print(f"  {' | '.join([f'{e:.2f}' for e in avg_energy])}")

    # Additional comparison: Composition ratio D0→D1 vs D1→D2
    print("\n" + "=" * 80)
    print("COMPOSITION DEPTH RATIO ANALYSIS")
    print("=" * 80)

    probs = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70]

    print(f"\n{'Prob':<6} | {'Coex':>6} | {'B/C':>8} | {'D0→D1':>8} | {'D1→D2':>8} | {'Ratio':>8}")
    print("-" * 60)

    for prob in probs:
        results = [run_detailed_analysis(seed, 29, prob) for seed in seeds[:15]]

        coex = sum(r['coex'] for r in results) / len(results) * 100
        bc = np.mean([r['bc'] for r in results])
        c01 = np.mean([r['comps'][0] for r in results])
        c12 = np.mean([r['comps'][1] for r in results])
        ratio = c01 / c12 if c12 > 0 else float('inf')

        print(f"{prob:<6} | {coex:>5.0f}% | {bc:>8.4f} | {c01:>8.0f} | {c12:>8.0f} | {ratio:>8.2f}")

if __name__ == "__main__":
    main()
