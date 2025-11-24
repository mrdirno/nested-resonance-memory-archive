"""
Cycle 2114: Graph Storage Test
==============================
Can we store and traverse graphs?

Method: Store edges as (source ⊛ edge_type → target)
- memory = source1 ⊛ target1 + source2 ⊛ target2 + ...

Query: source → target (traverse edge)
"""

import numpy as np
import json
from datetime import datetime

class GraphStorageTest:
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

    def run_trial(self, num_nodes, num_edges, seed):
        """Store and traverse a graph."""
        np.random.seed(seed)
        d = self.dimension

        # Create nodes
        nodes = [self._generate(d) for _ in range(num_nodes)]

        # Create random edges (source, target)
        edges = []
        for _ in range(num_edges):
            src_idx = np.random.randint(num_nodes)
            tgt_idx = np.random.randint(num_nodes)
            if src_idx != tgt_idx:  # No self-loops
                edges.append((src_idx, tgt_idx))

        # Store graph in memory
        memory = np.zeros(d)
        for src_idx, tgt_idx in edges:
            binding = self._circ_conv(nodes[src_idx], nodes[tgt_idx])
            memory = self._normalize(memory + binding)

        # Maintenance
        for cycle in range(self.num_cycles):
            noise = np.random.normal(0, 0.005, d)
            memory = self._normalize(memory + noise)

            # Refresh one edge
            edge_idx = cycle % len(edges)
            src_idx, tgt_idx = edges[edge_idx]
            binding = self._circ_conv(nodes[src_idx], nodes[tgt_idx])
            memory = self._normalize(memory + 0.3 * binding)

        # Test traversal
        correct = 0
        for src_idx, tgt_idx in edges:
            src_inv = np.roll(nodes[src_idx][::-1], 1)
            retrieved = self._circ_conv(memory, src_inv)
            retrieved = self._cleanup(retrieved, nodes)

            if np.dot(retrieved, nodes[tgt_idx]) > 0.5:
                correct += 1

        return correct / len(edges) if edges else 0

    def run_experiment(self):
        """Test graph storage at various sizes."""
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
        print(f"{'Nodes':<8} {'Edges':<8} {'Accuracy':<12}")
        print("-" * 30)

        test_cases = [
            (10, 20),   # Sparse
            (10, 30),   # Medium
            (10, 40),   # Dense
            (20, 40),   # Larger sparse
        ]

        for num_nodes, num_edges in test_cases:
            accs = []

            for trial in range(self.num_trials):
                acc = self.run_trial(num_nodes, num_edges, seed=trial*100+num_nodes)
                accs.append(acc)

            mean_acc = np.mean(accs)

            results["tests"].append({
                "num_nodes": num_nodes,
                "num_edges": num_edges,
                "accuracy": float(mean_acc)
            })

            print(f"{num_nodes:<8} {num_edges:<8} {mean_acc*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate graph storage capability."""
        tests = results["tests"]
        analysis = {"findings": []}

        # Average accuracy
        avg_acc = np.mean([t["accuracy"] for t in tests])

        if avg_acc >= 0.8:
            analysis["findings"].append(
                f"Graph storage works: {avg_acc*100:.0f}% avg traversal"
            )
        else:
            analysis["findings"].append(
                f"Graph storage limited: {avg_acc*100:.0f}% avg"
            )

        # Best configuration
        best = max(tests, key=lambda x: x["accuracy"])
        analysis["findings"].append(
            f"Best: {best['num_nodes']} nodes, {best['num_edges']} edges at {best['accuracy']*100:.0f}%"
        )

        # Edge density effect
        for t in tests:
            density = t["num_edges"] / (t["num_nodes"] * (t["num_nodes"]-1))
            if t["accuracy"] < 0.7:
                analysis["findings"].append(
                    f"Degradation at density {density:.2f}"
                )
                break

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2114: Graph Storage Test")
    print("=" * 60)
    print()

    exp = GraphStorageTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2114_graph_storage.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
