
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

def run_simulation(clustering_enabled: bool) -> float:
    print(f"\n--- Simulation: Clustering {'Enabled' if clustering_enabled else 'Disabled'} ---", flush=True)
    
    N_AGENTS = 100
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_RATE = 0.02
    COST_SINGLE = 0.02 # Lower cost so they don't die immediately
    
    # PGG Parameters
    CONTRIBUTION_COST = 0.05
    SYNERGY_FACTOR = 3.0
    
    cluster_registry: Dict[str, List[FractalAgent]] = {}
    
    # Strategies: 50% Cooperators, 50% Defectors
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        # Assign Strategy
        agent.strategy = "Cooperator" if i < N_AGENTS // 2 else "Defector"
        agents.append(agent)

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    fraction_cooperators = []
    
    for cycle in range(CYCLES):
        # 1. Movement (Random Walk)
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Composition (If Enabled)
        if clustering_enabled:
            active_agents = [a for a in agents if a.state.depth == 0] # Only singles cluster for simplicity here
            # Filter by energy? Let's say all want to cluster to play the game
            candidates = active_agents 
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
                
            # Update Agents List (Clusters replace Singles)
            # Note: In PGG, the game happens inside the cluster. 
            # Singles play against "Nature" (no game, just recharge/cost).
            
            # Remove singles that clustered
            agents = [a for a in agents if a.agent_id not in consumed_ids] + new_clusters
        
        # 3. PGG Game & Metabolism
        active_agents = []
        newly_released = []

        for agent in agents:
            # Determine if playing PGG
            pgg_payoff = 0.0
            pgg_cost = 0.0
            
            if agent.state.depth > 0:
                # It's a cluster. Play PGG among constituents.
                constituents = cluster_registry.get(agent.agent_id, [])
                if constituents:
                    pot = 0.0
                    contributors = 0
                    
                    # Collect Contributions
                    for child in constituents:
                        if child.strategy == "Cooperator":
                            pot += CONTRIBUTION_COST
                            child.state.energy -= CONTRIBUTION_COST # Pay cost
                            contributors += 1
                            
                    # Distribute Rewards
                    if pot > 0:
                        reward = (pot * SYNERGY_FACTOR) / len(constituents)
                        for child in constituents:
                            child.state.energy += reward
                            
                    # Update Cluster Energy (Sum of Children)
                    agent.state.energy = sum(c.state.energy for c in constituents)
            else:
                # Single Agent
                # No PGG. Just basic metabolism.
                # If Cooperator, maybe pays cost to "Nature" and gets nothing? 
                # Or just doesn't play. Let's say doesn't play.
                pass
            
            # Standard Metabolism
            cost = COST_SINGLE # Clusters don't have inherent efficiency here, benefit comes from PGG
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            # Death / Decomp
            decomposed = False
            if agent.state.depth > 0:
                # Propagate death of constituents
                constituents = cluster_registry.get(agent.agent_id, [])
                surviving_constituents = []
                for child in constituents:
                    # Child metabolism happened above via energy update
                    child.update_energy(RECHARGE_RATE - cost) # Everyone pays metabolic cost
                    if child.state.energy > 0:
                        surviving_constituents.append(child)
                
                cluster_registry[agent.agent_id] = surviving_constituents
                
                if not surviving_constituents:
                    # Cluster died
                    pass 
                elif len(surviving_constituents) == 1:
                    # Cluster broke (only 1 left)
                    decomposed = True
                    newly_released.extend(surviving_constituents)
                else:
                    active_agents.append(agent)
            else:
                # Single
                if agent.state.energy > 0:
                    active_agents.append(agent)
        
        agents = active_agents + newly_released
        
        # Count Strategies (Recursively)
        coop_count = 0
        def_count = 0
        
        def count_strat(agt):
            nonlocal coop_count, def_count
            if agt.state.depth == 0:
                if agt.strategy == "Cooperator": coop_count += 1
                else: def_count += 1
            else:
                children = cluster_registry.get(agt.agent_id, [])
                for c in children: count_strat(c)
                
        for a in agents: count_strat(a)
        
        total = coop_count + def_count
        if total > 0:
            frac = coop_count / total
            fraction_cooperators.append(frac)
        else:
            print(f"Cycle {cycle}: EXTINCTION.", flush=True)
            break
            
    final_frac = fraction_cooperators[-1] if fraction_cooperators else 0.0
    print(f"Final Cooperator Fraction: {final_frac:.2f}", flush=True)
    return final_frac

def run_experiment():
    print("MOG ONLINE: Cycle 2005 - Cooperation Baseline", flush=True)
    
    # Run without Clustering (Random Mixing approximation - actually singles don't play)
    # Wait, if singles don't play, they just die/survive on recharge.
    # To test "Random Mixing", we need a Global PGG where everyone plays with everyone.
    # But our engine is spatial.
    # Control: Clustering Disabled -> Singles don't play -> Neutral Drift (or death).
    # Treatment: Clustering Enabled -> Spatial PGG.
    
    # Actually, if Singles don't play, strategies don't matter for them.
    # We need to see if *inside clusters*, Cooperators win.
    # But Defectors benefit from pot without paying.
    # Within a mixed cluster, Defectors should win (highest payoff).
    # But clusters of pure Cooperators will grow faster/survive longer than clusters of Defectors.
    # This is Simpson's Paradox / Group Selection. 
    
    frac_clustered = run_simulation(clustering_enabled=True)
    
    if frac_clustered > 0.5:
        print("HYPOTHESIS CONFIRMED: Spatial structure favors Cooperation.", flush=True)
    else:
        print("HYPOTHESIS FAILED: Defectors dominated.", flush=True)

if __name__ == "__main__":
    run_experiment()
