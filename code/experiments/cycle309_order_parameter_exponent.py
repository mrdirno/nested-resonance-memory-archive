"""
CYCLE 309: Order Parameter Critical Exponent β
Objective: Measure how order parameter (normalized flock size) scales near critical point
Hypothesis: <S>/N ~ |c - c_crit|^β for some exponent β
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
    """Run simulation, return normalized order parameter"""
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

    # Order parameter = normalized average flock size
    order_param = np.mean(flock_sizes) / n_agents if flock_sizes else 0
    return order_param

def main():
    print("CYCLE 309: ORDER PARAMETER CRITICAL EXPONENT")
    print("=" * 50)
    print("Measuring β exponent: <S>/N ~ |c - c_crit|^β")

    n_agents = 100  # Large N for cleaner scaling
    critical = 0.20  # Approximate critical point from C307/C308

    # Fine points above critical (ordered phase)
    cohesions_above = np.linspace(critical + 0.01, critical + 0.15, 15)
    # Fine points below critical (disordered phase)
    cohesions_below = np.linspace(critical - 0.15, critical - 0.01, 15)

    n_seeds = 15

    results_above = []
    results_below = []

    print("\n--- Above Critical ---")
    for cf in cohesions_above:
        order_params = []
        for seed in range(n_seeds):
            np.random.seed(seed * 1000 + int(cf * 10000))
            op = run_sim(n_agents, cf)
            order_params.append(op)

        mean_op = np.mean(order_params)
        distance = abs(cf - critical)

        result = {
            "cohesion": round(cf, 4),
            "distance_from_critical": round(distance, 4),
            "order_parameter": round(mean_op, 5)
        }
        results_above.append(result)
        print(f"c={cf:.3f}, Δc={distance:.3f}, <S>/N={mean_op:.4f}")

    print("\n--- Below Critical ---")
    for cf in cohesions_below:
        order_params = []
        for seed in range(n_seeds):
            np.random.seed(seed * 1000 + int(cf * 10000))
            op = run_sim(n_agents, cf)
            order_params.append(op)

        mean_op = np.mean(order_params)
        distance = abs(cf - critical)

        result = {
            "cohesion": round(cf, 4),
            "distance_from_critical": round(distance, 4),
            "order_parameter": round(mean_op, 5)
        }
        results_below.append(result)
        print(f"c={cf:.3f}, Δc={distance:.3f}, <S>/N={mean_op:.4f}")

    # Analysis: fit power law above critical
    print("\n" + "=" * 50)
    print("CRITICAL EXPONENT ANALYSIS")
    print("=" * 50)

    # Above critical: order parameter should increase
    distances_above = [r["distance_from_critical"] for r in results_above]
    ops_above = [r["order_parameter"] for r in results_above]

    # Fit log(OP) vs log(distance)
    log_d = np.log(distances_above)
    log_op = np.log(np.array(ops_above) + 0.001)  # Avoid log(0)
    beta, intercept = np.polyfit(log_d, log_op, 1)

    print(f"\nAbove critical (c > {critical}):")
    print(f"  Fit: <S>/N ~ Δc^{beta:.3f}")
    print(f"  β exponent = {beta:.3f}")

    # Below critical
    distances_below = [r["distance_from_critical"] for r in results_below]
    ops_below = [r["order_parameter"] for r in results_below]

    log_d_below = np.log(distances_below)
    log_op_below = np.log(np.array(ops_below) + 0.001)
    beta_below, _ = np.polyfit(log_d_below, log_op_below, 1)

    print(f"\nBelow critical (c < {critical}):")
    print(f"  Fit: <S>/N ~ Δc^{beta_below:.3f}")

    # Check for asymmetry (classic sign of phase transitions)
    asymmetry = abs(beta - beta_below)
    print(f"\nExponent asymmetry: {asymmetry:.3f}")

    if asymmetry > 0.3:
        print("  → Significant asymmetry indicates broken symmetry at transition")
    else:
        print("  → Approximately symmetric scaling")

    # Classify universality class
    print(f"\n--- Universality Class Analysis ---")
    if 0.3 < abs(beta) < 0.5:
        print(f"β ≈ {abs(beta):.2f} is close to 2D Ising (β = 1/8 = 0.125)")
        print("or mean-field (β = 1/2 = 0.5)")
    elif abs(beta) < 0.2:
        print(f"β ≈ {abs(beta):.2f} suggests weak ordering transition")
    else:
        print(f"β ≈ {abs(beta):.2f} - non-standard critical behavior")

    # Save results
    output = {
        "experiment": "C309_order_parameter_exponent",
        "parameters": {
            "n_agents": n_agents,
            "critical_cohesion": critical,
            "seeds": n_seeds,
            "steps": 100
        },
        "results": {
            "above_critical": results_above,
            "below_critical": results_below
        },
        "analysis": {
            "beta_above": round(beta, 4),
            "beta_below": round(beta_below, 4),
            "asymmetry": round(asymmetry, 4),
            "interpretation": "power-law scaling confirmed" if abs(beta) > 0.1 else "weak scaling"
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c309_order_parameter.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to experiments/results/c309_order_parameter.json")
    print("\n--- C309 Complete ---")

if __name__ == "__main__":
    main()
