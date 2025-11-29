
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3300] {msg}")

class Content:
    def __init__(self, name, reward, duration):
        self.name = name
        self.reward = reward
        self.duration = duration
        
    def __repr__(self):
        return f"{self.name}(R={self.reward}, D={self.duration})"

def run_content_bcp(contents, time_budget_b):
    k = 1.0
    epsilon = 0.1
    lambda_val = k / (epsilon + time_budget_b)
    
    results = []
    for c in contents:
        # V = Reward - λ * Duration
        # Reward is Dopamine units. Duration is Minutes.
        # We need to scale them. Assume 1 min cost ~ 1 unit if λ=1.
        
        # Constraint: If Duration > Budget, V = -Infinity (Can't watch a 2hr movie in 5 mins)
        if c.duration > time_budget_b:
            v = -999.0
        else:
            v = c.reward - (lambda_val * c.duration)
            
        results.append({
            "content": c.name,
            "v": v,
            "reward": c.reward,
            "duration": c.duration
        })
    
    results.sort(key=lambda x: x['v'], reverse=True)
    return results, lambda_val

def main():
    log("GATE 925: CONTENT FORMAT AS BCP")
    
    # Content Types
    # Movie: High Reward (100), High Cost (120 min)
    # Episode: Med Reward (40), Med Cost (45 min)
    # Short: Low Reward (5), Low Cost (1 min)
    
    contents = [
        Content("Movie (Cinema)", 100.0, 120.0),
        Content("TV Episode", 40.0, 45.0),
        Content("Short/Reel", 5.0, 1.0)
    ]
    
    # Scenarios
    scenarios = [
        {"name": "Weekend Evening (Leisure)", "budget": 180.0}, # 3 hours
        {"name": "Lunch Break (Constrained)", "budget": 30.0},  # 30 mins
        {"name": "Micro-Break (Fragmented)", "budget": 5.0}     # 5 mins
    ]
    
    validation_score = 0
    total_checks = 0
    
    for scen in scenarios:
        log(f"\n--- Scenario: {scen['name']} (B={scen['budget']}) ---")
        results, lambda_val = run_content_bcp(contents, scen['budget'])
        log(f"Lambda: {lambda_val:.3f}")
        
        best = results[0]
        log(f"Selected: {best['content']} (V={best['v']:.2f})")
        
        if scen['name'] == "Weekend Evening (Leisure)":
            # B=180 -> λ=0.005
            # Movie V = 100 - 0.6 = 99.4
            # TV V = 40 - 0.2 = 39.8
            # Short V = 5 - 0.005 = 4.99
            # Movie wins.
            if best['content'] == "Movie (Cinema)":
                validation_score += 1
                log("VALID: Leisure allows deep engagement.")
            else:
                log(f"INVALID: Expected Movie, got {best['content']}")
                
        elif scen['name'] == "Lunch Break (Constrained)":
            # B=30 -> λ=0.033
            # Movie V = -999 (Too long)
            # TV V = -999 (Too long) -> 45 > 30
            # Short V = 5 - 0.033 = 4.96
            # Wait, TV is 45 min. Budget 30. Hard Constraint kills it.
            # What if we had a "Sitcom" (20 min)?
            # Let's assume user can watch 30 shorts?
            # Or just 1 short?
            # The model selects ONE item.
            # Short wins by default constraint.
            if best['content'] == "Short/Reel":
                validation_score += 1
                log("VALID: Constraints force short form.")
            else:
                log(f"INVALID: Expected Short, got {best['content']}")
                
        elif scen['name'] == "Micro-Break (Fragmented)":
            # B=5 -> λ=0.19
            # Movie/TV impossible.
            # Short V = 5 - 0.19 = 4.8
            if best['content'] == "Short/Reel":
                validation_score += 1
                log("VALID: Fragmentation enables micro-content.")
            else:
                 log(f"INVALID: Expected Short, got {best['content']}")
                 
        total_checks += 1

    log("\nValidation Summary:")
    log(f"Tests Passed: {validation_score}/{total_checks}")
    
    # Output results
    output = {
        "cycle": 3300,
        "phase": 186,
        "gate": 925,
        "validation": float(validation_score)/total_checks if total_checks else 0
    }
    
    with open("data/results/cycle3300_content_format.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 925 Complete.")

if __name__ == "__main__":
    main()
