import random

# ======================================================================
# CYCLE 3222: FLEET DISPATCH AS BCP
# ======================================================================
# Hypothesis: Dispatch timing is a BCP decision.
#   V(dispatch) = Value(Speed) - lambda(Fuel_Budget) * Cost(Trip)
#   Consolidating loads reduces Cost per Parcel.
#   Delaying reduces Value (Speed).
#   BCP finds the optimal batch size.
# ======================================================================

def run_experiment():
    print("CYCLE 3222: Fleet Dispatch as BCP")
    
    # Parameters
    T = 100
    arrival_rate = 2 # parcels per tick
    trip_cost = 100.0
    value_per_tick = 1.0 # Value decay per tick delayed
    
    # Scenarios
    budgets = [1000, 10000] # Tight vs Loose Fuel
    
    results = {}
    
    for B in budgets:
        lamb = 1000.0 / (10.0 + B)
        
        queue = []
        total_value_loss = 0
        total_fuel_cost = 0
        trips = 0
        
        for t in range(T):
            # Arrivals
            for _ in range(arrival_rate):
                queue.append(t) # Arrival time
                
            # BCP Decision: Dispatch Now?
            if not queue: continue
            
            # Option A: Wait (Cost=0, but Value Loss increases next tick)
            # Option B: Dispatch (Cost=Trip_Cost, Value Loss stops)
            
            # Gain of Dispatching = Avoiding future delay cost
            # Future Delay Cost ~ N_in_queue * Value_Per_Tick * Avg_Wait_Time?
            # Let's just say Gain = Cleared Utility.
            
            # V(dispatch) = (N_queue * Urgent_Factor) - lambda * Trip_Cost
            # Urgent_Factor increases as queue ages?
            
            urgency = sum([(t - arr) for arr in queue]) # Total wait time accumulated
            
            # V = Urgency - lambda * Trip_Cost
            v = urgency - lamb * trip_cost
            
            if v > 0:
                # Dispatch!
                trips += 1
                total_fuel_cost += trip_cost
                # Calculate final delay for these items
                for arr in queue:
                    total_value_loss += (t - arr)
                queue = []
                
        # Flush remaining
        if queue:
            trips += 1
            total_fuel_cost += trip_cost
            for arr in queue:
                total_value_loss += (T - arr)
                
        avg_wait = total_value_loss / (T * arrival_rate)
        avg_load = (T * arrival_rate) / trips
        
        results[B] = {"trips": trips, "avg_wait": avg_wait, "avg_load": avg_load}
        print(f"Budget {B}: {trips} Trips, Avg Wait {avg_wait:.2f}, Avg Load {avg_load:.2f}")

    # Analysis
    # Scarcity (1000) -> High lambda -> Fewer trips, Higher Load, Higher Wait
    # Abundance (10000) -> Low lambda -> More trips, Lower Load, Lower Wait
    
    res_s = results[1000]
    res_a = results[10000]
    
    if res_s["trips"] < res_a["trips"] and res_s["avg_load"] > res_a["avg_load"]:
        print("VERIFIED: BCP optimizes Batch Size based on budget.")
        return True
    else:
        print("FAILED: Dispatch logic did not adapt.")
        return False

if __name__ == "__main__":
    run_experiment()
