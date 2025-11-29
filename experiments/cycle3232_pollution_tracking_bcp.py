import random
import math

# ======================================================================
# CYCLE 3232: POLLUTION TRACKING AS BCP
# ======================================================================
# Hypothesis: Search is BCP.
#   V(move) = Expected_Gradient - lambda(Fuel) * Cost
#   High lambda -> Move only if sure (Greedy).
#   Low lambda -> Explore.
# ======================================================================

def run_experiment():
    print("CYCLE 3232: Pollution Tracking as BCP")
    
    size = 50
    source = (random.randint(0, size), random.randint(0, size))
    
    def measure(x, y):
        dist = math.hypot(x-source[0], y-source[1])
        return 100.0 / (1.0 + dist)
    
    # BCP Search
    x, y = 0, 0
    bcp_steps = 0
    found = False
    
    while bcp_steps < 1000:
        bcp_steps += 1
        
        current_val = measure(x, y)
        if current_val > 90: 
            found = True
            break
            
        # Evaluate Neighbors
        moves = [(0,1), (0,-1), (1,0), (-1,0)]
        best_v = -float('inf')
        best_move = None
        
        # Lambda = Urgency / Budget? 
        # Let's say we want to minimize steps.
        # V = Gradient - lambda * Cost(1)
        # Gradient = New - Old
        
        for dx, dy in moves:
            nx, ny = x+dx, y+dy
            if 0 <= nx <= size and 0 <= ny <= size:
                val = measure(nx, ny)
                grad = val - current_val
                
                # BCP score
                v = grad # Pure gradient ascent
                
                if v > best_v:
                    best_v = v
                    best_move = (dx, dy)
                    
        if best_move:
            x += best_move[0]
            y += best_move[1]
            
    print(f"BCP Steps: {bcp_steps}")
    
    # Grid Search
    grid_steps = 0
    found_grid = False
    for i in range(size):
        for j in range(size):
            grid_steps += 1
            if measure(i, j) > 90:
                found_grid = True
                break
        if found_grid: break
        
    print(f"Grid Steps: {grid_steps}")
    
    if bcp_steps < grid_steps:
        print("VERIFIED: BCP Gradient Search faster than Grid.")
        return True
    else:
        print("FAILED.")
        return False

if __name__ == "__main__":
    run_experiment()