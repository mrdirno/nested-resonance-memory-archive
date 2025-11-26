
import sys
import os
sys.path.append('.')

from src.memory.pattern_memory import PatternMemory
import numpy as np

def test_memory_decay():
    print("Initializing Memory (D=1024, K=1 for isolation)...")
    # Use K=1 to force all items into the same vector, making decay obvious
    memory = PatternMemory(dimension=1024, partitions=1)
    
    items = [f"ITEM_{i}" for i in range(1, 21)] # 20 items
    
    print("\nStoring 20 items sequentially...")
    for i, item in enumerate(items):
        memory.store(item, f"VALUE_{item}")
        # Check Item 1 immediately after storing Item 1 (Control)
        if i == 0:
            res = memory.retrieve("ITEM_1")
            print(f"  Step 1: Retrieved ITEM_1: {res}")

    print("\nRetrieving all items...")
    results = {}
    for item in items:
        res = memory.retrieve(item)
        results[item] = res
        print(f"  {item}: {res}")
    
    # Analyze
    item1_recovered = results["ITEM_1"] == "VALUE_ITEM_1"
    item20_recovered = results["ITEM_20"] == "VALUE_ITEM_20"
    
    print("\nAnalysis:")
    print(f"  First Item Recovered: {item1_recovered}")
    print(f"  Last Item Recovered:  {item20_recovered}")
    
    if item20_recovered and not item1_recovered:
        print("\nCONCLUSION: Decay Bug Detected! (Recency Bias)")
    elif item1_recovered and item20_recovered:
        print("\nCONCLUSION: System Stable (No Decay detected in this range)")
    else:
        print("\nCONCLUSION: General Failure (Capacity exceeded?)")

if __name__ == "__main__":
    test_memory_decay()
