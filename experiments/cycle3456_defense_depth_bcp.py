
import sys
import os

def log(msg):
    print(msg)

class AttackerBCP:
    def __init__(self, budget=1000.0):
        self.budget = budget
        self.current_spend = 0.0
        
    def attempt_breach(self, layer_name, difficulty_cost):
        # Check if affordable
        if self.current_spend + difficulty_cost > self.budget:
            return False, "BUDGET EXHAUSTED"
            
        self.current_spend += difficulty_cost
        return True, "BREACHED"

def main():
    log("======================================================================")
    log("CYCLE 3456: GATE 1035 - DEFENSE IN DEPTH AS BCP")
    log("Hypothesis: Layers work by exhausting the Attacker's Budget")
    log("======================================================================")
    
    # The Prize
    target_value = 50000
    
    # The Defense Layers
    layers = [
        {'name': 'Firewall',        'cost': 10},
        {'name': 'WAF',             'cost': 50},
        {'name': 'MFA',             'cost': 500},
        {'name': 'Zero Trust/Enc',  'cost': 5000}
    ]
    
    # Attackers
    attackers = [
        {'name': 'Script Kiddie', 'budget': 100},
        {'name': 'Crimeware',     'budget': 1000},
        {'name': 'APT Group',     'budget': 10000}
    ]
    
    for att in attackers:
        log(f"\nATTACKER: {att['name']} (Budget={att['budget']})")
        agent = AttackerBCP(budget=att['budget'])
        
        success = True
        for layer in layers:
            breached, status = agent.attempt_breach(layer['name'], layer['cost'])
            log(f"  Layer: {layer['name']:<15} | Cost: {layer['cost']:<5} | Status: {status}")
            
            if not breached:
                success = False
                break
        
        if success:
            roi = target_value - agent.current_spend
            log(f"RESULT: SUCCESS! Total Cost: {agent.current_spend}. ROI: {roi}")
        else:
            log(f"RESULT: FAILED at {layer['name']}. Attack abandoned.")

    log("\nFINDING: Defense in Depth is Budget Exhaustion Engineering.")
    log("         You don't need perfect security; you just need Total Cost > Attacker Budget.")
    log("======================================================================")
    log("GATE 1035 COMPLETE: LAYERS = ADDITIVE COST")
    log("======================================================================")

if __name__ == "__main__":
    main()
