
import sys
import os

def log(msg):
    print(msg)

class DeveloperBCP:
    def __init__(self, budget=10.0):
        self.budget = budget
        self.lambda_val = 1.0 / (0.1 + budget)
        
    def evaluate_project(self, rent_gain, build_cost, zoning_penalty):
        # V = Rent - λ * Cost - Penalty
        return rent_gain - self.lambda_val * build_cost - zoning_penalty

def main():
    log("======================================================================")
    log("CYCLE 3451: GATE 1031 - ZONING AS BCP")
    log("Hypothesis: Zoning is an artificial Cost injection to shape City Topology")
    log("======================================================================")
    
    dev = DeveloperBCP(budget=10.0) # Low λ ≈ 0.1
    
    # Projects
    # A: Skyscraper (High Rent, High Cost)
    # B: House (Low Rent, Low Cost)
    # C: Factory (Med Rent, Med Cost)
    
    projects = [
        {'name': 'Skyscraper', 'rent': 100, 'cost': 50},
        {'name': 'House',      'rent': 10,  'cost': 5},
        {'name': 'Factory',    'rent': 40,  'cost': 20}
    ]
    
    # SCENARIO 1: NO ZONING (Free Market)
    log("\nSCENARIO 1: NO ZONING (Free Market)")
    best_v = -float('inf')
    winner = None
    
    for p in projects:
        v = dev.evaluate_project(p['rent'], p['cost'], 0)
        log(f"{p['name']:<10} | Rent={p['rent']} | Cost={p['cost']} | V={v:.2f}")
        if v > best_v:
            best_v = v
            winner = p['name']
            
    log(f"WINNER: {winner} (Highest Best Use)")
    
    # SCENARIO 2: ZONING (Residential Only)
    log("\nSCENARIO 2: ZONING ENFORCEMENT (Residential Only)")
    # Zoning Penalty = 1000 for non-House
    
    best_v = -float('inf')
    winner = None
    
    for p in projects:
        penalty = 0 if p['name'] == 'House' else 1000
        v = dev.evaluate_project(p['rent'], p['cost'], penalty)
        log(f"{p['name']:<10} | Penalty={penalty} | V={v:.2f}")
        if v > best_v:
            best_v = v
            winner = p['name']
            
    log(f"WINNER: {winner}")
    
    log("\nFINDING: Zoning works by injecting infinite Cost (Penalty) into BCP equation.")
    log("         It forces sub-optimal land use (V_house < V_sky) for social goals.")
    log("======================================================================")
    log("GATE 1031 COMPLETE: ZONING IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
