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
    print("CYCLE 288: INTEGRATED CAUSAL LINEAGE")
    print("=====================================")
    
    # Initialize Agent
    agent = FractalAgent("Explorer_001", energy=10.0)
    print(f"Initialized agent: {agent.agent_id}")
    
    # Simulate a sequence of discoveries where each depends on the last
    # 1. Observation A
    obs_a = {"type": "raw_signal", "value": 42}
    id_a = agent.discover_pattern(obs_a)
    print(f"Discovered A: {id_a}")
    
    # 2. Insight B (Derived from A)
    obs_b = {"type": "insight", "source": id_a, "value": 42 * 2}
    id_b = agent.discover_pattern(obs_b, parent_pattern_id=id_a)
    print(f"Discovered B (from A): {id_b}")
    
    # 3. Hypothesis C (Derived from B)
    obs_c = {"type": "hypothesis", "source": id_b, "prediction": "growth"}
    id_c = agent.discover_pattern(obs_c, parent_pattern_id=id_b)
    print(f"Discovered C (from B): {id_c}")
    
    # 4. Validation D (Derived from C)
    obs_d = {"type": "validation", "source": id_c, "confirmed": True}
    id_d = agent.discover_pattern(obs_d, parent_pattern_id=id_c)
    print(f"Discovered D (from C): {id_d}")
    
    print("\nVerifying Lineage Depth via Archaeologist...")
    archaeologist = PatternArchaeologist()
    ancestry = archaeologist.trace_ancestry(id_d, max_depth=10)
    
    def get_depth(node):
        if not node.get("parents"):
            return 1
        return 1 + max(get_depth(p["pattern"]) for p in node["parents"])
        
    depth = get_depth(ancestry)
    print(f"Measured Ancestry Depth for D: {depth}")
    
    expected_depth = 4 # A -> B -> C -> D
    if depth >= expected_depth:
        print("SUCCESS: Integrated lineage tracking is functional.")
    else:
        print(f"FAILURE: Expected depth {expected_depth}, got {depth}")

    # Save results
    results = {
        "agent_id": agent.agent_id,
        "chain": [id_a, id_b, id_c, id_d],
        "measured_depth": depth,
        "success": depth >= expected_depth
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c288_integrated_lineage.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
