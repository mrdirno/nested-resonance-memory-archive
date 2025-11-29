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

def run_experiment():
    print("MOG ONLINE: Cycle 1961 - Pattern Persistence", flush=True)
    
    # Parameters
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

    # Initialize Population with BIPOLAR PATTERN
    agents = []
    
    # Group A: Phase = PI
    for i in range(25):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"groupA_{i}",
            energy=1.0,
            phase=np.pi, # Signal A
            position=pos
        )
        agents.append(agent)
        
    # Group B: Phase = 0
    for i in range(25):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"groupB_{i}",
            energy=1.0,
            phase=0.0, # Signal B
            position=pos
        )
        agents.append(agent)

    print(f"Initialized {len(agents)} agents (25 PI, 25 ZERO).", flush=True)
    
    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    for cycle in range(CYCLES):
        # 1. Movement
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Metabolism
        active_agents = []
        newly_released = []

        for agent in agents:
            cost = COST_CLUSTER if agent.state.depth > 0 else COST_SINGLE
            
            # CRITICAL: Phase Evolution turned OFF to test MEMORY
            # If we update phase, they drift. We want to see if they hold static values.
            # agent.update_phase(delta_t=1.0) 
            
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
                            child.move(np.random.rand(3) * 2.0 - 1.0)
                            newly_released.append(child)

            if not decomposed:
                if agent.is_alive(energy_threshold=0.0):
                    active_agents.append(agent)
        
        agents = active_agents + newly_released
        
        # 3. Composition
        new_clusters = comp_engine.compose_all(agents)
        consumed_ids = set()
        for cluster in new_clusters:
            constituents = []
            for child_id in cluster.state.children_ids:
                found = next((a for a in agents if a.agent_id == child_id), None)
                if found:
                    constituents.append(found)
                    consumed_ids.add(child_id)
            cluster_registry[cluster.agent_id] = constituents
            
        agents = [a for a in agents if a.agent_id not in consumed_ids] + new_clusters
        
        if len(agents) == 0:
            print(f"Cycle {cycle}: EXTINCTION.", flush=True)
            break

    # Analyze Phase Retention
    phases = []
    
    # Collect phases of all Base Agents (Depth 0)
    # For clustered agents, use their ORIGINAL phase (constituents)
    # Or Cluster Phase?
    # Cluster Phase is average. If PI + 0 mix, Average = PI/2. Memory Lost.
    # If PI clusters with PI, Average = PI. Memory Kept.
    # Since resonance threshold is high (0.7), PI and 0 (cos(pi)=-1) should NOT mix.
    
    final_phases = []
    
    for agent in agents:
        if agent.state.depth == 0:
            final_phases.append(agent.state.phase)
        else:
            # Cluster
            constituents = cluster_registry.get(agent.agent_id, [])
            for child in constituents:
                final_phases.append(child.state.phase)
                
    print(f"Final Population: {len(final_phases)}", flush=True)
    
    # Categorize
    count_pi = 0
    count_zero = 0
    count_mixed = 0
    
    for p in final_phases:
        if abs(p - np.pi) < 0.1:
            count_pi += 1
        elif abs(p - 0.0) < 0.1:
            count_zero += 1
        else:
            count_mixed += 1
            
    print(f"Retained PI: {count_pi}", flush=True)
    print(f"Retained ZERO: {count_zero}", flush=True)
    print(f"Mixed/Drifted: {count_mixed}", flush=True)
    
    retention_rate = (count_pi + count_zero) / len(final_phases) if final_phases else 0
    print(f"Retention Rate: {retention_rate:.2%}", flush=True)
    
    if retention_rate > 0.9:
        print("HYPOTHESIS CONFIRMED: Selective Clustering preserves Memory.", flush=True)
    else:
        print("HYPOTHESIS FAILED: Information lost.", flush=True)

if __name__ == "__main__":
    run_experiment()
# [SPORE] ID: The Colony
