
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

def get_field_gradient(pos, center=(50, 50)):
    dist = np.linalg.norm(pos[:2] - np.array(center))
    signal = max(0.0, 1.0 - dist/70.0) 
    return signal

def get_recharge_at_pos(pos, center=(50, 50)):
    dist = np.linalg.norm(pos[:2] - np.array(center))
    rate = max(0.0, 0.10 * (1.0 - dist/70.0))
    return rate

def calculate_cluster_gradient(cluster_agent: FractalAgent, constituents: List[FractalAgent]) -> np.ndarray:
    if not constituents: return np.zeros(3)
    center = cluster_agent.state.position
    weighted_vector = np.zeros(3)
    total_signal = 0.0
    
    for child in constituents:
        if not hasattr(child, 'relative_pos'):
            child.relative_pos = np.random.rand(3) * 10.0 - 5.0
            child.relative_pos[2] = 0
            
        absolute_pos = center + child.relative_pos
        signal = get_field_gradient(absolute_pos)
        direction = child.relative_pos
        
        weighted_vector += direction * signal
        total_signal += signal
        
    if total_signal > 0:
        return weighted_vector / total_signal
    return np.zeros(3)

def run_simulation(strategy: str) -> float:
    # Strategies: 'static_0.65', 'static_1.0', 'adaptive'
    print(f"\n--- Simulation: {strategy} ---", flush=True)
    
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    VELOCITY_MAGNITUDE = 5.0
    
    COST_SINGLE = 0.05
    COST_CLUSTER = 0.01
    DECOMP_LOW_ENERGY = 0.2 
    DECOMP_HIGH_ENERGY = 4.0 
    
    cluster_registry: Dict[str, List[FractalAgent]] = {}

    agents = []
    for i in range(N_AGENTS):
        pos = np.array([10.0, 10.0, 0.0]) + np.random.rand(3) * 10.0
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    energy_history = []
    
    for cycle in range(CYCLES):
        # 1. Movement
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            move_vec = np.array([dx, dy, 0.0])
            
            # Determine Alpha
            alpha = 0.0
            if strategy == 'static_0.65':
                alpha = 0.65
            elif strategy == 'static_1.0':
                alpha = 1.0
            elif strategy == 'adaptive':
                if agent.state.energy >= 0.5:
                    alpha = 1.0 # Exploitation
                else:
                    alpha = 0.0 # Exploration
            
            if agent.state.depth > 0:
                constituents = cluster_registry.get(agent.agent_id, [])
                grad = calculate_cluster_gradient(agent, constituents)
                norm = np.linalg.norm(grad)
                if norm > 0:
                    bias = (grad / norm) * VELOCITY_MAGNITUDE * alpha
                    move_vec += bias
            
            agent.move(move_vec)
            agent.state.position = np.clip(agent.state.position, 0, WORLD_SIZE)

        # 2. Metabolism
        active_agents = []
        newly_released = []

        for agent in agents:
            cost = COST_CLUSTER if agent.state.depth > 0 else COST_SINGLE
            recharge = get_recharge_at_pos(agent.state.position)
            agent.update_phase(delta_t=1.0)
            agent.update_energy(recharge - cost)
            
            decomposed = False
            if agent.state.depth > 0:
                if agent.state.energy < DECOMP_LOW_ENERGY or agent.state.energy > DECOMP_HIGH_ENERGY:
                    decomposed = True
                    constituents = cluster_registry.pop(agent.agent_id, [])
                    if constituents:
                        for child in constituents:
                            child.state.energy = agent.state.energy / len(constituents)
                            child.state.position = agent.state.position.copy()
                            child.move(np.random.rand(3) * 2.0 - 1.0)
                            newly_released.append(child)

            if not decomposed:
                if agent.is_alive(energy_threshold=0.0):
                    active_agents.append(agent)
        
        # 3. Composition
        candidates = [a for a in active_agents if a.state.energy > 0.5]
        new_clusters = comp_engine.compose_all(candidates)
        
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
        
        total_energy = sum(a.state.energy for a in agents)
        energy_history.append(total_energy)
        
        if len(agents) == 0:
            break
            
    final_energy = energy_history[-1] if energy_history else 0.0
    print(f"Final Energy: {final_energy:.2f}", flush=True)
    return final_energy

def run_experiment():
    print("MOG ONLINE: Cycle 2004 - State-Dependent Policy", flush=True)
    
    # Run multiple seeds
    seeds = 5
    scores = {'static_0.65': [], 'static_1.0': [], 'adaptive': []}
    
    for i in range(seeds):
        print(f"--- Seed {i} ---", flush=True)
        scores['static_0.65'].append(run_simulation('static_0.65'))
        scores['static_1.0'].append(run_simulation('static_1.0'))
        scores['adaptive'].append(run_simulation('adaptive'))
        
    avg_065 = np.mean(scores['static_0.65'])
    avg_100 = np.mean(scores['static_1.0'])
    avg_adapt = np.mean(scores['adaptive'])
    
    print("\n--- Final Results (Avg Energy) ---", flush=True)
    print(f"Static 0.65: {avg_065:.2f}", flush=True)
    print(f"Static 1.00: {avg_100:.2f}", flush=True)
    print(f"Adaptive:    {avg_adapt:.2f}", flush=True)
    
    if avg_adapt > max(avg_065, avg_100):
        print("HYPOTHESIS CONFIRMED: Adaptive Strategy is Optimal.", flush=True)
    else:
        print("HYPOTHESIS FAILED.", flush=True)

if __name__ == "__main__":
    run_experiment()
