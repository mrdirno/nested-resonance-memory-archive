#!/usr/bin/env python3
"""
V6a TEST - 5 Experiments to Validate Filesystem Sync Fix

Purpose: Test that filesystem sync delays prevent database I/O errors
         before launching full 50-experiment campaign.

Test Configuration:
- 1 spawn rate (0.10%)
- 5 seeds (42-46)
- Expected duration: ~1 minute (20s per experiment + 10s delays)

If all 5 succeed → Launch full campaign
If any fail → Diagnose and revise fix

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
Date: 2025-11-16
Cycle: 1374
"""

import sys
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')

# Import modified V6a script
from c186_v6a_net_zero_homeostasis import (
    run_experiment,
    RESULTS_DIR,
    F_SPAWN_VALUES,
    SPAWN_LABELS
)

import time
import json

def run_test():
    """Run 5-experiment test to validate filesystem sync fix."""
    print("="*80)
    print("V6a TEST - 5 EXPERIMENTS (Filesystem Sync Validation)")
    print("="*80)
    print()
    print("Purpose: Validate that 10-second delays prevent database I/O errors")
    print("Test: 1 spawn rate (0.10%) × 5 seeds (42-46)")
    print("Expected: 100% success rate (0 database I/O errors)")
    print()

    # Test configuration
    f_spawn = F_SPAWN_VALUES[0]  # 0.001 (0.10%)
    spawn_label = SPAWN_LABELS[0]  # "0.10%"
    test_seeds = list(range(42, 47))  # 5 seeds

    print(f"Spawn rate: {spawn_label} (f={f_spawn})")
    print(f"Seeds: {test_seeds}")
    print()

    results = []
    start_time = time.time()

    for i, seed in enumerate(test_seeds):
        print()
        print(f"--- Test Experiment {i+1}/5 ---")
        print()

        try:
            success = run_experiment(f_spawn, spawn_label, seed)
            results.append({
                'seed': seed,
                'success': success
            })

            # Filesystem sync delay (same as full campaign)
            print()
            print(f"[SYNC] Filesystem sync delay (10 seconds)...")
            import os
            os.sync()
            time.sleep(10)
            print(f"[SYNC] Ready for next experiment")
            print()

        except Exception as e:
            print()
            print(f"[ERROR] Experiment failed: {e}")
            print()
            import traceback
            traceback.print_exc()
            results.append({
                'seed': seed,
                'success': False,
                'error': str(e)
            })

            # Filesystem sync delay (even after errors)
            print()
            print(f"[SYNC] Filesystem sync delay (10 seconds)...")
            import os
            os.sync()
            time.sleep(10)
            print(f"[SYNC] Ready for next experiment")
            print()

    elapsed = time.time() - start_time

    # Test summary
    print()
    print("="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"Duration: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"Experiments: {len(results)}")
    print(f"Successes: {sum(1 for r in results if r['success'])}")
    print(f"Failures: {sum(1 for r in results if not r['success'])}")
    print()

    success_rate = sum(1 for r in results if r['success']) / len(results)

    if success_rate == 1.0:
        print("✓✓✓ TEST PASSED: 100% success rate")
        print("  → Filesystem sync fix is WORKING")
        print("  → Ready to launch full 50-experiment campaign")
    elif success_rate >= 0.8:
        print("⚠ TEST PARTIAL: 80%+ success rate")
        print("  → Fix improved success rate (was 8%, now {:.0%})".format(success_rate))
        print("  → May need additional delays or alternative approach")
    else:
        print("✗ TEST FAILED: <80% success rate")
        print("  → Fix did not resolve issue")
        print("  → Need alternative approach (RAM-based DB)")

    print("="*80)
    print()

    # Save test summary
    test_summary = {
        'test': 'V6a_5_EXPERIMENT_VALIDATION',
        'purpose': 'Validate filesystem sync fix prevents database I/O errors',
        'configuration': {
            'spawn_rate': f_spawn,
            'spawn_label': spawn_label,
            'seeds': test_seeds
        },
        'results': results,
        'summary': {
            'total': len(results),
            'successes': sum(1 for r in results if r['success']),
            'failures': sum(1 for r in results if not r['success']),
            'success_rate': success_rate,
            'duration_seconds': elapsed
        },
        'verdict': {
            'passed': success_rate == 1.0,
            'ready_for_full_campaign': success_rate >= 0.8
        }
    }

    test_output = RESULTS_DIR / "v6a_test_5experiments.json"
    with open(test_output, 'w') as f:
        json.dump(test_summary, f, indent=2)

    print(f"Test summary saved: {test_output}")
    print()

    return test_summary

if __name__ == '__main__':
    test_summary = run_test()
    sys.exit(0 if test_summary['verdict']['passed'] else 1)
