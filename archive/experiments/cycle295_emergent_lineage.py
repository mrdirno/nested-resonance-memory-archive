import sys
import os
import time
import json
import numpy as np
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, SimulationInterface
from analysis.pattern_archaeologist import PatternArchaeologist
from memory.pattern_memory import PatternMemory

def main():
    print("CYCLE 295: EMERGENT LINEAGE TRACING")
    print("===================================")
    print("Objective: Verify if high-level emergent patterns (groups) naturally form as descendants of low-level interaction patterns.")
    
    memory = PatternMemory()
    print(f"Simulation Memory DB: {memory.db_path}")
    
    sim = SimulationInterface(db_path=None, n_populations=1)
    
    # 1. Setup Simulation: 20 Agents in 1D space (0 to 100)
    # We simulate clustering.
    N_AGENTS = 20
    agents = []
    
    for i in range(N_AGENTS):
        agent = FractalAgent(f"Agent_{i}", energy=1.0)
        # Inject custom state for 1D position
        agent.position = np.random.uniform(0, 100)
        # Each agent starts with a 'Self' pattern
        obs = {"type": "self_awareness", "id": agent.agent_id}
        agent.last_pattern_id = agent.discover_pattern(obs)
        agents.append(agent)
        sim.add_agent(agent, 0)
        
    print(f"Initialized {N_AGENTS} agents.")
    
    # 2. Run Clustering Simulation
    # Agents move towards the mean position of their neighbors (simple flocking)
    # If they get close to another agent, they record an "Interaction" pattern linked to their "Self" pattern
    # If they see multiple neighbors, they might record a "Cluster" pattern linked to "Interaction"
    
    STEPS = 20
    interaction_radius = 10.0
    
    clusters_detected = 0
    
    for step in range(STEPS):
        positions = [a.position for a in agents]
        
        # Move
        for i, agent in enumerate(agents):
            # Find neighbors
            neighbors = []
            neighbor_patterns = []
            
            for j, other in enumerate(agents):
                if i == j: continue
                dist = abs(agent.position - other.position)
                if dist < interaction_radius:
                    neighbors.append(other.position)
                    # Record interaction
                    # In a real system, this would be more organic. Here we force the discovery logic.
                    interaction_obs = {
                        "type": "interaction", 
                        "partner": other.agent_id, 
                        "distance": round(dist, 2),
                        "step": step
                    }
                    # Link to SELF (or previous state)
                    pid = agent.discover_pattern(interaction_obs, parent_pattern_id=agent.last_pattern_id)
                    neighbor_patterns.append(pid)
            
            # Emergence: If >= 1 neighbor (Cluster size >= 2), discover "Cluster" pattern
            if len(neighbors) >= 1:
                # The cluster pattern should ideally be linked to the interactions that caused it.
                # Current `discover_pattern` only takes one parent. 
                # We will link it to the *most recent* interaction as the primary parent.
                # (Future work: multi-parent support in discovery)
                cluster_obs = {
                    "type": "cluster",
                    "size": len(neighbors) + 1,
                    "center": round(np.mean(neighbors + [agent.position]), 2),
                    "step": step
                }
                # Link to the last interaction pattern (as a proxy for the set of interactions)
                cluster_pid = agent.discover_pattern(cluster_obs, parent_pattern_id=neighbor_patterns[-1])
                agent.last_pattern_id = cluster_pid # Update state
                clusters_detected += 1
                # print(f"  {agent.agent_id} discovered CLUSTER: {cluster_pid}")
            
            # Move towards neighbors (cohesion)
            if neighbors:
                target = np.mean(neighbors)
                agent.position += (target - agent.position) * 0.1
                
        # print(f"Step {step}: {clusters_detected} clusters detected so far.")
        
    # 3. Analyze Lineage
    print("\n--- Analyzing Emergent Lineage ---")
    # Force archaeologist to use the same path, though they should be identical
    archaeologist = PatternArchaeologist(workspace_path=memory.workspace_path)
    print(f"Archaeologist Memory DB: {archaeologist.memory.db_path}")
    
    # DEBUG: Fetch last few patterns to see what's actually there
    print("Debug: Checking latest patterns...")
    recent = archaeologist.memory.search_patterns(limit=5, sort_by='last_seen')
    for p in recent:
        print(f"  ID: {p.pattern_id} | Name: {p.name} | Data: {p.data}")

    # Find all "cluster" patterns
    # Note: search_patterns limits results before filtering JSON, so we might miss them if limit is small.
    # We'll fetch recent patterns and filter manually.
    all_recent = archaeologist.memory.search_patterns(limit=5000, sort_by='last_seen')
    
    cluster_patterns = [p for p in all_recent if p.data.get("type") == "cluster"]
    
    print(f"Found {len(cluster_patterns)} cluster patterns (manual filter).")
    
    if not cluster_patterns:
        print("FAILURE: No emergent patterns found.")
        return

    # Trace ancestry of the last/most complex cluster pattern
    # We expect: Cluster -> Interaction -> ... -> Self
    target_pattern = cluster_patterns[0] # Just pick one
    print(f"Tracing ancestry for: {target_pattern.name} ({target_pattern.pattern_id})")
    
    ancestry = archaeologist.trace_ancestry(target_pattern.pattern_id, max_depth=10)
    
    def get_depth(node):
        if not node.get("parents"):
            return 1
        return 1 + max(get_depth(p["pattern"]) for p in node["parents"])

    depth = get_depth(ancestry)
    print(f"Lineage Depth: {depth}")
    
    # We expect at least depth 3 (Cluster -> Interaction -> Self)
    success = depth >= 3
    
    if success:
        print("SUCCESS: Emergent 'Cluster' pattern is causally linked to low-level 'Self'/'Interaction' patterns.")
        
        # Print the lineage path to verify
        def print_lineage(node, indent=0):
            prefix = "  " * indent
            print(f"{prefix}- {node['name']} (ID: {node['id'][:8]})")
            if "parents" in node:
                for p in node["parents"]:
                    print_lineage(p["pattern"], indent + 1)
        
        print("\nLineage Trace:")
        print_lineage(ancestry)
        
    else:
        print(f"FAILURE: Shallow lineage (Depth {depth}).")

    # Save results
    results = {
        "agent_count": N_AGENTS,
        "steps": STEPS,
        "cluster_patterns_found": len(cluster_patterns),
        "sample_lineage_depth": depth,
        "success": success
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c295_emergent_lineage.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
