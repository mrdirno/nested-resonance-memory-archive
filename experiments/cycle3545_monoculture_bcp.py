
import sys
import os

def log(msg):
    print(msg)

class FarmerBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_crop(self, yield_gain, resource_cost, risk_cost):
        # V = Yield - λ * (Inputs + Risk)
        return yield_gain - self.lambda_val * (resource_cost + risk_cost)

def main():
    log("======================================================================")
    log("CYCLE 3545: GATE 1104 - MONOCULTURE AS BCP")
    log("Hypothesis: Monoculture maximizes Short-Term V but increases Long-Term Risk")
    log("======================================================================")
    
    # Crops
    # 1. Monoculture (High Yield, Low Input Cost due to scale, High Risk of Blight)
    # 2. Polyculture (Med Yield, Med Input Cost, Low Risk)
    
    crops = [
        {'name': 'Monoculture', 'yield': 100.0, 'input': 10.0, 'risk': 50.0},
        {'name': 'Polyculture', 'yield': 60.0,  'input': 20.0, 'risk': 5.0}
    ]
    
    # Farmers
    # 1. Corporate (Low λ for Risk - Diversified Portfolio elsewhere / Insurance)
    #    Or maybe Corporate has Low λ for Capital Cost but High λ for Variance?
    #    Let's assume Corp focuses on Profit Maximization: Low λ.
    # 2. Subsistence (High λ for Risk - One bad harvest = Starvation)
    
    farmers = [
        {'name': 'Corporate',   'lambda': 0.5},
        {'name': 'Subsistence', 'lambda': 2.0}
    ]
    
    log(f"{ 'FARMER':<12} | {'CROP':<12} | {'YIELD':<5} | {'COST':<5} | {'RISK':<5} | {'V':<8} | {'CHOICE'}")
    log("-" * 70)
    
    for f in farmers:
        mgr = FarmerBCP(f['lambda'])
        best_v = -float('inf')
        choice = None
        
        for c in crops:
            v = mgr.evaluate_crop(c['yield'], c['input'], c['risk'])
            log(f"{f['name']:<12} | {c['name']:<12} | {c['yield']:<5} | {c['input']:<5} | {c['risk']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = c['name']
        
        log(f"WINNER ({f['name']}): {choice}")
        log("-" * 70)
        
    log("\nFINDING: Corporate farms choose Monoculture because they can absorb Risk (Low λ).")
    log("         Subsistence farms choose Polyculture because Risk Cost is existential (High λ).")
    log("         The Green Revolution was a λ-reduction technology (via Pesticides/Fertilizer).")
    log("======================================================================")
    log("GATE 1104 COMPLETE: MONOCULTURE IS RISK ARBITRAGE")
    log("======================================================================")

if __name__ == "__main__":
    main()
