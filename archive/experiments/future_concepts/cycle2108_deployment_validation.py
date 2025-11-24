"""
Cycle 2108: Deployment Validation Test
======================================
Comprehensive validation using optimized parameters from C2092-C2107.

Optimized parameters:
- K = 8 memories (C2096)
- D = 1024 (C2097)
- σ = 0.005 (C2106 - conservative)
- Hebbian = 0.3× (C2107 - optimal)
- Target: 80 items (safe zone from C2102)

Test complete deployment scenario:
1. Initial load
2. Operation for 500 cycles
3. Add 20 items
4. Remove 20 items
5. Final accuracy
"""

import numpy as np
import json
from datetime import datetime

class DeploymentValidation:
    def __init__(self):
        self.dimension = 1024
        self.k_memories = 8
        self.noise_sigma = 0.005  # Conservative
        self.hebbian_strength = 0.3  # Optimal
        self.initial_items = 60
        self.add_items = 20
        self.remove_items = 20

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

    def run_deployment(self, seed):
        """Run complete deployment scenario."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        active_items = []  # (key, value, mem_idx)
        all_values = []

        results = {"phases": []}

        # Phase 1: Initial load (60 items)
        for _ in range(self.initial_items):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            active_items.append((key, value, mem_idx))
            all_values.append(value)

        # Warmup (100 cycles)
        for cycle in range(100):
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue
                noise = np.random.normal(0, self.noise_sigma, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)
                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + self.hebbian_strength * binding)

        acc = self._test_accuracy(memories, active_items, all_values)
        results["phases"].append({"phase": "initial_60", "accuracy": float(acc), "n_items": 60})

        # Phase 2: Steady operation (400 more cycles)
        for cycle in range(400):
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue
                noise = np.random.normal(0, self.noise_sigma, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)
                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + self.hebbian_strength * binding)

        acc = self._test_accuracy(memories, active_items, all_values)
        results["phases"].append({"phase": "steady_500", "accuracy": float(acc), "n_items": 60})

        # Phase 3: Add 20 items (total 80)
        for _ in range(self.add_items):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            active_items.append((key, value, mem_idx))
            all_values.append(value)

        # Integration (100 cycles)
        for cycle in range(100):
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue
                noise = np.random.normal(0, self.noise_sigma, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)
                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + self.hebbian_strength * binding)

        acc = self._test_accuracy(memories, active_items, all_values)
        results["phases"].append({"phase": "added_80", "accuracy": float(acc), "n_items": 80})

        # Phase 4: Remove 20 items (back to 60)
        removed = active_items[:self.remove_items]
        active_items = active_items[self.remove_items:]

        # Update memory_items
        for mem_idx in range(self.k_memories):
            memory_items[mem_idx] = [(k, v) for k, v, m in active_items if m == mem_idx]

        # Stabilization (100 cycles)
        for cycle in range(100):
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue
                noise = np.random.normal(0, self.noise_sigma, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)
                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + self.hebbian_strength * binding)

        acc = self._test_accuracy(memories, active_items, all_values)
        results["phases"].append({"phase": "removed_60", "accuracy": float(acc), "n_items": 60})

        return results

    def _test_accuracy(self, memories, active_items, codebook):
        correct = 0
        for key, value, mem_idx in active_items:
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, value) > 0.5:
                correct += 1
        return correct / len(active_items) if active_items else 0

    def run_experiment(self):
        """Run deployment validation."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "noise_sigma": self.noise_sigma,
                "hebbian_strength": self.hebbian_strength,
                "timestamp": datetime.now().isoformat()
            },
            "phases": []
        }

        print("Optimized Deployment Parameters:")
        print(f"  D = {self.dimension}")
        print(f"  K = {self.k_memories}")
        print(f"  σ = {self.noise_sigma}")
        print(f"  Hebbian = {self.hebbian_strength}×")
        print()
        print(f"{'Phase':<15} {'Items':<8} {'Accuracy':<12}")
        print("-" * 40)

        # Single trial with optimized parameters
        trial_results = self.run_deployment(seed=42)

        for phase in trial_results["phases"]:
            results["phases"].append(phase)
            print(f"{phase['phase']:<15} {phase['n_items']:<8} {phase['accuracy']*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Validate deployment."""
        phases = results["phases"]
        analysis = {"findings": []}

        # Check all phases pass 90%
        all_pass = all(p["accuracy"] >= 0.9 for p in phases)

        if all_pass:
            analysis["findings"].append(
                "✅ DEPLOYMENT VALIDATED: All phases ≥90% accuracy"
            )
            analysis["validated"] = True
        else:
            failing = [p for p in phases if p["accuracy"] < 0.9]
            analysis["findings"].append(
                f"❌ Phases below 90%: {', '.join(p['phase'] for p in failing)}"
            )
            analysis["validated"] = False

        # Report final accuracy
        final = phases[-1]
        analysis["findings"].append(
            f"Final accuracy: {final['accuracy']*100:.0f}%"
        )

        # Overall assessment
        min_acc = min(p["accuracy"] for p in phases)
        analysis["findings"].append(
            f"Minimum accuracy: {min_acc*100:.0f}%"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2108: Deployment Validation Test")
    print("=" * 60)
    print()

    exp = DeploymentValidation()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2108_deployment_validation.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
