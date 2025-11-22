"""
Cycle 2117: Efficiency Measurement
==================================
Measure computational efficiency of the holographic memory.

Metrics:
- Storage operations per second
- Retrieval operations per second
- Maintenance cycles per second
"""

import numpy as np
import json
import time
from datetime import datetime

class EfficiencyMeasurement:
    def __init__(self):
        self.dimension = 1024
        self.k_memories = 8

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

    def measure_storage(self, num_items):
        """Measure storage operations per second."""
        d = self.dimension
        np.random.seed(42)

        memories = [np.zeros(d) for _ in range(self.k_memories)]

        keys = [self._generate(d) for _ in range(num_items)]
        values = [self._generate(d) for _ in range(num_items)]

        start = time.time()

        for key, value in zip(keys, values):
            mem_idx = self._hash_key(key, self.k_memories)
            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)

        elapsed = time.time() - start
        ops_per_sec = num_items / elapsed if elapsed > 0 else 0

        return ops_per_sec, elapsed

    def measure_retrieval(self, num_items, num_queries):
        """Measure retrieval operations per second."""
        d = self.dimension
        np.random.seed(42)

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        keys = []
        values = []

        # Setup
        for _ in range(num_items):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

            keys.append(key)
            values.append(value)

        codebook = values.copy()

        # Measure retrieval
        start = time.time()

        for i in range(num_queries):
            key = keys[i % num_items]
            value = values[i % num_items]
            mem_idx = self._hash_key(key, self.k_memories)

            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)

        elapsed = time.time() - start
        ops_per_sec = num_queries / elapsed if elapsed > 0 else 0

        return ops_per_sec, elapsed

    def measure_maintenance(self, num_items, num_cycles):
        """Measure maintenance cycles per second."""
        d = self.dimension
        np.random.seed(42)

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        # Setup
        for _ in range(num_items):
            key = self._generate(d)
            value = self._generate(d)
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

        # Measure maintenance
        start = time.time()

        for cycle in range(num_cycles):
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue

                noise = np.random.normal(0, 0.005, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)

                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.3 * binding)

        elapsed = time.time() - start
        cycles_per_sec = num_cycles / elapsed if elapsed > 0 else 0

        return cycles_per_sec, elapsed

    def run_experiment(self):
        """Measure all efficiency metrics."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "timestamp": datetime.now().isoformat()
            },
            "measurements": []
        }

        print(f"D={self.dimension}, K={self.k_memories}")
        print()

        # Storage efficiency
        print("Storage Efficiency:")
        for num_items in [100, 500, 1000]:
            ops, elapsed = self.measure_storage(num_items)
            results["measurements"].append({
                "operation": "storage",
                "items": num_items,
                "ops_per_sec": float(ops),
                "time_sec": float(elapsed)
            })
            print(f"  {num_items} items: {ops:.0f} ops/sec ({elapsed*1000:.1f}ms)")

        print()

        # Retrieval efficiency
        print("Retrieval Efficiency:")
        for num_items in [50, 100]:
            ops, elapsed = self.measure_retrieval(num_items, 1000)
            results["measurements"].append({
                "operation": "retrieval",
                "items": num_items,
                "queries": 1000,
                "ops_per_sec": float(ops),
                "time_sec": float(elapsed)
            })
            print(f"  {num_items} items, 1000 queries: {ops:.0f} ops/sec")

        print()

        # Maintenance efficiency
        print("Maintenance Efficiency:")
        ops, elapsed = self.measure_maintenance(50, 1000)
        results["measurements"].append({
            "operation": "maintenance",
            "items": 50,
            "cycles": 1000,
            "cycles_per_sec": float(ops),
            "time_sec": float(elapsed)
        })
        print(f"  50 items, 1000 cycles: {ops:.0f} cycles/sec")

        return results

    def analyze(self, results):
        """Summarize efficiency."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        # Storage
        storage = [m for m in measurements if m["operation"] == "storage"]
        if storage:
            avg_ops = np.mean([m["ops_per_sec"] for m in storage])
            analysis["findings"].append(
                f"Storage: ~{avg_ops:.0f} ops/sec"
            )

        # Retrieval
        retrieval = [m for m in measurements if m["operation"] == "retrieval"]
        if retrieval:
            avg_ops = np.mean([m["ops_per_sec"] for m in retrieval])
            analysis["findings"].append(
                f"Retrieval: ~{avg_ops:.0f} ops/sec"
            )

        # Maintenance
        maintenance = [m for m in measurements if m["operation"] == "maintenance"]
        if maintenance:
            cycles = maintenance[0]["cycles_per_sec"]
            analysis["findings"].append(
                f"Maintenance: ~{cycles:.0f} cycles/sec"
            )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2117: Efficiency Measurement")
    print("=" * 60)
    print()

    exp = EfficiencyMeasurement()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2117_efficiency.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
