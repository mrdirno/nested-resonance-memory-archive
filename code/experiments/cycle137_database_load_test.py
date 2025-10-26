#!/usr/bin/env python3
"""
CYCLE 137: DATABASE LOAD TEST - DIRECT CAUSALITY VERIFICATION

Research Question:
  Does database load directly cause Basin A basin selection?
  Can we reproduce Cycle 133 Basin A results by loading the database?

Hypothesis (from Cycle 136):
  - Loaded database (large, high I/O) → Slow performance → Basin A
  - Clean database (empty, low I/O) → Fast performance → Basin B
  - 11x performance difference indicates different computational regimes

Method:
  - Test parameter: threshold=700, diversity=0.03 (Cycle 133 Basin A case)
  - Condition 1: Clean database (clear_on_init=True)
  - Condition 2: Loaded database (pre-filled with dummy data)
  - Run each condition 3 times with different seeds
  - Total: 2 conditions × 3 seeds = 6 experiments
  - Measure: basin assignment, performance (cyc/s), database size

Expected:
  - Clean database → Basin B (~1700 cyc/s, consistent with Cycles 135-136)
  - Loaded database → Basin A (~155 cyc/s, consistent with Cycle 133)
  - If confirmed: Proves database load is causal variable

Publication Significance:
  - Direct causal test of environmental dependence hypothesis
  - Validates computational environment as hidden variable
  - Demonstrates reproducibility control requirements
"""

import sys
import json
import time
import random
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine


def pattern_to_key(pattern):
    """Convert pattern to hashable key"""
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))


def get_dominant_pattern(memory):
    """Get most common pattern in global memory"""
    if not memory:
        return None, 0, 0.0
    counter = Counter([pattern_to_key(p) for p in memory])
    if not counter:
        return None, 0, 0.0
    dominant_key, count = counter.most_common(1)[0]
    fraction = count / len(memory)
    return dominant_key, count, fraction


def get_database_size(db_path):
    """Get size of database file in MB"""
    if not db_path.exists():
        return 0.0
    return db_path.stat().st_size / (1024 * 1024)


