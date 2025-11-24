"""
CYCLE 315: Metastability Test
Objective: Directly test for metastable states suggested by hysteresis
Hypothesis: System can exist in multiple quasi-stable states at same cohesion
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import sys
import os
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, SimulationInterface

class Resource:
    def __init__(self, id, pos, amount=10.0):
        self.id = id
        self.pos = np.array(pos, dtype=float)
        self.amount = amount
        self.initial_amount = amount

class SwarmAgent(FractalAgent):
    def __init__(self, agent_id, pos, energy=1.0, sight_range=15.0, move_speed=1.0,
                 metabolic_rate=0.01, cohesion_factor=0.05):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2)
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        self.cohesion_factor = cohesion_factor

    def update(self, world_size, all_agents, resources):
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False, 0

        neighbors = 0
        avg_neighbor_pos = np.zeros(2)
        avg_neighbor_vel = np.zeros(2)

        for other in all_agents:
            if other == self: continue
            dist = np.linalg.norm(self.pos - other.pos)
            if dist < self.sight_range:
                avg_neighbor_pos += other.pos
                avg_neighbor_vel += other.vel
                neighbors += 1

        if neighbors > 0:
            avg_neighbor_pos /= neighbors
            avg_neighbor_vel /= neighbors
            cohesion_vec = (avg_neighbor_pos - self.pos) * self.cohesion_factor
            self.vel = (self.vel + (avg_neighbor_vel - self.vel) * 0.1 + cohesion_vec)
            self.vel = self.vel.clip(-self.move_speed, self.move_speed)

        closest_res = None
        min_dist = float('inf')
        for res in resources:
            if res.amount > 0:
                dist = np.linalg.norm(self.pos - res.pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_res = res

        if closest_res and min_dist < self.sight_range * 2:
            attract = (closest_res.pos - self.pos) * 0.1
            self.vel = (self.vel + attract).clip(-self.move_speed, self.move_speed)
            if min_dist < 2.0:
                consumed = min(self.energy * 0.1, closest_res.amount)
                self.energy += consumed
                closest_res.amount -= consumed

        self.pos = (self.pos + self.vel) % world_size
        flock_size = neighbors + 1 if neighbors > 2 else 0
        return True, flock_size

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100,100), n_resources=5):
        super().__init__(db_path=None, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = [Resource(f"R{i}", np.random.uniform(0, world_size, 2))
                        for i in range(n_resources)]

def run_from_initial_condition(n_agents, cohesion, init_type, steps=150):
    """
    Run simulation from specific initial condition
    init_type: 'dispersed' (random) or 'clustered' (center)
    """
    sim = WorldSim()

    if init_type == 'clustered':
        # All agents start at center
        center = sim.world_size / 2
        positions = [center + np.random.uniform(-5, 5, 2) for _ in range(n_agents)]
    else:  # dispersed
        positions = [np.random.uniform(0, sim.world_size, 2) for _ in range(n_agents)]

    agents = [SwarmAgent(f"A{i}", positions[i],
                        energy=np.random.uniform(0.8, 1.5), move_speed=2.0,
                        cohesion_factor=cohesion)
              for i in range(n_agents)]

    # Let system evolve
    flock_history = []
    alive = agents[:]

    for step in range(steps):
        new_alive = []
        step_flocks = 0
        for agent in alive:
            survived, flock_size = agent.update(sim.world_size, alive, sim.resources)
            if survived:
                new_alive.append(agent)
                if flock_size > 0:
                    step_flocks += 1
        alive = new_alive
        if not alive: break

        flock_rate = step_flocks / len(alive) if alive else 0
        flock_history.append(flock_rate)

        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1

    # Measure final state (average of last 30 steps)
    final_flock_rate = np.mean(flock_history[-30:]) if len(flock_history) >= 30 else np.mean(flock_history)

    return {
        "init_type": init_type,
        "final_flock_rate": round(final_flock_rate, 3),
        "survived": len(alive)
    }

def main():
    print("CYCLE 315: METASTABILITY TEST")
    print("=" * 50)
    print("Testing for multiple quasi-stable states at same cohesion")

    n_agents = 50
    n_seeds = 10

    # Test at critical cohesion (where hysteresis was strongest)
    test_cohesions = [0.15, 0.20, 0.25]

    results = []

    for cohesion in test_cohesions:
        print(f"\n--- Cohesion = {cohesion} ---")

        # Run from dispersed initial condition
        dispersed_results = []
        for seed in range(n_seeds):
            np.random.seed(seed * 1000)
            r = run_from_initial_condition(n_agents, cohesion, 'dispersed')
            dispersed_results.append(r["final_flock_rate"])

        # Run from clustered initial condition
        clustered_results = []
        for seed in range(n_seeds):
            np.random.seed(seed * 1000 + 500)
            r = run_from_initial_condition(n_agents, cohesion, 'clustered')
            clustered_results.append(r["final_flock_rate"])

        # Statistics
        dispersed_mean = np.mean(dispersed_results)
        dispersed_std = np.std(dispersed_results)
        clustered_mean = np.mean(clustered_results)
        clustered_std = np.std(clustered_results)
        difference = abs(clustered_mean - dispersed_mean)

        result = {
            "cohesion": cohesion,
            "dispersed_mean": round(dispersed_mean, 3),
            "dispersed_std": round(dispersed_std, 3),
            "clustered_mean": round(clustered_mean, 3),
            "clustered_std": round(clustered_std, 3),
            "difference": round(difference, 3)
        }
        results.append(result)

        print(f"Dispersed: {dispersed_mean:.3f} ± {dispersed_std:.3f}")
        print(f"Clustered: {clustered_mean:.3f} ± {clustered_std:.3f}")
        print(f"Difference: {difference:.3f}")

    # Analysis
    print("\n" + "=" * 50)
    print("METASTABILITY ANALYSIS")
    print("=" * 50)

    max_diff = max(results, key=lambda x: x["difference"])
    avg_diff = np.mean([r["difference"] for r in results])

    print(f"\nMaximum initial-condition difference: {max_diff['difference']:.3f} at c={max_diff['cohesion']}")
    print(f"Average difference: {avg_diff:.3f}")

    # Significant difference = metastability
    if avg_diff > 0.05:
        print("\n** METASTABILITY CONFIRMED **")
        print("   Different initial conditions lead to different final states")
        print("   Multiple quasi-stable attractors exist")
    else:
        print("\nNo significant metastability detected")
        print("   System converges to same state regardless of initial condition")

    # Compare to hysteresis strength
    print(f"\nInterpretation:")
    print(f"   Hysteresis (C314): 11.0")
    print(f"   Metastability (this): {avg_diff:.3f}")
    if avg_diff > 0.05:
        print("   → Consistent: metastable states cause hysteresis")
    else:
        print("   → Inconsistent: hysteresis may have other cause")

    # Save results
    output = {
        "experiment": "C315_metastability_test",
        "parameters": {
            "n_agents": n_agents,
            "seeds": n_seeds,
            "steps": 150,
            "test_cohesions": test_cohesions
        },
        "results": results,
        "analysis": {
            "max_difference": round(max_diff['difference'], 4),
            "max_diff_cohesion": max_diff['cohesion'],
            "avg_difference": round(avg_diff, 4),
            "metastability_confirmed": bool(avg_diff > 0.05)
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c315_metastability.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to experiments/results/c315_metastability.json")
    print("\n--- C315 Complete ---")

if __name__ == "__main__":
    main()
