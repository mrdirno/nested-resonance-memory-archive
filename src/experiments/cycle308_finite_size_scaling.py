"""
CYCLE 308: Finite-Size Scaling at Critical Cohesion
Objective: Test how phase transition changes with system size (N agents)
Hypothesis: True phase transitions sharpen with larger N
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

        avg_neighbor_pos = np.zeros(2)
        avg_neighbor_vel = np.zeros(2)
        neighbors = 0

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

def run_sim(n_agents, cohesion, steps=100):
    """Run simulation with variable N"""
    sim = WorldSim()
    agents = [SwarmAgent(f"A{i}", np.random.uniform(0, sim.world_size, 2),
                        energy=np.random.uniform(0.5, 1.5), move_speed=2.0,
                        cohesion_factor=cohesion) for i in range(n_agents)]

    flock_sizes = []
    alive = agents[:]

    for step in range(steps):
        new_alive = []
        for agent in alive:
            survived, flock_size = agent.update(sim.world_size, alive, sim.resources)
            if survived:
                new_alive.append(agent)
                if flock_size > 0:
                    flock_sizes.append(flock_size)
        alive = new_alive
        if not alive: break

        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1

    return {
        "survival_rate": len(alive) / n_agents * 100,
        "avg_flock_size": np.mean(flock_sizes) if flock_sizes else 0,
        "flock_size_var": np.var(flock_sizes) if flock_sizes else 0
    }

def main():
    print("CYCLE 308: FINITE-SIZE SCALING")
    print("=" * 50)
    print("Testing how phase transition scales with system size")

    # System sizes to test
    n_agents_list = [20, 35, 50, 75, 100]

    # Cohesion values around critical point (0.1947)
    critical = 0.1947
    cohesion_values = np.linspace(critical - 0.05, critical + 0.05, 11)

    n_seeds = 8

    results = []

    for n_agents in n_agents_list:
        print(f"\n--- N = {n_agents} agents ---")
        n_results = []

        for cf in cohesion_values:
            seed_results = []
            for seed in range(n_seeds):
                np.random.seed(seed * 1000 + n_agents + int(cf * 10000))
                r = run_sim(n_agents, cf)
                seed_results.append(r)

            # Calculate susceptibility
            sizes = [r["avg_flock_size"] for r in seed_results]
            suscept = np.var(sizes)

            avg = {
                "cohesion": round(cf, 4),
                "avg_flock_size": round(np.mean(sizes), 3),
                "susceptibility": round(suscept, 4)
            }
            n_results.append(avg)

        # Find peak susceptibility for this N
        peak = max(n_results, key=lambda x: x["susceptibility"])

        result = {
            "n_agents": n_agents,
            "peak_cohesion": peak["cohesion"],
            "peak_susceptibility": peak["susceptibility"],
            "peak_flock_size": peak["avg_flock_size"],
            "cohesion_sweep": n_results
        }
        results.append(result)

        print(f"Peak at c={peak['cohesion']:.4f}, suscept={peak['susceptibility']:.2f}, size={peak['avg_flock_size']:.2f}")

    # Analysis
    print("\n" + "=" * 50)
    print("FINITE-SIZE SCALING ANALYSIS")
    print("=" * 50)

    # Check if susceptibility increases with N (signature of true phase transition)
    ns = [r["n_agents"] for r in results]
    suscepts = [r["peak_susceptibility"] for r in results]
    critical_cohesions = [r["peak_cohesion"] for r in results]

    # Linear fit log(suscept) vs log(N)
    log_n = np.log(ns)
    log_s = np.log(np.array(suscepts) + 1)  # +1 to handle zeros
    slope, intercept = np.polyfit(log_n, log_s, 1)

    print(f"\nPeak Susceptibility vs N:")
    for n, s in zip(ns, suscepts):
        print(f"  N={n:3d}: suscept={s:.2f}")

    print(f"\nScaling exponent: γ/ν = {slope:.3f}")

    if slope > 0.3:
        print(f"\n** FINITE-SIZE SCALING CONFIRMED **")
        print(f"   Susceptibility grows with N (exponent: {slope:.2f})")
        print(f"   This is consistent with a true phase transition")
    else:
        print(f"\nWeak or no finite-size scaling (exponent: {slope:.2f})")

    # Check if critical point shifts with N
    critical_shift = np.std(critical_cohesions)
    print(f"\nCritical cohesion stability: std = {critical_shift:.4f}")

    if critical_shift < 0.01:
        print("Critical point is stable across system sizes")
    else:
        print(f"Critical point shifts with N (from {min(critical_cohesions):.4f} to {max(critical_cohesions):.4f})")

    # Save results
    output = {
        "experiment": "C308_finite_size_scaling",
        "parameters": {
            "n_agents_list": n_agents_list,
            "cohesion_range": [round(critical - 0.05, 4), round(critical + 0.05, 4)],
            "seeds": n_seeds,
            "steps": 100
        },
        "results": results,
        "analysis": {
            "scaling_exponent": round(slope, 4),
            "susceptibility_growth": "positive" if slope > 0.3 else "weak",
            "critical_cohesion_std": round(critical_shift, 4),
            "mean_critical_cohesion": round(np.mean(critical_cohesions), 4),
            "finite_size_scaling_confirmed": bool(slope > 0.3)
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c308_finite_size_scaling.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to experiments/results/c308_finite_size_scaling.json")
    print("\n--- C308 Complete ---")

if __name__ == "__main__":
    main()
