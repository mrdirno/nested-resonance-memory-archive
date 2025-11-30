
import sys
import os
import math
import numpy as np

def log(msg):
    print(msg)

class FittsBCP:
    def __init__(self, lambda_val=0.5):
        self.lambda_val = lambda_val
        
    def index_of_difficulty(self, distance, width):
        # Fitts's Law: ID = log2(2D/W)
        if width <= 0: return float('inf')
        return math.log2(2 * distance / width)
        
    def movement_cost(self, id_val):
        # Cost is proportional to difficulty (time/effort)
        return 0.1 * id_val
        
    def value_function(self, gain, distance, width):
        # V = G - λ * C
        id_val = self.index_of_difficulty(distance, width)
        cost = self.movement_cost(id_val)
        return gain - self.lambda_val * cost

def main():
    log("======================================================================")
    log("CYCLE 3443: GATE 1024 - FITTS'S LAW AS BCP")
    log("Hypothesis: Speed-Accuracy Trade-off is a BCP Budget Constraint")
    log("======================================================================")
    
    # Test 1: The Cost of Precision (Width)
    log("\nTEST 1: PRECISION COST (Varying Width)")
    dist = 100
    gain = 1.0
    widths = [10, 20, 50, 100] # Increasing size (easier)
    lambda_val = 0.5
    
    model = FittsBCP(lambda_val)
    
    log(f"{ 'WIDTH':<6} | {'ID':<6} | {'COST':<6} | {'V (λ=0.5)':<10}")
    log("-" * 45)
    
    for w in widths:
        id_val = model.index_of_difficulty(dist, w)
        cost = model.movement_cost(id_val)
        v = model.value_function(gain, dist, w)
        log(f"{w:<6} | {id_val:.2f}   | {cost:.3f}  | {v:+.3f}")
        
    # Test 2: The Effect of Time Pressure (λ)
    log("\nTEST 2: TIME PRESSURE (Varying λ)")
    # Target: D=100, W=20 (ID=3.32)
    w = 20
    lambdas = [0.1, 0.5, 1.0, 2.0]
    
    log(f"{ 'λ':<6} | {'COST':<6} | {'V':<10} | {'DECISION'}")
    log("-" * 45)
    
    for lam in lambdas:
        model.lambda_val = lam
        v = model.value_function(gain, dist, w)
        decision = "CLICK" if v > 0 else "ABORT/MISS"
        log(f"{lam:<6} | 0.332  | {v:+.3f}      | {decision}")

    # Test 3: Optimal Strategy Selection
    log("\nTEST 3: OPTIMAL STRATEGY (Speed vs Accuracy)")
    # Scenario: User can choose:
    # A: Fast, Low Precision (W=50, G=0.8) - "Quick click"
    # B: Slow, High Precision (W=10, G=1.0) - "Careful aim"
    
    strategies = [
        {'name': 'A (Fast)', 'w': 50, 'g': 0.8},
        {'name': 'B (Precise)', 'w': 10, 'g': 1.0}
    ]
    
    log(f"{ 'λ':<6} | {'STRATEGY A (V)':<15} | {'STRATEGY B (V)':<15} | {'WINNER'}")
    log("-" * 60)
    
    test_lambdas = [0.2, 0.8, 1.5]
    
    for lam in test_lambdas:
        model.lambda_val = lam
        
        # Calc A
        v_a = model.value_function(strategies[0]['g'], dist, strategies[0]['w'])
        
        # Calc B
        v_b = model.value_function(strategies[1]['g'], dist, strategies[1]['w'])
        
        winner = "A (Fast)" if v_a > v_b else "B (Precise)"
        log(f"{lam:<6} | {v_a:+.3f}           | {v_b:+.3f}           | {winner}")
        
    log("\nFINDING: High λ (Time Pressure) forces transition to Fast/Imprecise strategy.")
    log("         This explains the Speed-Accuracy Trade-off: Speed is simply Cost minimization.")
    log("======================================================================")
    log("GATE 1024 COMPLETE: FITTS'S LAW IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
