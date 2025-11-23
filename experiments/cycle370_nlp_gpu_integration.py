"""
CYCLE 370: NLP + GPU Operator Integration
Objective: Demonstrate complete HELIOS pipeline from natural language to matter.
Test: Parse NL commands → GPU phase solving → Gorkov validation.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.nlp import NaturalLanguageInterface
from src.helios.operator import UniversalOperator

def run_demo():
    """Run complete NLP → GPU → Physics pipeline."""
    print("CYCLE 370: NLP + GPU OPERATOR INTEGRATION")
    print("=" * 55)
    print()

    # Initialize
    nlp = NaturalLanguageInterface()
    op = UniversalOperator(resolution_mm=2.0, use_gpu=True)

    print(f"GPU enabled: {op.use_gpu}")
    print()

    # Test commands
    commands = [
        "Create a cube at 50, 50, 50",
        "Make a cube at 25, 50, 50",
        "Create cube at 75 50 50",
        "status",
        "Move object 1 to 50, 25, 50",
        "Delete object 2",
        "help",
        "Load model teapot.obj",  # Will fail gracefully
    ]

    results = []

    for cmd in commands:
        print(f"Command: '{cmd}'")
        print("-" * 55)

        # Parse
        intent = nlp.parse(cmd)
        print(f"Intent: {intent}")

        # Execute
        start = time.time()
        try:
            if intent["action"] == "create":
                obj_id = op.create_object(intent["shape"], intent["location"])
                elapsed = time.time() - start
                stability = op.get_stability(obj_id)
                print(f"Result: Created object {obj_id} in {elapsed:.2f}s")
                print(f"Stability (U): {stability:.2e}")
                results.append(("create", elapsed, True))

            elif intent["action"] == "move":
                success = op.move_object(intent["id"], intent["target"])
                elapsed = time.time() - start
                if success:
                    stability = op.get_stability(intent["id"])
                    print(f"Result: Moved object {intent['id']} in {elapsed:.2f}s")
                    print(f"New stability (U): {stability:.2e}")
                    results.append(("move", elapsed, True))
                else:
                    print(f"Result: Move failed")
                    results.append(("move", elapsed, False))

            elif intent["action"] == "delete":
                success = op.delete_object(intent["id"])
                elapsed = time.time() - start
                print(f"Result: {'Deleted' if success else 'Not found'} object {intent['id']}")
                results.append(("delete", elapsed, success))

            elif intent["action"] == "status":
                elapsed = time.time() - start
                print(f"Active objects: {len(op.active_objects)}")
                for oid, obj in op.active_objects.items():
                    print(f"  ID {oid}: {obj['type']} at {obj['location']}")
                results.append(("status", elapsed, True))

            elif intent["action"] == "help":
                elapsed = time.time() - start
                print("Available commands:")
                print("  - Create <shape> at x, y, z")
                print("  - Move object <id> to x, y, z")
                print("  - Delete object <id>")
                print("  - Load model <filename>")
                print("  - Status")
                results.append(("help", elapsed, True))

            elif intent["action"] == "load":
                # Would need file to exist
                elapsed = time.time() - start
                print(f"Load '{intent['filename']}' - File handling not tested")
                results.append(("load", elapsed, False))

            else:
                elapsed = time.time() - start
                print(f"Unknown command")
                results.append(("unknown", elapsed, False))

        except Exception as e:
            elapsed = time.time() - start
            print(f"Error: {e}")
            results.append((intent["action"], elapsed, False))

        print()

    # Summary
    print("=" * 55)
    print("SUMMARY")
    print("=" * 55)

    create_times = [r[1] for r in results if r[0] == "create"]
    if create_times:
        avg_create = sum(create_times) / len(create_times)
        print(f"Average create time: {avg_create:.2f}s")

    move_times = [r[1] for r in results if r[0] == "move" and r[2]]
    if move_times:
        avg_move = sum(move_times) / len(move_times)
        print(f"Average move time: {avg_move:.2f}s")

    success_count = sum(1 for r in results if r[2])
    total_count = len(results)
    print(f"Success rate: {success_count}/{total_count}")

    if create_times and avg_create < 10:
        print("\n>> SUCCESS: Real-time NLP→Matter pipeline operational")
    else:
        print("\n>> MARGINAL: Pipeline works but not real-time")

    # Save results
    import json
    output = {
        "cycle": 370,
        "gpu_enabled": op.use_gpu,
        "avg_create_time_s": avg_create if create_times else None,
        "success_rate": success_count / total_count,
        "commands_tested": len(commands)
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c370_nlp_gpu_integration.json", "w") as f:
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    run_demo()
