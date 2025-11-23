#!/usr/bin/env python3
"""
CYCLE 1695: LONG-TERM STABILITY TEST
Run n=25 for 100000 cycles to verify extended stability.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1695"
CYCLES = 100000  # 100k cycles
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

def run_long_term(seed, n_initial=25):
    """Run for 100k cycles."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track at checkpoints
    checkpoints = [1000, 5000, 10000, 30000, 50000, 100000]
    checkpoint_data = {}

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0:
            break

        # Record at checkpoints
        if cycle + 1 in checkpoints:
            depths_alive = sum(1 for d in range(N_DEPTHS) if len(pops[d]) > 0)
            checkpoint_data[cycle + 1] = {
                "depths": depths_alive,
                "total": total,
                "pops": [len(pops[d]) for d in range(N_DEPTHS)]
            }

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
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
    pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    final_depths = sum(1 for d in range(N_DEPTHS) if len(pops[d]) > 0)
    final_total = sum(len(p) for p in pops)

    return {
        "seed": seed,
        "final_depths": final_depths,
        "final_total": final_total,
        "coexist": final_depths >= 3,
        "checkpoints": checkpoint_data,
        "cycles_run": cycle + 1
    }

def main():
    print(f"CYCLE 1695: Long-Term Stability | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Verify n=25 stability for 100k cycles")
    print("=" * 70)

    seeds = list(range(1695001, 1695021))  # 20 seeds

    results = []
    for i, seed in enumerate(seeds):
        print(f"\nSeed {i+1}/20: {seed}")
        result = run_long_term(seed, 25)
        results.append(result)
        print(f"  → Cycles: {result['cycles_run']}, Final depths: {result['final_depths']}, Coexist: {result['coexist']}")

    # Summary
    print("\n" + "=" * 70)
    print("LONG-TERM STABILITY RESULTS")
    print("=" * 70)

    coexist_count = sum(1 for r in results if r["coexist"])
    avg_cycles = np.mean([r["cycles_run"] for r in results])

    print(f"\nOverall: {coexist_count}/{len(results)} coexist ({coexist_count/len(results)*100:.0f}%)")
    print(f"Avg cycles run: {avg_cycles:.0f}")

    # Checkpoint analysis
    print("\n" + "=" * 70)
    print("STABILITY OVER TIME")
    print("=" * 70)

    checkpoints = [1000, 5000, 10000, 30000, 50000, 100000]
    for cp in checkpoints:
        depths_at_cp = []
        for r in results:
            if cp in r["checkpoints"]:
                depths_at_cp.append(r["checkpoints"][cp]["depths"])
        if depths_at_cp:
            avg = np.mean(depths_at_cp)
            coexist = sum(1 for d in depths_at_cp if d >= 3)
            print(f"Cycle {cp:6d}: {coexist}/{len(depths_at_cp)} coexist ({coexist/len(depths_at_cp)*100:.0f}%), avg depths={avg:.1f}")

if __name__ == "__main__":
    main()
