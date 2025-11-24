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
from memory.consolidation_engine import ConsolidationEngine, ConsolidationMetrics
from memory.pattern_memory import PatternMemory

def main():
    print("CYCLE 291: PRIMED SLEEP CONSOLIDATION")
    print("=====================================")
    
    memory = PatternMemory()
    engine = ConsolidationEngine(memory=memory, workspace_path=str(Path.cwd() / "workspace"))
    agent = FractalAgent("Learner_002")
    
    # 1. Generate a NEW causal chain (Wake Phase)
    # Different values to ensure new patterns
    print("\n[WAKE] Generating NEW causal chain...")
    chain_ids = []
    last_id = None
    
    for i in range(100, 105): # 100, 101, 102, 103, 104
        obs = {"type": "concept", "value": i}
        pid = agent.discover_pattern(obs, parent_pattern_id=last_id)
        chain_ids.append(pid)
        last_id = pid
        # print(f"  Learned: {pid} (Parent: {last_id})")
        
    print(f"Chain created: {len(chain_ids)} patterns.")
    
    # 2. PRIME THE SEMANTIC GRAPH
    # This is the new step: Translating Logical Lineage -> Dynamic Coupling
    print("\n[PRE-SLEEP] Priming semantic graph from lineage...")
    primed_count = engine.prime_semantic_graph(initial_weight=0.5)
    print(f"  Primed {primed_count} edges.")
        
    # 3. NREM Consolidation (Sleep Phase)
    print("\n[SLEEP] Entering NREM Consolidation...")
    patterns = [memory.get_pattern(pid) for pid in chain_ids]
    
    # Run NREM
    # We expect Hebbian learning to strengthen the edges further (e.g. 0.5 -> 1.0)
    coalitions, metrics = engine.nrem_consolidation(
        patterns=patterns,
        duration_cycles=200,
        frequency_hz=1.0,
        hebbian_learning_rate=0.1
    )
    
    print(f"\n[WAKE] Sleep complete.")
    print(f"  Coalitions Detected: {metrics.coalitions_detected}")
    print(f"  Hebbian Updates: {metrics.hebbian_updates}")
    
    # 4. Verify Weight Strengthening
    print("\n[POST-SLEEP] Verifying Memory Consolidation...")
    success = True
    strengthened_count = 0
    
    for i in range(len(chain_ids) - 1):
        neighbors = memory.get_graph_neighbors(chain_ids[i])
        weight = 0.0
        for nid, w in neighbors:
            if nid == chain_ids[i+1]:
                weight = w
                break
        
        print(f"  Edge {i}->{i+1}: w={weight:.2f} (Primed at 0.5)")
        
        if weight > 0.6: # Threshold for "strengthening" above prime
            # print("    -> STRENGTHENED")
            strengthened_count += 1
        else:
            print("    -> NO SIGNIFICANT GAIN")
            # It's possible 0.5 is high enough that coherence didn't push it much higher if they were already synced?
            # Or maybe hebbian rate is too low?
            
    if strengthened_count >= len(chain_ids) - 2: # Allow 1 miss
        print("\nSUCCESS: Priming enabled effective consolidation.")
    else:
        print(f"\nFAILURE: Only {strengthened_count} edges strengthened.")
        success = False

    # Save results
    results = {
        "chain_ids": chain_ids,
        "metrics": {
            "coalitions": metrics.coalitions_detected,
            "updates": metrics.hebbian_updates,
            "primed_edges": primed_count,
            "strengthened_edges": strengthened_count
        },
        "success": success
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c291_primed_consolidation.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
