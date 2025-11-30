
import sys
import os

def log(msg):
    print(msg)

class DaterBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_partner(self, attractiveness_gain, commitment_cost):
        # V = Attractiveness - λ * Commitment
        return attractiveness_gain - self.lambda_val * commitment_cost

def main():
    log("======================================================================")
    log("CYCLE 3574: GATE 1126 - MATING MARKET AS BCP")
    log("Hypothesis: Mating strategies optimize for Gain (Genes) vs Cost (Investment)")
    log("======================================================================")
    
    # Partners
    # 1. The Cad (High Gain, High Cost/Risk)
    # 2. The Provider (Med Gain, Low Cost/Risk)
    # 3. The Ghost (Low Gain, Low Cost)
    
    partners = [
        {'name': 'Cad',      'gain': 100.0, 'cost': 80.0},
        {'name': 'Provider', 'gain': 60.0,  'cost': 10.0},
        {'name': 'Ghost',    'gain': 10.0,  'cost': 5.0}
    ]
    
    # Daters (λ = Risk Aversion / Need for Security)
    # 1. Adventurer (Low λ = 0.5)
    # 2. Settler (High λ = 1.5)
    
    daters = [
        {'name': 'Adventurer', 'lambda': 0.5},
        {'name': 'Settler',    'lambda': 1.5}
    ]
    
    log(f"{ 'DATER':<10} | {'PARTNER':<10} | {'GAIN':<5} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    for d in daters:
        agent = DaterBCP(d['lambda'])
        best_v = -float('inf')
        choice = None
        
        for p in partners:
            v = agent.evaluate_partner(p['gain'], p['cost'])
            log(f"{d['name']:<10} | {p['name']:<10} | {p['gain']:<5} | {p['cost']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = p['name']
        
        log(f"WINNER ({d['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Adventurers choose Cads (High Gain > Cost).")
    log("         Settlers choose Providers (Low Cost optimizes V).")
    log("         'Leagues' are BCP brackets.")
    log("======================================================================")
    log("GATE 1126 COMPLETE: DATING IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
