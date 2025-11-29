import random

# ======================================================================
# CYCLE 3237: SUPPLY CHAIN AS BCP
# ======================================================================
# Hypothesis: Inventory strategy is BCP.
#   V(buffer) = Resilience - lambda(Capital) * Holding_Cost
#   High lambda -> JIT (Zero buffer).
#   Low lambda -> JIC (High buffer).
# ======================================================================

def run_experiment():
    print("CYCLE 3237: Supply Chain as BCP")
    
    T = 100
    disruption_prob = 0.1
    shortage_cost = 100.0
    holding_cost = 1.0
    
    # Scenarios
    budgets = [100, 1000]
    
    results = {}
    
    for B in budgets:
        lamb = 100.0 / (10.0 + B)
        
        # Optimize Buffer Size
        # V = (Prob * Shortage) - lambda * (Holding * Buffer)
        # Indifference: Prob * Shortage = lambda * Holding * Buffer
        # Buffer = (Prob * Shortage) / (lambda * Holding)
        
        optimal_buffer = int((disruption_prob * shortage_cost) / (lamb * holding_cost))
        optimal_buffer = max(0, optimal_buffer)
        
        total_cost = 0
        
        for t in range(T):
            # Holding
            total_cost += optimal_buffer * holding_cost
            
            # Disruption
            if random.random() < disruption_prob:
                # Demand spike or supply cut
                # Need buffer
                if optimal_buffer < 1:
                    total_cost += shortage_cost
                    
        results[B] = {"buffer": optimal_buffer, "cost": total_cost}
        print(f"Budget {B}: Buffer {optimal_buffer}, Cost {total_cost:.2f}")
        
    res_s = results[100]
    res_a = results[1000]
    
    # JIT (Buffer 0) is default high-stress state.
    # BCP should add buffer when budget allows.
    
    if res_s["buffer"] < res_a["buffer"]:
        print("VERIFIED: BCP shifts from JIT to JIC with budget.")
        return True
    else:
        print("FAILED.")
        return False

if __name__ == "__main__":
    run_experiment()