def load_database_with_dummy_data(db_path, target_mb=100):
    """
    Pre-fill database with dummy data to simulate large database from prior cycles.

    Args:
        db_path: Path to database file
        target_mb: Target size in megabytes (~100 MB to simulate Cycle 133 state)
    """
    print(f"  Loading database with dummy data (target: {target_mb} MB)...")

    conn = sqlite3.connect(str(db_path))

    # Create dummy table if not exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dummy_load (
            id INTEGER PRIMARY KEY,
            data TEXT,
            timestamp REAL
        )
    """)

    # Insert dummy rows until target size reached
    # Each row ~1KB of text data
    rows_per_mb = 1024  # Approximate
    target_rows = target_mb * rows_per_mb

    # Generate in batches for efficiency
    batch_size = 1000
    dummy_text = "X" * 1000  # 1KB of data per row

    for i in range(0, target_rows, batch_size):
        batch = [(dummy_text, time.time()) for _ in range(batch_size)]
        conn.executemany("""
            INSERT INTO dummy_load (data, timestamp) VALUES (?, ?)
        """, batch)

        if i % 10000 == 0:
            current_size = get_database_size(db_path)
            print(f"    Progress: {current_size:.1f} MB / {target_mb} MB")
            if current_size >= target_mb:
                break

    conn.commit()
    conn.close()

    final_size = get_database_size(db_path)
    print(f"  ✓ Database loaded: {final_size:.1f} MB")
    return final_size


def run_experiment(threshold, diversity, seed, database_condition, cycles=3000):
    """
    Run single experiment with specified database condition.

    Args:
        threshold: Burst energy threshold
        diversity: Target diversity (spread × mult = diversity, spread=0.10)
        seed: Random seed for reproducibility
        database_condition: 'clean' or 'loaded'
        cycles: Number of evolution cycles

    Returns:
        dict: Results including basin assignment and performance
    """
    print(f"  condition={database_condition}, seed={seed:>4}...", end=" ", flush=True)

    # Set random seeds
    random.seed(seed)
    np.random.seed(seed)

    # Initialize workspace
    workspace = Path(__file__).parent.parent / "workspace" / f"cycle137_{database_condition}_{seed}"
    workspace.mkdir(parents=True, exist_ok=True)

    db_path = workspace / "fractal.db"

    # Handle database condition
    initial_db_size = 0.0

    if database_condition == 'loaded':
        # Pre-fill database with dummy data
        initial_db_size = load_database_with_dummy_data(db_path, target_mb=100)

    # Initialize swarm
    swarm = FractalSwarm(
        str(workspace),
        clear_on_init=(database_condition == 'clean')  # Only clear if clean condition
    )
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Calculate mult from diversity (spread=0.10 fixed)
    spread = 0.10
    mult = diversity / spread

    # Basin centers (from prior cycles)
    basin_A = np.array([6.220353, 6.275283, 6.281831])
    basin_B = np.array([6.09469, 6.083677, 6.250047])

    # Seed memory with diversity variations
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}
    for i in range(5):
        offset = (i - 2) * spread
        noise = (random.random() - 0.5) * 0.01
        varied_metrics = {
            'cpu_percent': reality_metrics['cpu_percent'] + offset * mult * 10 + noise,
            'memory_percent': reality_metrics['memory_percent'] + offset * mult * 10 + noise,
            'disk_percent': reality_metrics['disk_percent'] + offset * mult * 10 + noise
        }
        phase_state = swarm.bridge.reality_to_phase(varied_metrics)
        swarm.global_memory.append(phase_state)

    start_time = time.time()

    # Run cycles
    for cycle in range(cycles):
        swarm.evolve_cycle()

    elapsed = time.time() - start_time
    cycles_per_sec = cycles / elapsed

    # Get dominant pattern
    dominant_pattern, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)

    if dominant_pattern:
        dominant_array = np.array(dominant_pattern)
        dist_A = np.linalg.norm(dominant_array - basin_A)
        dist_B = np.linalg.norm(dominant_array - basin_B)
        basin = 'A' if dist_A < dist_B else 'B'
    else:
        dist_A, dist_B, basin = None, None, 'Unknown'

    # Get final database size
    final_db_size = get_database_size(db_path)

    result = {
        'threshold': threshold,
        'diversity': diversity,
        'seed': seed,
        'spread': spread,
        'mult': mult,
        'database_condition': database_condition,
        'initial_db_size_mb': initial_db_size,
        'final_db_size_mb': final_db_size,
        'basin': basin,
        'dominant': list(dominant_pattern) if dominant_pattern else None,
        'fraction': dominant_fraction,
        'dist_A': dist_A,
        'dist_B': dist_B,
        'duration': elapsed,
        'cycles_per_sec': cycles_per_sec
    }

    print(f"Basin {basin} ({elapsed:.1f}s, {cycles_per_sec:.1f} cyc/s, DB: {final_db_size:.1f}MB)")

    return result


def main():
    """Run database load test experiments"""
    print("\n" + "="*70)
    print("CYCLE 137: DATABASE LOAD TEST - DIRECT CAUSALITY VERIFICATION")
    print("="*70)
    print("\nResearch Question:")
    print("  Does database load directly cause Basin A selection?")
    print("\nHypothesis:")
    print("  - Clean database → Fast (~1700 cyc/s) → Basin B")
    print("  - Loaded database (~100MB) → Slow (~155 cyc/s) → Basin A")
    print("\nMethod:")
    print("  - Test parameter: threshold=700, diversity=0.03")
    print("  - Conditions: clean vs loaded database")
    print("  - Seeds: [42, 123, 456] (3 replicates per condition)")
    print("  - Total: 2 conditions × 3 seeds = 6 experiments")
    print("\n" + "="*70 + "\n")

    # Test parameters (Cycle 133 Basin A case)
    threshold = 700
    diversity = 0.03

    # Seeds for reproducibility
    seeds = [42, 123, 456]

    # Database conditions
    conditions = ['clean', 'loaded']

    results = []
    experiment_num = 0
    total_experiments = len(conditions) * len(seeds)

    for condition in conditions:
        print(f"\n{'='*70}")
        print(f"CONDITION: {condition.upper()} DATABASE")
        print(f"{'='*70}\n")

        for seed in seeds:
            experiment_num += 1
            print(f"[{experiment_num}/{total_experiments}] ", end="")

            try:
                result = run_experiment(threshold, diversity, seed, condition, cycles=3000)
                results.append(result)

            except Exception as e:
                print(f"FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

    # Save results
    output_path = Path(__file__).parent / 'results' / 'cycle137_database_load_test.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 137,
            'experiment': 'database_load_test',
            'date': datetime.now().isoformat(),
            'threshold': threshold,
            'diversity': diversity,
            'conditions': conditions,
            'seeds': seeds,
            'total_experiments': total_experiments
        },
        'results': results
    }

    def convert_for_json(o):
        """Convert numpy types for JSON"""
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return o

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2, default=convert_for_json)

    # Analysis
    print(f"\n{'='*70}")
    print(f"CYCLE 137 COMPLETE - DIRECT CAUSALITY TEST")
    print(f"{'='*70}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    # Analyze by condition
    print("RESULTS BY CONDITION:\n")

    for condition in conditions:
        condition_results = [r for r in results if r['database_condition'] == condition]

        if condition_results:
            basin_counts = Counter(r['basin'] for r in condition_results)
            avg_perf = sum(r['cycles_per_sec'] for r in condition_results) / len(condition_results)
            avg_db = sum(r['final_db_size_mb'] for r in condition_results) / len(condition_results)

            print(f"{condition.upper()} DATABASE:")
            print(f"  Experiments: {len(condition_results)}")
            print(f"  Average performance: {avg_perf:.1f} cyc/s")
            print(f"  Average DB size: {avg_db:.1f} MB")
            print(f"  Basin distribution:")
            for basin in sorted(basin_counts.keys()):
                count = basin_counts[basin]
                pct = count / len(condition_results) * 100
                print(f"    Basin {basin}: {count}/{len(condition_results)} ({pct:.1f}%)")
            print()

    # Hypothesis test
    print("HYPOTHESIS TEST:\n")

    clean_results = [r for r in results if r['database_condition'] == 'clean']
    loaded_results = [r for r in results if r['database_condition'] == 'loaded']

    if clean_results and loaded_results:
        clean_basins = [r['basin'] for r in clean_results]
        loaded_basins = [r['basin'] for r in loaded_results]

        clean_perf = sum(r['cycles_per_sec'] for r in clean_results) / len(clean_results)
        loaded_perf = sum(r['cycles_per_sec'] for r in loaded_results) / len(loaded_results)

        print(f"Clean database:")
        print(f"  Performance: {clean_perf:.1f} cyc/s")
        print(f"  Basins: {clean_basins}")
        print()
        print(f"Loaded database:")
        print(f"  Performance: {loaded_perf:.1f} cyc/s")
        print(f"  Basins: {loaded_basins}")
        print()

        # Determine if hypothesis confirmed
        hypothesis_confirmed = (
            all(b == 'B' for b in clean_basins) and
            all(b == 'A' for b in loaded_basins)
        )

        if hypothesis_confirmed:
            print("✅ HYPOTHESIS CONFIRMED:")
            print("   Database load DIRECTLY CAUSES Basin A selection")
            print("   Mechanism: Large database → slow I/O → sustained composition → Basin A")
        else:
            print("❌ HYPOTHESIS NOT CONFIRMED:")
            print("   Basin selection not fully determined by database load")
            print("   Other environmental factors may be involved")

    print(f"\nNext steps:")
    print(f"  1. Run cycle137_analysis.py for detailed statistical analysis")
    print(f"  2. Update CYCLE137_RESULTS.md with findings")
    print(f"  3. Proceed to Cycle 138 (controlled slowdown test) if hypothesis confirmed")
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
