
import sys
import os

def log(msg):
    print(msg)

class DogmaBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_dogma(self, certainty_gain, flexibility_cost):
        # V = Certainty - λ * Flexibility_Loss
        # Dogma provides absolute Certainty (High Gain) but destroys Flexibility (High Cost).
        return certainty_gain - self.lambda_val * flexibility_cost

def main():
    log("======================================================================")
    log("CYCLE 3597: GATE 1143 - DOGMA AS BCP")
    log("Hypothesis: Dogma minimizes Cognitive Load (Uncertainty) at the cost of Adaptation")
    log("======================================================================")
    
    # Belief Systems
    # 1. Orthodoxy (High Certainty, High Rigidity)
    # 2. Heresy (Low Certainty/High Flux, Low Rigidity)
    # 3. Reformation (Med Certainty, Med Rigidity)
    
    systems = [
        {'name': 'Orthodoxy',   'certainty': 100.0, 'rigidity': 80.0},
        {'name': 'Heresy',      'certainty': 10.0,  'rigidity': 5.0},
        {'name': 'Reformation', 'certainty': 50.0,  'rigidity': 30.0}
    ]
    
    # Eras
    # 1. Dark Age (High Uncertainty/Fear -> Needs Certainty -> Low λ for Rigidity)
    # 2. Enlightenment (Low Uncertainty -> Values Flexibility -> High λ for Rigidity)
    
    eras = [
        {'name': 'Dark Age',      'lambda': 0.5}, # Can afford rigidity to get certainty
        {'name': 'Enlightenment', 'lambda': 2.0}  # Rigidity is expensive
    ]
    
    log(f"{ 'ERA':<15} | {'SYSTEM':<12} | {'CERT':<5} | {'RIGID':<5} | {'V':<8} | {'STATUS'}")
    log("-" * 65)
    
    for e in eras:
        priest = DogmaBCP(e['lambda'])
        best_v = -float('inf')
        choice = None
        
        for s in systems:
            v = priest.evaluate_dogma(s['certainty'], s['rigidity'])
            log(f"{e['name']:<15} | {s['name']:<12} | {s['certainty']:<5} | {s['rigidity']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = s['name']
        
        log(f"WINNER ({e['name']}): {choice}")
        log("-" * 65)
        
    log("\nFINDING: Dogma thrives in Dark Ages because Uncertainty is expensive (Chaos).")
    log("         Enlightenment rejects Dogma because Adaptation is more valuable than Certainty.")
    log("         Fundamentalism is BCP optimization for a chaotic world.")
    log("======================================================================")
    log("GATE 1143 COMPLETE: DOGMA IS COGNITIVE SECURITY")
    log("======================================================================")

if __name__ == "__main__":
    main()
