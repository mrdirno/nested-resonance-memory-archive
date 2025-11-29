
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3290] {msg}")

class Schedule:
    def __init__(self, name, duration, cost):
        self.name = name
        self.duration = duration
        self.cost = cost
        
    def __repr__(self):
        return f"{self.name}(D={self.duration}, C={self.cost})"

def run_schedule_bcp(schedules, budget_b, late_penalty_per_day, target_days):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + budget_b)
    
    results = []
    for s in schedules:
        # Calculate Late Penalty
        lateness = max(0, s.duration - target_days)
        penalty = lateness * late_penalty_per_day
        
        # V = (BaseValue - Penalty) - λ * Cost
        # Assume BaseValue is constant, so we maximize -(Penalty + λ*Cost)
        # Or minimize Penalty + λ*Cost
        
        score = -(penalty + (lambda_val * s.cost))
        
        results.append({
            "schedule": s.name,
            "v": score,
            "duration": s.duration,
            "cost": s.cost,
            "penalty": penalty
        })
    
    results.sort(key=lambda x: x['v'], reverse=True)
    return results, lambda_val

def main():
    log("GATE 917: CONSTRUCTION SCHEDULING AS BCP")
    
    # Schedules
    # Standard: 100 days, Cost 100
    # Crashed: 60 days, Cost 200 (Double cost for speed)
    # Slow: 150 days, Cost 80 (Cheap but slow)
    schedules = [
        Schedule("Standard", 100, 100.0),
        Schedule("Crashed (Fast)", 60, 200.0),
        Schedule("Slow (Cheap)", 150, 80.0)
    ]
    
    target_days = 80
    late_penalty = 5.0 # Per day late
    
    # Penalties:
    # Standard (100): 20 days late * 5 = 100 penalty. Total Cost equivalent = 100 + λ100
    # Crashed (60): 0 days late. Penalty 0. Total Cost = 0 + λ200
    # Slow (150): 70 days late * 5 = 350 penalty. Total Cost = 350 + λ80
    
    # Comparison:
    # Standard: -100 - 100λ
    # Crashed: -200λ
    # Slow: -350 - 80λ
    
    # Crashed vs Standard: -200λ > -100 - 100λ => 100 > 100λ => λ < 1.0.
    # If λ < 1.0 (Abundance), Crash the schedule (Speed wins).
    # If λ > 1.0 (Scarcity), Standard wins (Cost wins).
    
    # Standard vs Slow: -100 - 100λ > -350 - 80λ => 250 > 20λ => λ < 12.5.
    # Slow only wins if λ > 12.5 (Extreme scarcity).
    
    scenarios = [
        {"name": "Well-Funded Project", "budget": 10.0}, # Expect Crashed
        {"name": "Tight Budget", "budget": 0.5},         # Expect Standard
        {"name": "Bankruptcy Imminent", "budget": 0.05}  # Expect Standard (Wait, λ=6.6, < 12.5)
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        results, lambda_val = run_schedule_bcp(schedules, scen['budget'], late_penalty, target_days)
        log(f"Lambda: {lambda_val:.3f}")
        
        best = results[0]
        log(f"Selected: {best['schedule']} (V={best['v']:.3f})")
        
        if scen['name'] == "Well-Funded Project":
            if best['schedule'] == "Crashed (Fast)":
                validation_score += 1
                log("VALID: Abundance favors Speed (Time is Money).")
            else:
                log(f"INVALID: Expected Crashed, got {best['schedule']}")
                
        elif scen['name'] == "Tight Budget":
            # B=0.5 -> λ=1.66
            # Crashed: -333
            # Standard: -100 - 166 = -266. Standard wins.
            if best['schedule'] == "Standard":
                validation_score += 1
                log("VALID: Scarcity favors Cost efficiency over Speed.")
            else:
                log(f"INVALID: Expected Standard, got {best['schedule']}")

        elif scen['name'] == "Bankruptcy Imminent":
            # B=0.05 -> λ=6.66
            # Crashed: -1333
            # Standard: -100 - 666 = -766
            # Slow: -350 - 533 = -883
            # Standard still wins. Slow only wins if Penalty is ignored?
            # Or if Penalty < λ*Savings.
            # Savings 20. λ=6.66. Value = 133. Penalty diff = 250.
            # Yeah, Standard is robust.
            if best['schedule'] == "Standard":
                validation_score += 1
                log("VALID: Standard remains optimal.")
            else:
                 log(f"INVALID: Expected Standard, got {best['schedule']}")
                 
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3290,
        "phase": 184,
        "gate": 917,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3290_construction_schedule.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 917 Complete.")

if __name__ == "__main__":
    main()
