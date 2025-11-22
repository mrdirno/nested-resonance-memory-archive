#!/usr/bin/env python3
"""
Test Advanced Pattern Search
================================

Demonstrates and validates the enhanced `search_patterns` method in the
`PatternMemory` class.
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "memory"))

from pattern_memory import PatternMemory, PatternType

def main():
    """Run the advanced pattern search tests."""
    print("=" * 80)
    print("Testing Advanced Pattern Search in PatternMemory")
    print("=" * 80)

    # Initialize memory
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    memory = PatternMemory(workspace_path=workspace)
    print(f"Loaded {memory.get_statistics()['total_patterns']} patterns from memory.db")

    # --- Test 1: Search by name_like ---
    print("\n--- Test 1: Search for patterns with 'CPU' in the name ---")
    cpu_patterns = memory.search_patterns(name_like="CPU")
    if cpu_patterns:
        print(f"Found {len(cpu_patterns)} patterns:")
        for p in cpu_patterns:
            print(f"  - {p.name} (ID: {p.pattern_id})")
    else:
        print("  No patterns found.")

    # --- Test 2: Search by data_query ---
    print("\n--- Test 2: Search for patterns with mechanism 'bistable_attractor' ---")
    bistable_patterns = memory.search_patterns(data_query={'mechanism': 'bistable_attractor'})
    if bistable_patterns:
        print(f"Found {len(bistable_patterns)} patterns:")
        for p in bistable_patterns:
            print(f"  - {p.name} (ID: {p.pattern_id})")
    else:
        print("  No patterns found.")

    # --- Test 3: Search with sorting ---
    print("\n--- Test 3: Search for patterns sorted by occurrences (DESC) ---")
    most_frequent = memory.search_patterns(sort_by='occurrences', limit=5)
    if most_frequent:
        print("Top 5 most frequent patterns:")
        for p in most_frequent:
            print(f"  - {p.name} (Occurrences: {p.occurrences})")
    else:
        print("  No patterns found.")

    # --- Test 4: Combined Search ---
    print("\n--- Test 4: Combined search for 'emergence' type with confidence > 0.9 ---")
    high_conf_emergence = memory.search_patterns(
        pattern_type=PatternType.EMERGENCE,
        min_confidence=0.9
    )
    if high_conf_emergence:
        print(f"Found {len(high_conf_emergence)} high-confidence emergence patterns:")
        for p in high_conf_emergence:
            print(f"  - {p.name} (Confidence: {p.confidence:.2f})")
    else:
        print("  No patterns found.")

if __name__ == '__main__':
    main()
