import random
import math

# ======================================================================
# CYCLE 3242: WATER LEAK LOCALIZATION AS BCP
# ======================================================================
# Hypothesis: Leak finding is BCP.
#   V(check) = Prob(Leak) * Cost(Leak) - lambda * Cost(Check)
#   Bayesian update of Prob(Leak) based on sensors.
# ======================================================================

def run_experiment():
    print("CYCLE 3242: Water Leak Localization as BCP")
    
    N = 50 # Pipe segments
    leak_pos = random.randint(0, N-1)
    
    # Prior Probability
    probs = [1.0/N] * N
    
    # Pressure Sensors (Noisy)
    def read_pressure(pos):
        dist = abs(pos - leak_pos)
        # Drop is highest at leak
        drop = 10.0 / (1.0 + dist) + random.gauss(0, 1.0)
        return drop
    
    # BCP Search
    budget = 10 # Checks
    lamb = 100.0 / (10.0 + budget)
    
    found_bcp = False
    checks_bcp = 0
    
    # Bayesian Search
    for t in range(budget):
        # Update Scores
        best_v = -float('inf')
        best_idx = -1
        
        for i in range(N):
            # Gain = Expected Value of Information? Or Expected Find?
            # Gain = Prob(Leak) * Value(Fix=100)
            gain = probs[i] * 100.0
            cost = 1.0 # Check cost
            
            v = gain - lamb * cost
            
            if v > best_v:
                best_v = v
                best_idx = i
                
        if best_idx == -1: break
        
        # Check
        checks_bcp += 1
        if best_idx == leak_pos:
            found_bcp = True
            break
            
        # Update Priors (Bayesian)
        # Observed LOW drop -> Leak is far
        # Observed HIGH drop -> Leak is near
        obs = read_pressure(best_idx)
        
        # Likelihood P(Obs | Leak=j)
        # Simple approximation: Boost neighbors if High Drop
        for j in range(N):
            expected = 10.0 / (1.0 + abs(best_idx - j))
            error = abs(obs - expected)
            likelihood = math.exp(-error)
            probs[j] *= likelihood
            
        # Normalize
        total_p = sum(probs)
        probs = [p/total_p for p in probs]
        
    print(f"BCP Checks: {checks_bcp}, Found: {found_bcp}")
    
    # Grid Search (Linear)
    found_grid = False
    checks_grid = 0
    for i in range(N):
        checks_grid += 1
        if i == leak_pos:
            found_grid = True
            break
            
    print(f"Grid Checks: {checks_grid}")
    
    if found_bcp and checks_bcp < checks_grid:
        print("VERIFIED: BCP Bayesian Search faster than Linear.")
        return True
    else:
        print("FAILED.")
        return False

if __name__ == "__main__":
    run_experiment()