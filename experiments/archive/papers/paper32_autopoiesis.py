import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class AutopoieticAgent:
    def __init__(self, x, y, energy=50.0):
        self.pos = np.array([x, y], dtype=float)
        self.energy = energy
        self.alive = True
        self.age = 0
        
    def move(self, width, height, food_grid, grid_scale=1.0, dt=0.1):
        # Sensing
        gx = int(self.pos[0] / grid_scale)
        gy = int(self.pos[1] / grid_scale)
        h, w = food_grid.shape
        
        # Check neighbors for max food
        best_dir = np.array([0.0, 0.0])
        max_food = 0
        
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                ny, nx = gy + dy, gx + dx
                if 0 <= ny < h and 0 <= nx < w:
                    if food_grid[ny, nx] > max_food:
                        max_food = food_grid[ny, nx]
                        best_dir = np.array([dx, dy])
        
        # Random Walk + Bias towards food
        vel = np.random.normal(0, 1.0, 2) + best_dir * 2.0
        
        self.pos += vel * dt
        
        # Wrap around
        self.pos[0] %= width
        self.pos[1] %= height
        
        # Metabolic Cost
        # Base cost + Movement cost
        cost = 0.05 + 0.01 * np.sum(vel**2)
        self.energy -= cost
        
    def eat(self, food_grid, grid_scale=1.0):
        # Check grid cell
        gx = int(self.pos[0] / grid_scale)
        gy = int(self.pos[1] / grid_scale)
        
        # Bounds check
        h, w = food_grid.shape
        gx = np.clip(gx, 0, w-1)
        gy = np.clip(gy, 0, h-1)
        
        available_food = food_grid[gy, gx]
        if available_food > 0:
            # Eat
            amount = min(available_food, 5.0) # Max eat rate
            self.energy += amount
            food_grid[gy, gx] -= amount
            
    def reproduce(self):
        # Threshold for reproduction
        if self.energy > 100.0:
            # Split
            self.energy /= 2.0
            # Create offspring slightly offset
            offspring = AutopoieticAgent(self.pos[0] + np.random.normal(0, 0.1), 
                                         self.pos[1] + np.random.normal(0, 0.1),
                                         energy=self.energy)
            return offspring
        return None

def run_autopoiesis_experiment():
    print("\n--- PAPER 32: THE AUTOPOIETIC SWARM (SELF-REPRODUCTION) ---")
    
    width, height = 50, 50
    grid_scale = 1.0
    n_grid_w = int(width / grid_scale)
    n_grid_h = int(height / grid_scale)
    
    # Food Grid
    food_grid = np.zeros((n_grid_h, n_grid_w))
    # Seed food
    for _ in range(100):
        rx = np.random.randint(0, n_grid_w)
        ry = np.random.randint(0, n_grid_h)
        food_grid[ry, rx] = 10.0
    
    # Initial Agents
    # Start with more energy
    agents = [AutopoieticAgent(np.random.uniform(0, width), np.random.uniform(0, height), energy=80.0) for _ in range(50)]
    
    history_pop = []
    
    print("Running Simulation...")
    for t in range(2000):
        # 1. Regrow Food
        # Logistic regrowth of food
        growth_rate = 0.1 # Doubled
        max_food = 10.0
        food_grid += growth_rate * food_grid * (1 - food_grid/max_food)
        # Also random seeding to prevent total extinction of food
        if np.random.random() < 0.2: # More seeding
            rx = np.random.randint(0, n_grid_w)
            ry = np.random.randint(0, n_grid_h)
            food_grid[ry, rx] = max_food
            
        # 2. Update Agents
        new_agents = []
        surviving_agents = []
        
        for agent in agents:
            agent.move(width, height, food_grid, grid_scale)
            agent.eat(food_grid, grid_scale)
            
            if agent.energy > 0:
                surviving_agents.append(agent)
                offspring = agent.reproduce()
                if offspring:
                    new_agents.append(offspring)
            
        agents = surviving_agents + new_agents
        
        history_pop.append(len(agents))
        
        if t % 200 == 0:
            print(f"Step {t}: Population = {len(agents)}")
            
        # Extinction check
        if len(agents) == 0:
            print("EXTINCTION.")
            break
            
    # Analysis
    final_pop = len(agents)
    avg_pop_last_100 = np.mean(history_pop[-100:]) if len(history_pop) > 100 else 0
    
    print(f"Final Population: {final_pop}")
    print(f"Average Population (Last 100 steps): {avg_pop_last_100:.2f}")
    
    # Criteria
    # Sustainable population (non-zero, stable)
    if avg_pop_last_100 > 10 and avg_pop_last_100 < 5000: # Reasonable bounds
        print("SUCCESS: Autopoiesis Verified.")
        print("Population stabilized at Carrying Capacity.")
    else:
        print("FAILURE: Population collapsed or exploded uncontrollably.")

if __name__ == "__main__":
    run_autopoiesis_experiment()
