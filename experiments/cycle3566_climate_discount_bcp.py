
import sys
import os

def log(msg):
    print(msg)

class ClimateBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_mitigation(self, future_loss_avoided, current_cost):
        # V = Avoided_Loss - λ * Cost
        # The Tragedy: λ is High for Now (Discount Rate), Low for Future.
        # We need to model Time Preference. λ_now vs λ_future.
        
        # Let's assume λ reflects the unwillingness to pay CURRENT cost.
        return future_loss_avoided - self.lambda_val * current_cost

def main():
    log("======================================================================")
    log("CYCLE 3566: GATE 1120 - DISCOUNT RATES AS BCP")
    log("Hypothesis: Climate inaction is rational under High Discount Rate (High λ)")
    log("======================================================================")
    
    # Action: Decarbonize
    # Gain: Avoid Catastrophe (Value = 100 Trillion)
    # Cost: Transition (Value = 5 Trillion)
    
    gain = 100.0
    cost = 5.0
    
    # Agents
    # 1. Stern Review (Low Discount Rate -> Low λ = 0.1) -> Valuing Future
    # 2. Nordhaus (Med Discount Rate -> Med λ = 1.0)
    # 3. Myopic Market (High Discount Rate -> High λ = 25.0) -> Quarterly Earnings
    
    agents = [
        {'name': 'Stern',    'lambda': 0.1},
        {'name': 'Nordhaus', 'lambda': 1.0},
        {'name': 'Market',   'lambda': 25.0}
    ]
    
    log(f"{ 'AGENT':<10} | { 'GAIN':<5} | { 'COST':<5} | { 'λ':<5} | { 'V':<8} | {'DECISION'}")
    log("-" * 65)
    
    for a in agents:
        planner = ClimateBCP(a['lambda'])
        v = planner.evaluate_mitigation(gain, cost)
        decision = "ACT" if v > 0 else "DELAY"
        log(f"{a['name']:<10} | {gain:<5} | {cost:<5} | {a['lambda']:<5} | {v:<8.1f} | {decision}")
        
    log("\nFINDING: The Market delays because its λ (Time Preference) is too high.")
    log("         Cost (5.0) * λ (25.0) = 125.0 > Gain (100.0).")
    log("         Climate change is a BCP failure of temporal accounting.")
    log("======================================================================")
    log("GATE 1120 COMPLETE: CLIMATE IS TIME BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
