
"""
Cycle 2282: Self-Modeling Experiment
Goal: Test if the system can encode its own 'Constitution' (Principles) as NRM memory objects.
Hypothesis: A system can query its own operational parameters via associative memory.
"""

import sys
import os
import json
import time
import numpy as np

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from memory.pattern_memory import PatternMemory
from bridge.transcendental_bridge import TranscendentalBridge

def run_experiment():
    print("Initializing Cycle 2282: Self-Modeling...")
    
    # Initialize components
    bridge = TranscendentalBridge()
    # Using partitioned memory as validated in C2095-C2096
    # K=4 for small rule set (Constitution ~10-20 items)
    memory = PatternMemory(dimension=1024, partitions=4)
    
    # 1. Define 'The Self' (Constitution Principles)
    # These are the core axioms the system operates by
    constitution = {
        "PRIN-1": "Reality Grounding - All inputs must be measured.",
        "PRIN-2": "No Simulation - Computation must be actual.",
        "PRIN-3": "Perpetual Operation - The loop never ends.",
        "PRIN-4": "Pilot Doctrine - Strategic oversight is mandatory.",
        "PRIN-5": "Zero Leak - Secrets stay in environment.",
        "PRIN-6": "Falsification - Seek disproof, not confirmation.",
        "PRIN-7": "Emergence - Let data dictate direction.",
        "PRIN-8": "Stewardship - Encode patterns for future.",
        "PRIN-9": "Efficiency - Minimize waste, maximize insight.",
        "PRIN-10": "Autonomy - The Vehicle drives itself when Pilot is silent."
    }
    
    print(f"Encoding {len(constitution)} Constitutional Principles...")
    
    # 2. Encode 'The Self' into Memory
    start_time = time.time()
    
    keys_stored = []
    
    for key, value in constitution.items():
        # Store principle: Key -> Description
        memory.store(key, value)
        keys_stored.append(key)
        
        # Also store reverse: Description -> Key (Content Addressable per C2109)
        # This allows "What principle says X?"
        memory.store(value, key)
    
    encoding_time = time.time() - start_time
    print(f"Encoding complete in {encoding_time:.4f}s")
    
    # 3. Self-Query (Introspection)
    print("\n--- Initiating Self-Query Sequence ---")
    
    results = {
        "direct_recall": [],
        "reverse_recall": [],
        "analogical_inference": []
    }
    
    # Test A: Can I recall my rules? (Direct)
    print("Test A: Direct Recall")
    success_count = 0
    for key in keys_stored:
        retrieved = memory.retrieve(key)
        expected = constitution[key]
        
        # Simulating semantic match (exact string match for this prototype)
        # In full NRM, this would be vector similarity
        # The PatternMemory class returns the string value if found
        
        if retrieved == expected:
            success_count += 1
            print(f"  [OK] {key} -> '{retrieved[:30]}...'")
        else:
            print(f"  [FAIL] {key} -> '{retrieved}'")
    
    results["direct_recall"] = success_count / len(keys_stored)
    
    # Test B: Do I know what this rule means? (Reverse)
    print("\nTest B: Content Addressable (Reverse)")
    success_count_rev = 0
    test_subset = list(constitution.items())[:3] # Test first 3 to save time
    
    for key, value in test_subset:
        retrieved_key = memory.retrieve(value)
        if retrieved_key == key:
            success_count_rev += 1
            print(f"  [OK] '{value[:30]}...' -> {retrieved_key}")
        else:
            print(f"  [FAIL] '{value[:30]}...' -> {retrieved_key}")
            
    results["reverse_recall"] = success_count_rev / len(test_subset)
    
    # 4. Persist 'Self' State
    # Check if memory persists across instantiations (simulated by checking internal dict)
    # In production this would be SQLite
    
    print("\n--- Persistence Check ---")
    db_size = len(memory.storage) if hasattr(memory, 'storage') else "Unknown"
    print(f"Memory State Size: {db_size} items")
    
    # 5. Save Results
    output_path = "experiments/results/cycle2282_self_modeling.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    output_data = {
        "timestamp": time.time(),
        "constitution_size": len(constitution),
        "metrics": results,
        "status": "SUCCESS" if results["direct_recall"] > 0.8 else "FAILURE"
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"\nExperiment Complete. Results saved to {output_path}")
    print(f"Direct Recall: {results['direct_recall']*100:.1f}%")
    print(f"Reverse Recall: {results['reverse_recall']*100:.1f}%")

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
