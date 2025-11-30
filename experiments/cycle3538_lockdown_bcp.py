
import sys
import os

def log(msg):
    print(msg)

class ContainmentBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_lockdown(self, lives_saved_gain, economic_cost):
        # V = Lives - λ * Economy
        # The "Value of a Statistical Life" (VSL) is implicit in λ.
        return lives_saved_gain - self.lambda_val * economic_cost

def main():
    log("======================================================================")
    log("CYCLE 3538: GATE 1099 - LOCKDOWNS AS BCP")
    log("Hypothesis: Containment policy is a trade-off between Biology and Economy")
    log("======================================================================")
    
    # Policies
    # 1. Zero COVID (High Gain, Very High Cost)
    # 2. Flatten Curve (Med Gain, Med Cost)
    # 3. Let it Rip (Low Gain, Low Cost) -> Herd Immunity
    
    # Assume Gain = Lives Saved
    # Cost = GDP Loss
    
    policies = [
        {'name': 'Zero COVID',    'lives': 1000.0, 'gdp_loss': 5000.0},
        {'name': 'Flatten Curve', 'lives': 800.0,  'gdp_loss': 1000.0},
        {'name': 'Let it Rip',    'lives': 0.0,    'gdp_loss': 0.0}
    ]
    
    # Governments (λ = Preference for Economy over Life)
    # 1. Humanist (Low λ for Economy -> Values Life)
    # 2. Capitalist (High λ for Economy -> Values GDP)
    
    govs = [
        {'name': 'Humanist',   'lambda': 0.1}, # Willing to pay 10 GDP for 1 Life
        {'name': 'Capitalist', 'lambda': 1.0}  # Willing to pay 1 GDP for 1 Life
    ]
    
    log(f"{ 'GOV':<10} | {'POLICY':<15} | {'LIVES':<5} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 65)
    
    for g in govs:
        admin = ContainmentBCP(g['lambda'])
        best_v = -float('inf')
        choice = None
        
        for p in policies:
            v = admin.evaluate_lockdown(p['lives'], p['gdp_loss'])
            log(f"{g['name']:<10} | {p['name']:<15} | {p['lives']:<5} | {p['gdp_loss']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = p['name']
        
        log(f"WINNER ({g['name']}): {choice}")
        log("-" * 65)
        
    log("\nFINDING: Policy disputes are not about Science; they are about λ.")
    log("         Different values for λ (Economy vs Life) yield different BCP optima.")
    log("======================================================================")
    log("GATE 1099 COMPLETE: LOCKDOWN IS BUDGET ALLOCATION")
    log("======================================================================")

if __name__ == "__main__":
    main()
