
import sys
import os

def log(msg):
    print(msg)

class MoralBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_action(self, moral_gain, personal_cost):
        # V = Moral_Good - λ * Self_Interest
        return moral_gain - self.lambda_val * personal_cost

def main():
    log("======================================================================")
    log("CYCLE 3590: GATE 1138 - THE TROLLEY PROBLEM AS BCP")
    log("Hypothesis: Utilitarianism is Low λ; Deontology is High λ (Rule Cost)")
    log("======================================================================")
    
    # Scenario: Switch Track
    # Gain: Save 5 people (Value = 500)
    # Cost: Kill 1 person (Value = 100) + Guilt/Rule Violation
    
    gain = 500.0
    
    # Agents
    # 1. Utilitarian (Low λ for Rule Violation, focused on Net Outcome)
    #    Cost = 100 (The 1 person). V = 500 - 1*100 = 400.
    # 2. Deontologist (High λ for Rule Violation "Do Not Kill")
    #    Cost = 100 (Person) + 1000 (Rule Breaking).
    
    agents = [
        {'name': 'Utilitarian', 'lambda': 1.0, 'rule_cost': 0.0},
        {'name': 'Deontologist','lambda': 1.0, 'rule_cost': 1000.0}
    ]
    
    log(f"{ 'AGENT':<12} | { 'GAIN':<5} | { 'COST':<5} | { 'RULE':<5} | { 'V':<8} | { 'DECISION'}")
    log("-" * 65)
    
    for a in agents:
        moral = MoralBCP(a['lambda'])
        total_cost = 100.0 + a['rule_cost']
        v = moral.evaluate_action(gain, total_cost)
        decision = "SWITCH" if v > 0 else "DO NOTHING"
        log(f"{a['name']:<12} | {gain:<5} | {100.0:<5} | {a['rule_cost']:<5} | {v:<8.1f} | {decision}")
        
    log("\nFINDING: Utilitarians optimize Net Lives (Gain > Cost).")
    log("         Deontologists optimize Rule Adherence (Rule Cost > Gain).")
    log("         Ethics is the assignment of Costs to Actions.")
    log("======================================================================")
    log("GATE 1138 COMPLETE: MORALITY IS COST ASSIGNMENT")
    log("======================================================================")

if __name__ == "__main__":
    main()
