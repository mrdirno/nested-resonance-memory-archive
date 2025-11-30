
import sys
import os

def log(msg):
    print(msg)

class NarrativeBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_plot(self, interest_gain, suspension_cost):
        # V = Interest - λ * Disbelief
        return interest_gain - self.lambda_val * suspension_cost

def main():
    log("======================================================================")
    log("CYCLE 3476: GATE 1051 - SUSPENSION OF DISBELIEF AS BCP")
    log("Hypothesis: Readers pay a Cost (Disbelief) for Gain (Entertainment)")
    log("======================================================================")
    
    # Stories
    # 1. Realistic Fiction (Low Gain, Low Cost)
    # 2. Fantasy (High Gain, High Cost of Magic)
    # 3. Bad Sci-Fi (Low Gain, High Cost of Plotholes)
    
    stories = [
        {'name': 'Realistic', 'gain': 5.0, 'cost': 1.0},
        {'name': 'Fantasy',   'gain': 20.0, 'cost': 10.0},
        {'name': 'Bad Sci-Fi','gain': 5.0,  'cost': 10.0}
    ]
    
    # Readers
    # 1. Cynic (High λ = 2.0)
    # 2. Fan (Low λ = 0.5)
    
    log(f"{ 'READER':<10} | {'STORY':<12} | {'GAIN':<5} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 60)
    
    readers = [
        {'name': 'Cynic', 'lambda': 2.0},
        {'name': 'Fan',   'lambda': 0.5}
    ]
    
    for r in readers:
        reader = NarrativeBCP(r['lambda'])
        for s in stories:
            v = reader.evaluate_plot(s['gain'], s['cost'])
            decision = "READ" if v > 0 else "DROP"
            log(f"{r['name']:<10} | {s['name']:<12} | {s['gain']:<5} | {s['cost']:<5} | {v:<8.1f} | {decision}")
            
    log("\nFINDING: 'Suspension of Disbelief' is a Budget Transaction.")
    log("         The author must provide enough Entertainment (Gain) to pay for the Implausibility (Cost).")
    log("         Fans have a subsidized Budget (Low λ).")
    log("======================================================================")
    log("GATE 1051 COMPLETE: DISBELIEF IS A COST")
    log("======================================================================")

if __name__ == "__main__":
    main()
