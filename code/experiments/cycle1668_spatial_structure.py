#!/usr/bin/env python3
"""
CYCLE 1668: SPATIAL STRUCTURE
Add spatial dimension with local interactions and dispersal.
Agents can only compose with neighbors in a 1D or 2D grid.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1668"
CYCLES = 30000
N_DEPTHS = 5
GRID_SIZE = 10  # 10x10 grid = 100 cells

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

def get_neighbors(pos, grid_size):
    """Get neighboring positions (4-connected)."""
    x, y = pos % grid_size, pos // grid_size
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            neighbors.append(ny * grid_size + nx)
    return neighbors

class SpatialAgent:
    def __init__(self, agent_id, depth, energy, position):
        self.agent_id = agent_id
        self.depth = depth
        self.energy = energy
        self.position = position

    def recharge(self, amount, cap=2.0):
        self.energy = min(cap, self.energy + amount)

    def consume(self, amount):
        self.energy -= amount
        return self.energy > 0

def run_experiment(seed, spatial=True):
    """
    Run experiment with or without spatial structure.
    """
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    # Initialize agents with positions
    agents = {d: [] for d in range(N_DEPTHS)}
    agent_counter = 0

    # Start with 100 agents distributed across grid
    for i in range(100):
        pos = i % (GRID_SIZE * GRID_SIZE) if spatial else 0
        agents[0].append(SpatialAgent(f"A{agent_counter}", 0, 1.0, pos))
        agent_counter += 1

    histories = {d: [] for d in range(N_DEPTHS)}

    for cycle in range(CYCLES):
        total = sum(len(agents[d]) for d in range(N_DEPTHS))
        if total >= 3000 or total == 0: break

        # Energy input
        for d in range(N_DEPTHS):
            for agent in agents[d]:
                agent.recharge(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        new_agents = []
        for agent in agents[0]:
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                # Offspring at same position
                new_agents.append(SpatialAgent(f"A{agent_counter}", 0, 0.5, agent.position))
                agent_counter += 1
                agent.energy -= 0.3
        agents[0].extend(new_agents)

        # Composition (spatial or global)
        for d in range(N_DEPTHS - 1):
            if len(agents[d]) < 2: continue

            if spatial:
                # Group by position
                by_pos = {}
                for agent in agents[d]:
                    if agent.position not in by_pos:
                        by_pos[agent.position] = []
                    by_pos[agent.position].append(agent)

                # Compose within same cell and neighbors
                to_remove = set()
                for pos, local_agents in by_pos.items():
                    # Include agents from neighboring cells
                    neighbor_agents = list(local_agents)
                    for npos in get_neighbors(pos, GRID_SIZE):
                        if npos in by_pos:
                            neighbor_agents.extend(by_pos[npos])

                    np.random.shuffle(neighbor_agents)
                    i = 0
                    while i < len(neighbor_agents) - 1:
                        a1, a2 = neighbor_agents[i], neighbor_agents[i+1]
                        if a1.agent_id in to_remove or a2.agent_id in to_remove:
                            i += 1
                            continue
                        sim = compute_phase_resonance(a1.energy, d, a2.energy, d)
                        if sim >= RESONANCE_THRESHOLD:
                            new_e = (a1.energy + a2.energy) * 0.85
                            # New agent at position of first parent
                            agents[d+1].append(SpatialAgent(f"A{agent_counter}", d+1, new_e, a1.position))
                            agent_counter += 1
                            to_remove.add(a1.agent_id)
                            to_remove.add(a2.agent_id)
                            i += 2
                        else:
                            i += 1

                agents[d] = [a for a in agents[d] if a.agent_id not in to_remove]
            else:
                # Global composition (original behavior)
                np.random.shuffle(agents[d])
                i = 0
                new_composed = []
                to_remove = []
                while i < len(agents[d]) - 1:
                    a1, a2 = agents[d][i], agents[d][i+1]
                    sim = compute_phase_resonance(a1.energy, d, a2.energy, d)
                    if sim >= RESONANCE_THRESHOLD:
                        new_e = (a1.energy + a2.energy) * 0.85
                        new_composed.append(SpatialAgent(f"A{agent_counter}", d+1, new_e, 0))
                        agent_counter += 1
                        to_remove.extend([i, i+1])
                        i += 2
                    else:
                        i += 1
                agents[d] = [a for i, a in enumerate(agents[d]) if i not in to_remove]
                agents[d+1].extend(new_composed)

        # Decomposition
        for d in range(1, N_DEPTHS):
            to_remove = []
            new_agents = []
            for i, agent in enumerate(agents[d]):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for _ in range(2):
                        new_agents.append(SpatialAgent(f"A{agent_counter}", d-1, ce, agent.position))
                        agent_counter += 1
                    to_remove.append(i)
            agents[d] = [a for i, a in enumerate(agents[d]) if i not in to_remove]
            agents[d-1].extend(new_agents)

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            agents[d] = [a for a in agents[d] if a.consume(decay)]

        # Dispersal (spatial only) - agents move to neighbors
        if spatial and cycle % 10 == 0:
            for d in range(N_DEPTHS):
                for agent in agents[d]:
                    if np.random.random() < 0.1:  # 10% move chance
                        neighbors = get_neighbors(agent.position, GRID_SIZE)
                        if neighbors:
                            agent.position = np.random.choice(neighbors)

        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(agents[d]))

    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    return {
        "seed": seed,
        "spatial": spatial,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)],
        "coexist": depths_alive >= 3
    }

def main():
    print(f"CYCLE 1668: Spatial Structure | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1668001, 1668051))  # 50 seeds

    # Test spatial vs global
    modes = [("Global", False), ("Spatial (10x10)", True)]
    all_results = []

    for name, spatial in modes:
        print(f"\n{name}")
        results = [run_experiment(seed, spatial) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"  → {coexist_count}/{len(results)} coexist ({coexist_count/len(results)*100:.0f}%)")
        print(f"    avg depths: {avg_depths:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("SPATIAL STRUCTURE RESULTS")
    print("=" * 70)

    for name, spatial in modes:
        subset = [r for r in all_results if r["spatial"] == spatial]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"{name:20s}: {rate*100:.0f}% coexist, {avg_depths:.1f} depths")

if __name__ == "__main__":
    main()
