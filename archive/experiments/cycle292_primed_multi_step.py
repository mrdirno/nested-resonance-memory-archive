import sys
import os
import time
import json
import numpy as np
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent
from analysis.pattern_archaeologist import PatternArchaeologist
from memory.consolidation_engine import ConsolidationEngine
from memory.pattern_memory import PatternMemory

def main():
    print("CYCLE 292: PRIMED MULTI-STEP REASONING")
    print("======================================")
    
    memory = PatternMemory()
    engine = ConsolidationEngine(memory=memory, workspace_path=str(Path.cwd() / "workspace"))
    agent = FractalAgent("PathFinder_002")
    
    # 1. Wake Phase: Solve Grid Task (0,0) -> (2,2)
    # Smaller grid for cleaner demo
    print("\n[WAKE] Solving Grid Task (0,0) -> (2,2)...")
    
    start_pos = (0, 0)
    target_pos = (2, 2)
    current_pos = start_pos
    
    root_obs = {"type": "position", "x": current_pos[0], "y": current_pos[1], "desc": "Start"}
    last_pattern_id = agent.discover_pattern(root_obs)
    print(f"  Start: {last_pattern_id}")
    
    chain_ids = [last_pattern_id]
    steps = 0
    
    while current_pos != target_pos:
        steps += 1
        next_pos = list(current_pos)
        move = ""
        if current_pos[0] < target_pos[0]:
            next_pos[0] += 1
            move = "EAST"
        elif current_pos[1] < target_pos[1]:
            next_pos[1] += 1
            move = "NORTH"
            
        current_pos = tuple(next_pos)
        
        step_obs = {"type": "action", "move": move, "new_pos": current_pos, "step": steps}
        new_pattern_id = agent.discover_pattern(step_obs, parent_pattern_id=last_pattern_id)
        chain_ids.append(new_pattern_id)
        last_pattern_id = new_pattern_id
        print(f"  Step {steps}: {move} -> {current_pos} ({new_pattern_id})")
        
    print(f"Task Complete. Chain length: {len(chain_ids)}")
    
    # 2. Priming Phase
    print("\n[PRE-SLEEP] Priming Semantic Graph...")
    primed_count = engine.prime_semantic_graph(initial_weight=0.5)
    print(f"  Primed {primed_count} edges.")
    
    # 3. Sleep Phase
    print("\n[SLEEP] Consolidating...")
    patterns = [memory.get_pattern(pid) for pid in chain_ids]
    
    coalitions, metrics = engine.nrem_consolidation(
        patterns=patterns,
        duration_cycles=200,
        frequency_hz=1.0,
        hebbian_learning_rate=0.1
    )
    
    print(f"  Coalitions: {metrics.coalitions_detected}")
    print(f"  Updates: {metrics.hebbian_updates}")
    
    # 4. Post-Sleep Retrieval / Pathfinding
    # Can we find the path from Start to Goal purely via high-weight edges in the semantic graph?
    print("\n[POST-SLEEP] Testing Memory Retrieval...")
    
    start_node = chain_ids[0]
    goal_node = chain_ids[-1]
    
    # Simple greedy search on semantic graph weights
    current_node = start_node
    retrieved_path = [current_node]
    
    print(f"  Starting retrieval from {start_node}...")
    
    found = False
    for _ in range(len(chain_ids) * 2): # Limit steps to prevent loops
        if current_node == goal_node:
            found = True
            break
            
        neighbors = memory.get_graph_neighbors(current_node, min_weight=0.1)
        if not neighbors:
            print("  Dead end (no neighbors).")
            break
            
        # Pick neighbor with highest weight that isn't visited (to avoid simple loops)
        best_next = None
        best_weight = -1.0
        
        for nid, w in neighbors:
            if nid not in retrieved_path and w > best_weight:
                best_weight = w
                best_next = nid
        
        if best_next:
            print(f"    -> {best_next} (w={best_weight:.2f})")
            current_node = best_next
            retrieved_path.append(current_node)
        else:
            print("  Dead end (all neighbors visited).")
            break
            
    if found:
        print("SUCCESS: Retrieved full path from consolidated memory!")
        print(f"  Original Path: {chain_ids}")
        print(f"  Retrieved:     {retrieved_path}")
    else:
        print("FAILURE: Could not retrieve path.")
        
    # Save results
    results = {
        "task": "Primed Multi-Step",
        "original_chain": chain_ids,
        "retrieved_path": retrieved_path,
        "success": found,
        "metrics": {
            "coalitions": metrics.coalitions_detected,
            "updates": metrics.hebbian_updates
        }
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c292_primed_multi_step.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
