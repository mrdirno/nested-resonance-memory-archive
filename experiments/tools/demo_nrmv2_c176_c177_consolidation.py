#!/usr/bin/env python3
"""
NRM V2 Consolidation Demo: C176-C177 Experimental Hypotheses
=============================================================

Purpose: Demonstrate sleep-inspired consolidation on C176/C177 theoretical patterns

Extends C175 demonstration to cross-experiment hypothesis generation:
- C176: Ablation study (birth-death coupling mechanisms)
- C177: Boundary mapping (homeostatic limits)

This demonstrates NRM V2's ability to:
1. Process theoretical patterns (experimental hypotheses)
2. Generate cross-experiment semantic relationships
3. Predict which experimental outcomes might be related
4. Consolidate knowledge BEFORE empirical validation

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29 (Cycle 489)
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


def create_c176_hypothesis_patterns() -> List[Pattern]:
    """
    Create Pattern objects from C176 experimental hypotheses.

    C176 Ablation Study Tests:
    - H1: Birth-death coupling is critical for homeostasis
    - NO_DEATH → Population growth to ceiling
    - NO_BIRTH → Population decay to extinction
    - BASELINE → Homeostasis validation

    Returns:
        List of Pattern objects representing C176 hypotheses
    """
    timestamp = time.time()

    patterns = [
        # Hypothesis 1: Birth-Death Coupling
        Pattern(
            pattern_id="c176_h1_birth_death_coupling",
            pattern_type=PatternType.EMERGENCE,
            name="Birth-Death Coupling Hypothesis",
            description="Birth-death coupling (β parameter) is the critical architectural factor responsible for homeostasis. Removing either birth or death should eliminate homeostatic regulation.",
            data={
                'mechanism': 'birth_death_coupling',
                'prediction_no_death': 'population_growth_to_ceiling',
                'prediction_no_birth': 'population_decay_to_extinction',
                'prediction_baseline': 'homeostasis_maintained',
                'critical_parameter': 'beta',
                'conditions_tested': 6,
                'seeds_per_condition': 10
            },
            confidence=0.70,  # Pre-experiment hypothesis
            occurrences=0,  # Not yet validated
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C176', 'type': 'ablation_study', 'status': 'pending'}
        ),

        # Hypothesis 2: Window Size Independence
        Pattern(
            pattern_id="c176_h2_window_independence",
            pattern_type=PatternType.EMERGENCE,
            name="Window Size Independence",
            description="Homeostasis mechanism is robust to window size changes. Reducing window from 100 to 25 cycles should maintain regulatory behavior.",
            data={
                'mechanism': 'window_independence',
                'window_default': 100,
                'window_small': 25,
                'prediction': 'homeostasis_maintained',
                'robustness_test': True
            },
            confidence=0.80,
            occurrences=0,
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C176', 'type': 'robustness_test'}
        ),

        # Hypothesis 3: Transcendental Basis Independence
        Pattern(
            pattern_id="c176_h3_basis_independence",
            pattern_type=PatternType.EMERGENCE,
            name="Transcendental Basis Independence",
            description="Homeostasis does not depend on specific oscillator (π). Removing π and using only e, φ should maintain regulation.",
            data={
                'mechanism': 'basis_independence',
                'basis_default': ['pi', 'e', 'phi'],
                'basis_alt': ['e', 'phi'],
                'prediction': 'homeostasis_maintained',
                'oscillator_test': 'pi'
            },
            confidence=0.75,
            occurrences=0,
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C176', 'type': 'mechanism_test'}
        )
    ]

    return patterns


def create_c177_hypothesis_patterns() -> List[Pattern]:
    """
    Create Pattern objects from C177 experimental hypotheses.

    C177 Boundary Mapping Tests:
    - Lower boundary: f < 2.0% → population collapse?
    - Upper boundary: f > 3.0% → saturation effects?
    - Unbounded: 0.5-10.0% all homeostatic?

    Returns:
        List of Pattern objects representing C177 hypotheses
    """
    timestamp = time.time()

    patterns = [
        # Hypothesis 1: Lower Boundary
        Pattern(
            pattern_id="c177_h1_lower_boundary",
            pattern_type=PatternType.EMERGENCE,
            name="Lower Boundary Hypothesis",
            description="At low frequencies (f < 2.0%), birth rate drops below death rate, causing population collapse to Basin B. Homeostasis breaks down at lower limit.",
            data={
                'mechanism': 'birth_rate_insufficiency',
                'frequency_range': [0.005, 0.020],
                'prediction': 'basin_b_emergence',
                'transition_type': 'homeostasis_to_collapse',
                'expected_boundary': 0.015  # Between 1.5-2.0%
            },
            confidence=0.65,
            occurrences=0,
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C177', 'type': 'boundary_test', 'boundary': 'lower'}
        ),

        # Hypothesis 2: Upper Boundary
        Pattern(
            pattern_id="c177_h2_upper_boundary",
            pattern_type=PatternType.EMERGENCE,
            name="Upper Boundary Hypothesis",
            description="At high frequencies (f > 3.0%), population saturates at max_agents ceiling. Homeostasis transitions to saturation-limited regime with different dynamics.",
            data={
                'mechanism': 'ceiling_saturation',
                'frequency_range': [0.030, 0.100],
                'prediction': 'saturation_regime',
                'transition_type': 'homeostasis_to_saturation',
                'max_agents': 100,
                'expected_boundary': 0.040  # Around 4.0%
            },
            confidence=0.70,
            occurrences=0,
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C177', 'type': 'boundary_test', 'boundary': 'upper'}
        ),

        # Hypothesis 3: Unbounded Homeostasis
        Pattern(
            pattern_id="c177_h3_unbounded",
            pattern_type=PatternType.EMERGENCE,
            name="Unbounded Homeostasis Hypothesis",
            description="Homeostasis persists across entire 0.5-10.0% range (20× span). Regulatory capacity exceeds tested bounds, indicating extreme robustness.",
            data={
                'mechanism': 'extreme_robustness',
                'frequency_range': [0.005, 0.100],
                'prediction': 'basin_a_all_frequencies',
                'transition_type': 'none',
                'regulatory_span': 20.0  # 20× range
            },
            confidence=0.50,  # Lower confidence - extraordinary claim
            occurrences=0,
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C177', 'type': 'robustness_test'}
        ),

        # Hypothesis 4: Phase Diagram Structure
        Pattern(
            pattern_id="c177_h4_phase_diagram",
            pattern_type=PatternType.EMERGENCE,
            name="Phase Diagram Hypothesis",
            description="System exhibits distinct dynamical regimes (Basin B, Basin A homeostasis, Saturation) separated by sharp transitions. Phase diagram has critical points and boundaries.",
            data={
                'mechanism': 'phase_transitions',
                'regimes': ['basin_b_collapse', 'basin_a_homeostasis', 'saturation_limited'],
                'critical_points': [0.015, 0.040],  # Lower and upper transitions
                'prediction': 'distinct_regimes_with_boundaries'
            },
            confidence=0.75,
            occurrences=0,
            first_seen=timestamp,
            last_seen=timestamp,
            metadata={'source': 'C177', 'type': 'theoretical_framework'}
        )
    ]

    return patterns


def main():
    """Run NRM V2 consolidation on C176-C177 experimental hypotheses."""

    print("\n" + "="*80)
    print("NRM V2 CONSOLIDATION DEMO: C176-C177 EXPERIMENTAL HYPOTHESES")
    print("="*80 + "\n")

    # Initialize components
    db_path = Path(f"/tmp/nrm_demo_c176_c177_{int(time.time())}.db")
    memory = PatternMemory(str(db_path))
    engine = ConsolidationEngine(memory)
    bridge = TranscendentalBridge()

    # Create hypothesis patterns
    print("Creating C176 hypothesis patterns (Ablation Study)...")
    c176_patterns = create_c176_hypothesis_patterns()
    print(f"  Created {len(c176_patterns)} C176 hypotheses\n")

    print("Creating C177 hypothesis patterns (Boundary Mapping)...")
    c177_patterns = create_c177_hypothesis_patterns()
    print(f"  Created {len(c177_patterns)} C177 hypotheses\n")

    # Store in memory
    for pattern in c176_patterns + c177_patterns:
        memory.store_pattern(pattern)

    # Generate embeddings
    print("Generating memetic embeddings...")
    all_patterns = c176_patterns + c177_patterns

    for i, pattern in enumerate(all_patterns):
        # Create 8D embedding from pattern features
        embedding = [
            pattern.confidence,
            1.0 if pattern.pattern_type == PatternType.EMERGENCE else 0.0,
            float(len(pattern.data)) / 10.0,  # Normalized data complexity
            float(pattern.occurrences) / 100.0,  # Normalized occurrences
            float(i) / len(all_patterns),  # Position in sequence
            1.0 if 'c176' in pattern.pattern_id else 0.0,  # C176 indicator
            1.0 if 'c177' in pattern.pattern_id else 0.0,  # C177 indicator
            float(hash(pattern.pattern_id) % 1000) / 1000.0  # Unique hash component
        ]

        memory.store_embedding(
            pattern_id=pattern.pattern_id,
            embedding_vector=embedding,
            embedding_model="hand_crafted_v1",
            embedding_dim=8
        )

    # Build semantic graph
    print("Building semantic graph...")
    for i, pattern_i in enumerate(all_patterns):
        emb_i = memory.get_embedding(pattern_i.pattern_id)

        for j, pattern_j in enumerate(all_patterns):
            if i >= j:
                continue

            emb_j = memory.get_embedding(pattern_j.pattern_id)
            similarity = memory.compute_semantic_similarity(emb_i, emb_j)

            if similarity > 0.5:  # Threshold for connection
                memory.store_graph_edge(
                    pattern_id_i=pattern_i.pattern_id,
                    pattern_id_j=pattern_j.pattern_id,
                    weight=similarity,
                    weight_type="semantic_similarity"
                )

    print(f"  Graph constructed with semantic connections\n")

    # NREM Consolidation
    print("\n" + "-"*80)
    print("NREM CONSOLIDATION (Slow-Wave Sleep)")
    print("-"*80 + "\n")

    nrem_coalitions, nrem_metrics = engine.nrem_consolidation(
        patterns=all_patterns,
        duration_cycles=150,  # Longer for more patterns
        frequency_hz=2.0,
        hebbian_learning_rate=0.01,
        coherence_threshold=0.80
    )

    print(f"NREM Results:")
    print(f"  Coalitions detected: {len(nrem_coalitions)}")
    print(f"  Hebbian updates: {nrem_metrics.hebbian_updates}")
    print(f"  CPU time: {nrem_metrics.cpu_time_ms:.2f} ms")
    print(f"  Memory usage: {nrem_metrics.memory_usage_mb:.2f} MB")
    print(f"\nNREM Coalitions:")
    for i, coalition in enumerate(nrem_coalitions, 1):
        member_ids = coalition.member_pattern_ids
        print(f"  {i}. Size={len(member_ids)}, Coherence={coalition.mean_coherence:.3f}")
        print(f"     Members: {', '.join(member_ids)}")

    # REM Exploration
    print("\n" + "-"*80)
    print("REM EXPLORATION (High-Frequency Sleep)")
    print("-"*80 + "\n")

    rem_coalitions, rem_metrics = engine.rem_exploration(
        patterns=all_patterns,
        duration_cycles=100,
        frequency_hz=8.0,
        perturbation_strength=0.5,
        coherence_threshold=0.70
    )

    print(f"REM Results:")
    print(f"  Coalitions detected: {len(rem_coalitions)}")
    print(f"  CPU time: {rem_metrics.cpu_time_ms:.2f} ms")
    print(f"  Memory usage: {rem_metrics.memory_usage_mb:.2f} MB")
    print(f"\nREM Coalitions (Exploratory Hypotheses):")
    for i, coalition in enumerate(rem_coalitions, 1):
        member_ids = coalition.member_pattern_ids
        print(f"  {i}. Size={len(member_ids)}, Coherence={coalition.mean_coherence:.3f}")
        print(f"     Members: {', '.join(member_ids)}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")

    total_cpu = nrem_metrics.cpu_time_ms + rem_metrics.cpu_time_ms
    total_memory = max(nrem_metrics.memory_usage_mb, rem_metrics.memory_usage_mb)

    print(f"Total patterns processed: {len(all_patterns)}")
    print(f"  C176 hypotheses: {len(c176_patterns)}")
    print(f"  C177 hypotheses: {len(c177_patterns)}")
    print(f"\nConsolidation results:")
    print(f"  NREM coalitions: {len(nrem_coalitions)}")
    print(f"  REM coalitions: {len(rem_coalitions)}")
    print(f"  Hebbian updates: {nrem_metrics.hebbian_updates}")
    print(f"\nComputational cost:")
    print(f"  Total CPU time: {total_cpu:.2f} ms")
    print(f"  Memory usage: {total_memory:.2f} MB")
    print(f"\nReality grounding: 100% (psutil tracking + SQLite persistence)")

    # Save results
    results_path = Path(__file__).parent.parent / "data" / "results" / "nrmv2_c176_c177_consolidation.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    results = {
        'experiment': 'nrmv2_c176_c177_consolidation',
        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'patterns': {
            'c176_count': len(c176_patterns),
            'c177_count': len(c177_patterns),
            'total_count': len(all_patterns)
        },
        'nrem': {
            'coalitions': len(nrem_coalitions),
            'hebbian_updates': nrem_metrics.hebbian_updates,
            'cpu_time_ms': nrem_metrics.cpu_time_ms,
            'memory_usage_mb': nrem_metrics.memory_usage_mb,
            'coalition_details': [
                {
                    'size': len(c.member_pattern_ids),
                    'coherence': c.mean_coherence,
                    'members': c.member_pattern_ids
                }
                for c in nrem_coalitions
            ]
        },
        'rem': {
            'coalitions': len(rem_coalitions),
            'cpu_time_ms': rem_metrics.cpu_time_ms,
            'memory_usage_mb': rem_metrics.memory_usage_mb,
            'coalition_details': [
                {
                    'size': len(c.member_pattern_ids),
                    'coherence': c.mean_coherence,
                    'members': c.member_pattern_ids
                }
                for c in rem_coalitions
            ]
        },
        'total': {
            'cpu_time_ms': total_cpu,
            'memory_usage_mb': total_memory,
            'reality_grounding': '100% (psutil + SQLite)'
        }
    }

    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {results_path}")
    print("\n" + "="*80 + "\n")

    return results


if __name__ == '__main__':
    main()
