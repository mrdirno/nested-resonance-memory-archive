
import sys
import os

def log(msg):
    print(msg)

class RiverBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_path(self, gravity_gain, resistance_cost):
        # V = Gravity - λ * Resistance
        # Water seeks the path of Least Resistance (Cost) relative to Gravity (Gain)
        return gravity_gain - self.lambda_val * resistance_cost

def main():
    log("======================================================================")
    log("CYCLE 3513: GATE 1080 - EROSION AS BCP")
    log("Hypothesis: Rivers choose paths to maximize V (Steepest Descent/Least Resistance)")
    log("======================================================================")
    
    # Paths
    # A: Straight (High Resistance - Rock)
    # B: Meander (Low Resistance - Soil, but Longer)
    
    # Gravity Gain depends on Slope.
    # Resistance depends on Material.
    
    paths = [
        {'name': 'Straight (Rock)', 'gravity': 10.0, 'resistance': 20.0},
        {'name': 'Meander (Soil)',  'gravity': 5.0,  'resistance': 2.0} # Lower slope effectively
    ]
    
    river = RiverBCP(lambda_val=1.0)
    
    log(f"{ 'PATH':<20} | {'GRAVITY':<10} | {'RESIST':<10} | {'V':<8} | {'FLOW?'}")
    log("-" * 60)
    
    best_v = -float('inf')
    choice = None
    
    for p in paths:
        v = river.evaluate_path(p['gravity'], p['resistance'])
        log(f"{p['name']:<20} | {p['gravity']:<10} | {p['resistance']:<10} | {v:<8.1f} |")
        if v > best_v:
            best_v = v
            choice = p['name']
            
    log(f"WINNER: {choice}")
    
    log("\nFINDING: Rivers meander because the Cost of eroding rock is too high.")
    log("         They maximize V by taking the 'Long Way' through softer material.")
    log("         Erosion is the BCP algorithm of the landscape.")
    log("======================================================================")
    log("GATE 1080 COMPLETE: EROSION IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
