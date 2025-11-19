#!/usr/bin/env python3
"""
NRM V2 Full NREM Consolidation
======================================

Purpose: Run a full NREM consolidation session on all patterns in memory.

This script demonstrates the scalability and utility of the ConsolidationEngine
by applying it to the entire pattern database, not just a small demo set.

This operationalizes the "Next Steps (Future)" from the NRM V2 integration plan.

Process:
1. Load all patterns from `memory.db`.
2. Generate memetic embeddings for any patterns that lack them.
3. Build a comprehensive semantic graph.
4. Run a long NREM consolidation session to strengthen the graph.
5. Save the consolidated graph and session metrics.
"""

import sys
import time
import json
from pathlib import Path
from typing import List, Dict

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "memory"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from pattern_memory import PatternMemory, Pattern, PatternType
from consolidation_engine import ConsolidationEngine
from transcendental_bridge import TranscendentalBridge


def generate_simple_embeddings(patterns: List[Pattern]) -> Dict[str, List[float]]:
    """
    Generate simple embeddings from pattern data.

    In production, would use sentence-transformers. For this demo, we use feature
    vectors from pattern data to remain self-contained.

    Returns:
        Dict mapping pattern_id to embedding vector (8D)
    """
    embeddings = {}

    for i, pattern in enumerate(patterns):
        data = pattern.data if isinstance(pattern.data, dict) else {}

        # Create 8D embedding from pattern features
        features = [
            data.get('agent_count_mean', data.get('basin_a_agent_count', 0.0)) / 20.0,
            data.get('frequency', data.get('critical_frequency', data.get('f_low', 0.0))) * 100.0,
            pattern.confidence,
            pattern.occurrences / 100.0,  # Normalize occurrences
            data.get('basin_a_composition', data.get('composition', 50.0)) / 100.0,
            data.get('transition_width', data.get('collapse_time_cycles', 500.0)) / 1000.0,
            1.0 if pattern.pattern_type == PatternType.EMERGENCE else 0.0,
            float(hash(pattern.pattern_id) % 1000) / 1000.0
        ]
        embeddings[pattern.pattern_id] = features

    return embeddings


def main():
    """Run the full NREM consolidation session."""
    print("=" * 80)
    print("NRM V2 FULL NREM CONSOLIDATION")
    print("=" * 80)
    print("\nApplying sleep-inspired consolidation to the entire pattern database.")

    # 1. Initialize components
    print("\n1. Initializing NRM V2 components...")
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    memory = PatternMemory(workspace_path=workspace)
    bridge = TranscendentalBridge(workspace_path=str(workspace))
    engine = ConsolidationEngine(memory=memory, bridge=bridge, workspace_path=str(workspace))
    print("   ✅ ConsolidationEngine initialized")

    # 2. Load all patterns
    print("\n2. Loading all patterns from memory.db...")
    all_patterns = memory.search_patterns(limit=10000)  # High limit to get all
    print(f"   ✅ Loaded {len(all_patterns)} patterns")

    if not all_patterns:
        print("\nNo patterns found in memory.db. Exiting.")
        return

    # 3. Generate and store embeddings for patterns that need them
    print("\n3. Generating and storing memetic embeddings...")
    existing_embeddings = {p.pattern_id: memory.get_embedding(p.pattern_id) for p in all_patterns}
    patterns_to_embed = [p for p, emb in zip(all_patterns, existing_embeddings.values()) if emb is None]

    if patterns_to_embed:
        print(f"   Found {len(patterns_to_embed)} patterns requiring new embeddings.")
        new_embeddings = generate_simple_embeddings(patterns_to_embed)
        for pattern_id, embedding in new_embeddings.items():
            memory.store_embedding(pattern_id, embedding, "simple_features_full_run", len(embedding))
        print(f"   ✅ Generated and stored {len(new_embeddings)} new embeddings.")
    else:
        print("   ✅ All patterns already have embeddings.")

    # 4. Build/Update semantic graph
    print("\n4. Building/Updating semantic graph (adjacency matrix W)...")
    edge_count = 0
    for i, pattern_i in enumerate(all_patterns):
        emb_i = memory.get_embedding(pattern_i.pattern_id)
        if not emb_i: continue

        for j, pattern_j in enumerate(all_patterns):
            if i >= j: continue

            emb_j = memory.get_embedding(pattern_j.pattern_id)
            if not emb_j: continue
            
            similarity = memory.compute_semantic_similarity(emb_i, emb_j)
            if similarity > 0.6:  # Slightly higher threshold for a denser graph
                memory.store_graph_edge(
                    pattern_i.pattern_id,
                    pattern_j.pattern_id,
                    similarity,
                    'semantic_full'
                )
                edge_count += 1
    print(f"   ✅ Built/Updated graph with {edge_count} new edges.")

    # 5. Run full NREM consolidation
    print("\n5. Running full NREM consolidation (2 Hz, 500 cycles)...")
    start_time = time.time()
    coalitions_nrem, metrics_nrem = engine.nrem_consolidation(
        patterns=all_patterns,
        duration_cycles=500,  # Longer duration for full consolidation
        frequency_hz=2.0,
        hebbian_learning_rate=0.01,
        coherence_threshold=0.80
    )
    nrem_duration = time.time() - start_time
    print(f"   ✅ NREM consolidation complete in {nrem_duration:.2f}s.")

    # 6. Report and Save Results
    print("\n" + "=" * 80)
    print("FULL NREM CONSOLIDATION COMPLETE")
    print("=" * 80)
    print(f"\nTotal Patterns Processed: {len(all_patterns)}")
    print(f"NREM Coalitions Detected: {len(coalitions_nrem)}")
    print(f"Hebbian Updates to Graph: {metrics_nrem.hebbian_updates}")
    
    print(f"\nComputational Cost:")
    print(f"  - CPU Time: {metrics_nrem.cpu_time_ms:.2f} ms")
    print(f"  - Memory Usage: {metrics_nrem.memory_usage_mb:.2f} MB")

    # Save results
    results_path = Path(__file__).parent / "results" / "nrem_full_consolidation_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    results = {
        'experiment': 'nrem_full_consolidation',
        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'patterns_processed': len(all_patterns),
        'new_embeddings_generated': len(patterns_to_embed) if patterns_to_embed else 0,
        'new_graph_edges': edge_count,
        'nrem_metrics': {
            'coalitions': len(coalitions_nrem),
            'hebbian_updates': metrics_nrem.hebbian_updates,
            'cpu_time_ms': metrics_nrem.cpu_time_ms,
            'memory_usage_mb': metrics_nrem.memory_usage_mb,
            'coalition_details': [
                {
                    'size': len(c.member_pattern_ids),
                    'coherence': c.mean_coherence,
                    'members': c.member_pattern_ids
                }
                for c in coalitions_nrem
            ]
        }
    }

    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {results_path}")
    print("\n✅ Full NREM consolidation session complete.")
    print("=" * 80)

if __name__ == '__main__':
    main()
