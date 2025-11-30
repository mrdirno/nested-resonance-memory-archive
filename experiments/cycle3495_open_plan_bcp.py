
import sys
import os

def log(msg):
    print(msg)

class SpaceBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_layout(self, interaction_gain, privacy_loss_cost, rent_cost):
        # V = Interaction - λ * (PrivacyLoss + Rent)
        return interaction_gain - self.lambda_val * (privacy_loss_cost + rent_cost)

def main():
    log("======================================================================")
    log("CYCLE 3495: GATE 1066 - OPEN PLAN AS BCP")
    log("Hypothesis: Open Plans trade Privacy (Cost) for Rent Savings (Gain)")
    log("======================================================================")
    
    # Layouts
    # 1. Private Offices: High Privacy, High Rent
    # 2. Open Plan: High Interaction (Theoretically), Low Rent, High Privacy Loss
    
    layouts = [
        {'name': 'Offices',   'interact': 5.0,  'privacy_loss': 0.0, 'rent': 20.0},
        {'name': 'Open Plan', 'interact': 8.0,  'privacy_loss': 10.0,'rent': 5.0}
    ]
    
    # Stakeholders
    # 1. Manager (Pays Rent -> High λ for Rent, Discounts Privacy Loss)
    #    Let's model Manager as having λ=1.0 but PrivacyLoss cost is externalized?
    #    No, let's assume Manager cares about Productivity. Privacy Loss hurts productivity.
    
    # Manager: Wants to cut Rent.
    manager = SpaceBCP(lambda_val=1.0) 
    
    # But wait, who bears the Privacy Cost? The Worker.
    # Manager sees: V = Interaction - λ * Rent
    # Worker sees: V = Interaction - λ * PrivacyLoss
    
    log(f"{ 'LAYOUT':<10} | {'RENT':<5} | {'PRIV':<5} | {'V (Mgr)':<8} | {'V (Work)':<8}")
    log("-" * 60)
    
    for l in layouts:
        # Manager V (Ignores Privacy Loss mostly)
        v_mgr = l['interact'] - 1.0 * l['rent']
        
        # Worker V (Ignores Rent)
        v_work = l['interact'] - 1.0 * l['privacy_loss']
        
        log(f"{l['name']:<10} | {l['rent']:<5} | {l['privacy_loss']:<5} | {v_mgr:<8.1f} | {v_work:<8.1f}")
        
    log("\nFINDING: Managers choose Open Plan (V_mgr > V_offices) to save Rent.")
    log("         Workers hate Open Plan (V_work < V_offices) due to Privacy Cost.")
    log("         Architecture is a Principal-Agent BCP conflict.")
    log("======================================================================")
    log("GATE 1066 COMPLETE: OPEN PLAN IS RENT ARBITRAGE")
    log("======================================================================")

if __name__ == "__main__":
    main()
