#!/usr/bin/env python3
"""
CYCLE 1689: COUPLED POPULATIONS AT OPTIMAL N=25
Do coupled populations perform better than independent ones?
Test energy/agent transfer between populations.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1689"
CYCLES = 30000
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

class CoupledPopulations:
    """Two coupled NRM populations."""

    def __init__(self, n_initial_each=25, coupling_strength=0.1):
        self.pop_a = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
        self.pop_b = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
        self.coupling = coupling_strength

        # Initialize both
        for i in range(n_initial_each):
            self.pop_a.add_agent(FractalAgent(f"A_D0_{i}", 0, 1.0, depth=0), 0)
            self.pop_b.add_agent(FractalAgent(f"B_D0_{i}", 0, 1.0, depth=0), 0)

    def run_cycle(self, cycle, np_random):
        DECAY_MULT = 0.1
        BASE_REPRO = 0.1
        DECOMP_THRESHOLD = 1.3
        RESONANCE_THRESHOLD = 0.5

        # Run one cycle on each population
        for prefix, reality in [("A", self.pop_a), ("B", self.pop_b)]:
            pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
            total = sum(len(p) for p in pops)
            if total >= 3000 or total == 0:
                continue

            # Energy input
            for d in range(N_DEPTHS):
                for agent in pops[d]:
                    agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

            # Reproduction
            for agent in list(reality.get_population_agents(0)):
                if agent.energy > 1.0 and np_random.random() < BASE_REPRO:
                    reality.add_agent(FractalAgent(f"{prefix}_D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                    agent.energy -= 0.3

            # Composition
            for d in range(N_DEPTHS - 1):
                agents = list(reality.get_population_agents(d))
                if len(agents) < 2:
                    continue
                np_random.shuffle(agents)
                i = 0
                while i < len(agents) - 1:
                    sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                    if sim >= RESONANCE_THRESHOLD:
                        new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                        reality.remove_agent(agents[i].agent_id, d)
                        reality.remove_agent(agents[i+1].agent_id, d)
                        reality.add_agent(FractalAgent(f"{prefix}_D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                        i += 2
                    else:
                        i += 1

            # Decomposition
            for d in range(1, N_DEPTHS):
                for agent in list(reality.get_population_agents(d)):
                    if agent.energy > DECOMP_THRESHOLD:
                        ce = agent.energy * 0.45
                        for j in range(2):
                            reality.add_agent(FractalAgent(f"{prefix}_D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                        reality.remove_agent(agent.agent_id, d)

            # Decay
            for d in range(N_DEPTHS):
                decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
                for agent in list(reality.get_population_agents(d)):
                    if not agent.consume_energy(decay):
                        reality.remove_agent(agent.agent_id, d)

        # Coupling: Transfer agents between populations
        if self.coupling > 0 and np_random.random() < self.coupling:
            # Transfer one D1 agent from A to B (if available)
            d1_a = list(self.pop_a.get_population_agents(1))
            if d1_a:
                agent = np_random.choice(d1_a)
                self.pop_a.remove_agent(agent.agent_id, 1)
                self.pop_b.add_agent(FractalAgent(f"B_D1_{cycle}_transfer", 1, agent.energy, depth=1), 1)

            # Transfer one D1 agent from B to A (if available)
            d1_b = list(self.pop_b.get_population_agents(1))
            if d1_b:
                agent = np_random.choice(d1_b)
                self.pop_b.remove_agent(agent.agent_id, 1)
                self.pop_a.add_agent(FractalAgent(f"A_D1_{cycle}_transfer", 1, agent.energy, depth=1), 1)

    def get_totals(self):
        a_total = sum(len(self.pop_a.get_population_agents(d)) for d in range(N_DEPTHS))
        b_total = sum(len(self.pop_b.get_population_agents(d)) for d in range(N_DEPTHS))
        return a_total, b_total

def run_coupled_experiment(seed, n_initial=25, coupling=0.1):
    """Run coupled populations."""
    np.random.seed(seed)
    system = CoupledPopulations(n_initial, coupling)

    histories = {"A": {d: [] for d in range(N_DEPTHS)}, "B": {d: [] for d in range(N_DEPTHS)}}

    for cycle in range(CYCLES):
        a_total, b_total = system.get_totals()
        if a_total >= 3000 or b_total >= 3000 or (a_total == 0 and b_total == 0):
            break

        system.run_cycle(cycle, np.random)

        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories["A"][d].append(len(system.pop_a.get_population_agents(d)))
                histories["B"][d].append(len(system.pop_b.get_population_agents(d)))

    # Compute coexistence for each
    a_finals = {d: np.mean(histories["A"][d][-10:]) if len(histories["A"][d]) > 10 else 0 for d in range(N_DEPTHS)}
    b_finals = {d: np.mean(histories["B"][d][-10:]) if len(histories["B"][d]) > 10 else 0 for d in range(N_DEPTHS)}

    a_depths = sum(1 for d in range(N_DEPTHS) if a_finals[d] >= 0.5)
    b_depths = sum(1 for d in range(N_DEPTHS) if b_finals[d] >= 0.5)

    return {
        "seed": seed,
        "coupling": coupling,
        "a_coexist": a_depths >= 3,
        "b_coexist": b_depths >= 3,
        "both_coexist": a_depths >= 3 and b_depths >= 3,
        "a_depths": a_depths,
        "b_depths": b_depths
    }

def main():
    print(f"CYCLE 1689: Coupled Populations | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Do coupled n=25 populations perform better?")
    print("=" * 70)

    seeds = list(range(1689001, 1689051))  # 50 seeds

    coupling_strengths = [0.0, 0.05, 0.1, 0.2, 0.5]
    all_results = []

    for coupling in coupling_strengths:
        print(f"\nCoupling = {coupling}")
        results = [run_coupled_experiment(seed, 25, coupling) for seed in seeds]

        a_rate = sum(1 for r in results if r["a_coexist"]) / len(results)
        b_rate = sum(1 for r in results if r["b_coexist"]) / len(results)
        both_rate = sum(1 for r in results if r["both_coexist"]) / len(results)

        print(f"  A: {a_rate*100:.0f}%, B: {b_rate*100:.0f}%, Both: {both_rate*100:.0f}%")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("COUPLING EFFECT ON COEXISTENCE")
    print("=" * 70)
    print(f"\n{'Coupling':>10} | {'Pop A':>8} | {'Pop B':>8} | {'Both':>8}")
    print("-" * 40)

    for coupling in coupling_strengths:
        subset = [r for r in all_results if r["coupling"] == coupling]
        a_rate = sum(1 for r in subset if r["a_coexist"]) / len(subset)
        b_rate = sum(1 for r in subset if r["b_coexist"]) / len(subset)
        both_rate = sum(1 for r in subset if r["both_coexist"]) / len(subset)
        print(f"{coupling:10.2f} | {a_rate*100:7.0f}% | {b_rate*100:7.0f}% | {both_rate*100:7.0f}%")

if __name__ == "__main__":
    main()
