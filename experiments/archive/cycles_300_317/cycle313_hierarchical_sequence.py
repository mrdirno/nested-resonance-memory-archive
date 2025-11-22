import numpy as np
import sys
import os

class HolographicSequenceMemory:
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
        """Circular Correlation (Unbinding: a * b^-1)"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def _permute(self, v):
        """Rotate vector by 1 (Permutation)"""
        return np.roll(v, 1)

    def _inv_permute(self, v):
        """Rotate vector by -1 (Inverse Permutation)"""
        return np.roll(v, -1)

    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)
    
    def encode_sequence(self, sequence_items):
        """
        Sequence = (A * P(B)) + (B * P(C)) + ...
        """
        trace = np.zeros(self.d)
        for i in range(len(sequence_items) - 1):
            # Bind Current * Permute(Next)
            pair = self._circ_conv(sequence_items[i], self._permute(sequence_items[i+1]))
            trace += pair
        return trace

    def step(self, trace, current_state):
        """
        Next_Noisy = InvPermute(Trace * Current^-1)
        """
        # Unbind current: Trace * Current^-1 -> P(Next) + Noise
        permuted_next = self._circ_corr(trace, current_state)
        # Inverse permute to get Next
        return self._inv_permute(permuted_next)

    def cleanup(self, noisy_vector, vocabulary, exclude_keys=None):
        """
        Find nearest neighbor in vocabulary.
        exclude_keys: list of keys to ignore (Inhibition of Return)
        """
        if exclude_keys is None:
            exclude_keys = []
            
        best_match = None
        max_sim = -1.0
        
        # Normalize noisy vector for comparison
        noisy_norm = self._normalize(noisy_vector)
        
        for name, vec in vocabulary.items():
            if name in exclude_keys:
                continue
                
            sim = np.dot(noisy_norm, vec)
            if sim > max_sim:
                max_sim = sim
                best_match = (name, vec)
        
        return best_match, max_sim

class HierarchicalSequenceExperiment:
    def __init__(self):
        self.mem = HolographicSequenceMemory(dimension=2048)
        self.num_trials = 20
        self.results = {
            "subseq1_accuracy": 0.0,
            "meta_accuracy": 0.0,
            "subseq2_accuracy": 0.0,
            "total_accuracy": 0.0
        }

    def run(self):
        print("Cycle 313: Hierarchical Sequence Experiment")
        print("-------------------------------------------")
        
        success_count = 0
        
        for t in range(self.num_trials):
            # 1. Define Concepts
            # Sub-sequence 1: A -> B -> C
            A = self.mem.generate_vector()
            B = self.mem.generate_vector()
            C = self.mem.generate_vector()
            vocab1 = {"A": A, "B": B, "C": C}
            
            # Sub-sequence 2: D -> E -> F
            D = self.mem.generate_vector()
            E = self.mem.generate_vector()
            F = self.mem.generate_vector()
            vocab2 = {"D": D, "E": E, "F": F}
            
            # 2. Encode Sub-Sequences (Chunks)
            trace1 = self.mem.encode_sequence([A, B, C])
            chunk1 = self.mem._normalize(trace1) # Chunk 1 represents the sequence A->B->C
            
            trace2 = self.mem.encode_sequence([D, E, F])
            chunk2 = self.mem._normalize(trace2) # Chunk 2 represents the sequence D->E->F
            
            # 3. Encode Meta-Sequence: Chunk1 -> Chunk2
            # We treat chunks as atomic items in the meta-sequence
            meta_trace = self.mem.encode_sequence([chunk1, chunk2])
            
            # Meta-Vocabulary
            meta_vocab = {"Chunk1": chunk1, "Chunk2": chunk2}
            
            # 4. Execution Simulation
            trial_success = True
            
            # --- Phase 1: Execute Chunk 1 (A -> B -> C) ---
            # Context: trace1. Start: A.
            current = A
            path1 = ["A"]
            
            # Step 1: A -> B
            next_noisy = self.mem.step(trace1, current)
            (match_name, match_vec), sim = self.mem.cleanup(next_noisy, vocab1, exclude_keys=["A"])
            if match_name != "B": trial_success = False
            current = match_vec
            path1.append(match_name)
            
            # Step 2: B -> C
            next_noisy = self.mem.step(trace1, current)
            (match_name, match_vec), sim = self.mem.cleanup(next_noisy, vocab1, exclude_keys=["B", "A"])
            if match_name != "C": trial_success = False
            current = match_vec
            path1.append(match_name)
            
            if t == 0: print(f"  Phase 1 Path: {path1}")

            # --- Phase 2: Meta-Transition (Chunk1 -> Chunk2) ---
            # Context: meta_trace. Start: chunk1.
            # Note: In a real agent, "End of Sequence" (C) would trigger the meta-step.
            # Here we manually trigger it.
            
            meta_next_noisy = self.mem.step(meta_trace, chunk1)
            (meta_match_name, meta_match_vec), meta_sim = self.mem.cleanup(meta_next_noisy, meta_vocab, exclude_keys=["Chunk1"])
            
            if meta_match_name != "Chunk2": 
                trial_success = False
                if t == 0: print(f"  Meta-Transition Failed: Got {meta_match_name}")
            else:
                if t == 0: print(f"  Meta-Transition: Chunk1 -> {meta_match_name} (Sim={meta_sim:.4f})")
            
            # --- Phase 3: Execute Chunk 2 (D -> E -> F) ---
            # Context: trace2 (which is the content of Chunk2, but un-normalized. 
            # Ideally, we should be able to use Chunk2 itself if we didn't normalize it, 
            # or if normalization doesn't destroy the info. 
            # Let's try using trace2 (the raw memory) first. 
            # In a real brain, Chunk2 *is* the pointer to trace2, or trace2 itself.
            # For this test, we assume we retrieved the trace associated with Chunk2.
            
            current = D
            path2 = ["D"]
            
            # Step 1: D -> E
            next_noisy = self.mem.step(trace2, current)
            (match_name, match_vec), sim = self.mem.cleanup(next_noisy, vocab2, exclude_keys=["D"])
            if match_name != "E": trial_success = False
            current = match_vec
            path2.append(match_name)
            
            # Step 2: E -> F
            next_noisy = self.mem.step(trace2, current)
            (match_name, match_vec), sim = self.mem.cleanup(next_noisy, vocab2, exclude_keys=["E", "D"])
            if match_name != "F": trial_success = False
            current = match_vec
            path2.append(match_name)
            
            if t == 0: print(f"  Phase 3 Path: {path2}")
            
            if trial_success:
                success_count += 1

        accuracy = success_count / self.num_trials
        print(f"\nTotal Hierarchical Accuracy: {accuracy*100:.1f}%")
        return accuracy

if __name__ == "__main__":
    exp = HierarchicalSequenceExperiment()
    exp.run()
