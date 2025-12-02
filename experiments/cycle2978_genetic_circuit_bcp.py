import random
import math

# BCP EXPERIMENT: THE GENETIC BUDGET (Phase 270)
# Simulating a Genetic Toggle Switch under Metabolic Scarcity (λ).

# The Model:
# Two proteins, A and B, repress each other.
# Production rate of A = k / (1 + [B]^n)
# Production rate of B = k / (1 + [A]^n)
# However, both require Global Resources (Ribosomes/ATP).
# BCP Constraint:
# Effective_Rate = Nominal_Rate * (1 - λ * Cost)
# If λ is high (Starvation), production drops.

def simulate_toggle_switch(lambda_val, steps=100):
    # Initial State
    a = 0.1
    b = 5.0 # B dominates initially
    
    # Parameters
    k_max = 10.0 # Max production rate
    n = 2.0 # Cooperativity (Hill coefficient)
    degradation = 0.5
    cost_per_unit = 0.1 # Metabolic cost of synthesis
    
    history = []
    
    for t in range(steps):
        # 1. Calculate Nominal Demand (Hill Function)
        demand_a = k_max / (1.0 + b**n)
        demand_b = k_max / (1.0 + a**n)
        
        # 2. Apply BCP Constraint (Metabolic Load)
        # V(synthesis) = Benefit - λ * Cost
        # Here, we model it as a throttle factor: 
        # Rate = Demand * max(0, 1 - λ * Cost)
        
        # Cost is proportional to demand (resource usage)
        # Let's assume λ acts as a global tax on translation efficiency.
        # Efficiency = 1 / (1 + λ * Total_Demand) ? 
        # Or simply: Rate = Demand - λ * Cost? No, rate can't be negative (unless degradation).
        
        # Let's use the BCP Allocation Logic:
        # If V < 0, allocation is 0.
        # V_a = Importance_A - λ * Cost_A
        # V_b = Importance_B - λ * Cost_B
        
        # Importance? Toggle switch doesn't have "importance" unless linked to survival.
        # Let's assume the cell tries to synthesize whatever is promoted.
        # But global resource scarcity reduces effective k_max.
        
        effective_k = k_max / (1.0 + lambda_val * 5.0) # Simple scarcity model
        
        prod_a = effective_k / (1.0 + b**n)
        prod_b = effective_k / (1.0 + a**n)
        
        # 3. Update State
        a = a + prod_a - (degradation * a)
        b = b + prod_b - (degradation * b)
        
        # Clamp
        if a < 0: a = 0
        if b < 0: b = 0
        
        history.append((a, b))
        
    return history

print("--- GENETIC TOGGLE SWITCH UNDER SCARCITY ---")

scenarios = [0.0, 0.5, 2.0, 5.0] # Increasing Lambda

for lam in scenarios:
    hist = simulate_toggle_switch(lam)
    final_a, final_b = hist[-1]
    
    # Check bistability
    # Ideally B dominates (since we started with B=5).
    # If B collapses, the memory is lost.
    
    state = "BISTABLE (Memory Kept)"
    if final_b < 1.0 and final_a < 1.0:
        state = "COLLAPSE (Memory Lost)"
    elif abs(final_a - final_b) < 0.1:
        state = "MONOSTABLE (Ambiguous)"
        
    print(f"λ={lam:<4} | A={final_a:.2f} | B={final_b:.2f} | {state}")

# HYPOTHESIS:
# Low λ: Strong bistability (B dominates).
# High λ: Rate drops below degradation threshold -> Collapse to (0,0). Memory lost.
