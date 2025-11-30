
import sys
import os

def log(msg):
    print(msg)

class JusticeBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_punishment(self, deterrence_gain, empathy_cost):
        # V = Safety - λ * Cruelty
        return deterrence_gain - self.lambda_val * empathy_cost

def main():
    log("======================================================================")
    log("CYCLE 3591: GATE 1139 - JUSTICE AS BCP")
    log("Hypothesis: Justice systems balance Safety Gain vs Empathy Cost")
    log("======================================================================")
    
    # Punishment: Incarceration
    # Gain: Deterrence/Safety (100)
    # Cost: Cruelty/Liberty Loss (50)
    
    gain = 100.0
    cost = 50.0
    
    # Systems
    # 1. Punitive (Low λ for Empathy - "Tough on Crime")
    # 2. Rehabilitative (High λ for Empathy - "Second Chance")
    
    systems = [
        {'name': 'Punitive',       'lambda': 0.5},
        {'name': 'Rehabilitative', 'lambda': 2.5}
    ]
    
    log(f"{ 'SYSTEM':<15} | { 'GAIN':<5} | { 'COST':<5} | { 'V':<8} | {'SENTENCE'}")
    log("-" * 60)
    
    for s in systems:
        judge = JusticeBCP(s['lambda'])
        v = judge.evaluate_punishment(gain, cost)
        sentence = "PRISON" if v > 0 else "PROBATION"
        log(f"{s['name']:<15} | {gain:<5} | {cost:<5} | {v:<8.1f} | {sentence}")
        
    log("\nFINDING: Punitive systems prioritize Safety/Deterrence (Gain).")
    log("         Rehabilitative systems prioritize Human Rights (Cost avoidance).")
    log("         Justice is the calibration of λ regarding suffering.")
    log("======================================================================")
    log("GATE 1139 COMPLETE: JUSTICE IS CALIBRATION")
    log("======================================================================")

if __name__ == "__main__":
    main()
