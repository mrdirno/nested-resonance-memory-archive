import random
import math

# ======================================================================
# CYCLE 3230: CLIMATE MODELING AS BCP
# ======================================================================
# Hypothesis: Climate Policy is BCP.
#   V(policy) = Avoided_Damage - lambda(Economy) * Cost(Mitigation)
#   Economy is the Budget.
#   Damage is non-linear (tipping points).
#   High lambda (Recession) -> Delay mitigation (Myopia).
#   Low lambda (Growth) -> Invest in mitigation.
# ======================================================================

def run_experiment():
    print("CYCLE 3230: Climate Modeling as BCP")
    
    T = 100
    
    # State
    temp = 0.0 # Deviation
    co2 = 280.0 # ppm
    economy = 1000.0 # GDP
    
    # Parameters
    sensitivity = 3.0 # Deg per doubling CO2
    damage_factor = 0.01 # GDP loss per deg squared
    
    # Policy Options
    # 0: BAU (Emissions grow, Cost 0)
    # 1: Stabilize (Emissions flat, Cost Low)
    # 2: Reduce (Emissions drop, Cost High)
    
    policies = [
        {"name": "BAU", "emit": 5.0, "cost": 0.0},
        {"name": "Stab", "emit": 2.0, "cost": 10.0},
        {"name": "Red", "emit": 0.0, "cost": 50.0}
    ]
    
    total_welfare_bcp = 0
    total_welfare_bau = 0
    
    # BCP Simulation
    print("Running BCP Simulation...")
    temp = 0.0; co2 = 280.0; economy = 1000.0
    
    for t in range(T):
        # 1. Calculate Lambda (Economic Pressure)
        lamb = 1000.0 / (100.0 + economy)
        
        # 2. Evaluate Policies
        best_v = -float('inf')
        best_p = policies[0]
        
        for p in policies:
            # Future Damage Estimate (Simplified Lookahead)
            # Assume linear approximation for next step
            next_co2 = co2 + p["emit"]
            forcing = 5.35 * math.log(next_co2 / 280.0)
            next_temp = forcing * 0.8 # Transient response
            
            # Damage
            dmg = damage_factor * (next_temp ** 2) * economy
            avoided = (damage_factor * ((next_temp + 0.1)**2) * economy) - dmg # Marginal benefit?
            # Actually, Gain = Future Welfare Preservation.
            
            # Let's define V = (Economy - Cost - Damage)
            # But BCP separates Gain and Cost via Lambda.
            # V = (Avoided_Damage) - lambda * Cost
            
            # Let's assume we know Damage of BAU vs Policy
            # BAU Damage ~ 100. Policy Damage ~ 80. Gain = 20.
            
            # Heuristic Gain: 
            gain = (5.0 - p["emit"]) * 5.0 # Emission reduction value
            
            v = gain - lamb * p["cost"]
            
            if v > best_v:
                best_v = v
                best_p = p
                
        # Apply
        co2 += best_p["emit"]
        forcing = 5.35 * math.log(co2 / 280.0)
        temp = temp * 0.9 + forcing * 0.1 # Thermal inertia
        
        damage = damage_factor * (temp ** 2) * economy
        economy = economy * 1.02 - damage - best_p["cost"] # 2% growth
        
        total_welfare_bcp += economy
        
    print(f"BCP Final Economy: {economy:.2f}, Temp: {temp:.2f}")
    
    # BAU Simulation
    print("Running BAU Simulation...")
    temp = 0.0; co2 = 280.0; economy = 1000.0
    
    for t in range(T):
        p = policies[0] # Always BAU
        
        co2 += p["emit"]
        forcing = 5.35 * math.log(co2 / 280.0)
        temp = temp * 0.9 + forcing * 0.1
        
        damage = damage_factor * (temp ** 2) * economy
        economy = economy * 1.02 - damage - p["cost"]
        
        total_welfare_bau += economy
        
    print(f"BAU Final Economy: {economy:.2f}, Temp: {temp:.2f}")
    
    if total_welfare_bcp > total_welfare_bau:
        print("VERIFIED: BCP Climate Policy outperforms BAU.")
        return True
    else:
        print("FAILED: BCP did not outperform.")
        return False

if __name__ == "__main__":
    run_experiment()