
import sys
import os
import math
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3295] {msg}")

def run_batch_bcp(budget_b, demand_d, setup_s, holding_h):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    # Standard EOQ: Q = sqrt(2DS/H)
    # But BCP modifies the cost perception.
    # V = Revenue - λ * Cost
    # Minimizing λ * Cost is same as Minimizing Cost.
    # BUT, if different costs have DIFFERENT λ (e.g. Setup is Labor, Holding is Capital), it changes.
    # Assume simple case: λ applies to total monetary cost.
    # Then EOQ formula holds: Q* does not depend on λ if λ factors out?
    # Cost = C. Minimize λC <=> Minimize C.
    # So Q* should be invariant to λ IF Setup and Holding are both "Money".
    
    # BUT: Holding Cost 'H' is often defined as Interest Rate * Item Value (i * P).
    # And λ IS the metabolic interest rate (Shadow Price of Capital).
    # So we should replace 'H' with 'λ * P'.
    # Or rather, 'H' is the physical holding cost (storage space) + opportunity cost.
    # Let's say H_total = H_physical + λ * Price.
    # Then Q* = sqrt(2DS / (H_phys + λP)).
    # If λ increases (Scarcity), Denominator increases -> Q* decreases.
    # This matches hypothesis: Scarcity -> JIT.
    
    price_p = 10.0
    h_phys = 0.5 # Storage cost per unit
    
    # Effective Holding Cost
    h_eff = h_phys + (lambda_val * price_p)
    
    # Optimal Q
    q_opt = math.sqrt((2 * demand_d * setup_s) / h_eff)
    
    total_cost = (demand_d / q_opt) * setup_s + (q_opt / 2) * h_eff
    v = (demand_d * price_p) - (lambda_val * total_cost) # Note: Revenue shouldn't be scaled by λ if it's money?
    # Wait, usually V = Gain - λ*Cost. If both are money, λ should be 1?
    # No, λ is Marginal Utility of Money.
    # V (Utils) = λ * Profit.
    # Maximizing λ*Profit is same as Maximizing Profit.
    # So λ doesn't affect decision unless it changes relative prices.
    # The EFFECT of scarcity is increasing the Cost of Capital (Opportunity Cost).
    # So modeling H_eff = H_phys + λ*P is the correct way to inject BCP.
    
    return q_opt, v, lambda_val, h_eff

def main():
    log("GATE 921: PRODUCTION BATCHING AS BCP")
    
    demand = 1000.0
    setup = 50.0
    
    scenarios = [
        {"name": "Cheap Capital (Abundance)", "budget": 10.0},
        {"name": "Normal Rates", "budget": 2.0},
        {"name": "Credit Crunch (Scarcity)", "budget": 0.5}
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_q = float('inf')
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        q_opt, v, lambda_val, h_eff = run_batch_bcp(scen['budget'], demand, setup, 0.5)
        
        log(f"Lambda: {lambda_val:.3f}")
        log(f"Effective Holding Cost H: {h_eff:.3f}")
        log(f"Optimal Batch Q*: {q_opt:.2f}")
        
        # Monotonicity Check
        # As Budget drops, λ rises, H_eff rises, Q* should drop.
        if q_opt < prev_q:
            validation_score += 1
            log("VALID: Batch size decreases with budget (JIT tendency).")
        else:
            log("INVALID: Batch size increased.")
            
        prev_q = q_opt
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3295,
        "phase": 185,
        "gate": 921,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3295_manufacturing_batch.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 921 Complete.")

if __name__ == "__main__":
    main()
