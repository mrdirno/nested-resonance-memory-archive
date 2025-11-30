
import sys
import os

def log(msg):
    print(msg)

class PalateBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_taste(self, nutrient_gain, toxin_cost):
        # V = Nutrient - λ * Toxin
        # Bitterness = Cost signal (potential toxin)
        # Sweetness/Fat = Gain signal (energy)
        return nutrient_gain - self.lambda_val * toxin_cost

def main():
    log("======================================================================")
    log("CYCLE 3520: GATE 1085 - ACQUIRED TASTE AS BCP")
    log("Hypothesis: Acquired taste is λ-reduction for specific costs (Bitterness)")
    log("======================================================================")
    
    # Foods
    # 1. Sugar (High Gain, Low Cost) -> Universally liked
    # 2. Coffee (Med Gain - Caffeine, High Cost - Bitter)
    # 3. Rotten Meat (Low Gain, Very High Cost - Pathogen)
    
    foods = [
        {'name': 'Sugar',  'gain': 10.0, 'cost': 0.0},
        {'name': 'Coffee', 'gain': 5.0,  'cost': 8.0}, # Bitter!
        {'name': 'Rotten', 'gain': 1.0,  'cost': 100.0}
    ]
    
    # Tasters
    # 1. Child (High λ for Toxin, risk averse)
    # 2. Adult (Low λ for Bitterness due to experience)
    
    tasters = [
        {'name': 'Child', 'lambda': 2.0},
        {'name': 'Adult', 'lambda': 0.5}
    ]
    
    log(f"{ 'TASTER':<10} | { 'FOOD':<10} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8} | {'REACTION'}")
    log("-" * 60)
    
    for t in tasters:
        tongue = PalateBCP(t['lambda'])
        for f in foods:
            v = tongue.evaluate_taste(f['gain'], f['cost'])
            reaction = "YUM" if v > 0 else "YUCK"
            log(f"{t['name']:<10} | {f['name']:<10} | {f['gain']:<5} | {f['cost']:<5} | {v:<8.1f} | {reaction}")
            
    log("\nFINDING: Children reject Coffee (V < 0) because λ is high.")
    log("         Adults acquire the taste by lowering λ (learning that Bitterness != Death).")
    log("         Cuisine is the art of balancing Gain and Cost signals.")
    log("======================================================================")
    log("GATE 1085 COMPLETE: TASTE IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
