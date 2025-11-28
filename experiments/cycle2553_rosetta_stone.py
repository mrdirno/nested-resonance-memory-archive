
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

from src.life.genesis import DigitalLifeform

class Linguist(DigitalLifeform):
    def __init__(self, name):
        super().__init__(name=name)
        # Private Lexicon: Concept -> Frequency
        # Concepts: 'FOOD', 'DANGER', 'HOME'
        self.lexicon = {
            'FOOD': random.uniform(1.0, 10.0),
            'DANGER': random.uniform(1.0, 10.0),
            'HOME': random.uniform(1.0, 10.0)
        }
        # Confidence in each mapping (0.0 - 1.0)
        self.confidence = {k: 0.1 for k in self.lexicon}
        
    def speak(self, concept):
        # Return frequency
        return self.lexicon[concept]
        
    def hear(self, frequency):
        # Find closest concept in own lexicon
        best_concept = None
        min_dist = 1000.0
        for concept, f in self.lexicon.items():
            dist = abs(f - frequency)
            if dist < min_dist:
                min_dist = dist
                best_concept = concept
        return best_concept, min_dist
        
    def learn(self, concept, frequency, feedback):
        if feedback == 'SUCCESS':
            # Reinforce: Move closer to heard frequency
            # New = Old + alpha * (Target - Old)
            alpha = 0.5
            self.lexicon[concept] += alpha * (frequency - self.lexicon[concept])
            self.confidence[concept] = min(1.0, self.confidence[concept] + 0.1)
        else:
            # Weakly punish? Or just shift randomly?
            # Lateral Inhibition: Shift away slightly? 
            # Or just do nothing and let success drive convergence.
            self.confidence[concept] = max(0.0, self.confidence[concept] - 0.05)

def run_rosetta_experiment():
    print("🗣️ CYCLE 2553: THE ROSETTA STONE - FREQUENCY NEGOTIATION")
    print("   (Emergent Protocol Formation)")
    
    agents = [Linguist(f"Agent-{i}") for i in range(10)]
    concepts = ['FOOD', 'DANGER', 'HOME']
    
    duration = 500
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2553_rosetta_stone.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "avg_variance_food", "avg_variance_danger", "avg_variance_home", "success_rate"])
        
        history_success = []
        
        for tick in range(1, duration + 1):
            # Pair up
            speaker = random.choice(agents)
            listener = random.choice(agents)
            if speaker == listener: continue
            
            # Interaction
            topic = random.choice(concepts)
            signal = speaker.speak(topic)
            
            # Listener guesses
            guess, dist = listener.hear(signal)
            
            # Feedback Loop (The "Pointing" Mechanism)
            # In reality, context provides feedback (e.g., Speaker points at Food).
            # Here we assume they share context "This is Food", and check if signals match.
            # Actually, the Naming Game assumes: Speaker transmits Word. Listener retrieves Object. If Object matches Context, Success.
            
            # Simulation:
            # Speaker intends 'FOOD'. Sends Freq X.
            # Listener hears Freq X. Maps to 'DANGER' (closest).
            # Context reveals it was actually 'FOOD'.
            # Listener says "Oh, X means FOOD, not DANGER".
            
            success = (guess == topic)
            history_success.append(1 if success else 0)
            
            if success:
                # Both reinforce
                speaker.learn(topic, signal, 'SUCCESS')
                listener.learn(topic, signal, 'SUCCESS')
            else:
                # Mismatch. 
                # Listener adjusts 'topic' mapping towards 'signal'
                # Speaker adjusts 'topic' mapping towards 'signal'? No, speaker generated it.
                # In Naming Game: Listener adds word, or adjusts weight.
                
                # Simplified: Listener realizes "Signal X meant Topic Y".
                listener.learn(topic, signal, 'SUCCESS')
                
            # Metrics
            vars = []
            for c in concepts:
                freqs = [a.lexicon[c] for a in agents]
                vars.append(np.var(freqs))
                
            avg_success = sum(history_success[-50:]) / min(len(history_success), 50)
            
            writer.writerow([tick] + [f"{v:.4f}" for v in vars] + [f"{avg_success:.2f}"])
            
            if tick % 50 == 0:
                print(f"   Tick {tick}: Success={avg_success:.2f} Var(FOOD)={vars[0]:.2f}")
                
            if avg_success > 0.95 and max(vars) < 0.1:
                print("✨ PROTOCOL ESTABLISHED.")
                break

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_rosetta_experiment()
