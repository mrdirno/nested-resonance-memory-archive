"""
Cycle 2553: The Rosetta Stone (Gate 181)
Experiment: Linguistic Emergence.
Goal: Determine if agents develop a shared communication protocol beyond basic utility maps.
Hypothesis: If agents are given a flexible communication channel, they will evolve a compressed signaling grammar to coordinate more effectively.
"""

import sys
import os
import random
import json
import csv
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem
from src.life.signal import Signal

class Linguist(DigitalLifeform):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.vocabulary = {} # Map 'concept' to 'symbol'
        self.lexicon_size = 0
        
    def invent_word(self, concept):
        """Create a new random symbol for a concept."""
        symbol = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
        self.vocabulary[concept] = symbol
        self.lexicon_size += 1
        return symbol
        
    def speak(self, concept):
        """Broadcast a symbol representing a concept."""
        if concept not in self.vocabulary:
            self.invent_word(concept)
        
        symbol = self.vocabulary[concept]
        # print(f"🗣️ {self.name} says: '{symbol}' (meaning: {concept})")
        
        # Return Signal object (Corrected for list return type in act)
        return Signal(type='SPEECH', strength=1.0, source_id=self.id, payload={'symbol': symbol, 'concept': concept})

    def listen(self, signals):
        """Learn words from others."""
        for sig in signals:
            if sig.type == 'SPEECH':
                symbol = sig.payload['symbol']
                concept = sig.payload['concept'] # In reality, concept would be inferred. Here we cheat for ground truth.
                
                if concept not in self.vocabulary:
                    self.vocabulary[concept] = symbol
                    self.lexicon_size += 1
                    # print(f"👂 {self.name} learned '{symbol}' = {concept}")
                elif self.vocabulary[concept] != symbol:
                    # Synonym / Dialect conflict
                    # Simplest resolution: Overwrite (adopt latest)
                    self.vocabulary[concept] = symbol

    def act(self, bridge_state=None):
        """Override act to include speaking."""
        signals = super().act(bridge_state)
        if not isinstance(signals, list):
            signals = [signals] if signals else []
            
        # Randomly decide to speak about a concept
        concepts = ['FOOD', 'DANGER', 'HOME', 'SELF']
        if random.random() < 0.1:
            concept = random.choice(concepts)
            signals.append(self.speak(concept))
            
        return signals
        
    def sense(self, signals):
        """Override sense to listen."""
        super().sense(signals)
        self.listen(signals)


def run_rosetta_stone_experiment():
    print("🗣️ CYCLE 2553: THE ROSETTA STONE - LINGUISTIC EMERGENCE")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=20)
    
    # Seed Linguists
    print("📚 Seeding The Linguists...")
    for i in range(10):
        agent = Linguist(name=f"Speaker-{i}")
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2553_rosetta_stone.csv"
    
    env.running = True
    duration = 100
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "total_vocabulary_size", "unique_symbols_for_FOOD"])
        
        print("📝 Running simulation...")
        for tick in range(1, duration + 1):
            env.update()
            
            # Analyze Vocabulary
            total_vocab = sum(a.lexicon_size for a in env.agents if isinstance(a, Linguist))
            
            # Convergence Check: How many different words for "FOOD"?
            food_symbols = set()
            for a in env.agents:
                if isinstance(a, Linguist) and 'FOOD' in a.vocabulary:
                    food_symbols.add(a.vocabulary['FOOD'])
            
            writer.writerow([tick, total_vocab, len(food_symbols)])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Total Vocab={total_vocab}, Food Synonyms={len(food_symbols)}")
                if len(food_symbols) == 1:
                    print(f"   🏁 CONVERGENCE! The word for FOOD is '{list(food_symbols)[0]}'")
                    
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_rosetta_stone_experiment()