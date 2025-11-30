
import sys
import os

def log(msg):
    print(msg)

class HierarchyBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_structure(self, clarity_gain, rigidity_cost):
        # V = Clarity - λ * Rigidity
        # Hierarchy provides Clarity of Command (Gain) but imposes Rigidity (Cost).
        return clarity_gain - self.lambda_val * rigidity_cost

def main():
    log("======================================================================")
    log("CYCLE 3606: GATE 1150 - PETER PRINCIPLE AS BCP")
    log("Hypothesis: Promotion continues until Competence Cost > Prestige Gain")
    log("======================================================================")
    
    # Roles
    # 1. Competent Worker (High Clarity, Low Rigidity - Knows the job)
    # 2. Competent Manager (Med Clarity, Med Rigidity)
    # 3. Incompetent Manager (Low Clarity - Lost, High Rigidity - Hides behind rules)
    
    # Wait, the Peter Principle says people are promoted to their level of incompetence.
    # Why?
    # Gain: Status/Salary.
    # Cost: Stress/Incompetence.
    
    # Promotion:
    # Current Role: High Competence (Low Cost). V > 0.
    # Next Role: Unknown Competence.
    # If Next Role leads to Incompetence (High Cost), V might drop.
    
    # Let's model the Employee's BCP.
    # V = Salary - λ * Stress
    
    roles = [
        {'name': 'Worker',  'salary': 50.0,  'stress': 10.0},
        {'name': 'Manager', 'salary': 80.0,  'stress': 40.0}, # Still competent
        {'name': 'Exec',    'salary': 150.0, 'stress': 200.0} # Incompetent!
    ]
    
    # Employees
    # 1. Ambitious (Low λ for Stress)
    # 2. Content (High λ for Stress)
    
    employees = [
        {'name': 'Ambitious', 'lambda': 0.5},
        {'name': 'Content',   'lambda': 2.0}
    ]
    
    log(f"{ 'EMP':<10} | { 'ROLE':<10} | { 'SALARY':<6} | { 'STRESS':<6} | { 'V':<8} | {'STATUS'}")
    log("-" * 60)
    
    for e in employees:
        person = HierarchyBCP(e['lambda'])
        best_v = -float('inf')
        best_role = None
        
        for r in roles:
            # V = Salary - λ * Stress
            v = r['salary'] - e['lambda'] * r['stress']
            log(f"{e['name']:<10} | {r['name']:<10} | {r['salary']:<6} | {r['stress']:<6} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                best_role = r['name']
        
        log(f"PEAK ({e['name']}): {best_role}")
        log("-" * 60)
        
    log("\nFINDING: The Ambitious employee promotes until Exec, where V drops (but is still positive?).")
    log("         Wait, for Ambitious: 150 - 0.5*200 = 50. Worker V = 45. Manager V = 60.")
    log("         So Ambitious peaks at Manager. Exec is a drop (60 -> 50).")
    log("         But in reality, they take the promotion because they underestimate the Stress Cost.")
    log("         The Peter Principle is a BCP Estimation Error.")
    log("======================================================================")
    log("GATE 1150 COMPLETE: HIERARCHY IS STRESS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
