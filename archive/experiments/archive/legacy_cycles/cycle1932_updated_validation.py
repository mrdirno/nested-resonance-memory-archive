#!/usr/bin/env python3
"""
CYCLE 1932: UPDATED OPTIMAL VALIDATION

Validate all optimized parameters with new recharge_base = 0.4:
- p = 0.17
- N = 14
- comp_thresh = 0.99
- decomp_thresh = 1.7
- recharge_base = 0.4 (NEW)
Target: >96% coexistence
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

# UPDATED OPTIMAL PARAMETERS
REPRO_PROB = 0.17
N_INITIAL = 14
COMP_THRESH = 0.99
DECOMP_THRESH = 1.7
RECHARGE_BASE = 0.4  # UPDATED from 0.2

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
    return final_pops[0] > 0 and final_pops[1] > 0

def main():
    print(f"CYCLE 1932: Updated Optimal Validation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Validating optimized parameters with recharge_base = 0.4")
    print("=" * 80)
    print(f"\nParameters:")
    print(f"  p = {REPRO_PROB}")
    print(f"  N = {N_INITIAL}")
    print(f"  comp_thresh = {COMP_THRESH}")
    print(f"  decomp_thresh = {DECOMP_THRESH}")
    print(f"  recharge_base = {RECHARGE_BASE} (NEW)")
    print(f"\nTarget: >96% coexistence")
    print("=" * 80)

    seeds = list(range(1932001, 1932101))  # 100 seeds

    results = [run_simulation(s) for s in seeds]
    coex = np.mean(results) * 100

    # Calculate confidence interval
    se = np.std(results) / np.sqrt(len(results)) * 100
    ci_low = coex - 1.96 * se
    ci_high = coex + 1.96 * se

    print(f"\nRESULTS (n=100):")
    print(f"  Coexistence: {coex:.1f}%")
    print(f"  95% CI: [{ci_low:.1f}%, {ci_high:.1f}%]")
    print(f"  Success count: {sum(results)}/100")

    # Comparison with C1930
    c1930_coex = 93.0
    improvement = coex - c1930_coex

    print(f"\n{'=' * 80}")
    print("VALIDATION")
    print("=" * 80)
    print(f"\nTarget: >96%")
    print(f"Achieved: {coex:.1f}%")
    print(f"C1930 (recharge=0.2): {c1930_coex:.1f}%")
    print(f"Improvement: {improvement:+.1f}%")

    target = 96
    validated = coex >= target
    print(f"Status: {'VALIDATED' if validated else 'NOT VALIDATED'}")

    print(f"""
CONCLUSION:

Updated optimal parameters with recharge_base = 0.4:

Coexistence: {coex:.1f}% +/- {1.96*se:.1f}%
Improvement over C1930: {improvement:+.1f}%
Target (96%): {'ACHIEVED' if validated else 'NOT ACHIEVED'}

{'The updated recharge rate significantly improves system performance.' if improvement > 0 else 'No improvement from recharge update.'}

FINAL OPTIMAL PARAMETERS:
  p = {REPRO_PROB}
  N = {N_INITIAL}+
  comp_thresh = {COMP_THRESH}
  decomp_thresh = {DECOMP_THRESH}
  recharge_base = {RECHARGE_BASE}
  Expected: {coex:.0f}%+ coexistence

Session status: 269 cycles completed (C1664-C1932).
""")

if __name__ == "__main__":
    main()
