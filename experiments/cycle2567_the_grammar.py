"""
Cycle 2567: The Grammar (Gate 195)
Goal: Agents combine symbols to form complex sentences.
Mechanism:
1. Initialize 2 Agents (Speaker/Listener).
2. Speaker sees 'FOOD' at (10, 10) (North-East of them).
3. Speaker invents/uses label for 'FOOD' and 'NORTH_EAST'.
4. Speaker broadcasts sequence ["FOOD_LABEL", "DIRECTION_LABEL"].
5. Listener parses sequence and updates knowledge.
"""

import time
import random
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform
from src.life.signal import Signal

def run_experiment():
    print("--- Cycle 2567: The Grammar ---")
    
    ecosystem = Ecosystem()
    
    # 1. Initialize Agents
    adam = DigitalLifeform(name="Adam") # Speaker
    eve = DigitalLifeform(name="Eve") # Listener
    
    for a in [adam, eve]:
        while len(a.genome) < 11: a.genome.append(0.5)
        a.genome[9] = 0.99 # Genius
        a.energy = 1000
        ecosystem.add_agent(a)
        
    # 2. Pre-load Vocabulary (Skip the Babble/Agreement phase for this test)
    # We assume they already agreed on basic terms to test Grammar.
    print("Pre-loading Vocabulary...")
    adam.brain.vocabulary = {
        'F1': {'FOOD': 1.0}, 
        'N1': {'NORTH': 1.0},
        'E1': {'EAST': 1.0}
    }
    eve.brain.vocabulary = {
        'F1': {'FOOD': 1.0}, 
        'N1': {'NORTH': 1.0},
        'E1': {'EAST': 1.0}
    }
    
    # 3. Simulate Sentence Generation
    # Adam wants to say "Food is North".
    # Currently `label_object` only emits one symbol.
    # We need a new intent `speak_sentence`.
    # But for this cycle, we can manually construct the signal to test the *parsing* logic in `Brain`.
    
    print("Simulating Sentence Broadcast...")
    sentence = ['F1', 'N1'] # "FOOD", "NORTH"
    
    # Eve receives the signal
    # We need a signal type that supports lists? Or just payload label is a list?
    # `process_social_signals` expects `sig.type == 'LABEL'` with `payload['label']` as string.
    # We need to update `process_social_signals` to handle `SEQUENCE`.
    
    # Since we haven't updated `process_social_signals` to handle SEQUENCES yet, we must do that first.
    # But the instructions said "Modify brain.py to parse sequences" which we did.
    # Now we need to wire it up in `genesis.py`.
    
    print("Updating Genesis to handle SEQUENCE signals (Pending Implementation).")
    
    # Test Brain Parsing Logic directly first
    print("[TEST] Testing Brain.parse_sequence...")
    parsed = eve.brain.parse_sequence(sentence)
    print(f"Sentence: {sentence}")
    print(f"Parsed: {parsed}")
    
    if parsed['target'] == 'FOOD' and parsed['direction'] == 'NORTH':
        print("SUCCESS: Brain correctly parsed the sequence.")
    else:
        print("FAILURE: Parsing error.")

if __name__ == "__main__":
    run_experiment()
