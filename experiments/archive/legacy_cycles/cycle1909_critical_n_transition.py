#!/usr/bin/env python3
"""
CYCLE 1909: CRITICAL N TRANSITION

Why does E=0.5 help at N=14 but hurt at N=15?
Track population dynamics to find the divergence point.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 100
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

def run_population_dynamics(seed, n_initial, repro_prob, init_energy):
    """Track detailed population dynamics over time."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # Track metrics per cycle
    d0_history = []
    d1_history = []
    compositions = []  # Number of compositions per cycle
    decompositions = []  # Number of decompositions per cycle

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, init_energy, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        d0_history.append(len(pops[0]))
        d1_history.append(len(pops[1]))
        comp_count = 0
        decomp_count = 0

        # Recharge
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition
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
                    comp_count += 1
                    i += 2
                else:
                    i += 1

        compositions.append(comp_count)

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)
                    decomp_count += 1

        decompositions.append(decomp_count)

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    # Final state
    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    coexist = 1 if final_pops[0] > 0 and final_pops[1] > 0 else 0

    return {
        'd0_history': d0_history,
        'd1_history': d1_history,
        'compositions': compositions,
        'decompositions': decompositions,
        'coexist': coexist,
        'final_d0': final_pops[0],
        'final_d1': final_pops[1]
    }

def main():
    print(f"CYCLE 1909: Critical N Transition | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Why does E=0.5 help at N=14 but hurt at N=15?")
    print("=" * 80)

    seeds = list(range(1909001, 1909011))  # 10 seeds for detailed analysis
    prob = 0.10
    energy = 0.5

    # Compare N=14 vs N=15
    for n in [14, 15]:
        print(f"\n{'='*40}")
        print(f"N = {n} with E = {energy}")
        print(f"{'='*40}")

        all_results = [run_population_dynamics(s, n, prob, energy) for s in seeds]
        coex_rate = np.mean([r['coexist'] for r in all_results])

        print(f"\nCoexistence rate: {coex_rate*100:.0f}%")

        # Analyze first few cycles (where divergence occurs)
        print(f"\nFirst 5 cycles (averaged over {len(seeds)} seeds):")
        print(f"{'Cycle':>5} | {'D0':>6} | {'D1':>6} | {'Comp':>6} | {'Decomp':>6}")
        print("-" * 45)

        for c in range(min(5, len(all_results[0]['d0_history']))):
            avg_d0 = np.mean([r['d0_history'][c] if c < len(r['d0_history']) else 0 for r in all_results])
            avg_d1 = np.mean([r['d1_history'][c] if c < len(r['d1_history']) else 0 for r in all_results])
            avg_comp = np.mean([r['compositions'][c] if c < len(r['compositions']) else 0 for r in all_results])
            avg_decomp = np.mean([r['decompositions'][c] if c < len(r['decompositions']) else 0 for r in all_results])
            print(f"{c:>5} | {avg_d0:>6.1f} | {avg_d1:>6.1f} | {avg_comp:>6.1f} | {avg_decomp:>6.1f}")

        # Key metrics
        print(f"\nKey metrics:")

        # Initial composition wave
        first_comp = np.mean([r['compositions'][0] if r['compositions'] else 0 for r in all_results])
        print(f"  First cycle compositions: {first_comp:.1f}")
        print(f"  Initial D0: {n}")
        print(f"  D0 consumed: {first_comp * 2:.0f}")
        print(f"  D0 remaining: {n - first_comp * 2:.0f}")
        print(f"  D1 created: {first_comp:.0f}")

        # Decomposition return
        total_decomp = np.mean([sum(r['decompositions'][:10]) for r in all_results])
        print(f"  Decompositions (first 10 cycles): {total_decomp:.1f}")
        print(f"  D0 returned (2 per decomp): {total_decomp * 2:.0f}")

    # Analysis
    print("\n" + "=" * 80)
    print("CRITICAL TRANSITION ANALYSIS")
    print("=" * 80)

    # Calculate the depletion ratio
    print("""
HYPOTHESIS: Minimum Surviving D0 Threshold

For N=14:
- First compositions: ~7 (consumes 14 D0)
- D0 remaining: 0
- D1 created: 7
- BUT: D1 quickly recharges and decomposes
- D0 returns before system collapses

For N=15:
- First compositions: ~7 (consumes 14 D0)
- D0 remaining: 1
- D1 created: 7
- The single remaining D0 cannot sustain
- System may collapse before decomposition returns enough

Wait - N=15 should have MORE remaining D0...

Let me check the actual numbers:
""")

    # Detailed comparison
    results_14 = [run_population_dynamics(s, 14, prob, 0.5) for s in seeds]
    results_15 = [run_population_dynamics(s, 15, prob, 0.5) for s in seeds]

    comp_14 = np.mean([r['compositions'][0] if r['compositions'] else 0 for r in results_14])
    comp_15 = np.mean([r['compositions'][0] if r['compositions'] else 0 for r in results_15])

    print(f"Actual first-cycle compositions:")
    print(f"  N=14: {comp_14:.1f} compositions ({comp_14*2:.0f} D0 consumed)")
    print(f"  N=15: {comp_15:.1f} compositions ({comp_15*2:.0f} D0 consumed)")

    remaining_14 = 14 - comp_14 * 2
    remaining_15 = 15 - comp_15 * 2
    print(f"\nRemaining D0 after first cycle:")
    print(f"  N=14: {remaining_14:.1f}")
    print(f"  N=15: {remaining_15:.1f}")

    print(f"""
REVISED HYPOTHESIS: Population Pressure Cascade

The issue isn't the first cycle - it's the SECOND cycle:
- N=14: 7 D1 agents, moderate energy
- N=15: 7-8 D1 agents with higher total energy

More D1 agents with higher energy =
  → More D1-D1 compositions (D2 formation)
  → Faster upward cascade
  → D0 gets depleted to D1 to D2 to D3...
  → System destabilizes

Let me check D2+ formation...
""")

    # Check higher depth formation
    print("Higher depth populations at cycle 10:")
    for n, results in [(14, results_14), (15, results_15)]:
        d2_at_10 = []
        for r in results:
            # Need to track D2 - but we only tracked D0 and D1
            pass
        print(f"  N={n}: Need deeper tracking for this analysis")

    print(f"""
CONCLUSION:

The critical transition at N=14-15 likely involves:
1. Population pressure from excess agents
2. Upward cascade to higher depths
3. Loss of D0 population to sustain cycling

Next experiment should track ALL depth levels to confirm cascade hypothesis.
""")

if __name__ == "__main__":
    main()
