"""
CYCLE 369: End-to-End GPU Validation
Objective: Validate complete HELIOS pipeline with GPU acceleration.
Test: Create object, solve phases, calculate stability - measure total time.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.operator import UniversalOperator

def test_cube_creation():
    """Test basic cube creation with GPU acceleration."""
    print("Test 1: Cube Creation")
    print("-" * 40)

    # GPU operator
    op_gpu = UniversalOperator(resolution_mm=2.0, use_gpu=True)
    print(f"GPU enabled: {op_gpu.use_gpu}")

    start = time.time()
    obj_id = op_gpu.create_object("cube", (50, 50, 50))
    gpu_time = time.time() - start

    print(f"Object created: ID {obj_id}")
    print(f"Time: {gpu_time:.2f} s")

    # Get stability
    stability = op_gpu.get_stability(obj_id)
    print(f"Stability (Gorkov U): {stability:.2e}")

    return gpu_time, stability

def test_resolution_scaling():
    """Test performance at different resolutions."""
    print("\nTest 2: Resolution Scaling")
    print("-" * 40)

    results = []

    for res in [4.0, 2.0, 1.0]:
        voxels = int((100/res)**3)
        op = UniversalOperator(resolution_mm=res, use_gpu=True)

        start = time.time()
        obj_id = op.create_object("cube", (50, 50, 50))
        elapsed = time.time() - start

        stability = op.get_stability(obj_id)

        print(f"Resolution {res}mm: {voxels:,} voxels, {elapsed:.2f}s, U={stability:.2e}")
        results.append((res, voxels, elapsed, stability))

    return results

def test_multi_object():
    """Test creating multiple objects."""
    print("\nTest 3: Multi-Object Scene")
    print("-" * 40)

    op = UniversalOperator(resolution_mm=2.0, use_gpu=True)

    start = time.time()

    # Create 3 cubes at different locations
    id1 = op.create_object("cube", (25, 50, 50))
    id2 = op.create_object("cube", (50, 50, 50))
    id3 = op.create_object("cube", (75, 50, 50))

    elapsed = time.time() - start

    print(f"Created 3 objects in {elapsed:.2f}s")
    print(f"Average per object: {elapsed/3:.2f}s")

    return elapsed

def main():
    print("CYCLE 369: END-TO-END GPU VALIDATION")
    print("=" * 50)
    print()

    # Test 1: Basic creation
    cube_time, stability = test_cube_creation()

    # Test 2: Resolution scaling
    scaling_results = test_resolution_scaling()

    # Test 3: Multi-object
    multi_time = test_multi_object()

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Cube creation (2mm res): {cube_time:.2f}s")
    print(f"Multi-object (3 cubes): {multi_time:.2f}s ({multi_time/3:.2f}s each)")

    # Find 1mm resolution result
    for res, voxels, elapsed, _ in scaling_results:
        if res == 1.0:
            print(f"High-res (1mm, {voxels:,} voxels): {elapsed:.2f}s")

    if cube_time < 10:
        print("\n>> SUCCESS: Real-time capable (<10s per object)")
    else:
        print("\n>> MARGINAL: Usable but not real-time")

    # Save results
    output = {
        "cycle": 369,
        "cube_creation_time_s": cube_time,
        "multi_object_time_s": multi_time,
        "resolution_scaling": [
            {"res_mm": r, "voxels": v, "time_s": t}
            for r, v, t, _ in scaling_results
        ]
    }

    import json
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c369_gpu_validation.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nResults saved to experiments/results/c369_gpu_validation.json")


if __name__ == "__main__":
    main()
