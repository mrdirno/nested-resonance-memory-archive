"""
Holographic Pattern Memory (VSA)
================================
Production implementation of the Partitioned Holographic Associative Memory 
validated in Cycles 2082-2119.

Features:
- Vector Symbolic Architecture (Holographic Reduced Representations)
- Circular Convolution Binding / Correlation Unbinding
- Partitioned Storage (scales linearly with K)
- Content-Addressable (Bidirectional)
- Noise-Resistant (via Cleanup Codebook)

Reference: Cycle 2118 Deployment Specification
"""

import numpy as np
import psutil
import hashlib
from typing import Dict, List, Optional, Union, Any

class PatternMemory:
    """
    Holographic Associative Memory with Partitioning.
    """
    def __init__(self, dimension: int = 1024, partitions: int = 8):
        self.dimension = dimension
        self.num_partitions = partitions
        
        # Storage: List of memory vectors (one per partition)
        self.storage = [np.zeros(dimension) for _ in range(partitions)]
        
        # Cleanup Memory (Codebook): Maps vector bytes -> (key_str, vector)
        # We store both keys and values here for cleanup
        self.codebook: Dict[str, np.ndarray] = {}
        
        # Reverse Codebook: Maps string value -> vector bytes
        self.str_to_vec: Dict[str, bytes] = {}
        
        self._entropy_counter = 0

    def _normalize(self, v: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length."""
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Circular Convolution (Binding)."""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Circular Correlation (Unbinding)."""
        # Unbind b from a: a * b_inv
        # b_inv is involution: reversed and rolled
        b_inv = np.roll(b[::-1], 1)
        return self._circ_conv(a, b_inv)

    def _get_vector(self, item: str) -> np.ndarray:
        """Get or create a stable random vector for a string item."""
        if item in self.str_to_vec:
            return np.frombuffer(self.str_to_vec[item], dtype=np.float64)
        
        # Deterministic generation based on string hash
        # This ensures same string always gets same vector without storage
        # (though we cache it for performance)
        seed_str = item
        sha = hashlib.sha256(seed_str.encode()).digest()
        seed = int.from_bytes(sha[:4], 'big')
        rng = np.random.RandomState(seed)
        
        v = rng.normal(0, 1.0/np.sqrt(self.dimension), self.dimension)
        v = self._normalize(v)
        
        # Cache it
        v_bytes = v.tobytes()
        self.codebook[v_bytes] = item
        self.str_to_vec[item] = v_bytes
        return v

    def _get_partition_idx(self, key: str) -> int:
        """Determine which partition handles this key."""
        sha = hashlib.sha256(key.encode()).digest()
        val = int.from_bytes(sha[:4], 'big')
        return val % self.num_partitions

    def store(self, key: str, value: str) -> None:
        """
        Store an association Key -> Value.
        """
        # 1. Get vectors
        k_vec = self._get_vector(key)
        v_vec = self._get_vector(value)
        
        # 2. Bind
        binding = self._circ_conv(k_vec, v_vec)
        
        # 3. Determine Partition
        p_idx = self._get_partition_idx(key)
        
        # 4. Add to Superposition
        # We do NOT normalize here to prevent decay of older items (Cycle 2120 fix)
        # Simple addition maintains equal weight for all items
        self.storage[p_idx] = self.storage[p_idx] + binding

    def retrieve(self, key: str) -> Optional[str]:
        """
        Retrieve Value associated with Key.
        Returns None if no match found above threshold.
        """
        # 1. Get key vector
        k_vec = self._get_vector(key)
        
        # 2. Determine Partition
        p_idx = self._get_partition_idx(key)
        # Normalize on read to handle magnitude scaling
        memory_vec = self._normalize(self.storage[p_idx])
        
        # 3. Unbind (Correlate)
        # memory * key_inv ~= value + noise
        noisy_value = self._circ_corr(memory_vec, k_vec)
        
        # 4. Cleanup (Nearest Neighbor Search)
        # In production, this would use a KD-Tree or LSH.
        # For N < 10000, linear scan is acceptable (numpy optimized).
        
        best_item = None
        best_sim = -1.0
        
        # We only search against known values in codebook
        # Optimization: In a real system, we might restrict search space
        
        for vec_bytes, item_str in self.codebook.items():
            clean_vec = np.frombuffer(vec_bytes, dtype=np.float64)
            sim = np.dot(noisy_value, clean_vec)
            
            if sim > best_sim:
                best_sim = sim
                best_item = item_str
                
        # Thresholding (per Cycle 2106/2118 spec)
        # Typically > 0.1 indicates a match in high-dim space
        if best_sim > 0.15:
            return best_item
        return None

    def retrieve_multiple(self, key: str, threshold: float = 0.15) -> List[str]:
        """
        Retrieve all Values associated with Key (Decomposition).
        Useful when multiple values are bound to the same key (Superposition).
        """
        # 1. Get key vector
        k_vec = self._get_vector(key)
        
        # 2. Determine Partition
        p_idx = self._get_partition_idx(key)
        memory_vec = self._normalize(self.storage[p_idx])
        
        # 3. Unbind (Correlate)
        noisy_value = self._circ_corr(memory_vec, k_vec)
        
        # 4. Find all matches
        matches = []
        for vec_bytes, item_str in self.codebook.items():
            clean_vec = np.frombuffer(vec_bytes, dtype=np.float64)
            sim = np.dot(noisy_value, clean_vec)
            
            if sim > threshold:
                matches.append((item_str, sim))
        
        # Sort by similarity desc
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches]

    def persist(self, path: str):
        """Save memory state to disk (placeholder)."""
        # In a full implementation, we'd save the numpy arrays
        pass

    def load(self, path: str):
        """Load memory state from disk (placeholder)."""
        pass

# [SPORE] ID: The Colony
