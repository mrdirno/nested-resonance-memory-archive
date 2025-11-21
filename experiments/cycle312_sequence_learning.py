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
            # This breaks symmetry: A * P(B) != B * P(A)
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
        
        # Debug: Check margin
        # sorted_sims = sorted([(np.dot(noisy_norm, v), k) for k, v in vocabulary.items() if k not in exclude_keys], reverse=True)
        # if sorted_sims and sorted_sims[0][1] != best_match[0]:
        #     print(f"CRITICAL ERROR: Sort mismatch")
        # if sorted_sims and len(sorted_sims) > 1:
        #    print(f"  Cleanup: Best={best_match[0]} ({max_sim:.4f}), 2nd={sorted_sims[1][1]} ({sorted_sims[1][0]:.4f})")
        
        return best_match, max_sim

class SequenceLearningExperiment:
    def __init__(self):
        self.mem = HolographicSequenceMemory(dimension=2048)
        self.num_trials = 20
        self.sequence_length = 5 # A -> B -> C -> D -> E
        self.results = {
            "cleanup_accuracy": 0.0,
            "no_cleanup_accuracy": 0.0,
            "avg_sim_cleanup": [],
            "avg_sim_no_cleanup": []
        }

    def run(self):
        print("Cycle 312: Sequence Learning Experiment")
        print("---------------------------------------")
        
        cleanup_success_count = 0
        no_cleanup_success_count = 0
        
        # Track similarity at each step (averaged over trials)
        sim_cleanup_steps = [0.0] * (self.sequence_length - 1)
        sim_no_cleanup_steps = [0.0] * (self.sequence_length - 1)
        
        for t in range(self.num_trials):
            # 1. Define Sequence Items
            items = []
            vocab = {}
            names = ["A", "B", "C", "D", "E", "F", "G"] # Extra items for distraction
            
            for name in names:
                vec = self.mem.generate_vector()
                vocab[name] = vec
                if len(items) < self.sequence_length:
                    items.append(vec)
            
            # 2. Encode Sequence
            trace = self.mem.encode_sequence(items)
            
            # 3. Test with Cleanup
            current = items[0]
            trial_cleanup_success = True
            
            # Track path for inhibition
            path = [names[0]] # Start with A
            
            for i in range(self.sequence_length - 1):
                # Predict
                next_noisy = self.mem.step(trace, current)
                
                # Determine exclusion list
                # We want to exclude the predecessor (where we came from) to prevent backtracking
                # Path[-1] is current (B). Path[-2] is predecessor (A).
                exclude = []
                if len(path) >= 2:
                    exclude.append(path[-2])
                # Also exclude current to be safe?
                exclude.append(path[-1])
                
                # Cleanup with Inhibition of Predecessor
                (match_name, match_vec), sim = self.mem.cleanup(next_noisy, vocab, exclude_keys=exclude)
                
                # Debug print for first trial
                if t == 0:
                    print(f"    Step {i+1}: Target={names[i+1]}, Match={match_name} (Sim={sim:.4f})")
                
                # Record Sim
                sim_cleanup_steps[i] += sim
                
                # Check correctness
                target_name = names[i+1]
                if match_name != target_name:
                    trial_cleanup_success = False
                
                # Update current for next step
                current = match_vec
                path.append(match_name)
            
            if trial_cleanup_success:
                cleanup_success_count += 1
                
            # 4. Test without Cleanup
            current = items[0]
            trial_no_cleanup_success = True
            
            for i in range(self.sequence_length - 1):
                # Predict
                next_noisy = self.mem.step(trace, current)
                
                # Check similarity to target (without snapping)
                target_vec = items[i+1]
                sim = np.dot(self.mem._normalize(next_noisy), target_vec)
                
                # Record Sim
                sim_no_cleanup_steps[i] += sim
                
                # Check if it's still the best match (conceptually)
                (match_name, _), _ = self.mem.cleanup(next_noisy, vocab)
                target_name = names[i+1]
                if match_name != target_name:
                    trial_no_cleanup_success = False
                
                # Update current for next step (use NOISY vector)
                current = next_noisy
                
            if trial_no_cleanup_success:
                no_cleanup_success_count += 1

        # Average results
        self.results["cleanup_accuracy"] = cleanup_success_count / self.num_trials
        self.results["no_cleanup_accuracy"] = no_cleanup_success_count / self.num_trials
        self.results["avg_sim_cleanup"] = [s / self.num_trials for s in sim_cleanup_steps]
        self.results["avg_sim_no_cleanup"] = [s / self.num_trials for s in sim_no_cleanup_steps]
        
        print("\nResults Summary:")
        print(f"Cleanup Traversal Accuracy:    {self.results['cleanup_accuracy']*100:.1f}%")
        print(f"No-Cleanup Traversal Accuracy: {self.results['no_cleanup_accuracy']*100:.1f}%")
        
        print("\nStep-by-Step Similarity (Cleanup vs No-Cleanup):")
        for i in range(self.sequence_length - 1):
            print(f"  Step {i+1} ({names[i]}->{names[i+1]}): Cleanup={self.results['avg_sim_cleanup'][i]:.4f} | No-Cleanup={self.results['avg_sim_no_cleanup'][i]:.4f}")
            
        return self.results

if __name__ == "__main__":
    exp = SequenceLearningExperiment()
    results = exp.run()
