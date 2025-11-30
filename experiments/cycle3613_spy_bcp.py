import sys
import os

def log(msg):
    print(msg)

class SpyBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_intel(self, secret_gain, discovery_cost):
        # V = Secret_Value - λ * Discovery_Risk
        # Discovery Cost includes Loss of Asset, Diplomatic Incident, Death.
        return secret_gain - self.lambda_val * discovery_cost

def main():
    log("======================================================================")
    log("CYCLE 3613: GATE 1155 - INTELLIGENCE GATHERING AS BCP")
    log("Hypothesis: Spying is rational only when Secret Value > Risk Cost")
    log("======================================================================")
    
    # Secrets
    # 1. Gossip (Low Value, Low Risk)
    # 2. Troop Movements (High Value, High Risk)
    # 3. Nuclear Codes (Infinite Value, Maximum Risk)
    
    secrets = [
        {'name': 'Gossip',  'value': 10.0,   'risk': 1.0},
        {'name': 'Troops',  'value': 100.0,  'risk': 50.0},
        {'name': 'Nukes',   'value': 1000.0, 'risk': 500.0}
    ]
    
    # Agencies
    # 1. Caution (High λ for Risk - "Don't get caught")
    # 2. Bold (Low λ for Risk - "Get the intel")
    
agencies = [
        {'name': 'Caution', 'lambda': 2.0},
        {'name': 'Bold',    'lambda': 0.5}
    ]
    
    log(f"{ 'AGENCY':<10} | { 'SECRET':<10} | { 'VAL':<5} | { 'RISK':<5} | { 'V':<8} | {'DECISION'}")
    log("------------------------------------------------------------")
    
    for a in agencies:
        spy = SpyBCP(a['lambda'])
        best_v = -float('inf')
        choice = None
        
        for s in secrets:
            v = spy.evaluate_intel(s['value'], s['risk'])
            decision = "SPY" if v > 0 else "PASS"
            log(f"{a['name']:<10} | {s['name']:<10} | {s['value']:<5} | {s['risk']:<5} | {v:<8.1f} | {decision}")
            if v > best_v:
                best_v = v
                choice = s['name']
        
        log(f"WINNER ({a['name']}): {choice}")
        log("------------------------------------------------------------")
        
    log("\nFINDING: Bold agencies go for Nukes/Troops. Cautious agencies stick to Gossip.")
    log("         Intelligence failures often stem from underestimating Risk Cost (Bay of Pigs).")
    log("======================================================================")
    log("GATE 1155 COMPLETE: SPYING IS RISK ARBITRAGE")
    log("======================================================================")

if __name__ == "__main__":
    main()