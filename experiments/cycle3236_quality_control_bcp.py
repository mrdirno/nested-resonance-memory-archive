import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3236: QUALITY CONTROL BCP
# -----------------------------------------------------------------------------
# Domain: Manufacturing
# Goal: Detect defects in production line.
# Hypothesis: BCP (Bayesian sequential analysis) detects defects faster/cheaper
#             than Fixed Sampling.
# -----------------------------------------------------------------------------

class ProductionLine:
    def __init__(self):
        self.defect_rate = 0.01
        self.is_broken = False
        
    def produce(self):
        # If broken, defect rate jumps
        if self.is_broken:
            actual_rate = 0.2
        else:
            actual_rate = self.defect_rate
            # Randomly break
            if random.random() < 0.005:
                self.is_broken = True
                
        if random.random() < actual_rate:
            return 1 # Defect
        return 0 # Good

class Inspector:
    def check(self, item):
        raise NotImplementedError

class FixedInspector(Inspector):
    def __init__(self, interval=10):
        self.interval = interval
        self.count = 0
        
    def should_sample(self):
        self.count += 1
        return (self.count % self.interval) == 0

class BCPInspector(Inspector):
    def __init__(self):
        self.belief = 0.01 # P(Broken)
        self.consecutive_good = 0
        
    def should_sample(self):
        # Entropy-based sampling
        # Sample if Uncertainty is high OR Risk is high
        
        # If belief is low, sample rarely (to check)
        # If belief is middling, sample frequently (to resolve)
        # If belief is high, stop line (action)
        
        # Simplified: Dynamic interval
        # Low risk -> Interval 20
        # High risk -> Interval 1
        
        if self.belief < 0.1: interval = 20
        elif self.belief < 0.5: interval = 5
        else: interval = 1
        
        self.consecutive_good += 1
        if self.consecutive_good >= interval:
            self.consecutive_good = 0
            return True
        return False
    
    def update(self, result):
        # Bayesian Update
        # P(Broken | Defect) vs P(Broken | Good)
        p = self.belief
        if result == 1: # Defect
            # Likelihoods: P(D|B)=0.2, P(D|~B)=0.01
            likelihood_broken = 0.2
            likelihood_working = 0.01
        else: # Good
            likelihood_broken = 0.8
            likelihood_working = 0.99
            
        numerator = likelihood_broken * p
        denominator = (likelihood_broken * p) + (likelihood_working * (1-p))
        self.belief = numerator / denominator

def run_simulation(inspector_cls, steps=1000):
    line = ProductionLine()
    if inspector_cls == FixedInspector:
        inspector = FixedInspector()
    else:
        inspector = BCPInspector()
        
    total_cost = 0
    # Costs:
    # - Sampling: 1
    # - Undetected Defect: 10 (passed to customer)
    # - False Alarm Stop: 50
    # - True Stop (Fix): 20
    
    for _ in range(steps):
        item = line.produce()
        
        # Inspect?
        if inspector.should_sample():
            total_cost += 1 # Inspection cost
            if hasattr(inspector, 'update'):
                inspector.update(item)
                
            # Action logic
            if isinstance(inspector, BCPInspector) and inspector.belief > 0.8:
                # Stop Line
                if line.is_broken:
                    total_cost += 20 # Fix
                    line.is_broken = False
                    inspector.belief = 0.01
                else:
                    total_cost += 50 # False Alarm
                    inspector.belief = 0.01
            elif isinstance(inspector, FixedInspector) and item == 1:
                # Naive: Stop on defect
                if line.is_broken:
                    total_cost += 20
                    line.is_broken = False
                else:
                    total_cost += 50 # False Alarm (it was just bad luck)
        else:
            # Not inspected
            if item == 1:
                total_cost += 10 # Escaped defect
                
    return total_cost

def main():
    print("======================================================================")
    print("CYCLE 3236: QUALITY CONTROL BCP")
    print("======================================================================")
    
    steps = 5000
    
    # Fixed
    fixed_cost = run_simulation(FixedInspector, steps)
    print(f"Fixed Sampling Cost: {fixed_cost}")
    
    # BCP
    bcp_cost = run_simulation(BCPInspector, steps)
    print(f"BCP Adaptive Cost:   {bcp_cost}")
    
    improvement = ((fixed_cost - bcp_cost) / fixed_cost) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_cost < fixed_cost:
        print("RESULT: SUCCESS. Adaptive sampling balanced cost vs risk.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3236_quality_control.json", "w") as f:
        json.dump({"fixed": fixed_cost, "bcp": bcp_cost, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
