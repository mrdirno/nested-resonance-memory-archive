#!/usr/bin/env python3
"""
CYCLE 1941: HIERARCHY DEPTH WITH DENSITY-DEPENDENT DYNAMICS

Test if four-level hierarchy (D0-D3) is maintained under density-dependent
reproduction with optimal K=50.
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

# COMPLETE OPTIMAL PARAMETERS
P_BASE = 0.17
K = 50  # Density-dependent carrying capacity
N_INITIAL = 14
COMP_THRESH = 0.99
DECOMP_THRESH = 1.7
RECHARGE_BASE = 0.4

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

def run_simulation(seed):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    for i in range(N_INITIAL):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Density-dependent reproduction
        p_effective = P_BASE / (1 + total / K)

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < p_effective:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= COMP_THRESH:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESH:
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
    return final_pops

def main():
    print(f"CYCLE 1941: Hierarchy Depth (DD) | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing depth hierarchy under density-dependent dynamics (K=50)")
    print("=" * 80)

    seeds = list(range(1941001, 1941051))  # 50 seeds

    all_pops = [run_simulation(s) for s in seeds]

    # Calculate statistics
    avg_pops = [np.mean([p[d] for p in all_pops]) for d in range(N_DEPTHS)]
    survival = [np.mean([p[d] > 0 for p in all_pops]) * 100 for d in range(N_DEPTHS)]

    print(f"\nHIERARCHY STRUCTURE (n=50):")
    print(f"\n{'Depth':>6} | {'Survival %':>10} | {'Avg Pop':>8} | {'Ratio':>8}")
    print("-" * 42)

    for d in range(N_DEPTHS):
        ratio = avg_pops[d] / avg_pops[d-1] if d > 0 and avg_pops[d-1] > 0 else 0
        print(f"D{d:>5} | {survival[d]:>9.1f}% | {avg_pops[d]:>8.1f} | {ratio:>7.2f}")

    # Coexistence metrics
    d0_d1 = np.mean([p[0] > 0 and p[1] > 0 for p in all_pops]) * 100
    d0_d1_d2 = np.mean([p[0] > 0 and p[1] > 0 and p[2] > 0 for p in all_pops]) * 100
    d0_d1_d2_d3 = np.mean([all(p[i] > 0 for i in range(4)) for p in all_pops]) * 100

    print(f"\nCOEXISTENCE RATES:")
    print(f"  D0+D1: {d0_d1:.1f}%")
    print(f"  D0+D1+D2: {d0_d1_d2:.1f}%")
    print(f"  D0+D1+D2+D3: {d0_d1_d2_d3:.1f}%")

    # Compare to C1933 (no density dependence)
    print(f"\n{'=' * 80}")
    print("COMPARISON WITH C1933 (No DD)")
    print("=" * 80)
    print(f"""
C1933 (no DD):     D0-D3 all 100%, avg total ~3160
C1941 (DD, K=50):  D0-D3 {d0_d1_d2_d3:.0f}%, avg total ~{sum(avg_pops):.0f}

{'Hierarchy maintained under density-dependent dynamics!' if d0_d1_d2_d3 >= 90 else 'Hierarchy reduced under density-dependent dynamics.'}

Population structure comparison:
- C1933 (no DD): D0~2684, D1~409, D2~52, D3~17
- C1941 (DD): D0~{avg_pops[0]:.0f}, D1~{avg_pops[1]:.0f}, D2~{avg_pops[2]:.0f}, D3~{avg_pops[3]:.0f}

Session status: 278 cycles completed (C1664-C1941).
""")

if __name__ == "__main__":
    main()
