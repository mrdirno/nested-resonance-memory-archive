"""
Cycle 2116: Tree with Positional Child Binding
=============================================
C2115 failed because parent→children is multi-binding.

Workaround: Use positional binding
- parent ⊛ pos_0 → child_0
- parent ⊛ pos_1 → child_1

This makes each binding unique.
"""

import numpy as np
import json
from datetime import datetime

class TreePositionalTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
        self.num_cycles = 200

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_trial(self, depth, branching, seed):
        """Store tree with positional child binding."""
        np.random.seed(seed)
        d = self.dimension

        # Position vectors for children
        positions = [self._generate(d) for _ in range(branching)]

        # Create tree
        num_nodes = sum(branching**i for i in range(depth + 1))
        nodes = [self._generate(d) for _ in range(num_nodes)]

        # Create edges with positions
        edges = []  # (parent_idx, child_pos, child_idx)
        current_idx = 0

        for level in range(depth):
            nodes_at_level = branching**level
            for i in range(nodes_at_level):
                parent_idx = current_idx + i
                for j in range(branching):
                    child_idx = current_idx + nodes_at_level + i * branching + j
                    if child_idx < num_nodes:
                        edges.append((parent_idx, j, child_idx))
            current_idx += nodes_at_level

        if not edges:
            return 1.0

        # Store with positional binding: (parent ⊛ pos) → child
        memory = np.zeros(d)
        for parent_idx, child_pos, child_idx in edges:
            key = self._circ_conv(nodes[parent_idx], positions[child_pos])
            binding = self._circ_conv(key, nodes[child_idx])
            memory = self._normalize(memory + binding)

        # Maintenance
        for cycle in range(self.num_cycles):
            noise = np.random.normal(0, 0.005, d)
            memory = self._normalize(memory + noise)

            edge_idx = cycle % len(edges)
            parent_idx, child_pos, child_idx = edges[edge_idx]
            key = self._circ_conv(nodes[parent_idx], positions[child_pos])
            binding = self._circ_conv(key, nodes[child_idx])
            memory = self._normalize(memory + 0.3 * binding)

        # Test
        correct = 0
        for parent_idx, child_pos, child_idx in edges:
            key = self._circ_conv(nodes[parent_idx], positions[child_pos])
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memory, key_inv)
            retrieved = self._cleanup(retrieved, nodes)

            if np.dot(retrieved, nodes[child_idx]) > 0.5:
                correct += 1

        return correct / len(edges)

    def run_experiment(self):
        """Test tree with positional binding."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "num_cycles": self.num_cycles,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "tests": []
        }

        print(f"D={self.dimension}")
        print()
        print(f"{'Depth':<8} {'Branch':<10} {'Edges':<8} {'Accuracy':<10}")
        print("-" * 40)

        test_cases = [
            (3, 2),
            (4, 2),
            (3, 3),
            (2, 5),
        ]

        for depth, branching in test_cases:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_trial(depth, branching, seed=trial*100+depth+branching)
                accs.append(acc)

            mean_acc = np.mean(accs)
            num_nodes = sum(branching**i for i in range(depth + 1))
            num_edges = num_nodes - 1

            results["tests"].append({
                "depth": depth,
                "branching": branching,
                "num_edges": num_edges,
                "accuracy": float(mean_acc)
            })

            print(f"{depth:<8} {branching:<10} {num_edges:<8} {mean_acc*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate positional tree storage."""
        tests = results["tests"]
        analysis = {"findings": []}

        avg_acc = np.mean([t["accuracy"] for t in tests])

        if avg_acc >= 0.8:
            analysis["findings"].append(
                f"Positional tree works: {avg_acc*100:.0f}% avg"
            )
        else:
            analysis["findings"].append(
                f"Positional tree limited: {avg_acc*100:.0f}% avg"
            )

        # Compare to C2115
        c2115_avg = 25  # From previous experiment
        improvement = (avg_acc * 100) - c2115_avg
        if improvement > 10:
            analysis["findings"].append(
                f"Improvement over direct binding: +{improvement:.0f}%"
            )

        # Best configuration
        best = max(tests, key=lambda x: x["accuracy"])
        analysis["findings"].append(
            f"Best: depth={best['depth']}, branch={best['branching']} at {best['accuracy']*100:.0f}%"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2116: Tree with Positional Child Binding")
    print("=" * 60)
    print()

    exp = TreePositionalTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2116_tree_positional.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
