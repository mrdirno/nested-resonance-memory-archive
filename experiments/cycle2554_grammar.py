
import sys
import os
import csv
import time
import random
import math
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Linguist:
    def __init__(self, name, lexicon):
        self.name = name
        self.lexicon = lexicon # Shared Lexicon (from C2553)
        
    def speak_sentence(self, concepts):
        # Return a composite waveform
        def signal(t):
            val = 0
            for c in concepts:
                f = self.lexicon[c]
                val += math.sin(f * t) # Phase 0
            return val
        return signal
        
    def hear_sentence(self, waveform_func, duration=100.0, rate=100):
        # Sample
        N = int(duration * rate)
        dt = 1.0 / rate
        samples = [waveform_func(i * dt) for i in range(N)]
        
        # FFT
        fft_result = np.fft.fft(samples)
        freqs = np.fft.fftfreq(N, dt)
        # Map to Angular Freq (if lexicon is angular) 
        # Or Hertz. Let's assume lexicon is Angular Freq (omega) for sin(wt)
        # freq_hz = freqs
        # omega = 2 * pi * freq_hz
        omegas = freqs * 2 * math.pi
        
        magnitudes = np.abs(fft_result) / (N/2)
        
        detected = []
        threshold = 0.5 # Amplitude threshold
        
        # Scan for peaks matching lexicon
        for concept, target_omega in self.lexicon.items():
            # Find closest bin
            idx = np.argmin(np.abs(omegas - target_omega))
            mag = magnitudes[idx]
            if mag > threshold:
                detected.append(concept)
                
        return detected

def run_grammar_experiment():
    print("📜 CYCLE 2554: THE GRAMMAR - COMPOSITIONALITY")
    print("   (Superposition of Concepts)")
    
    # 1. Shared Lexicon (Result of C2553)
    lexicon = {
        'FOOD': 1.0,   # Omega
        'DANGER': 3.0,
        'HOME': 5.0,
        'SELF': 7.0
    }
    
    agent_a = Linguist("Alice", lexicon)
    agent_b = Linguist("Bob", lexicon)
    
    test_sentences = [
        ['FOOD', 'DANGER'],      # Poison?
        ['SELF', 'HOME'],        # I am home?
        ['FOOD', 'HOME', 'SELF'] # I eat at home?
    ]
    
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2554_grammar.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["sentence", "detected", "success"])
        
        for sent in test_sentences:
            print(f"🗣️  Speaking: {sent}")
            wave = agent_a.speak_sentence(sent)
            
            heard = agent_b.hear_sentence(wave)
            print(f"👂 Hearing: {heard}")
            
            # Check set equality
            success = set(sent) == set(heard)
            writer.writerow([str(sent), str(heard), success])
            
            if success:
                print("   ✅ UNDERSTOOD.")
            else:
                print("   ❌ MISUNDERSTOOD.")

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_grammar_experiment()
