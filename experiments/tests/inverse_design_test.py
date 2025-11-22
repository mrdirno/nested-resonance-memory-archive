import sys
import os
import numpy as np
import scipy.stats as stats
from typing import List, Dict, Tuple

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from code.fractal.fractal_swarm import FractalSwarm
from code.fractal.agent import FractalAgent

def run_swarm_simulation(params: Dict[str, float], steps: int = 1000) -> List[float]:
    """Runs a swarm simulation and returns avalanche sizes."""
    N_AGENTS = 50
    swarm = FractalSwarm(max_agents=N_AGENTS, burst_threshold=200.0)
    
    # Initialize agents
    agents = []
    for i in range(N_AGENTS):
        # Random initial energy
        agent = swarm.spawn_agent(reality_metrics={}, initial_energy=np.random.uniform(0, 100))
        agents.append(agent)
        
    # Unpack parameters
    K = params.get('K', 0.1)
    Inflow = params.get('Inflow', 1.0)
    Dissipation = params.get('Dissipation', 0.1)
    Threshold = 100.0 # Fixed threshold for avalanche
    
    avalanches = []
    current_avalanche = 0
    
    for t in range(steps):
        active_count = 0
        
        # 1. Drive (Inflow)
        # Randomly select one agent to receive energy (Sandpile style)
        target = np.random.choice(agents)
        target.state.energy += Inflow
        
        # 2. Relaxation (Dynamics)
        # Check for instability
        unstable_agents = [a for a in agents if a.state.energy > Threshold]
        
        if unstable_agents:
            current_avalanche += len(unstable_agents)
            
            # Topple / Fire
            for agent in unstable_agents:
                # Dissipate some energy
                loss = agent.state.energy * Dissipation
                transfer = (agent.state.energy - loss) * K # Share fraction K
                
                agent.state.energy = 0 # Reset (or reduce)
                
                # Distribute to neighbors (Global coupling for now, or random)
                # In mean-field, distribute to all others
                share = transfer / (N_AGENTS - 1)
                for neighbor in agents:
                    if neighbor != agent:
                        neighbor.state.energy += share
        else:
            if current_avalanche > 0:
                avalanches.append(current_avalanche)
                current_avalanche = 0
                
    return avalanches

def evaluate_fitness(avalanches: List[float]) -> float:
    """Calculates fitness based on Power Law fit (R^2) of avalanche distribution."""
    if len(avalanches) < 10:
        return 0.0
        
    # Histogram
    counts, bins = np.histogram(avalanches, bins=np.logspace(0, np.log10(max(avalanches)), 10))
    # Filter zeros
    x = (bins[:-1] + bins[1:]) / 2
    y = counts
    
    mask = y > 0
    x_log = np.log10(x[mask])
    y_log = np.log10(y[mask])
    
    if len(x_log) < 3:
        return 0.0
        
    # Linear Regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_log, y_log)
    
    # We want a power law, so high R^2. 
    # Also, slope should be typically between -1 and -3 for SOC.
    
    r_squared = r_value**2
    
    # Penalty for bad slope
    slope_penalty = 0.0
    if slope > -0.5 or slope < -3.0:
        slope_penalty = 0.5
        
    return r_squared - slope_penalty

def inverse_design_test():
    print("--- INVERSE DESIGN EXPERIMENT (PAPER 9) ---")
    print("Goal: Autonomously discover parameters for Self-Organized Criticality (SOC).")
    print("Objective: Maximize Power Law fit (R^2) of energy avalanches.")
    
    # Genetic Algorithm Parameters
    POP_SIZE = 10
    GENERATIONS = 5
    MUTATION_RATE = 0.2
    
    # Gene Ranges
    # K: [0, 1]
    # Inflow: [0, 10]
    # Dissipation: [0, 1]
    
    # Initialize Population
    population = []
    for _ in range(POP_SIZE):
        ind = {
            'K': np.random.uniform(0, 1),
            'Inflow': np.random.uniform(0, 10),
            'Dissipation': np.random.uniform(0, 1)
        }
        population.append(ind)
        
    best_fitness = -1.0
    best_ind = None
    
    for gen in range(GENERATIONS):
        print(f"\nGeneration {gen+1}/{GENERATIONS}")
        
        fitness_scores = []
        for i, ind in enumerate(population):
            avalanches = run_swarm_simulation(ind, steps=2000)
            fitness = evaluate_fitness(avalanches)
            fitness_scores.append(fitness)
            
            print(f"  Ind {i}: K={ind['K']:.2f}, I={ind['Inflow']:.2f}, D={ind['Dissipation']:.2f} -> Fitness={fitness:.4f}")
            
            if fitness > best_fitness:
                best_fitness = fitness
                best_ind = ind.copy()
                
        # Selection (Tournament)
        new_pop = []
        while len(new_pop) < POP_SIZE:
            # Select 2 parents
            p1_idx = np.random.randint(0, POP_SIZE)
            p2_idx = np.random.randint(0, POP_SIZE)
            
            if fitness_scores[p1_idx] > fitness_scores[p2_idx]:
                parent = population[p1_idx]
            else:
                parent = population[p2_idx]
                
            # Mutation
            child = parent.copy()
            if np.random.random() < MUTATION_RATE:
                child['K'] = np.clip(child['K'] + np.random.normal(0, 0.1), 0, 1)
            if np.random.random() < MUTATION_RATE:
                child['Inflow'] = np.clip(child['Inflow'] + np.random.normal(0, 1.0), 0, 10)
            if np.random.random() < MUTATION_RATE:
                child['Dissipation'] = np.clip(child['Dissipation'] + np.random.normal(0, 0.1), 0, 1)
                
            new_pop.append(child)
            
        population = new_pop
        
    print(f"\n--- BEST SOLUTION FOUND ---")
    print(f"Parameters: {best_ind}")
    print(f"Fitness (R^2): {best_fitness:.4f}")
    
    if best_fitness > 0.8: # Lower threshold for stochastic simulation
        print("SUCCESS: Inverse Design Engine discovered SOC parameters.")
    else:
        print("FAILURE: Could not find SOC parameters.")

if __name__ == "__main__":
    inverse_design_test()
