
import sys
import os
import math
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3292] {msg}")

def run_safety_bcp(budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    # Speed vs Risk model
    # Speed S in [0, 10]
    # Gain = S
    # Risk Cost = e^(0.5 * S)  (Exponential risk with speed)
    
    best_s = 0
    best_v = -float('inf')
    
    for s in range(0, 11):
        risk = math.exp(0.5 * s)
        v = s - (lambda_val * risk)
        
        if v > best_v:
            best_v = v
            best_s = s
            
    return best_s, best_v, lambda_val

def main():
    log("GATE 919: SAFETY VS SPEED AS BCP")
    
    # Note: Here Budget B represents "Safety Budget" or "Slack".
    # High B = Low Pressure -> Can afford to go slow? 
    # Wait. If B is high (Abundance), λ is low.
    # V = Speed - λ * Risk.
    # If λ is low, Risk is cheap. So Speed should be HIGH?
    # This implies Rich projects go FASTER safely?
    # Or does "Risk Cost" include the catastrophic loss?
    # If Risk Cost is huge (Loss of Life), then λ scales it. 
    
    # Alternative Interpretation:
    # V = Completion - λ * (Time + Risk)
    # Let's stick to the simple tradeoff:
    # We want Speed (Gain). We pay Risk (Cost).
    # If we are Desperate (High λ), do we take MORE risk?
    # Standard BCP: High λ -> Avoid Cost.
    # If Risk is Cost, High λ -> Avoid Risk -> Go Slow.
    # This contradicts "Cutting corners".
    
    # CORRECTION:
    # Cutting corners happens when Speed is NECESSARY (High Gain) and Budget is Low.
    # The "Gain" of Speed increases under Deadline Pressure.
    # Let's model Deadline Pressure explicitly.
    # V = P(Deadline) * Bonus - λ * Risk.
    # P(Deadline) increases with Speed.
    
    # Let's simulate "Pressure" directly as the Gain multiplier for Speed.
    # Pressure P.
    # V = P * Speed - λ(Safety_Budget) * Risk.
    
    # Scenario 1: Normal. P=1. B=10 (λ=0.1).
    # Scenario 2: Deadline Crisis. P=10. B=10 (λ=0.1). -> Speed UP.
    # Scenario 3: Budget Crisis. P=1. B=0.1 (λ=5). -> Speed DOWN (Cant afford risk).
    
    # "Cutting Corners" usually means: Reducing Cost at expense of Safety.
    # Cost = Base + Safety_Measure.
    # V = Value - λ * (Base + Safety).
    # If λ is high, we minimize Safety Cost.
    # Risk is a probabilistic future cost.
    # V = Value - λ * (Current_Cost + Prob * Future_Cost).
    # Under high λ, IMMEDIATE cost savings (cutting safety) might outweigh FUTURE risk if discount rate is high.
    # But BCP λ applies to both.
    
    # Let's stick to the "Speed vs Risk" model defined in `run_safety_bcp`.
    # V = Speed - λ * Risk.
    # High B (Low λ): Speed dominates. High Speed.
    # Low B (High λ): Risk penalty dominates. Low Speed.
    
    # Does this match reality?
    # Rich projects (SpaceX) move fast and break things? Yes.
    # Poor projects cannot afford to break things? Yes.
    # EXCEPT when "Desperation" sets in (Gambling for resurrection).
    # That requires a non-linear utility function (Prospect Theory).
    # Standard BCP is risk-averse under scarcity.
    
    scenarios = [
        {"name": "Well-Funded", "budget": 10.0}, # Expect High Speed
        {"name": "Average", "budget": 2.0},      # Expect Med Speed
        {"name": "Precarious", "budget": 0.1}    # Expect Low Speed
    ]
    
    validation_score = 0
    total_checks = 0
    
    prev_s = -1
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        s_opt, v, lambda_val = run_safety_bcp(scen['budget'])
        log(f"Lambda: {lambda_val:.3f}")
        log(f"Optimal Speed: {s_opt}")
        
        # Monotonicity Check
        # As B drops, Speed should drop (Risk Aversion increases).
        if prev_s == -1:
            pass
        elif s_opt <= prev_s:
            validation_score += 1
            log("VALID: Speed decreased/maintained as budget tightened.")
        else:
            log("INVALID: Speed increased under scarcity.")
            
        prev_s = s_opt
        total_checks += 1 # Count checks after first

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks-1}") # First one doesn't count
    
    # Output results
    output = {
        "cycle": 3292,
        "phase": 184,
        "gate": 919,
        "validation": float(validation_score)/(total_checks-1) if total_checks > 1 else 0
    }
    
    with open("data/results/cycle3292_safety_bcp.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 919 Complete.")

if __name__ == "__main__":
    main()
