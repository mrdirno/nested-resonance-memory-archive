import sys
import os
import time
import json
import numpy as np
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent
from memory.consolidation_engine import ConsolidationEngine
from memory.pattern_memory import PatternMemory

def retrieve_via_resonance(memory: PatternMemory, start_node: str, goal_node: str, iterations: int = 20, decay: float = 0.9) -> bool:
    """
    Retrieve a path via Spreading Activation (Resonance).
    
    Injects energy into start_node and propagates it through the semantic graph.
    Checks if goal_node accumulates significant energy.
    """
    activations = {start_node: 1.0}
    
    print(f"\n[RESONANCE] Spreading activation from {start_node}...")
    
    for t in range(iterations):
        new_activations = {}
        
        # Decay existing
        for node, energy in activations.items():
            new_activations[node] = new_activations.get(node, 0.0) + (energy * decay)
            
            # Spread to neighbors
            neighbors = memory.get_graph_neighbors(node, min_weight=0.01)
            for neighbor, weight in neighbors:
                # Energy flow = Source Energy * Connection Weight
                # We normalize by number of neighbors to prevent explosion? Or just let it flow?
                # Standard spreading activation: Flow = Energy * Weight
                flow = energy * weight * 0.5 # Damping factor for spread
                new_activations[neighbor] = new_activations.get(neighbor, 0.0) + flow
        
        activations = new_activations
        
        # Check Goal Activation
        goal_energy = activations.get(goal_node, 0.0)
        # print(f"  T={t}: Goal Energy = {goal_energy:.4f}")
        
        if goal_energy > 0.1: # Threshold for "Resonance"
            print(f"  -> RESONANCE DETECTED at Goal (T={t}, E={goal_energy:.4f})")
            return True
            
    print(f"  -> No resonance at Goal after {iterations} iterations. Max E={activations.get(goal_node, 0.0):.4f}")
    return False

def main():
    print("CYCLE 293: RESONANT RETRIEVAL (SPREADING ACTIVATION)")
    print("====================================================")
    
    memory = PatternMemory()
    engine = ConsolidationEngine(memory=memory, workspace_path=str(Path.cwd() / "workspace"))
    agent = FractalAgent("PathFinder_003")
    
    # 1. Wake Phase: Solve Grid Task (0,0) -> (2,2)
    # Re-using logic from C292 to ensure clean state for this run
    print("\n[WAKE] Solving Grid Task (0,0) -> (2,2)...")
    
    start_pos = (0, 0)
    target_pos = (2, 2)
    current_pos = start_pos
    
    root_obs = {"type": "position", "x": current_pos[0], "y": current_pos[1], "desc": "Start"}
    last_pattern_id = agent.discover_pattern(root_obs)
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
        
    print(f"Task Complete. Chain length: {len(chain_ids)}")
    
    # 2. Priming Phase
    print("\n[PRE-SLEEP] Priming Semantic Graph...")
    engine.prime_semantic_graph(initial_weight=0.5)
    
    # 3. Sleep Phase
    print("\n[SLEEP] Consolidating...")
    patterns = [memory.get_pattern(pid) for pid in chain_ids]
    engine.nrem_consolidation(patterns=patterns, duration_cycles=200, frequency_hz=1.0, hebbian_learning_rate=0.1)
    
    # 4. Resonant Retrieval
    print("\n[POST-SLEEP] Attempting Resonant Retrieval...")
    start_node = chain_ids[0]
    goal_node = chain_ids[-1]
    
    success = retrieve_via_resonance(memory, start_node, goal_node)
    
    # 5. Compare with Unrelated Node (Control)
    print("\n[CONTROL] Checking resonance with unrelated node...")
    # Generate a dummy pattern not connected to the chain
    dummy_obs = {"type": "noise", "value": 999}
    dummy_id = agent.discover_pattern(dummy_obs) # No parent
    
    control_resonance = retrieve_via_resonance(memory, start_node, dummy_id)
    
    if success and not control_resonance:
        print("\nSUCCESS: Goal resonated, Control did not. Semantic path is active.")
    else:
        print(f"\nFAILURE: Success={success}, Control={control_resonance}")

    # Save results
    results = {
        "task": "Resonant Retrieval",
        "chain_length": len(chain_ids),
        "resonance_success": success,
        "control_resonance": control_resonance
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c293_resonant_retrieval.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()