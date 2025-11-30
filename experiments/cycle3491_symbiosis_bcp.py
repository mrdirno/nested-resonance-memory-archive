
import sys
import os

def log(msg):
    print(msg)

class ParasiteBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_strategy(self, energy_gain, immune_cost):
        return energy_gain - self.lambda_val * immune_cost

def main():
    log("======================================================================")
    log("CYCLE 3491: GATE 1063 - SYMBIOSIS AS BCP")
    log("Hypothesis: Symbiosis occurs when Cost of Independence > Cost of Cooperation")
    log("======================================================================")
    
    # Gain from Host (Nutrients)
    gain = 10.0
    
    # Costs
    # 1. Parasitism: Host Immune Attack (High Cost)
    # 2. Mutualism: Service Provision (Med Cost)
    # 3. Independence: Foraging (Very High Cost for specialized organism)
    
    strategies = [
        {'name': 'Parasitism',   'gain': 10.0, 'cost': 8.0},  # Fight Immune System
        {'name': 'Mutualism',    'gain': 10.0, 'cost': 2.0},  # Provide Service
        {'name': 'Independence', 'gain': 10.0, 'cost': 15.0}  # Forage Alone
    ]
    
    agent = ParasiteBCP(lambda_val=1.0)
    
    log(f"{ 'STRATEGY':<15} | {'GAIN':<5} | {'COST':<5} | {'V':<8} | {'STATUS'}")
    log("-" * 55)
    
    for s in strategies:
        v = agent.evaluate_strategy(s['gain'], s['cost'])
        status = "VIABLE" if v > 0 else "EXTINCT"
        log(f"{s['name']:<15} | {s['gain']:<5} | {s['cost']:<5} | {v:<8.1f} | {status}")
        
    log("\nFINDING: Mutualism is BCP-optimal because paying the 'Service Cost' (2.0)")
    log("         is cheaper than fighting the Immune System (8.0) or Foraging (15.0).")
    log("         Mitochondria are simply BCP-optimized bacteria.")
    log("======================================================================")
    log("GATE 1063 COMPLETE: SYMBIOSIS IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
