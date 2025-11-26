import sys
import os
sys.path.append('.')

from src.memory.pattern_memory import PatternMemory

def test_decomposition():
    print("Initializing Memory...")
    memory = PatternMemory(dimension=1024, partitions=8)
    
    key = "Composite_Key"
    constituents = ["Part_A", "Part_B", "Part_C"]
    
    print(f"\nStoring {constituents} bound to '{key}'...")
    for part in constituents:
        memory.store(key, part)
        
    print("\nAttempting Decomposition (retrieve_multiple)...")
    results = memory.retrieve_multiple(key, threshold=0.15)
    
    print(f"Results: {results}")
    
    missing = set(constituents) - set(results)
    if not missing:
        print("\nCONCLUSION: Decomposition Successful! All parts retrieved.")
    else:
        print(f"\nCONCLUSION: Decomposition Failed. Missing: {missing}")

if __name__ == "__main__":
    test_decomposition()
