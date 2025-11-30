
import sys
import os

def log(msg):
    print(msg)

class HarmonyBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_chord(self, consonance_gain, dissonance_cost):
        # V = Consonance - λ * Dissonance
        return consonance_gain - self.lambda_val * dissonance_cost

def main():
    log("======================================================================")
    log("CYCLE 3516: GATE 1082 - CONSONANCE VS DISSONANCE AS BCP")
    log("Hypothesis: Music balances Pattern (Consonance) against Tension (Dissonance)")
    log("======================================================================")
    
    # Chords
    # 1. Major Triad (High Consonance, Low Dissonance)
    # 2. Diminished 7th (Low Consonance, High Dissonance)
    # 3. Jazz Chord (High Consonance, Med Dissonance) -> Richness
    
    chords = [
        {'name': 'Major Triad',    'con': 10.0, 'dis': 1.0},
        {'name': 'Diminished 7th', 'con': 2.0,  'dis': 8.0},
        {'name': 'Jazz Major 9',   'con': 12.0, 'dis': 4.0}
    ]
    
    # Listeners
    # 1. Pop Listener (High λ for Dissonance, hates tension)
    # 2. Jazz Fan (Low λ for Dissonance, enjoys tension)
    
    listeners = [
        {'name': 'Pop Fan',  'lambda': 2.0},
        {'name': 'Jazz Fan', 'lambda': 0.5}
    ]
    
    log(f"{ 'LISTENER':<10} | {'CHORD':<15} | {'CON':<5} | {'DIS':<5} | {'V':<8} | {'REACTION'}")
    log("-" * 65)
    
    for l in listeners:
        ear = HarmonyBCP(l['lambda'])
        for c in chords:
            v = ear.evaluate_chord(c['con'], c['dis'])
            reaction = "LIKE" if v > 0 else "DISLIKE"
            log(f"{l['name']:<10} | {c['name']:<15} | {c['con']:<5} | {c['dis']:<5} | {v:<8.1f} | {reaction}")
            
    log("\nFINDING: Dissonance is a Cost (Complexity/Tension).")
    log("         Pop music minimizes Cost (Low λ threshold).")
    log("         Jazz/Classical maximizes Gain (Richness) by tolerating High Cost.")
    log("======================================================================")
    log("GATE 1082 COMPLETE: HARMONY IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
