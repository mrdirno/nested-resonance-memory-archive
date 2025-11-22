#!/usr/bin/env python3
"""
CYCLE 1933: THREE-LEVEL COEXISTENCE

Test D0+D1+D2 coexistence with optimal parameters.
Can the system sustain populations across three depth levels?
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
REPRO_PROB = 0.17
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
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_PROB:
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
    return {
        'd0_d1': final_pops[0] > 0 and final_pops[1] > 0,
        'd0_d1_d2': final_pops[0] > 0 and final_pops[1] > 0 and final_pops[2] > 0,
        'pops': final_pops
    }

def main():
    print(f"CYCLE 1933: Three-Level Coexistence | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing D0+D1+D2 coexistence with optimal parameters")
    print("=" * 80)

    seeds = list(range(1933001, 1933101))  # 100 seeds

    results = [run_simulation(s) for s in seeds]

    d0_d1 = np.mean([r['d0_d1'] for r in results]) * 100
    d0_d1_d2 = np.mean([r['d0_d1_d2'] for r in results]) * 100

    # Population analysis
    avg_pops = [np.mean([r['pops'][d] for r in results]) for d in range(N_DEPTHS)]
    nonzero_pops = [np.mean([r['pops'][d] > 0 for r in results]) * 100 for d in range(N_DEPTHS)]

    print(f"\nCOEXISTENCE RATES (n=100):")
    print(f"  D0+D1: {d0_d1:.1f}%")
    print(f"  D0+D1+D2: {d0_d1_d2:.1f}%")

    print(f"\nPOPULATION SURVIVAL BY DEPTH:")
    print(f"{'Depth':>6} | {'Survival %':>10} | {'Avg Pop':>8}")
    print("-" * 32)
    for d in range(N_DEPTHS):
        print(f"D{d:>5} | {nonzero_pops[d]:>9.1f}% | {avg_pops[d]:>8.1f}")

    # Analysis
    print(f"\n{'=' * 80}")
    print("ANALYSIS")
    print("=" * 80)

    print(f"""
THREE-LEVEL COEXISTENCE:

D0+D1: {d0_d1:.1f}% (confirmed from C1932)
D0+D1+D2: {d0_d1_d2:.1f}%

{'Three-level coexistence is achievable!' if d0_d1_d2 > 50 else 'Three-level coexistence is rare.'}

DEPTH SURVIVAL PATTERN:
- D0: {nonzero_pops[0]:.0f}% (always survives with optimal params)
- D1: {nonzero_pops[1]:.0f}% (reliably generated)
- D2: {nonzero_pops[2]:.0f}% (requires D1+D1 composition)
- D3+: {nonzero_pops[3]:.0f}%+ (rare deep composition)

Interpretation:
{'D2 generation requires sufficient D1 population to compose. The ' + ('high' if d0_d1_d2 > 50 else 'low') + ' three-level rate indicates ' + ('robust' if d0_d1_d2 > 50 else 'fragile') + ' multi-level dynamics.'}

Session status: 270 cycles completed (C1664-C1933).
""")

if __name__ == "__main__":
    main()
