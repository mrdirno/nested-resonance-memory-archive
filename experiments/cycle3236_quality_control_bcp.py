import random

# ======================================================================
# CYCLE 3236: QUALITY CONTROL AS BCP
# ======================================================================
# Hypothesis: Sensor calibration is BCP.
#   V(cal) = Error_Reduction - lambda * Cost
#   High lambda -> Tolerate drift.
# ======================================================================

def run_experiment():
    print("CYCLE 3236: Quality Control as BCP")
    
    N = 100 # Sensors
    sensors = []
    for _ in range(N):
        sensors.append({
            "Drift": random.uniform(0, 10), # Current Error
            "Importance": random.uniform(1, 10),
            "Cost": random.uniform(1, 5)
        })
        
    budget = 100
    
    # BCP Strategy
    lamb = 100.0 / (10.0 + budget)
    
    for s in sensors:
        # Gain = Error Reduction (Drift * Importance)
        s["score"] = (s["Drift"] * s["Importance"]) - lamb * s["Cost"]
        
    sensors.sort(key=lambda x: x["score"], reverse=True)
    
    spent = 0
    error_removed_bcp = 0
    
    for s in sensors:
        if s["score"] > 0 and spent + s["Cost"] <= budget:
            spent += s["Cost"]
            error_removed_bcp += s["Drift"] * s["Importance"]
            
    print(f"BCP Error Removed: {error_removed_bcp:.2f}")
    
    # Periodic (Random)
    random.shuffle(sensors)
    spent_p = 0
    error_removed_p = 0
    
    for s in sensors:
        if spent_p + s["Cost"] <= budget:
            spent_p += s["Cost"]
            error_removed_p += s["Drift"] * s["Importance"]
            
    print(f"Periodic Error Removed: {error_removed_p:.2f}")
    
    if error_removed_bcp > error_removed_p:
        print("VERIFIED: BCP Quality Control outperforms Periodic.")
        return True
    else:
        print("FAILED.")
        return False

if __name__ == "__main__":
    run_experiment()