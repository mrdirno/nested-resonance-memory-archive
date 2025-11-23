"""
CYCLE 375: Multi-Parameter Emergence Control
Objective: Map 2D parameter space (cohesion × sight_range) to find optimal combinations.
Builds on C374 single-parameter mapping.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, SimulationInterface
from memory.pattern_memory import PatternMemory

# Agent and Sim classes from C374
class Resource:
    def __init__(self, id, pos, amount=10.0):
        self.id = id
        self.pos = np.array(pos, dtype=float)
        self.amount = amount
        self.initial_amount = amount

class SwarmAgent(FractalAgent):
    def __init__(self, agent_id, pos, energy=1.0, sight_range=15.0,
                 move_speed=1.0, metabolic_rate=0.01, cohesion_factor=0.05):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2)
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        self.cohesion_factor = cohesion_factor
        self.flock_count = 0

    def update(self, sim, all_agents, resources):
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False

        neighbors = [a for a in all_agents if a != self and
                    np.linalg.norm(self.pos - a.pos) < self.sight_range]

        if neighbors:
            avg_pos = np.mean([n.pos for n in neighbors], axis=0)
            avg_vel = np.mean([n.vel for n in neighbors], axis=0)
            cohesion = (avg_pos - self.pos) * self.cohesion_factor
            alignment = (avg_vel - self.vel) * 0.1
            self.vel = (self.vel + cohesion + alignment).clip(-self.move_speed, self.move_speed)
            if len(neighbors) > 2:
                self.flock_count += 1

        # Resource seeking
        closest = min((r for r in resources if r.amount > 0),
                     key=lambda r: np.linalg.norm(self.pos - r.pos), default=None)
        if closest:
            dist = np.linalg.norm(self.pos - closest.pos)
            if dist < self.sight_range * 2:
                attract = (closest.pos - self.pos) * 0.1
                self.vel = (self.vel + attract).clip(-self.move_speed, self.move_speed)
                if dist < 2.0:
                    consumed = min(0.1, closest.amount)
                    self.energy += consumed
                    closest.amount -= consumed

        self.pos = (self.pos + self.vel) % sim.world_size
        return True

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100, 100), db_path=None, n_resources=5):
        super().__init__(db_path=db_path, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = [Resource(f"R{i}", np.random.uniform(0, self.world_size, 2))
                        for i in range(n_resources)]

def run_trial(cohesion, sight_range, n_agents=50, n_steps=100, seed=None):
    if seed:
        np.random.seed(seed)

    sim = WorldSim()
    agents = [SwarmAgent(f"A{i}", np.random.uniform(0, sim.world_size, 2),
                        energy=np.random.uniform(0.5, 1.5), move_speed=2.0,
                        cohesion_factor=cohesion, sight_range=sight_range)
             for i in range(n_agents)]
    for a in agents:
        sim.add_agent(a, 0)

    alive = agents.copy()
    for _ in range(n_steps):
        alive = [a for a in alive if a.update(sim, alive, sim.resources)]
        for r in sim.resources:
            if r.amount < r.initial_amount / 2:
                r.amount += 0.1
        if not alive:
            break

    return {
        "survivors": len(alive),
        "total_flocks": sum(a.flock_count for a in agents),
        "flocks_per_agent": sum(a.flock_count for a in agents) / n_agents
    }

def main():
    print("CYCLE 375: MULTI-PARAMETER EMERGENCE CONTROL")
    print("=" * 55)
    print()

    # Clear patterns
    PatternMemory().clear_patterns()

    # 2D parameter grid
    cohesion_vals = [0.03, 0.05, 0.07, 0.10]
    sight_vals = [10.0, 15.0, 20.0, 25.0]

    results = []
    grid = np.zeros((len(cohesion_vals), len(sight_vals)))

    for i, cohesion in enumerate(cohesion_vals):
        for j, sight in enumerate(sight_vals):
            # Average over 3 trials
            trials = [run_trial(cohesion, sight, seed=42+t) for t in range(3)]
            avg_flocks = np.mean([t["flocks_per_agent"] for t in trials])
            avg_surv = np.mean([t["survivors"] for t in trials])

            grid[i, j] = avg_flocks
            results.append({
                "cohesion": cohesion,
                "sight_range": sight,
                "avg_flocks": round(avg_flocks, 1),
                "avg_survivors": round(avg_surv, 1)
            })
            print(f"C={cohesion:.2f}, S={sight:4.0f}: Flocks={avg_flocks:5.1f}, Surv={avg_surv:4.1f}")

    # Find optimum
    max_idx = np.unravel_index(grid.argmax(), grid.shape)
    opt_cohesion = cohesion_vals[max_idx[0]]
    opt_sight = sight_vals[max_idx[1]]
    opt_flocks = grid[max_idx]

    print("\n" + "=" * 55)
    print("2D HEATMAP (Flocks/Agent)")
    print("=" * 55)

    # Header
    print("         " + "  ".join(f"S={s:4.0f}" for s in sight_vals))
    for i, c in enumerate(cohesion_vals):
        row = "  ".join(f"{grid[i,j]:5.1f}" for j in range(len(sight_vals)))
        print(f"C={c:.2f}: {row}")

    print(f"\nOptimal: Cohesion={opt_cohesion}, Sight={opt_sight} ({opt_flocks:.1f} flocks/agent)")

    # Save
    output = {
        "cycle": 375,
        "grid": grid.tolist(),
        "cohesion_vals": cohesion_vals,
        "sight_vals": sight_vals,
        "results": results,
        "optimal": {
            "cohesion": opt_cohesion,
            "sight_range": opt_sight,
            "flocks_per_agent": round(opt_flocks, 1)
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c375_multiparameter_control.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults saved.")

if __name__ == "__main__":
    main()
