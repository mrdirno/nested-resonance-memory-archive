import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3232: POLLUTION SOURCE TRACKING BCP
# -----------------------------------------------------------------------------
# Domain: Environmental
# Goal: Locate a pollution source on a grid.
# Hypothesis: BCP (Bayesian Search) finds source in fewer steps than Grid Search.
# -----------------------------------------------------------------------------

class Grid:
    def __init__(self, size=20):
        self.size = size
        self.source_x = random.randint(0, size-1)
        self.source_y = random.randint(0, size-1)
        
    def measure(self, x, y):
        # Pollution = 1 / distance
        dist = math.sqrt((x - self.source_x)**2 + (y - self.source_y)**2)
        if dist == 0: return 100.0
        signal = 10.0 / dist
        return signal + random.gauss(0, 0.5) # Noise

class GridSearcher:
    def __init__(self, size):
        self.size = size
        self.x = 0
        self.y = 0
        
    def next_step(self, measurement):
        # Snake scan
        curr = (self.x, self.y)
        
        self.x += 1
        if self.x >= self.size:
            self.x = 0
            self.y += 1
            
        return curr # Return where we *were* (to check if found)

class BCPSearcher:
    def __init__(self, size):
        self.size = size
        self.belief = [[1.0/(size*size) for _ in range(size)] for _ in range(size)]
        self.history = [] # (x, y, val)
        
    def next_step(self, measurement):
        # 1. Update belief based on LAST measurement
        if self.history:
            last_x, last_y, last_val = self.history[-1]
            
            # Likelihood: P(Measurement | Source is at i,j)
            # Ideal signal = 10 / dist((i,j), (last_x, last_y))
            # Error = abs(measurement - ideal)
            # Likelihood ~ exp(-error)
            
            for i in range(self.size):
                for j in range(self.size):
                    dist = math.sqrt((i - last_x)**2 + (j - last_y)**2)
                    if dist == 0: ideal = 100.0
                    else: ideal = 10.0 / dist
                    
                    error = abs(last_val - ideal)
                    likelihood = math.exp(-error) # Simplified Gaussian
                    self.belief[i][j] *= likelihood
            
            # Normalize
            total = sum(sum(row) for row in self.belief)
            if total > 0:
                for i in range(self.size):
                    for j in range(self.size):
                        self.belief[i][j] /= total
                        
        # 2. Choose next point: Max Probability (Greedy)
        best_p = -1
        best_pos = (0,0)
        
        # Add some exploration noise or we get stuck
        # For simulation, just pick max belief
        
        for i in range(self.size):
            for j in range(self.size):
                if self.belief[i][j] > best_p:
                    # Don't re-visit exact same spot immediately (heuristic)
                    if (i,j) not in [h[:2] for h in self.history]:
                        best_p = self.belief[i][j]
                        best_pos = (i,j)
        
        self.history.append((*best_pos, measurement)) # Store measurement for next update (actually we store the measurement we GET there, but here we store placeholder)
        # Fix: We need to store the measurement *after* we get it. 
        # So 'next_step' returns coordinates. The caller gets measurement. 
        # Then we need to pass it back.
        # Refactoring flow: next_step takes *previous* measurement.
        
        # Update history with ACTUAL measurement received
        if self.history:
             self.history[-1] = (self.history[-1][0], self.history[-1][1], measurement)
             
        return best_pos

# Correction: The Searcher API needs to separate "Suggest Next" and "Update"
# But to keep simple, 'next_step(measurement)' updates with prev, then suggests next.

class CorrectBCPSearcher:
    def __init__(self, size):
        self.size = size
        self.belief = [[1.0/(size*size) for _ in range(size)] for _ in range(size)]
        self.last_pos = None
        
    def next_step(self, measurement):
        # Update if we have a previous position
        if self.last_pos:
            last_x, last_y = self.last_pos
            
            for i in range(self.size):
                for j in range(self.size):
                    dist = math.sqrt((i - last_x)**2 + (j - last_y)**2)
                    if dist == 0: ideal = 100.0
                    else: ideal = 10.0 / dist
                    
                    # We expect signal 'ideal'. We got 'measurement'.
                    error = abs(measurement - ideal)
                    likelihood = math.exp(-error * 0.5) 
                    self.belief[i][j] *= likelihood
            
            # Normalize
            total = sum(sum(row) for row in self.belief)
            if total > 0:
                for i in range(self.size):
                    for j in range(self.size):
                        self.belief[i][j] /= total

        # Pick Max
        best_p = -1
        best_pos = (random.randint(0, self.size-1), random.randint(0, self.size-1))
        
        for i in range(self.size):
            for j in range(self.size):
                if self.belief[i][j] > best_p:
                    best_p = self.belief[i][j]
                    best_pos = (i,j)
                    
        self.last_pos = best_pos
        return best_pos

def run_test(searcher_cls, runs=100):
    total_steps = 0
    
    for _ in range(runs):
        grid = Grid()
        searcher = searcher_cls(grid.size)
        
        measurement = 0 # dummy for first step
        found = False
        
        for step in range(grid.size * grid.size):
            x, y = searcher.next_step(measurement)
            
            if x == grid.source_x and y == grid.source_y:
                total_steps += step
                found = True
                break
                
            measurement = grid.measure(x, y)
            
        if not found:
            total_steps += grid.size * grid.size
            
    return total_steps / runs

def main():
    print("======================================================================")
    print("CYCLE 3232: POLLUTION SOURCE TRACKING BCP")
    print("======================================================================")
    
    # Grid Search
    grid_steps = run_test(GridSearcher)
    print(f"Grid Search Avg Steps: {grid_steps:.1f}")
    
    # BCP Search
    bcp_steps = run_test(CorrectBCPSearcher)
    print(f"BCP Search Avg Steps:  {bcp_steps:.1f}")
    
    improvement = ((grid_steps - bcp_steps) / grid_steps) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_steps < grid_steps:
        print("RESULT: SUCCESS. Bayesian Search found source faster.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3232_pollution_tracking.json", "w") as f:
        json.dump({"grid": grid_steps, "bcp": bcp_steps, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
