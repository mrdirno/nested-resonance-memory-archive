import numpy as np
import sys
import os

class HolographicChunkingMemory:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.memory_trace = np.zeros(self.d)
        
    def _normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0: return v
        return v / norm

    def _circ_conv(self, a, b):
        """Circular Convolution (Binding)"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))
    
    def _circ_corr(self, a, b):
        """Circular Correlation (Unbinding)"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))
    
    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return v 
    
    def store_pair(self, key, value):
        """Store K -> V as K * V"""
        term = self._circ_conv(key, value)
        self.memory_trace += term
        
    def retrieve(self, key):
        """Retrieve V given K"""
        return self._circ_corr(self.memory_trace, key)

    def encode_sequence(self, items, positions):
        """
        Encode sequence S = P1*A + P2*B + ...
        """
        S = np.zeros(self.d)
        for i, item in enumerate(items):
            if i < len(positions):
                term = self._circ_conv(positions[i], item)
                S += term
        return S

    def decode_sequence(self, sequence_vector, positions, possible_items):
        """
        Decode items from sequence vector.
        """
        decoded_items = []
        for p in positions:
            # Unbind position: S # P -> Item + Noise
            noisy_item = self._circ_corr(sequence_vector, p)
            
            # Cleanup
            best_match = None
            max_sim = -1.0
            noisy_norm = self._normalize(noisy_item)
            
            for item in possible_items:
                sim = np.dot(noisy_norm, self._normalize(item))
                if sim > max_sim:
                    max_sim = sim
                    best_match = item
            
            decoded_items.append((best_match, max_sim))
        return decoded_items

class ChunkingExperiment:
    def __init__(self):
        self.mem = HolographicChunkingMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "avg_decoding_accuracy": 0.0,
            "avg_item_similarity": 0.0
        }

    def run(self):
        print("Cycle 303: Hierarchical Chunking Experiment")
        print("-------------------------------------------")
        
        total_items = 0
        correct_items = 0
        total_similarity = 0.0
        
        # Define Position Vectors (Global)
        P1 = self.mem.generate_vector()
        P2 = self.mem.generate_vector()
        P3 = self.mem.generate_vector()
        positions = [P1, P2, P3]
        
        for i in range(self.num_trials):
            # 1. Generate Items
            A = self.mem.generate_vector()
            B = self.mem.generate_vector()
            C = self.mem.generate_vector()
            items = [A, B, C]
            
            # Distractors for cleanup
            X = self.mem.generate_vector()
            Y = self.mem.generate_vector()
            possible_items = [A, B, C, X, Y]
            
            # 2. Encode Sequence S
            S = self.mem.encode_sequence(items, positions)
            
            # 3. Chunking: Store ChunkID -> S
            ChunkID = self.mem.generate_vector()
            self.mem.memory_trace = np.zeros(self.mem.d) # Reset memory for this trial
            self.mem.store_pair(ChunkID, S)
            
            # 4. Unchunking: Retrieve S from ChunkID
            # S_retrieved = Memory # ChunkID = (ChunkID * S) # ChunkID = S + Noise
            S_retrieved = self.mem.retrieve(ChunkID)
            
            # 5. Decoding: Retrieve items from S_retrieved
            decoded = self.mem.decode_sequence(S_retrieved, positions, possible_items)
            
            # 6. Verify
            print(f"Trial {i+1}:")
            for j, (dec_item, sim) in enumerate(decoded):
                total_items += 1
                total_similarity += sim
                
                is_correct = (dec_item is items[j])
                if is_correct:
                    correct_items += 1
                
                status = "OK" if is_correct else "FAIL"
                print(f"  Item {j+1}: Sim={sim:.4f} [{status}]")
                
        self.results["avg_decoding_accuracy"] = correct_items / total_items
        self.results["avg_item_similarity"] = total_similarity / total_items
        
        print("\nResults Summary:")
        print(f"Decoding Accuracy: {self.results['avg_decoding_accuracy']*100:.1f}%")
        print(f"Avg Item Similarity: {self.results['avg_item_similarity']:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = ChunkingExperiment()
    results = exp.run()
