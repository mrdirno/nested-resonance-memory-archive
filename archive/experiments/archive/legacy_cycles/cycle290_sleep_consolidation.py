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
    print("CYCLE 290: SLEEP-DEPENDENT MEMORY CONSOLIDATION")
    print("==============================================")
    
    memory = PatternMemory()
    engine = ConsolidationEngine(memory=memory, workspace_path=str(Path.cwd() / "workspace"))
    agent = FractalAgent("Learner_001")
    
    # 1. Generate a causal chain (Wake Phase)
    print("\n[WAKE] Generating causal chain of patterns...")
    chain_ids = []
    last_id = None
    
    for i in range(5):
        obs = {"type": "concept", "value": i}
        pid = agent.discover_pattern(obs, parent_pattern_id=last_id)
        chain_ids.append(pid)
        last_id = pid
        print(f"  Learned: {pid} (Parent: {last_id})")
        
    print(f"Chain created: {len(chain_ids)} patterns.")
    
    # 2. Check initial weights (Should be weak or non-existent in semantic graph unless implicitly created)
    # Actually, causal linking creates `pattern_relationships`, but `semantic_graph` is separate (for Kuramoto).
    # We need to see if NREM creates semantic graph edges based on causal links or temporal proximity.
    # The current ConsolidationEngine uses `get_graph_neighbors` which uses `semantic_graph`.
    # But `semantic_graph` might be empty.
    # Let's seed the semantic graph with weak connections for the chain to simulate "recent co-activation".
    
    print("\n[PRE-SLEEP] Seeding weak associations...")
    for i in range(len(chain_ids) - 1):
        # Weak association between steps
        memory.store_graph_edge(chain_ids[i], chain_ids[i+1], weight=0.1, weight_type="temporal")
        print(f"  Seeded weak edge: {chain_ids[i]} <-> {chain_ids[i+1]} (w=0.1)")
        
    # 3. NREM Consolidation (Sleep Phase)
    print("\n[SLEEP] Entering NREM Consolidation...")
    patterns = [memory.get_pattern(pid) for pid in chain_ids]
    
    # Run NREM
    # We expect Hebbian learning to strengthen the edges between causally/temporally linked patterns
    # because they will phase-lock due to the weak initial coupling.
    coalitions, metrics = engine.nrem_consolidation(
        patterns=patterns,
        duration_cycles=200, # Enough time to sync
        frequency_hz=1.0,
        hebbian_learning_rate=0.1 # Aggressive learning for demo
    )
    
    print(f"\n[WAKE] Sleep complete.")
    print(f"  Coalitions Detected: {metrics.coalitions_detected}")
    print(f"  Hebbian Updates: {metrics.hebbian_updates}")
    
    # 4. Verify Weight Strengthening
    print("\n[POST-SLEEP] Verifying Memory Consolidation...")
    success = True
    
    for i in range(len(chain_ids) - 1):
        neighbors = memory.get_graph_neighbors(chain_ids[i])
        # Find neighbor j
        weight = 0.0
        for nid, w in neighbors:
            if nid == chain_ids[i+1]:
                weight = w
                break
        
        print(f"  Edge {chain_ids[i]} <-> {chain_ids[i+1]}: w={weight:.2f} (Started at 0.1)")
        
        if weight > 0.15:
            print("    -> STRENGTHENED")
        else:
            print("    -> NO CHANGE (Failed)")
            success = False
            
    if success:
        print("\nSUCCESS: Sleep consolidation successfully strengthened causal chain associations.")
    else:
        print("\nFAILURE: Consolidation did not significantly strengthen connections.")

    # Save results
    results = {
        "chain_ids": chain_ids,
        "metrics": {
            "coalitions": metrics.coalitions_detected,
            "updates": metrics.hebbian_updates
        },
        "success": success
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c290_sleep_consolidation.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
