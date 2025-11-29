"""
Cycle 2565: The Agreement (Gate 192)
Goal: Agents share labels and reinforce them based on shared context.
Mechanism:
1. Adam sees Food, invents label "X1", broadcasts it.
2. Eve hears "X1" for "FOOD".
3. Eve also sees Food (is near Adam).
4. Eve verifies "X1" -> "FOOD" and reinforces her brain.
5. We check Eve's vocabulary.
"""

import time
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform
from src.life.signal import Signal

def run_experiment():
    print("--- Cycle 2565: The Agreement ---")
    
    ecosystem = Ecosystem()
    
    # 1. Initialize Agents
    adam = DigitalLifeform(name="Adam")
    eve = DigitalLifeform(name="Eve")
    
    # Adam is the Speaker (High Innovation)
    while len(adam.genome) < 11: adam.genome.append(0.5)
    adam.genome[9] = 0.95 
    adam.energy = 500
    
    # Eve is the Listener
    while len(eve.genome) < 11: eve.genome.append(0.5)
    eve.energy = 500
    
    ecosystem.add_agent(adam)
    ecosystem.add_agent(eve)
    
    # 2. Setup Context
    # Both agents need to see 'FOOD' for verification to work.
    # In `genesis.py`, `sense` clears `sensed_signals` at start.
    # So we need to inject the signal RIGHT BEFORE `sense` or during the signal propagation phase.
    # But `ecosystem.update()` handles the loop.
    # Let's manually simulate the interaction step-by-step to ensure control.
    
    # Step A: Adam acts and generates a Label
    print("[STEP 1] Adam sees FOOD and speaks...")
    adam.sensed_signals['FOOD'] = (10, 10) # Artificial sense
    adam.reality_monitor.update()
    
    # Force Adam to Label (he did in Cycle 2564, let's assume logic holds)
    # We need to capture the signal Adam emits.
    bridge_state = {'pi_phase': 0, 'e_phase': 0, 'phi_phase': 0}
    signals = adam.act(bridge_state)
    
    label_signal = None
    if signals:
        if not isinstance(signals, list): signals = [signals]
        for s in signals:
            if s.type == 'LABEL':
                label_signal = s
                break
    
    if not label_signal:
        print("FAILURE: Adam did not speak.")
        return
        
    print(f"Adam broadcast: '{label_signal.payload['label']}' = {label_signal.payload['type']}")
    
    # Step B: Eve hears the signal while seeing FOOD
    print("[STEP 2] Eve hears signal and checks reality...")
    
    # 1. Eve Senses (Receives Signal)
    eve.sense([label_signal])
    
    # 2. Eve Scans (Simulated: She sees FOOD nearby)
    eve.sensed_signals['FOOD'] = (10, 10)
    
    # 3. Eve Acts (Processes Signal + Verification)
    eve.act(bridge_state)
    
    # Step C: Verification
    print("[STEP 3] Checking Eve's Brain...")
    
    label_text = label_signal.payload['label']
    obj_type = label_signal.payload['type']
    
    if label_text in eve.brain.vocabulary:
        strength = eve.brain.vocabulary[label_text].get(obj_type, 0)
        print(f"Eve's Strength for '{label_text}' -> {obj_type}: {strength}")
        
        if strength > 0:
            print("SUCCESS: Eve verified the label and learned it.")
        else:
            print("FAILURE: Eve did not reinforce the label.")
    else:
        print("FAILURE: Eve ignored the label.")

if __name__ == "__main__":
    run_experiment()
