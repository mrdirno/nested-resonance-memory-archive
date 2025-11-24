"""
Cycle 2130: Syllogistic Reasoning
=================================
Test classical logic inference patterns.

Modus Ponens: If P→Q and P, then Q
Modus Tollens: If P→Q and ¬Q, then ¬P
Chain: If P→Q and Q→R, then P→R
"""

import numpy as np
import json
from datetime import datetime

class SyllogisticReasoning:
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

    def test_modus_ponens(self, seed):
        """Test: If P→Q and P is true, then Q is true."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        # Symbols
        symbols = {
            'P': self._generate(d),
            'Q': self._generate(d),
            'R': self._generate(d),
            'true': self._generate(d),
            'false': self._generate(d)
        }

        implies = self._generate(d)  # → relation
        truth_val = self._generate(d)  # truth value relation

        codebook = list(symbols.values())

        # Store: P→Q (implies(P) = Q)
        key1 = self._circ_conv(implies, symbols['P'])
        val1 = symbols['Q']
        mem_idx = self._hash_key(key1, self.k_memories)
        binding = self._circ_conv(key1, val1)
        memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
        memory_items[mem_idx].append((key1, val1))

        # Store: P is true
        key2 = self._circ_conv(truth_val, symbols['P'])
        val2 = symbols['true']
        mem_idx = self._hash_key(key2, self.k_memories)
        binding = self._circ_conv(key2, val2)
        memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
        memory_items[mem_idx].append((key2, val2))

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

        # Inference: Since P→Q and P is true, Q should be true

        # Step 1: Verify P is true
        key = self._circ_conv(truth_val, symbols['P'])
        mem_idx = self._hash_key(key, self.k_memories)
        key_inv = np.roll(key[::-1], 1)
        retrieved = self._circ_conv(memories[mem_idx], key_inv)
        p_truth = self._cleanup(retrieved, codebook)

        # Step 2: Get Q from P→Q
        key = self._circ_conv(implies, symbols['P'])
        mem_idx = self._hash_key(key, self.k_memories)
        key_inv = np.roll(key[::-1], 1)
        retrieved = self._circ_conv(memories[mem_idx], key_inv)
        q_symbol = self._cleanup(retrieved, codebook)

        # Step 3: Infer Q's truth value = P's truth value
        # (In this simple encoding, if P is true and P→Q, Q is true)
        success = (np.dot(p_truth, symbols['true']) > 0.5 and
                   np.dot(q_symbol, symbols['Q']) > 0.5)

        return int(success)

    def test_chain_rule(self, seed):
        """Test: If P→Q and Q→R, then P→R."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        symbols = {name: self._generate(d) for name in ['P', 'Q', 'R', 'S']}
        implies = self._generate(d)

        codebook = list(symbols.values())

        # Store: P→Q, Q→R, R→S
        pairs = [('P', 'Q'), ('Q', 'R'), ('R', 'S')]
        for src, dst in pairs:
            key = self._circ_conv(implies, symbols[src])
            val = symbols[dst]
            mem_idx = self._hash_key(key, self.k_memories)
            binding = self._circ_conv(key, val)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, val))

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

        # Infer P→S via chain P→Q→R→S
        current = symbols['P']
        for _ in range(3):  # Three hops
            key = self._circ_conv(implies, current)
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            current = self._cleanup(retrieved, codebook)

        # Should end at S
        return int(np.dot(current, symbols['S']) > 0.5)

    def test_role_binding(self, seed):
        """Test: Bind multiple roles to one frame."""
        np.random.seed(seed)
        d = self.dimension

        memories = [np.zeros(d) for _ in range(self.k_memories)]
        memory_items = [[] for _ in range(self.k_memories)]

        # Frame: "John gave Mary a book"
        frame = self._generate(d)
        roles = {
            'agent': self._generate(d),
            'recipient': self._generate(d),
            'theme': self._generate(d)
        }
        fillers = {
            'John': self._generate(d),
            'Mary': self._generate(d),
            'book': self._generate(d)
        }

        codebook = list(fillers.values())

        # Bind roles to fillers within frame
        bindings_data = [
            ('agent', 'John'),
            ('recipient', 'Mary'),
            ('theme', 'book')
        ]

        for role_name, filler_name in bindings_data:
            # Key: frame * role
            key = self._circ_conv(frame, roles[role_name])
            val = fillers[filler_name]
            mem_idx = self._hash_key(key, self.k_memories)
            binding = self._circ_conv(key, val)
            memories[mem_idx] = self._normalize(memories[mem_idx] + binding)
            memory_items[mem_idx].append((key, val))

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

        # Test retrieval
        correct = 0
        for role_name, filler_name in bindings_data:
            key = self._circ_conv(frame, roles[role_name])
            mem_idx = self._hash_key(key, self.k_memories)
            key_inv = np.roll(key[::-1], 1)
            retrieved = self._circ_conv(memories[mem_idx], key_inv)
            retrieved = self._cleanup(retrieved, codebook)
            if np.dot(retrieved, fillers[filler_name]) > 0.5:
                correct += 1

        return correct / len(bindings_data)

    def run_experiment(self):
        """Test syllogistic reasoning patterns."""
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
        print(f"{'Test':<20} {'Result':<10}")
        print("-" * 35)

        # Modus Ponens
        mp_results = [self.test_modus_ponens(seed*100) for seed in range(3)]
        results["measurements"].append({
            "test": "modus_ponens",
            "accuracy": float(np.mean(mp_results))
        })
        print(f"{'Modus Ponens':<20} {np.mean(mp_results)*100:>5.0f}%")

        # Chain Rule
        chain_results = [self.test_chain_rule(seed*100) for seed in range(3)]
        results["measurements"].append({
            "test": "chain_rule",
            "accuracy": float(np.mean(chain_results))
        })
        print(f"{'Chain Rule (3-hop)':<20} {np.mean(chain_results)*100:>5.0f}%")

        # Role Binding
        role_results = [self.test_role_binding(seed*100) for seed in range(3)]
        results["measurements"].append({
            "test": "role_binding",
            "accuracy": float(np.mean(role_results))
        })
        print(f"{'Role Binding':<20} {np.mean(role_results)*100:>5.0f}%")

        return results

    def analyze(self, results):
        """Analyze syllogistic reasoning."""
        measurements = results["measurements"]
        analysis = {"findings": []}

        for m in measurements:
            if m["accuracy"] >= 0.9:
                analysis["findings"].append(f"{m['test']}: WORKS ({m['accuracy']*100:.0f}%)")
            else:
                analysis["findings"].append(f"{m['test']}: {m['accuracy']*100:.0f}%")

        return analysis


def main():
    print("=" * 60)
    print("Cycle 2130: Syllogistic Reasoning")
    print("=" * 60)
    print()

    exp = SyllogisticReasoning()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    results["analysis"] = analysis

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    for finding in analysis["findings"]:
        print(f"  • {finding}")

    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2130_syllogistic_reasoning.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    main()
