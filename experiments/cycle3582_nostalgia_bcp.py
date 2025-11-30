
import sys
import os

def log(msg):
    print(msg)

class MemoryBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_memory(self, comfort_gain, distortion_cost):
        # V = Comfort - λ * Distortion
        # Nostalgia maximizes Comfort by editing out the painful details (Distortion).
        # Accuracy is expensive (Pain).
        return comfort_gain - self.lambda_val * distortion_cost

def main():
    log("======================================================================")
    log("CYCLE 3582: GATE 1132 - ROSY RETROSPECTION AS BCP")
    log("Hypothesis: Nostalgia is efficient memory compression (Keep the Gain, delete the Cost)")
    log("======================================================================")
    
    # Memories
    # 1. Accurate (High Accuracy, Low Comfort - Includes Pain)
    # 2. Nostalgic (Low Accuracy, High Comfort - All Gain, No Pain)
    
    # The "Cost" here is Distortion (Loss of Truth).
    
    memories = [
        {'name': 'Accurate',  'comfort': 10.0, 'distortion': 0.0},
        {'name': 'Nostalgic', 'comfort': 50.0, 'distortion': 20.0}
    ]
    
    # Agents
    # 1. Historian (High λ for Distortion - Values Truth)
    # 2. Human (Low λ for Distortion - Values Comfort)
    
    agents = [
        {'name': 'Historian', 'lambda': 2.0},
        {'name': 'Human',     'lambda': 0.5}
    ]
    
    log(f"{ 'AGENT':<10} | { 'MEMORY':<10} | { 'COMF':<5} | { 'DIST':<5} | { 'V':<8} | {'CHOICE'}")
    log("-" * 60)
    
    for a in agents:
        mind = MemoryBCP(a['lambda'])
        best_v = -float('inf')
        choice = None
        
        for m in memories:
            v = mind.evaluate_memory(m['comfort'], m['distortion'])
            log(f"{a['name']:<10} | {m['name']:<10} | {m['comfort']:<5} | {m['distortion']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = m['name']
        
        log(f"WINNER ({a['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Humans choose Nostalgia because V(Nostalgia) > V(Accurate).")
    log("         Distortion is a price we happily pay for Comfort.")
    log("         'The Good Old Days' is a BCP construct, not a historical one.")
    log("======================================================================")
    log("GATE 1132 COMPLETE: NOSTALGIA IS EDITED GAIN")
    log("======================================================================")

if __name__ == "__main__":
    main()
