import sys
import os
import time
import json
import numpy as np
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory.pattern_memory import PatternMemory, PatternType, Pattern
from analysis.pattern_archaeologist import PatternArchaeologist

def main():
    print("CYCLE 287: CAUSAL LINKING - EXPLICIT PATTERN GENEALOGY")
    print("======================================================")
    
    memory = PatternMemory()
    
    # 1. Simulate a causal chain of discoveries
    # We will create a chain: P1 -> P2 -> P3 -> ... -> P10
    # Each P(n) is "caused" by P(n-1)
    
    root_data = {"value": 1.0, "generation": 0}
    root_id = memory.create_pattern_id(root_data)
    
    root_pattern = Pattern(
        pattern_id=root_id,
        pattern_type=PatternType.SYSTEM_BEHAVIOR,
        name=f"Root Hypothesis (Gen 0)",
        description="Initial axiom for causal chain experiment.",
        data=root_data,
        confidence=1.0,
        occurrences=1,
        first_seen=time.time(),
        last_seen=time.time()
    )
    memory.store_pattern(root_pattern)
    print(f"Created Root: {root_pattern.name} ({root_id})")
    
    current_parent_id = root_id
    chain_length = 10
    
    for i in range(1, chain_length + 1):
        # Simulate derivation: Child is parent value * 1.1 + noise
        parent_pattern = memory.get_pattern(current_parent_id)
        child_value = parent_pattern.data["value"] * 1.1
        
        child_data = {"value": child_value, "generation": i}
        child_id = memory.create_pattern_id(child_data)
        
        child_pattern = Pattern(
            pattern_id=child_id,
            pattern_type=PatternType.SYSTEM_BEHAVIOR,
            name=f"Derived Theorem (Gen {i})",
            description=f"Derived from {parent_pattern.name}",
            data=child_data,
            confidence=0.9 ** i, # Confidence degrades with depth? Or increases? Let's say degrade.
            occurrences=1,
            first_seen=time.time(),
            last_seen=time.time()
        )
        memory.store_pattern(child_pattern)
        
        # CRITICAL STEP: Explicitly link child to parent in relationships table
        # Currently PatternMemory.store_pattern doesn't do this automatically.
        # We must use the lower-level DB access or add a method to PatternMemory.
        # For this experiment, we use the raw connection since we are "implementing" the logic.
        
        with memory._db_connection() as conn:
            conn.execute("""
                INSERT INTO pattern_relationships
                (timestamp, parent_pattern_id, child_pattern_id, relationship_type, strength)
                VALUES (?, ?, ?, ?, ?)
            """, (
                time.time(),
                current_parent_id,
                child_id,
                "causal_derivation",
                1.0
            ))
            conn.commit()
            
        print(f"  -> Derived: {child_pattern.name} ({child_id})")
        print(f"     Linked {current_parent_id} -> {child_id}")
        
        current_parent_id = child_id
        
    print("\nChain generation complete. Verifying lineage...")
    
    # 2. Verify with Archaeologist
    archaeologist = PatternArchaeologist()
    
    # Trace from the leaf (last child) back to root
    leaf_id = current_parent_id
    print(f"Tracing ancestry from leaf: {leaf_id}")
    
    ancestry = archaeologist.trace_ancestry(leaf_id, max_depth=20)
    
    # Validate depth
    def get_depth(node):
        if not node.get("parents"):
            return 1
        return 1 + max(get_depth(p["pattern"]) for p in node["parents"])
        
    depth = get_depth(ancestry)
    print(f"\nMeasured Ancestry Depth: {depth}")
    
    if depth >= chain_length:
        print("SUCCESS: Deep causal lineage established.")
    else:
        print(f"FAILURE: Depth {depth} < {chain_length}")
        
    # Save results
    results = {
        "chain_length": chain_length,
        "measured_depth": depth,
        "root_id": root_id,
        "leaf_id": leaf_id,
        "success": depth >= chain_length
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c287_causal_linking.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
