
import sys
import os

def log(msg):
    print(msg)

class InvestigateBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_investigation(self, impact_gain, time_cost):
        # V = Impact - λ * Time
        return impact_gain - self.lambda_val * time_cost

def main():
    log("======================================================================")
    log("CYCLE 3559: GATE 1115 - INVESTIGATIVE JOURNALISM AS BCP")
    log("Hypothesis: Deep reporting is a luxury good (requires Low λ for Time/Money)")
    log("======================================================================")
    
    # Stories
    # 1. Churn (Low Impact, Low Cost)
    # 2. Deep Dive (High Impact, High Cost) 
    
    stories = [
        {'name': 'Churn',     'impact': 10.0, 'cost': 1.0},
        {'name': 'Deep Dive', 'impact': 100.0,'cost': 50.0}
    ]
    
    # Outlets
    # 1. Blog (High λ for Money - needs content daily)
    # 2. ProPublica (Low λ for Money - Donor funded / Subscription)
    
    outlets = [
        {'name': 'Blog',       'lambda': 2.5},
        {'name': 'ProPublica', 'lambda': 0.5}
    ]
    
    log(f"{ 'OUTLET':<12} | {'STORY':<10} | {'IMPACT':<6} | {'COST':<5} | {'V':<8} | {'CHOICE'}")
    log("-" * 65)
    
    for o in outlets:
        editor = InvestigateBCP(o['lambda'])
        best_v = -float('inf')
        choice = None
        
        for s in stories:
            v = editor.evaluate_investigation(s['impact'], s['cost'])
            log(f"{o['name']:<12} | {s['name']:<10} | {s['impact']:<6} | {s['cost']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = s['name']
        
        log(f"WINNER ({o['name']}): {choice}")
        log("-" * 65)
        
    log("\nFINDING: High-quality information requires a subsidized budget (Low λ).")
    log("         The market (High λ) naturally selects for Churn.")
    log("         Truth is expensive.")
    log("======================================================================")
    log("GATE 1115 COMPLETE: TRUTH IS A LUXURY")
    log("======================================================================")

if __name__ == "__main__":
    main()
