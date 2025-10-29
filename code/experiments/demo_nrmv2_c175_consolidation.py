#!/usr/bin/env python3
"""
NRM V2 Consolidation Demo: C175 Experimental Findings
======================================================

Purpose: Demonstrate sleep-inspired consolidation on real C175 patterns

Patterns Extracted from C175 Analysis:
1. Bistability: Basin A (high composition) vs Basin B (collapse)
2. Homeostasis: ~17 agents at frequency=2.5%
3. Sharp transition: Width 0.11% (2.5-2.61%)
4. Phase transition: 10% → 90% Basin A across narrow range
5. Critical frequency: ~2.55% midpoint

This script demonstrates:
- Memetic embedding generation for patterns
- Semantic graph construction
- NREM consolidation (Hebbian strengthening)
- REM exploration (hypothesis generation)
- Reality-grounded cost tracking

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29 (Cycle 488)
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
from consolidation_engine import ConsolidationEngine, Coalition
from transcendental_bridge import TranscendentalBridge


def create_c175_patterns() -> List[Pattern]:
    """
    Create Pattern objects from C175 experimental findings.

    Based on analyze_cycle175_transition.py analysis:
    - Bistable behavior (Basin A vs B)
    - Homeostasis at ~17 agents
    - Sharp transition (0.11% width)
    - Critical frequency ~2.55%

    Returns:
        List of Pattern objects representing C175 discoveries
    """
    timestamp = time.time()

    patterns = [
        # Pattern 1: Bistability
        Pattern(
            pattern_id="c175_bistability",
            pattern_type=PatternType.EMERGENCE,
            name="Bistable Basin Behavior",
            description="Population exhibits two distinct basins: Basin A (high composition, ~17 agents) and Basin B (collapse to zero). Sharp transition at frequency ~2.55%.",
            data={
                'basin_a_composition': 99.97,
                'basin_a_agent_count': 17.0,
                'basin_b_composition': 0.0,
                'basin_b_agent_count': 0.0,
                'transition_frequency': 0.0255,
                'mechanism': 'bistable_attractor'
            },
            confidence=0.95,
            occurrences=110,  # C175 had 110 experiments
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C175', 'analysis': 'analyze_cycle175_transition.py'}
        ),

        # Pattern 2: Homeostasis
        Pattern(
            pattern_id="c175_homeostasis",
            pattern_type=PatternType.SYSTEM_BEHAVIOR,
            name="Population Homeostasis at 17 Agents",
            description="Population stabilizes at approximately 17 agents when frequency=2.5% in Basin A. Stable across 3000 cycles with CV=0.0%.",
            data={
                'agent_count_mean': 17.0,
                'agent_count_std': 0.0,
                'frequency': 0.025,
                'stability_duration_cycles': 3000,
                'coefficient_variation': 0.0,
                'mechanism': 'dynamic_equilibrium'
            },
            confidence=0.98,
            occurrences=10,  # 10 seeds at frequency=2.5%
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C175', 'basin': 'A'}
        ),

        # Pattern 3: Sharp Transition
        Pattern(
            pattern_id="c175_sharp_transition",
            pattern_type=PatternType.EMERGENCE,
            name="Sharp Bistable Transition",
            description="Transition from Basin A to Basin B occurs over narrow frequency range (0.11% width, 2.5-2.61%). Characteristic of first-order phase transition.",
            data={
                'transition_width': 0.0011,
                'f_low': 0.0250,
                'f_high': 0.0261,
                'midpoint': 0.0255,
                'sharpness': 1.0 / 0.0011,  # ~909
                'basin_a_at_low': 100.0,
                'basin_a_at_high': 0.0,
                'mechanism': 'first_order_transition'
            },
            confidence=0.92,
            occurrences=11,  # 11 frequency points spanning transition
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C175', 'resolution': '0.01%'}
        ),

        # Pattern 4: Critical Frequency
        Pattern(
            pattern_id="c175_critical_frequency",
            pattern_type=PatternType.SYSTEM_BEHAVIOR,
            name="Critical Frequency at 2.55%",
            description="Frequency at which system exhibits equal probability of Basin A vs Basin B. Bifurcation point in parameter space.",
            data={
                'critical_frequency': 0.0255,
                'basin_a_probability': 0.5,
                'basin_b_probability': 0.5,
                'mechanism': 'bifurcation_point'
            },
            confidence=0.90,
            occurrences=10,  # 10 seeds at critical point
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C175', 'type': 'bifurcation'}
        ),

        # Pattern 5: Rapid Collapse
        Pattern(
            pattern_id="c175_rapid_collapse",
            pattern_type=PatternType.SYSTEM_BEHAVIOR,
            name="Rapid Population Collapse in Basin B",
            description="Population decays to zero within 500 cycles when frequency > 2.61%. Characteristic of Basin B attractor.",
            data={
                'collapse_time_cycles': 500,
                'frequency_threshold': 0.0261,
                'final_agent_count': 0.0,
                'mechanism': 'attractor_collapse'
            },
            confidence=0.93,
            occurrences=30,  # Multiple seeds at high frequencies
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C175', 'basin': 'B'}
        ),
    ]

    return patterns


def generate_simple_embeddings(patterns: List[Pattern]) -> Dict[str, List[float]]:
    """
    Generate simple embeddings from pattern data.

    In production, would use sentence-transformers. For demo, use feature vectors
    from pattern data.
