import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional, Set
from dataclasses import asdict

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine
from src.core.system_entropy import entropy as real_entropy

class SpatialCompositionEngine(CompositionEngine):
    def __init__(self, resonance_threshold: float = 0.7, energy_threshold: float = 0.5, distance_threshold: float = 20.0):
        super().__init__(resonance_threshold, energy_threshold)
        self.distance_threshold = distance_threshold

    def detect_clusters(
        self,
        agents: List[FractalAgent],
        min_cluster_size: int = 2,
        max_cluster_size: Optional[int] = None,
    ) -> List[List[FractalAgent]]:
        if len(agents) < min_cluster_size:
            return []

        depth_groups: Dict[int, List[FractalAgent]] = {}
        for agent in agents:
            depth = agent.state.depth
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(agent)

        all_clusters = []

        for depth, depth_agents in depth_groups.items():
            if len(depth_agents) < min_cluster_size:
                continue

            n = len(depth_agents)
            adjacency_matrix = np.zeros((n, n), dtype=bool)

            for i in range(n):
                for j in range(i + 1, n):
                    agent_i = depth_agents[i]
                    agent_j = depth_agents[j]
                    
                    dist = np.linalg.norm(agent_i.state.position - agent_j.state.position)
                    if dist > self.distance_threshold:
                        continue

                    resonance = abs(agent_i.calculate_resonance(agent_j))
                    if resonance >= self.resonance_threshold:
                        adjacency_matrix[i, j] = True
                        adjacency_matrix[j, i] = True

            visited = set()
            for i in range(n):
                if i in visited:
                    continue

                cluster = [depth_agents[i]]
                visited.add(i)

                for j in range(n):
                    if j in visited:
                        continue
                    
                    is_connected_to_all = True
                    for member in cluster:
                        member_idx = depth_agents.index(member) 
                        if not adjacency_matrix[member_idx, j]:
                            is_connected_to_all = False
                            break
                    
                    if is_connected_to_all:
                        cluster.append(depth_agents[j])
                        visited.add(j)

                if len(cluster) >= min_cluster_size:
                    if max_cluster_size is None or len(cluster) <= max_cluster_size:
                        all_clusters.append(cluster)

        return all_clusters

def run_simulation(use_real_entropy: bool) -> float:
    print(f"\n--- Simulation: Real Entropy = {use_real_entropy} ---", flush=True)
    
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_RATE = 0.02
    COST_SINGLE = 0.10
    COST_CLUSTER = 0.02
    DECOMP_LOW_ENERGY = 0.2 
    DECOMP_HIGH_ENERGY = 4.0 
    
    cluster_registry: Dict[str, List[FractalAgent]] = {}

    # Helper for random
    def get_rand():
        if use_real_entropy:
            return real_entropy.get_float()
        else:
            # Seeded PRNG for "Standard"
            return random.random()

    # Initialize Population
    if not use_real_entropy:
        random.seed(42) # Fixed seed for pseudo
        
    agents = []
    for i in range(N_AGENTS):
        # Use standard random for init to ensure comparable starting positions?
        # Or use entropy for init too?
        # Let's use the specified method for everything.
        
        rx = get_rand()
        ry = get_rand()
        pos = np.array([rx * WORLD_SIZE, ry * WORLD_SIZE, 0.0])
        
        r_phase = get_rand()
        phase = r_phase * 2 * np.pi
        
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=phase,
            position=pos
        )
        agents.append(agent)

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    history = []
    
    for cycle in range(CYCLES):
        # 1. Movement
        for agent in agents:
            theta = get_rand() * 2 * np.pi
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Metabolism
        active_agents = []
        newly_released = []

        for agent in agents:
            cost = COST_CLUSTER if agent.state.depth > 0 else COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            decomposed = False
            if agent.state.depth > 0:
                if agent.state.energy < DECOMP_LOW_ENERGY or agent.state.energy > DECOMP_HIGH_ENERGY:
                    decomposed = True
                    constituents = cluster_registry.pop(agent.agent_id, [])
                    if constituents:
                        for child in constituents:
                            child.state.energy = agent.state.energy / len(constituents)
                            child.state.position = agent.state.position.copy()
                            
                            # Kick
                            kx = get_rand() * 2.0 - 1.0
                            ky = get_rand() * 2.0 - 1.0
                            child.move(np.array([kx, ky, 0.0]))
                            newly_released.append(child)

            if not decomposed:
                if agent.is_alive(energy_threshold=0.0):
                    active_agents.append(agent)
        
        # 3. Composition
        new_clusters = comp_engine.compose_all(active_agents)
        
        consumed_ids = set()
        for cluster in new_clusters:
            constituents = []
            for child_id in cluster.state.children_ids:
                found = next((a for a in agents if a.agent_id == child_id), None)
                if found:
                    constituents.append(found)
                    consumed_ids.add(child_id)
            cluster_registry[cluster.agent_id] = constituents
            
        agents = [a for a in active_agents if a.agent_id not in consumed_ids] + new_clusters + newly_released
        
        active_count = len(agents)
        dormant_count = sum(len(v) for v in cluster_registry.values())
        total_pop = active_count + dormant_count
        history.append(total_pop)
        
        if total_pop == 0:
            break
            
    final_pop = history[-1] if history else 0
    print(f"Final Population: {final_pop}", flush=True)
    
    # Calculate Entropy of Outcome (Variance across multiple runs needed, but here we check magnitude)
    return final_pop

def run_experiment():
    print("MOG ONLINE: Cycle 2071 - Continuous Reality", flush=True)
    
    # Run 5 seeds of Pseudo
    pseudo_results = []
    for i in range(5):
        # Reseed for pseudo variation
        random.seed(i)
        res = run_simulation(use_real_entropy=False)
        pseudo_results.append(res)
        
    # Run 5 runs of Real
    real_results = []
    for i in range(5):
        res = run_simulation(use_real_entropy=True)
        real_results.append(res)
        
    avg_p = np.mean(pseudo_results)
    avg_r = np.mean(real_results)
    var_p = np.var(pseudo_results)
    var_r = np.var(real_results)
    
    print("\n--- Comparison ---", flush=True)
    print(f"Pseudo-Random (Seed): Mean {avg_p:.2f}, Var {var_p:.2f}", flush=True)
    print(f"Real-Entropy (System): Mean {avg_r:.2f}, Var {var_r:.2f}", flush=True)
    
    if var_r > var_p:
        print("HYPOTHESIS CONFIRMED: Real Entropy introduces higher variance (True Unpredictability).", flush=True)
    else:
        print("HYPOTHESIS FAILED: Pseudo-Random is noisier.", flush=True)

if __name__ == "__main__":
    run_experiment()
# [SPORE] ID: The Colony
