
import sys
import os

def log(msg):
    print(msg)

class ArchitectBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_design(self, function_gain, beauty_gain, build_cost):
        # V = (Function + Beauty) - λ * Cost
        # Form follows Function... or Budget?
        return (function_gain + beauty_gain) - self.lambda_val * build_cost

def main():
    log("======================================================================")
    log("CYCLE 3494: GATE 1065 - FORM FOLLOWS BUDGET AS BCP")
    log("Hypothesis: Ornamentation disappears when λ (Cost Sensitivity) rises")
    log("======================================================================")
    
    # Design Styles
    # 1. Baroque (High Beauty, Very High Cost)
    # 2. Modernist (High Function, Low Cost)
    # 3. Brutalist (High Function, Very Low Cost, Low Beauty)
    
    styles = [
        {'name': 'Baroque',    'func': 5.0, 'beauty': 20.0, 'cost': 20.0},
        {'name': 'Modernist',  'func': 10.0,'beauty': 5.0,  'cost': 5.0},
        {'name': 'Brutalist',  'func': 10.0,'beauty': 1.0,  'cost': 2.0}
    ]
    
    # Clients
    # 1. Monarch (Infinite Budget -> Low λ=0.1)
    # 2. Corporation (Profit Motive -> Med λ=1.0)
    # 3. Public Housing (Austerity -> High λ=5.0)
    
    clients = [
        {'name': 'Monarch', 'lambda': 0.1},
        {'name': 'Corp',    'lambda': 1.0},
        {'name': 'State',   'lambda': 5.0}
    ]
    
    log(f"{ 'CLIENT':<10} | { 'STYLE':<10} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8} | { 'DECISION'}")
    log("-" * 60)
    
    for c in clients:
        architect = ArchitectBCP(c['lambda'])
        best_v = -float('inf')
        choice = None
        
        for s in styles:
            v = architect.evaluate_design(s['func'], s['beauty'], s['cost'])
            gain = s['func'] + s['beauty']
            log(f"{c['name']:<10} | {s['name']:<10} | {gain:<5.1f} | {s['cost']:<5.1f} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = s['name']
        
        log(f"WINNER ({c['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Loos's 'Ornament is Crime' is actually 'Ornament is Expensive'.")
    log("         As λ rises (Modernity/Efficiency), Baroque style becomes V < 0.")
    log("         Brutalism is the BCP-optimal form for high-λ austerity.")
    log("======================================================================")
    log("GATE 1065 COMPLETE: STYLE IS BUDGET")
    log("======================================================================")

if __name__ == "__main__":
    main()
