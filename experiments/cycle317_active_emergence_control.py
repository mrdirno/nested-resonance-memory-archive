"""
CYCLE 317: Active Emergence Control
Objective: Use the Holographic Reasoner (Pilot) to steer the Swarm (Plane) to Criticality.
Hypothesis: Active stewardship can maintain the system at the Edge of Chaos (c=0.195) despite the natural attractor (c=0.044).
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
from memory.pattern_memory import PatternMemory

# --- THE PLANE (Swarm Simulation) ---

class Resource:
    def __init__(self, id, pos, amount=10.0):
        self.id = id
        self.pos = np.array(pos, dtype=float)
        self.amount = amount
        self.initial_amount = amount

class AdaptiveSwarmAgent(FractalAgent):
    """Agent with adaptive cohesion that evolves based on local conditions"""
    def __init__(self, agent_id, pos, energy=1.0, sight_range=15.0, move_speed=1.0,
                 metabolic_rate=0.01, cohesion_factor=0.20):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2)
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        self.cohesion_factor = cohesion_factor
        self.adaptation_rate = 0.01  # How fast cohesion adapts naturally

    def update(self, world_size, all_agents, resources):
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False, 0, self.cohesion_factor

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

        # Natural adaptation (The Drift to 0.044)
        if neighbors < 2:
            # Lonely -> Increase cohesion
            self.cohesion_factor = min(0.5, self.cohesion_factor + self.adaptation_rate)
        elif neighbors > 6:
            # Crowded -> Decrease cohesion
            self.cohesion_factor = max(0.01, self.cohesion_factor - self.adaptation_rate)

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
        return True, flock_size, self.cohesion_factor

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100,100), n_resources=5):
        super().__init__(db_path=None, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = [Resource(f"R{i}", np.random.uniform(0, world_size, 2))
                        for i in range(n_resources)]

# --- THE PILOT (Holographic Reasoner) ---

class PilotAgent:
    def __init__(self, dimension=512):
        self.memory = PatternMemory() # No args as per C316 fix
        self.dimension = dimension
        self.vectors = {}
        
        # Initialize Knowledge Base
        self.create_concept("SUB_CRITICAL")
        self.create_concept("SUPER_CRITICAL")
        self.create_concept("CRITICAL")
        self.create_concept("INCREASE")
        self.create_concept("DECREASE")
        self.create_concept("MAINTAIN")
        self.knowledge_base = self.encode_rules()
        
    def create_concept(self, name):
        phases = np.random.uniform(0, 2*np.pi, self.dimension)
        self.vectors[name] = np.exp(1j * phases)
        
    def encode_rules(self):
        # Rule 1: If Sub-Critical (c < 0.18) -> Increase Cohesion
        r1 = self.vectors["SUB_CRITICAL"] * self.vectors["INCREASE"]
        # Rule 2: If Super-Critical (c > 0.22) -> Decrease Cohesion
        r2 = self.vectors["SUPER_CRITICAL"] * self.vectors["DECREASE"]
        # Rule 3: If Critical (0.18 <= c <= 0.22) -> Maintain
        r3 = self.vectors["CRITICAL"] * self.vectors["MAINTAIN"]
        return r1 + r2 + r3
        
    def perceive(self, current_cohesion):
        """Translate scalar value to holographic concept"""
        if current_cohesion < 0.18:
            return "SUB_CRITICAL"
        elif current_cohesion > 0.22:
            return "SUPER_CRITICAL"
        else:
            return "CRITICAL"
            
    def decide(self, percept_name):
        """Retrieve action via vector unbinding"""
        percept_vec = self.vectors[percept_name]
        percept_inv = np.conj(percept_vec)
        
        # Retrieval: Knowledge * Inverse(Percept)
        retrieved = self.knowledge_base * percept_inv
        
        # Match to actions
        best_action = None
        max_sim = -1.0
        
        for action in ["INCREASE", "DECREASE", "MAINTAIN"]:
            action_vec = self.vectors[action]
            sim = np.real(np.vdot(retrieved, action_vec)) / self.dimension
            if sim > max_sim:
                max_sim = sim
                best_action = action
                
        return best_action, max_sim

# --- THE EXPERIMENT ---

def run_controlled_sim(n_agents=50, steps=300, pilot_interval=10):
    sim = WorldSim()
    agents = [AdaptiveSwarmAgent(f"A{i}", np.random.uniform(0, sim.world_size, 2),
                                 energy=np.random.uniform(0.5, 1.5), move_speed=2.0,
                                 cohesion_factor=0.05) # Start sub-critical
              for i in range(n_agents)]
              
    pilot = PilotAgent(dimension=1024)
    
    cohesion_history = []
    control_actions = []
    alive = agents[:]
    
    print(f"Starting Simulation with {n_agents} agents.")
    print(f"Pilot active every {pilot_interval} steps.")
    
    for step in range(steps):
        # 1. Swarm Update
        new_alive = []
        step_cohesions = []
        for agent in alive:
            survived, _, c = agent.update(sim.world_size, alive, sim.resources)
            if survived:
                new_alive.append(agent)
                step_cohesions.append(c)
        alive = new_alive
        if not alive: break
        
        avg_cohesion = np.mean(step_cohesions)
        cohesion_history.append(avg_cohesion)
        
        # 2. Resource Regrowth
        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1
                
        # 3. Pilot Intervention
        if step % pilot_interval == 0:
            percept = pilot.perceive(avg_cohesion)
            action, conf = pilot.decide(percept)
            control_actions.append((step, percept, action, conf))
            
            # Apply Action (The "Stewardship" Signal)
            # The Pilot nudges the agents' internal parameters
            if action == "INCREASE":
                for agent in alive:
                    agent.cohesion_factor = min(0.5, agent.cohesion_factor + 0.02)
            elif action == "DECREASE":
                for agent in alive:
                    agent.cohesion_factor = max(0.01, agent.cohesion_factor - 0.02)
            # else: MAINTAIN (Do nothing)
            
    return cohesion_history, control_actions

def main():
    print("CYCLE 317: ACTIVE EMERGENCE CONTROL")
    print("===================================")
    
    # Run Control Experiment
    history, log = run_controlled_sim(steps=400)
    
    # Analysis
    final_c = np.mean(history[-50:])
    target_c = 0.195
    distance = abs(final_c - target_c)
    
    print("\n--- Pilot Log (Sample) ---")
    for i in range(0, len(log), 5): # Print every 5th action
        step, percept, action, conf = log[i]
        print(f"Step {step:3d}: Saw {percept:15s} -> Act {action:10s} (Conf: {conf:.4f})")
        
    print("\n--- Result ---")
    print(f"Target Criticality: {target_c}")
    print(f"Final Convergence:  {final_c:.4f}")
    print(f"Error:              {distance:.4f}")
    
    success = distance < 0.05
    if success:
        print(">> SUCCESS: Pilot successfully steered swarm to Criticality.")
    else:
        print(">> FAILURE: Pilot failed to overcome natural attractor.")
        
    # Save results
    results = {
        "cycle": 317,
        "target": target_c,
        "final": final_c,
        "success": bool(success),
        "history": history,
        "log": [{"step":s, "p":p, "a":a, "c":c} for s,p,a,c in log]
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c317_active_control.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n--- C317 Complete ---")

if __name__ == "__main__":
    main()
