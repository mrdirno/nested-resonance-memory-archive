"""
Cycle 2098: Dynamic Operations Test
====================================
Real deployments need continuous add/remove operations.

Test: Start with 50 items, then:
1. Add 25 more items
2. Remove 25 items (via intentional forgetting)
3. Add 25 different items
4. Measure accuracy throughout

This tests the practical deployment scenario.
"""

import numpy as np
import json
from datetime import datetime

class DynamicOperationsTest:
    def __init__(self):
        self.num_trials = 3
        self.dimension = 1024
        self.k_memories = 8
        self.cycles_per_phase = 100

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _hash_key(self, key, k_memories):
        return int(abs(key[0]) * 1000) % k_memories

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def test_retrieval(self, memories, active_items, codebook):
        """Test retrieval accuracy for active items."""
        correct = 0
        for key, value, mem_idx in active_items:
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1
        return correct / len(active_items) if active_items else 0

    def run_cycles(self, memories, active_items):
        """Run maintenance cycles for active items."""
        d = self.dimension

        for cycle in range(self.cycles_per_phase):
            for mem_idx in range(self.k_memories):
                # Get items in this memory
                mem_items = [(k, v) for k, v, m in active_items if m == mem_idx]
                if not mem_items:
                    continue

                # Add noise
                noise = np.random.normal(0, 0.01, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                # Hebbian refresh
                item_idx = cycle % len(mem_items)
                key, value = mem_items[item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.5 * binding)

    def run_trial(self, seed):
        """Run dynamic operations trial."""
        np.random.seed(seed)
        d = self.dimension

        # Initialize memories
        memories = [np.zeros(d) for _ in range(self.k_memories)]
        active_items = []  # (key, value, mem_idx)
        all_values = []    # Global codebook

        results = {
            "phases": []
        }

        # Phase 1: Initial 50 items
        for _ in range(50):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)

            active_items.append((key, value, mem_idx))
            all_values.append(value)

        self.run_cycles(memories, active_items)
        acc_p1 = self.test_retrieval(memories, active_items, all_values)
        results["phases"].append({
            "phase": "initial_50",
            "n_active": len(active_items),
            "accuracy": float(acc_p1)
        })

        # Phase 2: Add 25 more items (total 75)
        for _ in range(25):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)

            active_items.append((key, value, mem_idx))
            all_values.append(value)

        self.run_cycles(memories, active_items)
        acc_p2 = self.test_retrieval(memories, active_items, all_values)
        results["phases"].append({
            "phase": "add_25",
            "n_active": len(active_items),
            "accuracy": float(acc_p2)
        })

        # Phase 3: Remove 25 items (back to 50)
        # Remove by not refreshing (intentional forgetting)
        items_to_remove = active_items[:25]
        active_items = active_items[25:]  # Keep only last 50

        # Run cycles without the removed items
        self.run_cycles(memories, active_items)
        acc_p3 = self.test_retrieval(memories, active_items, all_values)
        results["phases"].append({
            "phase": "remove_25",
            "n_active": len(active_items),
            "accuracy": float(acc_p3)
        })

        # Phase 4: Add 25 new items (back to 75)
        for _ in range(25):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)

            active_items.append((key, value, mem_idx))
            all_values.append(value)

        self.run_cycles(memories, active_items)
        acc_p4 = self.test_retrieval(memories, active_items, all_values)
        results["phases"].append({
            "phase": "add_new_25",
            "n_active": len(active_items),
            "accuracy": float(acc_p4)
        })

        return results

    def run_experiment(self):
        """Run multiple trials."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "cycles_per_phase": self.cycles_per_phase,
                "num_trials": self.num_trials,
                "timestamp": datetime.now().isoformat()
            },
            "phases": []
        }

        print(f"D={self.dimension}, K={self.k_memories}, {self.cycles_per_phase} cycles/phase")
        print()
        print(f"{'Phase':<15} {'Items':<8} {'Accuracy':<12}")
        print("-" * 40)

        # Aggregate across trials
        phase_accs = {
            "initial_50": [],
            "add_25": [],
            "remove_25": [],
            "add_new_25": []
        }

        for trial in range(self.num_trials):
            trial_results = self.run_trial(seed=trial*100)
            for phase in trial_results["phases"]:
                phase_accs[phase["phase"]].append(phase["accuracy"])

        for phase_name in ["initial_50", "add_25", "remove_25", "add_new_25"]:
            mean_acc = np.mean(phase_accs[phase_name])
            n_items = {"initial_50": 50, "add_25": 75, "remove_25": 50, "add_new_25": 75}[phase_name]

            results["phases"].append({
                "phase": phase_name,
                "n_active": n_items,
                "accuracy": float(mean_acc)
            })

            print(f"{phase_name:<15} {n_items:<8} {mean_acc*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Evaluate dynamic operation performance."""
        phases = results["phases"]
        analysis = {"findings": []}

        # Check if accuracy maintained through all phases
        accs = [p["accuracy"] for p in phases]
        if min(accs) >= 0.8:
            analysis["findings"].append(
                "All phases maintain 80%+ accuracy"
            )
            analysis["stable"] = True
        else:
            low_phases = [p["phase"] for p in phases if p["accuracy"] < 0.8]
            analysis["findings"].append(
                f"Accuracy drops below 80% in: {', '.join(low_phases)}"
            )
            analysis["stable"] = False

        # Check recovery after removal
        p3 = [p for p in phases if p["phase"] == "remove_25"][0]
        p4 = [p for p in phases if p["phase"] == "add_new_25"][0]

        if p4["accuracy"] >= p3["accuracy"]:
            analysis["findings"].append(
                "System recovers after removal + addition cycle"
            )
        else:
            analysis["findings"].append(
                f"Degradation after removal+add: {p3['accuracy']*100:.0f}% → {p4['accuracy']*100:.0f}%"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2098: Dynamic Operations Test")
    print("=" * 60)
    print()

    exp = DynamicOperationsTest()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2098_dynamic_operations.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
