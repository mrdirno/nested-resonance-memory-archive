"""
Cycle 2556: The Oracle (Gate 184)
Experiment: Predictive Resonance.
Goal: Determine if agents can anticipate the Bridge's phase shift.
Hypothesis: If an agent resonates with the DERIVATIVE of the bridge phase, it acts *before* the peak.
"""

import sys
import os
import math
import csv
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem
from bridge.transcendental_bridge import TranscendentalBridge

class Oracle(DigitalLifeform):
    def __init__(self, name=None, phase_offset=0.0):
        super().__init__(name=name)
        self.genome[0] = phase_offset # Gene 0 = Phase
        
    def calculate_utility(self, bridge_state=None):
        # Override to check prediction success
        if bridge_state:
            pi_phase = bridge_state.get('pi_phase', 0.0)
            agent_phase = self.genome[0] * 6.28
            
            # Resonance
            resonance = math.cos(agent_phase - pi_phase)
            
            # Prediction: Can we guess the NEXT phase?
            # The bridge oscillates at freq=0.1
            # Next phase = pi_phase + 0.1 * PI
            # If agent_phase aligns with NEXT phase, resonance will be higher NEXT tick.
            
            # For this experiment, we just return 'predict' if resonance is high
            if resonance > 0.9:
                return 'predict'
                
        return 'wait'

    def act(self, bridge_state=None):
        intent = self.calculate_utility(bridge_state)
        if intent == 'predict':
            # Check if we are "early" or "late" relative to the peak (PI/2)
            # Just logging for analysis
            pass
        return None

def run_oracle_experiment():
    print("🔮 CYCLE 2556: THE ORACLE - PREDICTIVE RESONANCE")
    
    env = Ecosystem(capacity=20)
    # We need access to the bridge instance to get true phase
    # Ecosystem creates its own bridge.
    
    # Seed Oracles with different phase offsets
    print("✨ Seeding The Prophets...")
    for i in range(10):
        # Phases from 0 to 1.0
        phase = i / 10.0
        agent = Oracle(name=f"Oracle-{i}", phase_offset=phase)
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2556_the_oracle.csv"
    
    env.running = True
    duration = 100
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "bridge_pi_phase", "predicting_agents_count", "best_predictor_phase"])
        
        print("📝 Running simulation...")
        # Access internal bridge for ground truth
        bridge = env.bridge 
        
        for tick in range(1, duration + 1):
            env.update()
            
            # Get current bridge state (approximate, as update generates new sequence)
            # We need to peek at the bridge state used in update.
            # Ecosystem.update generates a sequence.
            # But we can't easily access local variables of update().
            # However, the bridge object state (offsets) persists.
            
            pi_phase = bridge.pi_offset
            
            # Count predictors
            predictors = [a for a in env.agents if isinstance(a, Oracle) and a.calculate_utility({'pi_phase': pi_phase}) == 'predict']
            count = len(predictors)
            
            best_phase = 0
            if predictors:
                best_phase = predictors[0].genome[0] # Just take the first one
            
            writer.writerow([tick, pi_phase, count, best_phase])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Bridge Phase={pi_phase:.2f}, Prophets={count}")
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_oracle_experiment()