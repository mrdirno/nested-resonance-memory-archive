import sys
import os
import time
import json
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, RealityInterface

def run_experiment(seed, e_consume, sigma):
    """
    Runs a single experiment with metabolic cost and initial energy variance.
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=None, # In-memory for speed
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001
    initial_energy_mean = 1.0
    spawn_energy = 0.5
    max_population = 1000
    
    np.random.seed(seed)
    
    # Initialize Agents with Variance
    for i in range(100):
        # Gaussian noise, clipped to [0.1, 2.0]
        noise = np.random.normal(0, sigma)
        e_init = np.clip(initial_energy_mean + noise, 0.1, 2.0)
        
        agent = FractalAgent(agent_id=f"init_{i}", energy=e_init)
        reality.add_agent(agent, population_id=0)
    
    # Run Simulation
    max_steps = 2000 # Increased to see recovery
    history = []
    
    for step in range(max_steps):
        # 1. Spawn
        if np.random.random() < spawn_rate:
            agent = FractalAgent(agent_id=f"spawn_{step}", energy=spawn_energy)
            reality.add_agent(agent, population_id=0)
            
        # 2. Dynamics
        agents = reality.get_population_agents(0)
        resource_inflow = 10.0
        n_agents = len(agents)
        energy_gain = resource_inflow / n_agents if n_agents > 0 else 0
        
        for agent in list(agents):
            agent.energy -= e_consume
            agent.energy += energy_gain
            
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
                continue
                
            if agent.energy > 1.5:
                agent.energy -= 0.5
                child = FractalAgent(
                    agent_id=f"rep_{step}_{agent.agent_id}",
                    energy=0.5
                )
                reality.add_agent(child, population_id=0)
                
        # Cap population
        current_agents = reality.get_population_agents(0)
        if len(current_agents) > max_population:
            to_remove = len(current_agents) - max_population
            for _ in range(to_remove):
                victim = current_agents[np.random.randint(len(current_agents))]
                reality.remove_agent(victim.agent_id, 0)
        
        population = len(reality.get_population_agents(0))
        history.append(population)
        
        if population == 0:
            break
            
    final_pop = history[-1] if history else 0
    mean_pop = np.mean(history[-100:]) if len(history) >= 100 else final_pop
    
    reality.close()
    
    return {
        "e_consume": e_consume,
        "sigma": sigma,
        "seed": seed,
        "final_population": final_pop,
        "mean_population": mean_pop,
        "survived": final_pop > 0
    }

def main():
    print("CYCLE 282: VARIANCE SURVIVAL TEST")
    print("=================================")
    print("Hypothesis: Variance prevents simultaneous extinction at critical boundaries.")
    
    # Test Conditions
    # E=0.105 was lethal (5% survival).
    # We test E=0.105 with varying sigma.
    e_consume = 0.105
    sigmas = [0.0, 0.1, 0.2, 0.5, 0.8]
    seeds = range(1000, 1020) # 20 seeds
    
    results = []
    
    for sigma in sigmas:
        print(f"\nTesting Sigma = {sigma} (E={e_consume})")
        batch_results = []
        for seed in seeds:
            res = run_experiment(seed, e_consume, sigma)
            batch_results.append(res)
            results.append(res)
            
        survived = sum(1 for r in batch_results if r['survived'])
        mean_final = np.mean([r['final_population'] for r in batch_results])
        print(f"  Survival Rate: {survived}/20 ({survived/20*100:.0f}%)")
        print(f"  Mean Final Pop: {mean_final:.1f}")

    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c282_variance_survival.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
