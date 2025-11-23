#!/usr/bin/env python3
"""
CYCLE 1661: MEMORY DYNAMICS
Add pattern memory to composition-decomposition. Agents remember past
compositions and are more likely to compose with similar agents again.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1661"
CYCLES = 30000
N_DEPTHS = 5

DECAY_MULT = 0.1
REPRO_RATE = 0.1
DECOMP_THRESHOLD = 1.3
RESONANCE_THRESHOLD = 0.5

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

def run_experiment(seed, memory_boost=0.0):
    """
    Run experiment with memory dynamics.

    Args:
        memory_boost: How much past compositions boost resonance (0-1)
                     Effective threshold = base - memory_boost * memory_factor
    """
    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1661_m{memory_boost}_s{seed}.db",
        n_populations=N_DEPTHS, mode="SEARCH"
    )
    np.random.seed(seed)

    for i in range(100):
        agent = FractalAgent(f"D0_{i}", 0, 1.0, depth=0)
        agent.memory = {"composition_count": 0, "last_partner_energy": None}
        reality.add_agent(agent, 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    n_comps = n_decomps = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_RATE:
                child = FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0)
                child.memory = {"composition_count": 0, "last_partner_energy": None}
                reality.add_agent(child, 0)
                agent.energy -= 0.3

        # Composition with MEMORY
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                a1 = agents[i]
                a2 = agents[i + 1]

                # Base resonance
                similarity = compute_phase_resonance(a1.energy, d, a2.energy, d)

                # Memory boost: agents with more compositions have lower threshold
                mem1 = a1.memory.get("composition_count", 0)
                mem2 = a2.memory.get("composition_count", 0)
                memory_factor = (mem1 + mem2) / max(1, mem1 + mem2 + 10)  # Saturating boost
                effective_threshold = RESONANCE_THRESHOLD - memory_boost * memory_factor

                if similarity >= effective_threshold:
                    new_e = (a1.energy + a2.energy) * 0.85

                    # Create new agent with combined memory
                    new_agent = FractalAgent(f"D{d+1}_{cycle}_{n_comps}", d+1, new_e, depth=d+1)
                    new_agent.memory = {
                        "composition_count": max(mem1, mem2) + 1,
                        "last_partner_energy": (a1.energy + a2.energy) / 2
                    }
                    new_agent.compositions = max(a1.compositions, a2.compositions) + 1

                    reality.remove_agent(a1.agent_id, d)
                    reality.remove_agent(a2.agent_id, d)
                    reality.add_agent(new_agent, d + 1)
                    n_comps += 1
                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45

                    # Children inherit half of parent's memory
                    parent_mem = agent.memory.get("composition_count", 0)

                    for j in range(2):
                        child = FractalAgent(f"D{d-1}_{cycle}_{n_decomps}_{j}", d-1, ce, depth=d-1)
                        child.memory = {
                            "composition_count": parent_mem // 2,
                            "last_partner_energy": agent.energy
                        }
                        child.decompositions = agent.decompositions + 1
                        reality.add_agent(child, d - 1)

                    reality.remove_agent(agent.agent_id, d)
                    n_decomps += 1

        # Energy decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    return {
        "seed": seed,
        "memory_boost": memory_boost,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "n_comps": n_comps,
        "n_decomps": n_decomps,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1661: Memory Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing memory-boosted composition")
    print("=" * 70)

    seeds = list(range(1020001, 1020021))

    memory_boosts = [0.0, 0.1, 0.2, 0.3, 0.5]
    all_results = []

    for boost in memory_boosts:
        print(f"\nmemory_boost={boost}")
        results = [run_experiment(seed, boost) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        rate = coexist_count / len(results)
        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"  → {coexist_count}/{len(results)} coexist ({rate*100:.0f}%), depths={avg_depths:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("MEMORY DYNAMICS RESULTS")
    print("=" * 70)

    for boost in memory_boosts:
        subset = [r for r in all_results if r["memory_boost"] == boost]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"boost={boost}: {rate*100:.0f}% ({avg_depths:.1f} depths)")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1661_memory_dynamics_results.json", 'w') as f:
        json.dump({"cycle_id": CYCLE_ID, "results": all_results}, f, indent=2)

if __name__ == "__main__":
    main()
