"""
CYCLE 371: Complex Mesh Compilation
Objective: Test HELIOS with 3D mesh files (OBJ format).
Validates: Mesh loading → Voxelization → GPU phase solving → Physics.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import sys
import os
import time
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.operator import UniversalOperator

def test_mesh_file(op, filepath, name):
    """Test loading and compiling a mesh file."""
    print(f"\nTest: {name}")
    print("-" * 50)

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None

    start = time.time()
    try:
        obj_id, num_targets = op.create_from_file(filepath, scale_mm=40.0)
        elapsed = time.time() - start

        stability = op.get_stability(obj_id)

        print(f"Object ID: {obj_id}")
        print(f"Target points: {num_targets}")
        print(f"Compile time: {elapsed:.2f}s")
        print(f"Stability (U): {stability:.2e}")

        return {
            "name": name,
            "targets": num_targets,
            "time_s": elapsed,
            "stability": stability,
            "success": True
        }

    except Exception as e:
        elapsed = time.time() - start
        print(f"Error: {e}")
        return {
            "name": name,
            "time_s": elapsed,
            "error": str(e),
            "success": False
        }


def main():
    print("CYCLE 371: COMPLEX MESH COMPILATION")
    print("=" * 55)

    # Initialize GPU operator
    op = UniversalOperator(resolution_mm=2.0, use_gpu=True)
    print(f"GPU enabled: {op.use_gpu}")

    # Test meshes
    models_dir = "/Volumes/dual/DUALITY-ZERO-V2/data/models"
    meshes = [
        (f"{models_dir}/cube_demo.obj", "Cube Demo"),
        (f"{models_dir}/pyramid.obj", "Pyramid"),
        (f"{models_dir}/pyramid_demo.obj", "Pyramid Demo"),
    ]

    results = []

    for filepath, name in meshes:
        result = test_mesh_file(op, filepath, name)
        if result:
            results.append(result)

    # Summary
    print("\n" + "=" * 55)
    print("SUMMARY")
    print("=" * 55)

    successful = [r for r in results if r.get("success")]
    if successful:
        avg_time = sum(r["time_s"] for r in successful) / len(successful)
        total_targets = sum(r["targets"] for r in successful)

        print(f"Meshes compiled: {len(successful)}/{len(results)}")
        print(f"Total target points: {total_targets}")
        print(f"Average compile time: {avg_time:.2f}s")

        if avg_time < 15:
            print("\n>> SUCCESS: Mesh compilation operational")
        else:
            print("\n>> MARGINAL: Mesh compilation slow but functional")
    else:
        print(">> FAILURE: No meshes compiled successfully")

    # Save results
    output = {
        "cycle": 371,
        "gpu_enabled": op.use_gpu,
        "results": results
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c371_mesh_compilation.json", "w") as f:
        json.dump(output, f, indent=2, default=str)


if __name__ == "__main__":
    main()
