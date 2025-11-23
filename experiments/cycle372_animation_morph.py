"""
CYCLE 372: Animation Morph Test
Objective: Test shape morphing (cube → pyramid) with GPU acceleration.
Validates: Animator interpolation → GPU phase solving → 4D printing sequence.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import sys
import os
import time
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.operator import UniversalOperator
from src.helios.animator import Animator

def main():
    print("CYCLE 372: ANIMATION MORPH TEST")
    print("=" * 55)

    # Initialize
    op = UniversalOperator(resolution_mm=2.0, use_gpu=True)
    animator = Animator()

    print(f"GPU enabled: {op.use_gpu}")
    print()

    # Load keyframes
    models_dir = "/Volumes/dual/DUALITY-ZERO-V2/data/models"
    cube_path = f"{models_dir}/cube_demo.obj"
    pyramid_path = f"{models_dir}/pyramid.obj"

    print("Loading keyframes...")
    start = time.time()
    cube_mesh = animator.load_keyframe(cube_path, scale_mm=40.0)
    pyramid_mesh = animator.load_keyframe(pyramid_path, scale_mm=40.0)
    load_time = time.time() - start
    print(f"  Cube: {len(cube_mesh[0])} vertices")
    print(f"  Pyramid: {len(pyramid_mesh[0])} vertices")
    print(f"  Load time: {load_time:.2f}s")
    print()

    # Generate interpolation sequence
    num_frames = 5  # Keep small for testing
    print(f"Generating {num_frames} interpolation frames...")
    start = time.time()
    targets_sequence = animator.interpolate(cube_mesh, pyramid_mesh, num_frames)
    interp_time = time.time() - start
    print(f"  Points per frame: {len(targets_sequence[0])}")
    print(f"  Interpolation time: {interp_time:.2f}s")
    print()

    # Compile phases for each frame
    print("Compiling phase sequences (GPU)...")
    start = time.time()
    phase_sequence = animator.generate_sequence(op, targets_sequence)
    compile_time = time.time() - start
    print(f"  Total compile time: {compile_time:.2f}s")
    print(f"  Per-frame average: {compile_time/num_frames:.2f}s")
    print()

    # Validate last frame
    print("Validating final frame...")
    for i, e in enumerate(op.emitters):
        e.phase = phase_sequence[-1][i]
    field = op.box.propagate(op.emitters)
    potential = op.box.calculate_gorkov_potential(field)
    min_U = potential.min()
    print(f"  Min Gorkov potential: {min_U:.2e}")
    print()

    # Summary
    total_time = load_time + interp_time + compile_time
    print("=" * 55)
    print("SUMMARY")
    print("=" * 55)
    print(f"Frames: {num_frames}")
    print(f"Points per frame: {len(targets_sequence[0])}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Per-frame: {compile_time/num_frames:.2f}s")

    if compile_time/num_frames < 10:
        print("\n>> SUCCESS: Animation compilation real-time capable")
    else:
        print("\n>> MARGINAL: Animation works but not real-time")

    # Save results
    output = {
        "cycle": 372,
        "gpu_enabled": op.use_gpu,
        "num_frames": num_frames,
        "points_per_frame": len(targets_sequence[0]),
        "load_time_s": load_time,
        "interp_time_s": interp_time,
        "compile_time_s": compile_time,
        "per_frame_s": compile_time/num_frames,
        "min_gorkov_U": min_U
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c372_animation_morph.json", "w") as f:
        json.dump(output, f, indent=2, default=float)


if __name__ == "__main__":
    main()
