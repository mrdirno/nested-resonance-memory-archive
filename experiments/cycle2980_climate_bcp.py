import random
import math

# BCP EXPERIMENT: THE PLANETARY BUDGET (Phase 271)
# Simulating Climate Strategy Selection under Urgency (λ).

# Strategies:
# 1. REDUCTION: Cut emissions. High Transition Cost, Slow Effect. Gain = Long-term Stability.
# 2. CDR (Removal): Suck carbon. High Energy Cost, Medium Effect. Gain = Reversibility.
# 3. SRM (Solar Radiation Management): Dim sun. Low Money Cost, High Risk Cost, Instant Effect. Gain = Survival.

def simulate_climate_triage(urgency_lambda):
    # Strategies
    strategies = [
        {"name": "REDUCTION", "base_gain": 10.0, "base_cost": 5.0, "risk": 0.1},
        {"name": "CDR",       "base_gain": 8.0,  "base_cost": 8.0, "risk": 0.2},
        {"name": "SRM",       "base_gain": 5.0,  "base_cost": 1.0, "risk": 5.0} # Cheap but risky
    ]
    
    print(f"--- CLIMATE TRIAGE (Urgency λ={urgency_lambda:.2f}) ---")
    
    best_v = -999
    winner = None
    
    for s in strategies:
        # V = Gain - λ * (Cost + Risk)
        # Wait, High λ usually means Scarcity of Resources.
        # Here, High λ means URGENCY / CRISIS.
        # "The Budget of Time is low".
        # Or "The Tolerance for Cost is low"?
        
        # In BCP, High λ means "Cost is Expensive".
        # If we are in Crisis, Time is the scarce resource.
        # Let's model Cost as (Monetary + Temporal).
        
        # Reduction: High Temporal Cost.
        # SRM: Low Temporal Cost.
        
        # If λ represents "Pressure", then High λ makes "Expensive things" unviable.
        # If Time is the budget, Reduction is "Time-Expensive".
        
        # Let's define Cost = Time_Cost + Money_Cost
        # Reduction: Time=10, Money=5. Total=15
        # SRM: Time=1, Money=1. Total=2. (But Risk is high)
        
        # Is Risk a cost? Yes.
        # V = Gain - λ * Total_Cost
        
        # Mapping:
        # Reduction: Slow (High Cost). Safe (Low Risk).
        # SRM: Fast (Low Cost). Dangerous (High Risk).
        
        cost_time = 0
        if s["name"] == "REDUCTION": cost_time = 10.0
        if s["name"] == "CDR":       cost_time = 5.0
        if s["name"] == "SRM":       cost_time = 0.5
        
        cost_money = s["base_cost"]
        cost_risk = s["risk"]
        
        # Urgency λ scales Time Cost massively.
        # Resource Scarcity λ scales Money Cost.
        
        # Let's assume λ is "Global Stress" aggregating both.
        # But specifically Urgency favors Speed.
        
        # Let's use standard BCP:
        # V = Gain - λ * Cost
        # Where Cost = Time. (We assume Money is secondary in survival).
        
        # Or better:
        # V = Gain - λ * (Time_Cost) - (Risk * Risk_Aversion)
        # In Crisis, we ignore Risk? No, usually High λ makes us risk-averse?
        # Actually, "Desperate times call for desperate measures".
        # Prospect Theory: In domain of losses, we become Risk Seeking.
        # So High λ might REDUCE the penalty of Risk.
        
        # Let's try:
        # V = Gain - λ * Time_Cost - (1/λ) * Risk
        # As λ increases (Urgency), Time becomes expensive, but Risk becomes cheap (Hail Mary).
        
        if urgency_lambda < 0.1: urgency_lambda = 0.1 # Avoid div by zero
        
        v = s["base_gain"] - (urgency_lambda * cost_time) - ((1.0/urgency_lambda) * cost_risk)
        
        print(f"{s['name']:<10} | Time={cost_time:<4} | Risk={cost_risk:<4} | V={v:.2f}")
        
        if v > best_v:
            best_v = v
            winner = s
            
    print(f"WINNER: {winner['name']}")
    return winner['name']

# Scenarios
simulate_climate_triage(0.5) # Stable (Low Urgency)
simulate_climate_triage(1.0) # Concern
simulate_climate_triage(5.0) # Crisis (High Urgency)
simulate_climate_triage(20.0) # Collapse (Extreme Urgency)
