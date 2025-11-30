
import sys
import os

def log(msg):
    print(msg)

class CuisineBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_dish(self, flavor_gain, preparation_cost, spice_cost):
        # V = Flavor - \u03bb * (Prep + Spice)
        # Spices were historically expensive (High Cost).
        # Why use them? Antimicrobial Gain? Signaling?
        return flavor_gain - self.lambda_val * (preparation_cost + spice_cost)

def main():
    log("======================================================================")
    log("CYCLE 3521: GATE 1086 - SPICE AS BCP")
    log("Hypothesis: Spice use correlates with pathogen risk (Gain) and availability (Cost)")
    log("======================================================================")
    
    # Dishes
    # 1. Bland Stew (Low Gain, Low Cost)
    # 2. Spicy Curry (High Gain - Flavor/Antimicrobial, High Cost - Spice)
    
    dishes = [
        {'name': 'Bland', 'gain': 5.0,  'cost': 1.0},
        {'name': 'Spicy', 'gain': 10.0, 'cost': 5.0}
    ]
    
    # Regions
    # 1. Cold Climate (Low Pathogen Risk -> Low Gain from Spice, High Cost of Import -> High \u03bb)
    #    Gain of Spice is purely Flavor (say 2.0 extra). Total Gain = 7.0
    # 2. Hot Climate (High Pathogen Risk -> High Gain from Spice, Local Availability -> Low \u03bb)
    #    Gain of Spice is Flavor + Survival (say 5.0 extra). Total Gain = 10.0
    
    # Wait, let's model this better.
    # V = (Flavor + Antimicrobial) - \u03bb * Cost
    
    regions = [
        {'name': 'Cold', 'anti_gain': 0.0, 'lambda': 2.0}, # High cost to get spice
        {'name': 'Hot',  'anti_gain': 5.0, 'lambda': 0.5}  # Low cost (local)
    ]
    
    log(f"{ 'REGION':<10} | { 'DISH':<10} | { 'FLAV':<5} | { 'ANTI':<5} | { 'COST':<5} | { 'V':<8} | {'CHOICE'}")
    log("-" * 70)
    
    base_flavor_bland = 5.0
    base_flavor_spicy = 7.0 # Spice tastes good too
    
    for r in regions:
        best_v = -float('inf')
        choice = None
        
        # Bland Dish
        v_bland = base_flavor_bland - r['lambda'] * 1.0
        log(f"{r['name']:<10} | Bland      | {base_flavor_bland:<5} | {0.0:<5} | {1.0:<5} | {v_bland:<8.1f} |")
        if v_bland > best_v:
            best_v = v_bland
            choice = "Bland"
            
        # Spicy Dish
        # Gain includes Antimicrobial benefit in Hot climates
        total_gain_spicy = base_flavor_spicy + r['anti_gain']
        v_spicy = total_gain_spicy - r['lambda'] * 5.0
        log(f"{r['name']:<10} | Spicy      | {base_flavor_spicy:<5} | {r['anti_gain']:<5} | {5.0:<5} | {v_spicy:<8.1f} |")
        if v_spicy > best_v:
            best_v = v_spicy
            choice = "Spicy"
            
        log(f"WINNER ({r['name']}): {choice}")
        log("-" * 70)
        
    log("\nFINDING: Hot climates use spice because V(Spicy) > V(Bland) due to Antimicrobial Gain")
    log("         and lower availability cost. Cold climates stick to bland because Cost > Gain.")
    log("         Gastronomy is ecological BCP.")
    log("======================================================================")
    log("GATE 1086 COMPLETE: SPICE IS SURVIVAL")
    log("======================================================================")

if __name__ == "__main__":
    main()