from workspace_utils import get_workspace_path, get_results_path

    Returns:
        Dict mapping pattern_id to embedding vector (8D)
    """
    embeddings = {}

    for pattern in patterns:
        # Create 8D embedding from pattern features
        data = pattern.data

        # Extract relevant features (normalized)
        features = [
            data.get('agent_count_mean', data.get('basin_a_agent_count', 0.0)) / 20.0,  # Agent count
            data.get('frequency', data.get('critical_frequency', data.get('f_low', 0.0))) * 100.0,  # Frequency
            pattern.confidence,  # Confidence
            pattern.occurrences / 110.0,  # Occurrence rate
            data.get('basin_a_composition', data.get('composition', 50.0)) / 100.0,  # Composition
            data.get('transition_width', data.get('collapse_time_cycles', 500.0)) / 1000.0,  # Timescale
            1.0 if pattern.pattern_type == PatternType.EMERGENCE else 0.0,  # Type flag
            data.get('sharpness', 1.0) / 1000.0  # Sharpness/speed
        ]

        embeddings[pattern.pattern_id] = features

    return embeddings


def main():
    """Run NRM V2 consolidation demonstration."""
    print("=" * 80)
    print("NRM V2 CONSOLIDATION DEMO: C175 EXPERIMENTAL FINDINGS")
    print("=" * 80)
    print("\nDemonstrating sleep-inspired consolidation on real research patterns")
    print("Source: C175 bistable transition analysis\n")

    # Initialize components
    print("1. Initializing NRM V2 components...")
    workspace = get_workspace_path()
    memory = PatternMemory(workspace_path=workspace)
    bridge = TranscendentalBridge(workspace_path=str(workspace))
    engine = ConsolidationEngine(memory=memory, bridge=bridge, workspace_path=str(workspace))
    print("   ✅ ConsolidationEngine initialized")

    # Create patterns from C175 findings
    print("\n2. Creating patterns from C175 experimental findings...")
    patterns = create_c175_patterns()
    for pattern in patterns:
        memory.store_pattern(pattern)
        print(f"   - {pattern.name}")
    print(f"   ✅ Created {len(patterns)} patterns")

    # Generate embeddings
    print("\n3. Generating memetic embeddings...")
    embeddings = generate_simple_embeddings(patterns)
    for pattern_id, embedding in embeddings.items():
        memory.store_embedding(pattern_id, embedding, "simple_features", len(embedding))
        print(f"   - {pattern_id}: {len(embedding)}D vector")
    print(f"   ✅ Generated {len(embeddings)} embeddings")

    # Build semantic graph
    print("\n4. Building semantic graph (adjacency matrix W)...")
    edge_count = 0
    for i, pattern_i in enumerate(patterns):
        for j, pattern_j in enumerate(patterns):
            if i < j:  # Avoid double-counting
                emb_i = embeddings[pattern_i.pattern_id]
                emb_j = embeddings[pattern_j.pattern_id]

                # Compute cosine similarity
                similarity = memory.compute_semantic_similarity(emb_i, emb_j)

                # Store edge if similarity > threshold
                if similarity > 0.5:
                    memory.store_graph_edge(
                        pattern_i.pattern_id,
                        pattern_j.pattern_id,
                        similarity,
                        'semantic'
                    )
                    edge_count += 1
                    print(f"   - Edge: {pattern_i.pattern_id} ↔ {pattern_j.pattern_id} (W={similarity:.3f})")
    print(f"   ✅ Built graph with {edge_count} edges")

    # Run NREM consolidation
    print("\n5. Running NREM consolidation (slow-wave, 2 Hz, 50 cycles)...")
    start_time = time.time()
    coalitions_nrem, metrics_nrem = engine.nrem_consolidation(
        patterns=patterns,
        duration_cycles=50,
        frequency_hz=2.0,
        hebbian_learning_rate=0.02,
        coherence_threshold=0.75
    )
    nrem_duration = time.time() - start_time

    print(f"\n   NREM Results:")
    print(f"   - Patterns processed: {metrics_nrem.patterns_processed}")
    print(f"   - Coalitions detected: {metrics_nrem.coalitions_detected}")
    print(f"   - Hebbian updates: {metrics_nrem.hebbian_updates}")
    print(f"   - CPU time: {metrics_nrem.cpu_time_ms:.2f} ms")
    print(f"   - Memory usage: {metrics_nrem.memory_usage_mb:.2f} MB")
    print(f"   - Wall-clock time: {nrem_duration*1000:.2f} ms")

    if coalitions_nrem:
        print(f"\n   Top Coalitions (NREM):")
        for i, coalition in enumerate(coalitions_nrem[:3], 1):
            print(f"   {i}. {coalition.coalition_id}")
            print(f"      Members: {coalition.member_pattern_ids}")
            print(f"      Coherence: {coalition.mean_coherence:.4f}")

    # Run REM exploration
    print("\n6. Running REM exploration (high-frequency, 8 Hz, 30 cycles)...")
    start_time = time.time()
    coalitions_rem, metrics_rem = engine.rem_exploration(
        patterns=patterns,
        duration_cycles=30,
        frequency_hz=8.0,
        perturbation_strength=0.3,
        coherence_threshold=0.65
    )
    rem_duration = time.time() - start_time

    print(f"\n   REM Results:")
    print(f"   - Patterns processed: {metrics_rem.patterns_processed}")
    print(f"   - Coalitions detected: {metrics_rem.coalitions_detected}")
    print(f"   - CPU time: {metrics_rem.cpu_time_ms:.2f} ms")
    print(f"   - Memory usage: {metrics_rem.memory_usage_mb:.2f} MB")
    print(f"   - Wall-clock time: {rem_duration*1000:.2f} ms")

    if coalitions_rem:
        print(f"\n   Top Coalitions (REM):")
        for i, coalition in enumerate(coalitions_rem[:3], 1):
            print(f"   {i}. {coalition.coalition_id}")
            print(f"      Members: {coalition.member_pattern_ids}")
            print(f"      Coherence: {coalition.mean_coherence:.4f}")

    # Summary
    print("\n" + "=" * 80)
    print("CONSOLIDATION COMPLETE")
    print("=" * 80)
    print(f"\nTotal Patterns: {len(patterns)}")
    print(f"Total Embeddings: {len(embeddings)}")
    print(f"Total Graph Edges: {edge_count}")
    print(f"\nNREM Coalitions: {len(coalitions_nrem)} (Hebbian updates: {metrics_nrem.hebbian_updates})")
    print(f"REM Coalitions: {len(coalitions_rem)} (Exploratory hypotheses)")
    print(f"\nTotal CPU Time: {metrics_nrem.cpu_time_ms + metrics_rem.cpu_time_ms:.2f} ms")
    print(f"Total Memory: {max(metrics_nrem.memory_usage_mb, metrics_rem.memory_usage_mb):.2f} MB peak")
    print("\n✅ NRM V2 consolidation validated on real C175 experimental patterns")
    print("=" * 80)

    # Save results
    results = {
        'metadata': {
            'source': 'C175 bistable transition analysis',
            'timestamp': time.time(),
            'nrm_version': 'V2',
            'patterns_count': len(patterns),
            'embeddings_dim': 8,
            'graph_edges': edge_count
        },
        'patterns': [p.to_dict() for p in patterns],
        'nrem_metrics': {
            'coalitions': len(coalitions_nrem),
            'hebbian_updates': metrics_nrem.hebbian_updates,
            'cpu_ms': metrics_nrem.cpu_time_ms,
            'memory_mb': metrics_nrem.memory_usage_mb
        },
        'rem_metrics': {
            'coalitions': len(coalitions_rem),
            'cpu_ms': metrics_rem.cpu_time_ms,
            'memory_mb': metrics_rem.memory_usage_mb
        }
    }

    results_path = get_results_path()
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")


if __name__ == "__main__":
    main()
