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

def main():
    print("CYCLE 289: MULTI-STEP REASONING VIA CAUSAL LINEAGE")
    print("====================================================")
    
    # 1. Setup Grid World Task
    # Goal: Navigate from (0,0) to (3,3)
    # Agent must discover "moves" and link them.
    
    agent = FractalAgent("PathFinder_001")
    print(f"Agent initialized: {agent.agent_id}")
    
    start_pos = (0, 0)
    target_pos = (3, 3)
    
    # Initial Observation
    current_pos = start_pos
    root_obs = {
        "type": "position",
        "x": current_pos[0],
        "y": current_pos[1],
        "description": "Start"
    }
    last_pattern_id = agent.discover_pattern(root_obs)
    print(f"Start Position Recorded: {last_pattern_id}")
    
    path = []
    steps = 0
    
    # Simple greedy navigation to simulate reasoning steps
    while current_pos != target_pos:
        steps += 1
        next_pos = list(current_pos)
        
        # Decide move
        move = ""
        if current_pos[0] < target_pos[0]:
            next_pos[0] += 1
            move = "EAST"
        elif current_pos[1] < target_pos[1]:
            next_pos[1] += 1
            move = "NORTH"
            
        current_pos = tuple(next_pos)
        path.append(move)
        
        # Record Step as a new Pattern linked to the previous one
        step_obs = {
            "type": "action",
            "move": move,
            "new_pos": current_pos,
            "step": steps
        }
        
        # CRITICAL: Linking current step to previous step
        new_pattern_id = agent.discover_pattern(step_obs, parent_pattern_id=last_pattern_id)
        print(f"Step {steps}: Moved {move} -> {current_pos} (Pattern: {new_pattern_id})")
        print(f"   Linked {last_pattern_id} -> {new_pattern_id}")
        
        last_pattern_id = new_pattern_id
        
    print(f"\nGoal Reached! Final Pattern: {last_pattern_id}")
    
    # 2. Verify Reasoning Chain (Lineage)
    print("\n--- Verifying Solution Lineage ---")
    archaeologist = PatternArchaeologist()
    
    # Trace from Goal (Solution) back to Start
    ancestry = archaeologist.trace_ancestry(last_pattern_id, max_depth=20)
    
    def get_depth(node):
        if not node.get("parents"):
            return 1 # Only self
        return 1 + max(get_depth(p["pattern"]) for p in node["parents"])
        
    measured_depth = get_depth(ancestry)
    # Expected depth = Steps + 1 (Start node)
    expected_depth = steps + 1
    
    print(f"Path Length: {steps}")
    print(f"Lineage Depth: {measured_depth}")
    
    success = (measured_depth == expected_depth)
    
    if success:
        print("SUCCESS: Lineage perfectly mirrors the reasoning path.")
    else:
        print(f"FAILURE: Discrepancy detected. Expected {expected_depth}, got {measured_depth}.")
        
    # Save results
    results = {
        "task": "Grid Navigation (0,0) to (3,3)",
        "path": path,
        "steps": steps,
        "lineage_depth": measured_depth,
        "success": success
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c289_multi_step_reasoning.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
