"""
Cycle 2564: The Babble (Gate 191)
Goal: Verify agents can invent labels and reinforce them.
Mechanism:
1. Initialize 2 agents.
2. Simulate one agent labeling 'FOOD' and 'PREDATOR'.
3. Check if brain vocabulary is updated.
"""

import time
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2564: The Babble ---")
    
    ecosystem = Ecosystem()
    
    # 1. Agent Adam (High Innovation)
    adam = DigitalLifeform(name="Adam")
    while len(adam.genome) < 11: adam.genome.append(0.5)
    adam.genome[9] = 0.95 
    adam.energy = 500
    
    # 2. Agent Eve (High Innovation)
    eve = DigitalLifeform(name="Eve")
    while len(eve.genome) < 11: eve.genome.append(0.5)
    eve.genome[9] = 0.95
    eve.energy = 500
    
    ecosystem.add_agent(adam)
    ecosystem.add_agent(eve)
    
    print("Agents Initialized.")
    
    # Inject Signals to trigger Labeling
    # Adam sees Food
    adam.sensed_signals['FOOD'] = (10, 10)
    
    # Force update to trigger act()
    # We need to capture the emitted signal from act()
    # Ecosystem.update() propagates signals but doesn't easily return them to us here for inspection
    # unless we hook into it.
    # Instead, let's manually run act() for Adam to inspect the result.
    
    print("\n[TEST] Adam sensing FOOD...")
    adam.reality_monitor.update() # Prep
    
    # Fake bridge state
    bridge_state = {'pi_phase': 0, 'e_phase': 0, 'phi_phase': 0}
    
    # We expect Adam to choose 'label' because innovation is high and 'FOOD' is present
    # His utility for label is 60 * 0.95 = 57.
    # His utility for move_to_food might be higher if he is hungry.
    # Let's make sure he isn't too hungry. Energy 500 is abundant.
    # Survival score = 0.
    
    signals = adam.act(bridge_state)
    
    label_signal = None
    if signals:
        if not isinstance(signals, list): signals = [signals]
        for s in signals:
            if s.type == 'LABEL':
                label_signal = s
                break
                
    if label_signal:
        lbl = label_signal.payload['label']
        typ = label_signal.payload['type']
        print(f"SUCCESS: Adam invented label '{lbl}' for '{typ}'")
        
        # Verify Brain State
        print(f"Adam's Vocabulary: {adam.brain.vocabulary}")
        if lbl in adam.brain.vocabulary and typ in adam.brain.vocabulary[lbl]:
             print("SUCCESS: Adam remembered the label.")
        else:
             print("FAILURE: Adam has amnesia.")
             
    else:
        print(f"FAILURE: Adam did not label. Intent: {adam.intent}")
        # Debug utility
        # We can't easily see local vars of act(), but we saw the code.
        # Label score is 57.
        # What else?
        # He has 'FOOD' signal.
        # If he has no knowledge of food location (sensed signals -> knowledge happens inside act),
        # wait, act() does: `if 'NEAREST_FOOD' in self.sensed_signals: self.knowledge...`
        # But our signal key is just 'FOOD'.
        # scan() sets 'FOOD' target type but not the signal key 'NEAREST_FOOD' (which seems to be legacy or specific to `move_to_food`).
        # Actually `scan` sets `self.target_location`.
        # The utility logic checks `self.knowledge` for `NEAREST_FOOD`.
        # Let's check `genesis.py`:
        # `if 'NEAREST_FOOD' in self.knowledge: options['move_to_food']...`
        # `scan` logic in `genesis.py`:
        # `if nearest_food: ... self.target_type = 'FOOD'`
        # It does NOT set `sensed_signals['NEAREST_FOOD']`.
        # Wait, `sense` sets `sensed_signals`.
        # `act` checks `sensed_signals` for 'FOOD' to enable labeling.
        # My injection `adam.sensed_signals['FOOD'] = ...` should work for the label logic.
        pass

if __name__ == "__main__":
    run_experiment()
