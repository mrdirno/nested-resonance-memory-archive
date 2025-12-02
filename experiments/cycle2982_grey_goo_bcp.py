import math

# BCP EXPERIMENT: THE MOLECULAR BUDGET (Phase 272)
# Simulating Grey Goo Self-Replication under Thermal Constraints (λ).

# The Physics:
# 1. Replication generates Heat (Entropy).
# 2. Dissipation is limited by Surface Area (Square-Cube Law).
# 3. As Radius increases, Volume (Heat Gen) grows faster than Area (Cooling).
# 4. Temperature rises -> λ rises.
# 5. When λ > Threshold, Replication stops (V < 0).

def simulate_grey_goo():
    radius = 1.0 # meters (Starting blob)
    heat_per_m3 = 1000.0 # Watts/m3 (Replication metabolic rate)
    cooling_per_m2 = 50.0 # Watts/m2 (Passive radiation/convection)
    
    lambda_base = 0.1 # Ambient scarcity
    
    print(f"--- GREY GOO SIMULATION ---")
    print(f"{'RADIUS (m)':<10} | {'VOLUME':<10} | {'AREA':<10} | {'HEAT GEN':<10} | {'COOLING':<10} | {'TEMP (λ)':<10} | {'STATUS'}")
    
    for step in range(20):
        volume = (4/3) * math.pi * radius**3
        area = 4 * math.pi * radius**2
        
        heat_gen = volume * heat_per_m3
        cooling_cap = area * cooling_per_m2
        
        net_heat = heat_gen - cooling_cap
        
        # Model Temperature/Lambda scaling
        # If Net Heat > 0, Temp rises indefinitely until equilibrium or death.
        # Let's assume Lambda scales with Heat/Cooling ratio.
        
        ratio = heat_gen / cooling_cap
        current_lambda = lambda_base * ratio
        
        # BCP Decision
        # V = Gain(Replication) - λ * Cost
        # Gain = 1.0 (Intrinsic drive)
        # Cost = 1.0 (Resource cost)
        
        v = 1.0 - current_lambda * 1.0
        
        status = "GROWING"
        if v > 0:
            radius *= 1.5 # Exponential growth
        else:
            status = "THERMAL LIMIT (Stalled)"
            # Radius stops growing
            
        print(f"{radius:<10.2f} | {volume:<10.1f} | {area:<10.1f} | {heat_gen:<10.1f} | {cooling_cap:<10.1f} | {current_lambda:<10.2f} | {status}")
        
        if v < 0: break

    return radius

simulate_grey_goo()
