#!/usr/bin/env python3
"""
CYCLE 1688: DETAILED DYNAMICS AT N=25
Track cycle-by-cycle events to understand stabilization mechanism.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1688"
CYCLES = 1000  # First 1000 cycles detailed
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

def run_detailed(seed, n_initial=25):
    """Track detailed dynamics."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Detailed tracking
    pop_history = {d: [] for d in range(N_DEPTHS)}
    comp_history = []  # compositions per cycle
    decomp_history = []  # decompositions per cycle
    avg_energy = {d: [] for d in range(N_DEPTHS)}

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Record populations
        for d in range(N_DEPTHS):
            pop_history[d].append(len(pops[d]))
            if pops[d]:
                avg_energy[d].append(np.mean([a.energy for a in pops[d]]))
            else:
                avg_energy[d].append(0)

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition
        cycle_comps = 0
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
                    cycle_comps += 1
                    i += 2
                else:
                    i += 1
        comp_history.append(cycle_comps)

        # Decomposition
        cycle_decomps = 0
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)
                    cycle_decomps += 1
        decomp_history.append(cycle_decomps)

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    # Compute metrics
    finals = {d: np.mean(pop_history[d][-100:]) if len(pop_history[d]) >= 100 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    return {
        "seed": seed,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "pop_history": pop_history,
        "comp_history": comp_history,
        "decomp_history": decomp_history,
        "avg_energy": avg_energy
    }

def main():
    print(f"CYCLE 1688: Detailed Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Understand cycle-by-cycle dynamics at n=25")
    print("=" * 70)

    # Run 10 seeds for detailed analysis
    seeds = list(range(1688001, 1688011))
    results = [run_detailed(seed, 25) for seed in seeds]

    successes = [r for r in results if r["coexist"]]
    failures = [r for r in results if not r["coexist"]]

    print(f"\nSuccess rate: {len(successes)}/{len(results)} ({len(successes)/len(results)*100:.0f}%)")

    # Average dynamics for successful runs
    print("\n" + "=" * 70)
    print("AVERAGE DYNAMICS (Successful Runs)")
    print("=" * 70)

    checkpoints = [0, 5, 10, 20, 50, 100, 500]

    print(f"\n{'Cycle':>6} | {'D0':>6} | {'D1':>6} | {'D2':>6} | {'D3':>6} | {'D4':>6} | {'Comps':>6}")
    print("-" * 55)

    for cp in checkpoints:
        if cp >= CYCLES:
            break
        d0 = np.mean([r["pop_history"][0][cp] for r in successes if len(r["pop_history"][0]) > cp])
        d1 = np.mean([r["pop_history"][1][cp] for r in successes if len(r["pop_history"][1]) > cp])
        d2 = np.mean([r["pop_history"][2][cp] for r in successes if len(r["pop_history"][2]) > cp])
        d3 = np.mean([r["pop_history"][3][cp] for r in successes if len(r["pop_history"][3]) > cp])
        d4 = np.mean([r["pop_history"][4][cp] for r in successes if len(r["pop_history"][4]) > cp])

        # Sum compositions up to checkpoint
        total_comps = np.mean([sum(r["comp_history"][:cp+1]) for r in successes if len(r["comp_history"]) > cp])

        print(f"{cp:6d} | {d0:6.1f} | {d1:6.1f} | {d2:6.1f} | {d3:6.1f} | {d4:6.1f} | {total_comps:6.0f}")

    # Composition/decomposition balance
    print("\n" + "=" * 70)
    print("COMPOSITION/DECOMPOSITION BALANCE")
    print("=" * 70)

    for period_name, start, end in [("First 10", 0, 10), ("Cycles 10-50", 10, 50), ("Cycles 50-100", 50, 100)]:
        if end > CYCLES:
            break
        comps = np.mean([sum(r["comp_history"][start:end]) for r in successes])
        decomps = np.mean([sum(r["decomp_history"][start:end]) for r in successes])
        print(f"\n{period_name}:")
        print(f"  Compositions: {comps:.1f}")
        print(f"  Decompositions: {decomps:.1f}")
        print(f"  Net: {comps - decomps:.1f}")

    # Energy evolution
    print("\n" + "=" * 70)
    print("AVERAGE D1 ENERGY EVOLUTION")
    print("=" * 70)

    for cp in [10, 50, 100, 500]:
        if cp >= CYCLES:
            break
        e1 = np.mean([r["avg_energy"][1][cp] for r in successes if len(r["avg_energy"][1]) > cp and r["avg_energy"][1][cp] > 0])
        print(f"Cycle {cp}: D1 avg energy = {e1:.2f}")

    # Compare success vs failure dynamics
    if failures:
        print("\n" + "=" * 70)
        print("SUCCESS VS FAILURE: First 10 Cycles")
        print("=" * 70)

        s_comps = np.mean([sum(r["comp_history"][:10]) for r in successes])
        f_comps = np.mean([sum(r["comp_history"][:10]) for r in failures])
        s_d1 = np.mean([r["pop_history"][1][10] for r in successes if len(r["pop_history"][1]) > 10])
        f_d1 = np.mean([r["pop_history"][1][10] for r in failures if len(r["pop_history"][1]) > 10])

        print(f"\nSuccess: {s_comps:.1f} comps, {s_d1:.1f} D1 at cycle 10")
        print(f"Failure: {f_comps:.1f} comps, {f_d1:.1f} D1 at cycle 10")

if __name__ == "__main__":
    main()
