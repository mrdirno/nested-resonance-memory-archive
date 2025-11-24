"""
Cycle 2129: Symbolic Reasoning Test
===================================
Can holographic memory support symbolic AI operations?

Test simple logical relationships and inference.
"""

import numpy as np
import json
from datetime import datetime

class SymbolicReasoning:
    def __init__(self):
        self.dimension = 1024
        self.k_memories = 8
        self.num_cycles = 200

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

    def test_transitivity(self, seed):
        """Test: If A→B and B→C, can we infer A→C?"""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        # Create symbols
        symbols = {name: self._generate(d) for name in ['A', 'B', 'C', 'D', 'E']}
        relation = self._generate(d)  # "relates_to" relation

        # Store relationships: A→B, B→C, C→D, D→E
        pairs = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E')]
        codebook = list(symbols.values())

        for src, dst in pairs:
            # Encode: relation(A) = B
            key = self._circ_conv(relation, symbols[src])
            value = symbols[dst]
            mem_idx = self._hash_key(key, self.k_memories)

            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

        # Maintenance
        for cycle in range(self.num_cycles):
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue
                noise = np.random.normal(0, 0.005, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)
                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.3 * binding)

        # Test direct retrieval
        direct_correct = 0
        for src, dst in pairs:
            key = self._circ_conv(relation, symbols[src])
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, symbols[dst]) > 0.5:
                direct_correct += 1

        # Test transitive inference: A→C (via B)
        # First get B from A
        key_a = self._circ_conv(relation, symbols['A'])
        mem_idx = self._hash_key(key_a, self.k_memories)
        key_inv = np.roll(key_a[::-1], 1)
        b_retrieved = self._circ_conv(memories[mem_idx], key_inv)
        b_retrieved = self._cleanup(b_retrieved, codebook)

        # Then get C from B
        key_b = self._circ_conv(relation, b_retrieved)
        mem_idx = self._hash_key(key_b, self.k_memories)
        key_inv = np.roll(key_b[::-1], 1)
        c_retrieved = self._circ_conv(memories[mem_idx], key_inv)
        c_retrieved = self._cleanup(c_retrieved, codebook)

        trans_correct = np.dot(c_retrieved, symbols['C']) > 0.5

        return direct_correct / len(pairs), int(trans_correct)

    def test_negation(self, seed):
        """Test: Can we encode and retrieve negations?"""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        # Create symbols
        symbols = {name: self._generate(d) for name in ['true', 'false', 'P', 'Q']}
        not_rel = self._generate(d)  # "NOT" relation

        # Store: NOT(true) = false, NOT(false) = true
        pairs = [('true', 'false'), ('false', 'true')]
        codebook = list(symbols.values())

        for src, dst in pairs:
            key = self._circ_conv(not_rel, symbols[src])
            value = symbols[dst]
            mem_idx = self._hash_key(key, self.k_memories)
            binding = self._circ_conv(key, value)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, value))

        # Maintenance
        for cycle in range(self.num_cycles):
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue
                noise = np.random.normal(0, 0.005, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)
                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.3 * binding)

        # Test
        correct = 0
        for src, dst in pairs:
            key = self._circ_conv(not_rel, symbols[src])
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, symbols[dst]) > 0.5:
                correct += 1

        return correct / len(pairs)

    def test_conjunction(self, seed):
        """Test: Can we encode AND(A, B) = C?"""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        # Create symbols
        symbols = {name: self._generate(d) for name in ['A', 'B', 'C', 'D']}

        # AND operation: combine two inputs
        # Encode: A*B → C (composition as conjunction)
        key = self._circ_conv(symbols['A'], symbols['B'])
        value = symbols['C']
        codebook = list(symbols.values())

        mem_idx = self._hash_key(key, self.k_memories)
        binding = self._circ_conv(key, value)
        memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
        memory_items[mem_idx].append((key, value))

        # Maintenance
        for cycle in range(self.num_cycles):
            for mem_idx in range(self.k_memories):
                if not memory_items[mem_idx]:
                    continue
                noise = np.random.normal(0, 0.005, d)
                memories[mem_idx] = self._normalize(memories[mem_idx] + noise)
                item_idx = cycle % len(memory_items[mem_idx])
                key, value = memory_items[mem_idx][item_idx]
                binding = self._circ_conv(key, value)
                memories[mem_idx] = self._normalize(memories[mem_idx] + 0.3 * binding)

        # Test
        key = self._circ_conv(symbols['A'], symbols['B'])
        mem_idx = self._hash_key(key, self.k_memories)
        key_inv = np.roll(key[::-1], 1)
        retrieved = self._circ_conv(memories[mem_idx], key_inv)
        retrieved = self._cleanup(retrieved, codebook)

        return int(np.dot(retrieved, symbols['C']) > 0.5)

    def run_experiment(self):
        """Test symbolic reasoning capabilities."""
        results = {
            "metadata": {
                "dimension": self.dimension,
                "k_memories": self.k_memories,
                "num_cycles": self.num_cycles,
                "timestamp": datetime.now().isoformat()
            },
            "measurements": []
        }

        print(f"D={self.dimension}, K={self.k_memories}")
        print()
        print(f"{'Test':<20} {'Result':<15}")
        print("-" * 40)

        # Transitivity
        trans_direct = []
        trans_infer = []
        for seed in range(3):
            direct, infer = self.test_transitivity(seed*100)
            trans_direct.append(direct)
            trans_infer.append(infer)

        results["measurements"].append({
            "test": "transitivity_direct",
            "accuracy": float(np.mean(trans_direct))
        })
        results["measurements"].append({
            "test": "transitivity_infer",
            "accuracy": float(np.mean(trans_infer))
        })
        print(f"{'Transitivity (direct)':<20} {np.mean(trans_direct)*100:>5.0f}%")
        print(f"{'Transitivity (infer)':<20} {np.mean(trans_infer)*100:>5.0f}%")

        # Negation
        neg_results = [self.test_negation(seed*100) for seed in range(3)]
        results["measurements"].append({
            "test": "negation",
            "accuracy": float(np.mean(neg_results))
        })
        print(f"{'Negation':<20} {np.mean(neg_results)*100:>5.0f}%")

        # Conjunction
        conj_results = [self.test_conjunction(seed*100) for seed in range(3)]
        results["measurements"].append({
            "test": "conjunction",
            "accuracy": float(np.mean(conj_results))
        })
        print(f"{'Conjunction (AND)':<20} {np.mean(conj_results)*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Analyze symbolic reasoning capabilities."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        for m in measurements:
            if m["accuracy"] >= 0.9:
                analysis["findings"].append(f"{m['test']}: WORKS ({m['accuracy']*100:.0f}%)")
            elif m["accuracy"] >= 0.5:
                analysis["findings"].append(f"{m['test']}: PARTIAL ({m['accuracy']*100:.0f}%)")
            else:
                analysis["findings"].append(f"{m['test']}: FAILS ({m['accuracy']*100:.0f}%)")

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2129: Symbolic Reasoning Test")
    print("=" * 60)
    print()

    exp = SymbolicReasoning()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2129_symbolic_reasoning.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
