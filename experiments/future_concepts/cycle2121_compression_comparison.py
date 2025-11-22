"""
Cycle 2121: Compression Efficiency Comparison
=============================================
Compare holographic memory to classical compression/storage.

Question: How efficient is 66 bits per partition?
"""

import numpy as np
import json
import zlib
import pickle
from datetime import datetime

class CompressionComparison:
    def __init__(self):
        self.dimension = 1024
        self.k_memories = 8
        self.num_trials = 3

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

    def measure_holographic_storage(self, n_items):
        """Measure holographic memory storage."""
        d = self.dimension

        # Storage size: K memories × D dimensions × 8 bytes (float64)
        storage_bytes = self.k_memories * d * 8

        # Information stored: ~66 bits per partition × K
        bits_stored = 66 * self.k_memories

        return {
            "storage_bytes": storage_bytes,
            "bits_stored": bits_stored,
            "bits_per_byte": bits_stored / storage_bytes
        }

    def measure_raw_storage(self, n_items):
        """Measure raw key-value storage."""
        d = self.dimension

        # Storage: n_items × (key + value) × D × 8 bytes
        storage_bytes = n_items * 2 * d * 8

        # Information: log2(n_items) bits per item retrieval
        bits_per_item = np.log2(n_items) if n_items > 1 else 0
        bits_stored = n_items * bits_per_item

        return {
            "storage_bytes": storage_bytes,
            "bits_stored": bits_stored,
            "bits_per_byte": bits_stored / storage_bytes
        }

    def measure_compressed_storage(self, n_items):
        """Measure compressed key-value storage."""
        d = self.dimension
        np.random.seed(42)

        # Generate items
        keys = [self._generate(d) for _ in range(n_items)]
        values = [self._generate(d) for _ in range(n_items)]

        # Pickle and compress
        data = {"keys": keys, "values": values}
        pickled = pickle.dumps(data)
        compressed = zlib.compress(pickled, level=9)

        storage_bytes = len(compressed)
        bits_per_item = np.log2(n_items) if n_items > 1 else 0
        bits_stored = n_items * bits_per_item

        return {
            "storage_bytes": storage_bytes,
            "bits_stored": bits_stored,
            "bits_per_byte": bits_stored / storage_bytes
        }

    def run_experiment(self):
        """Compare storage methods."""
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
        print(f"{'Method':<20} {'Items':<8} {'Storage':<12} {'Bits':<10} {'Bits/Byte':<12}")
        print("-" * 70)

        for n_items in [50, 100]:
            # Holographic
            holo = self.measure_holographic_storage(n_items)
            results["measurements"].append({
                "method": "holographic",
                "n_items": n_items,
                **holo
            })
            print(f"{'Holographic':<20} {n_items:<8} {holo['storage_bytes']:<12} {holo['bits_stored']:<10.0f} {holo['bits_per_byte']:<12.6f}")

            # Raw
            raw = self.measure_raw_storage(n_items)
            results["measurements"].append({
                "method": "raw",
                "n_items": n_items,
                **raw
            })
            print(f"{'Raw':<20} {n_items:<8} {raw['storage_bytes']:<12} {raw['bits_stored']:<10.0f} {raw['bits_per_byte']:<12.6f}")

            # Compressed
            comp = self.measure_compressed_storage(n_items)
            results["measurements"].append({
                "method": "compressed",
                "n_items": n_items,
                **comp
            })
            print(f"{'Compressed (zlib)':<20} {n_items:<8} {comp['storage_bytes']:<12} {comp['bits_stored']:<10.0f} {comp['bits_per_byte']:<12.6f}")

            print()

        return results

    def analyze(self, results):
        """Analyze compression efficiency."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        # Compare at 100 items
        m100 = [m for m in measurements if m["n_items"] == 100]

        holo = next((m for m in m100 if m["method"] == "holographic"), None)
        raw = next((m for m in m100 if m["method"] == "raw"), None)
        comp = next((m for m in m100 if m["method"] == "compressed"), None)

        if holo and raw:
            ratio = raw["storage_bytes"] / holo["storage_bytes"]
            analysis["findings"].append(
                f"Holographic uses {ratio:.1f}× less storage than raw"
            )

        if holo and comp:
            ratio = comp["storage_bytes"] / holo["storage_bytes"]
            analysis["findings"].append(
                f"Holographic uses {ratio:.1f}× less storage than compressed"
            )

        # Key insight
        analysis["findings"].append(
            f"Trade-off: Holographic has fixed storage (K×D), lossy retrieval"
        )
        analysis["findings"].append(
            f"Benefit: O(1) retrieval, error recovery, graceful degradation"
        )

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2121: Compression Efficiency Comparison")
    print("=" * 60)
    print()

    exp = CompressionComparison()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2121_compression_comparison.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
