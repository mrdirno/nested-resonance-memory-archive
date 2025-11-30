
import sys
import os

def log(msg):
    print(msg)

class MasteryBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_practice(self, skill_gain, effort_cost):
        # V = Gain - λ * Cost
        return skill_gain - self.lambda_val * effort_cost

def main():
    log("======================================================================")
    log("CYCLE 3468: GATE 1045 - THE 10,000 HOUR RULE AS BCP")
    log("Hypothesis: Mastery requires λ-reduction to sustain long-term Cost")
    log("======================================================================")
    
    # Mastery Goal
    total_hours = 10000
    gain_per_hour = 1.0
    cost_per_hour = 1.0 # Baseline effort
    
    # Scenarios:
    # A: Grind (High Cost Perception, λ=1.0)
    # B: Flow/Passion (Low Cost Perception, λ=0.1)
    
    log(f"{ 'MODE':<10} | { 'λ':<5} | { 'HOURLY V':<10} | {'SUSTAINABLE?'}")
    log("-" * 50)
    
    modes = [
        {'name': 'Grind', 'lambda': 1.5}, # Hate it
        {'name': 'Work',  'lambda': 1.0}, # Neutral
        {'name': 'Flow',  'lambda': 0.1}  # Love it
    ]
    
    for m in modes:
        agent = MasteryBCP(lambda_val=m['lambda'])
        v = agent.evaluate_practice(gain_per_hour, cost_per_hour)
        status = "YES" if v > 0 else "BURNOUT"
        log(f"{m['name']:<10} | {m['lambda']:<5} | {v:+.2f}       | {status}")
        
    log("\nFINDING: The 10,000 Hour Rule is impossible under High λ (Grind).")
    log("         Mastery requires passion (Flow) which lowers effective λ,")
    log("         making the immense cost affordable.")
    log("         Genius is not just talent; it is a budget anomaly.")
    log("======================================================================")
    log("GATE 1045 COMPLETE: MASTERY IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
