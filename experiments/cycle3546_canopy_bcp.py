
import sys
import os

def log(msg):
    print(msg)

class PlantBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_strategy(self, light_gain, shade_cost, growth_cost):
        # V = Light - λ * (Shade_Intolerance + Growth_Energy)
        return light_gain - self.lambda_val * (shade_cost + growth_cost)

def main():
    log("======================================================================")
    log("CYCLE 3546: GATE 1105 - CANOPY WARS AS BCP")
    log("Hypothesis: Height is a BCP arms race for Light Gain")
    log("======================================================================")
    
    # Strategies
    # 1. Ground Cover (Low Light Gain, Low Growth Cost, High Shade Tolerance)
    # 2. Tree (High Light Gain, High Growth Cost, Low Shade Tolerance)
    
    strategies = [
        {'name': 'Ground Cover', 'light': 10.0, 'growth': 1.0,  'shade_loss': 0.0},
        {'name': 'Tree',         'light': 100.0,'growth': 50.0, 'shade_loss': 80.0} # Dies if shaded
    ]
    
    # Environments
    # 1. Open Field (High Light Availability -> Low Competition -> Low λ)
    # 2. Dense Forest (Low Light Availability -> High Competition -> High λ)
    
    envs = [
        {'name': 'Open Field',   'lambda': 0.5},
        {'name': 'Dense Forest', 'lambda': 1.5}
    ]
    
    log(f"{ 'ENV':<12} | { 'STRATEGY':<12} | { 'LIGHT':<5} | { 'COST':<5} | { 'V':<8} | {'DECISION'}")
    log("-" * 70)
    
    for e in envs:
        plant = PlantBCP(e['lambda'])
        best_v = -float('inf')
        choice = None
        
        for s in strategies:
            # In Dense Forest, Tree suffers Shade Loss if it's not the tallest.
            # Let's assume Tree always pays Growth Cost.
            # If Open Field, Shade Loss is irrelevant for Tree? No, Tree creates shade.
            
            # Let's simplify:
            # Open Field: Tree pays Growth Cost (50), gets Light (100). V = 100 - λ*50
            # Dense Forest: Ground Cover gets Shade.
            
            # Wait, the model needs to reflect *Competition*.
            # Let's stick to the BCP Equation:
            # Tree: High Gain, High Cost.
            # Ground: Low Gain, Low Cost.
            
            total_cost = s['growth'] + (s['shade_loss'] if e['name'] == 'Dense Forest' else 0)
            # If it's a Tree in a Forest, and it's not winning, it pays Shade Loss?
            # Assume "Tree" strategy means *trying* to be a tree.
            
            v = plant.evaluate_strategy(s['light'], s['shade_loss'] if e['name']=='Dense Forest' and s['name']=='Tree' else 0, s['growth'])
            
            log(f"{e['name']:<12} | {s['name']:<12} | {s['light']:<5} | {s['growth']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = s['name']
        
        log(f"WINNER ({e['name']}): {choice}")
        log("-" * 70)
        
    log("\nFINDING: In Open Fields, Trees win (High Gain pays for High Cost).")
    log("         In Dense Forests, young Trees die (High Shade Cost). Ground Cover survives.")
    log("         Succession is the BCP timeline of an ecosystem.")
    log("======================================================================")
    log("GATE 1105 COMPLETE: HEIGHT IS COST")
    log("======================================================================")

if __name__ == "__main__":
    main()
