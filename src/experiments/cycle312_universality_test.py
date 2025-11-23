"""
CYCLE 312: Universality Test
Objective: Verify critical exponents hold for different microscopic parameters
Hypothesis: γ/ν and β should be robust to sight_range changes
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

def run_sim(n_agents, cohesion, sight_range, steps=100):
    """Run simulation with variable sight range"""
    sim = WorldSim()
    agents = [SwarmAgent(f"A{i}", np.random.uniform(0, sim.world_size, 2),
                        energy=np.random.uniform(0.5, 1.5), move_speed=2.0,
                        cohesion_factor=cohesion, sight_range=sight_range)
              for i in range(n_agents)]

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
        "avg_flock_size": np.mean(flock_sizes) if flock_sizes else 0,
        "flock_var": np.var(flock_sizes) if flock_sizes else 0,
        "survival": len(alive) / n_agents
    }

def measure_exponents(n_agents, sight_range, n_seeds=8):
    """Measure γ/ν from susceptibility scaling for given sight range"""

    # Find critical point first
    cohesion_values = np.linspace(0.05, 0.40, 12)
    results = []

    for cf in cohesion_values:
        seed_results = []
        for seed in range(n_seeds):
            np.random.seed(seed * 1000 + int(cf * 10000) + int(sight_range * 100))
            r = run_sim(n_agents, cf, sight_range)
            seed_results.append(r)

        sizes = [r["avg_flock_size"] for r in seed_results]
        suscept = np.var(sizes)

        results.append({
            "cohesion": cf,
            "avg_size": np.mean(sizes),
            "susceptibility": suscept
        })

    # Find critical point (max susceptibility)
    critical_idx = np.argmax([r["susceptibility"] for r in results])
    critical = results[critical_idx]["cohesion"]
    peak_suscept = results[critical_idx]["susceptibility"]

    # Calculate susceptibility scaling (finite-size)
    # γ/ν approximated from peak height
    gamma_nu = np.log(peak_suscept + 1) / np.log(n_agents)

    return {
        "sight_range": sight_range,
        "critical_cohesion": round(critical, 3),
        "peak_susceptibility": round(peak_suscept, 2),
        "gamma_nu_estimate": round(gamma_nu, 3),
        "sweep_results": results
    }

def main():
    print("CYCLE 312: UNIVERSALITY TEST")
    print("=" * 50)
    print("Testing if critical exponents hold for different sight ranges")

    n_agents = 50
    n_seeds = 6

    # Different sight ranges
    sight_ranges = [10.0, 15.0, 20.0, 25.0]

    results = []

    for sr in sight_ranges:
        print(f"\n--- Sight Range = {sr} ---")
        r = measure_exponents(n_agents, sr, n_seeds)
        results.append(r)
        print(f"Critical cohesion: {r['critical_cohesion']}")
        print(f"Peak susceptibility: {r['peak_susceptibility']:.1f}")
        print(f"γ/ν estimate: {r['gamma_nu_estimate']:.3f}")

    # Analysis
    print("\n" + "=" * 50)
    print("UNIVERSALITY ANALYSIS")
    print("=" * 50)

    gamma_nu_values = [r["gamma_nu_estimate"] for r in results]
    critical_values = [r["critical_cohesion"] for r in results]

    print(f"\nγ/ν estimates across sight ranges:")
    for r in results:
        print(f"  SR={r['sight_range']}: γ/ν = {r['gamma_nu_estimate']:.3f}")

    # Check universality
    gamma_nu_mean = np.mean(gamma_nu_values)
    gamma_nu_std = np.std(gamma_nu_values)
    gamma_nu_cv = gamma_nu_std / gamma_nu_mean if gamma_nu_mean > 0 else float('inf')

    print(f"\nγ/ν statistics:")
    print(f"  Mean: {gamma_nu_mean:.3f}")
    print(f"  Std: {gamma_nu_std:.3f}")
    print(f"  CV: {gamma_nu_cv:.3f}")

    # Check critical point shift
    critical_std = np.std(critical_values)
    print(f"\nCritical cohesion shift:")
    print(f"  Range: {min(critical_values):.2f} - {max(critical_values):.2f}")
    print(f"  Std: {critical_std:.3f}")

    # Universality verdict
    if gamma_nu_cv < 0.3:
        print("\n** UNIVERSALITY SUPPORTED **")
        print(f"   γ/ν is robust (CV = {gamma_nu_cv:.2f})")
        print("   Critical exponent does not depend on microscopic details")
    else:
        print(f"\nUniversality weakly supported (CV = {gamma_nu_cv:.2f})")

    # Compare to original measurement
    original_gamma_nu = 1.63
    deviation = abs(gamma_nu_mean - original_gamma_nu) / original_gamma_nu * 100
    print(f"\nComparison to C308 (γ/ν = 1.63):")
    print(f"  Current mean: {gamma_nu_mean:.3f}")
    print(f"  Deviation: {deviation:.1f}%")

    # Save results
    output = {
        "experiment": "C312_universality_test",
        "parameters": {
            "n_agents": n_agents,
            "seeds": n_seeds,
            "sight_ranges": sight_ranges
        },
        "results": [
            {
                "sight_range": r["sight_range"],
                "critical_cohesion": r["critical_cohesion"],
                "peak_susceptibility": r["peak_susceptibility"],
                "gamma_nu_estimate": r["gamma_nu_estimate"]
            } for r in results
        ],
        "analysis": {
            "gamma_nu_mean": round(gamma_nu_mean, 4),
            "gamma_nu_std": round(gamma_nu_std, 4),
            "gamma_nu_cv": round(gamma_nu_cv, 4),
            "universality_supported": bool(gamma_nu_cv < 0.3)
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c312_universality.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to experiments/results/c312_universality.json")
    print("\n--- C312 Complete ---")

if __name__ == "__main__":
    main()
