import sys
import os
import time
import json
import sqlite3
import numpy as np
from collections import Counter

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, RealityInterface

def run_experiment(seed, base_e_consume, adaptive_gain, target_pop):
    """
    Runs a long-duration experiment to analyze avalanche dynamics in SOC state.
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c283_SOC_Avalanche_seed{seed}.db",
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001
    spawn_energy = 0.5
    max_population = 1000
    
    # Initialize Agents with Diversity
    np.random.seed(seed)
    for i in range(100):
        init_e = np.random.uniform(0.8, 1.2) # Diversity
        agent = FractalAgent(agent_id=f"init_{i}", energy=init_e)
        reality.add_agent(agent, population_id=0)
    
    # Run Simulation
    max_steps = 10000 # Long run for statistics
    history_pop = []
    history_e = []
    history_activity = [] # births + deaths
    
    current_e_consume = base_e_consume
    
    start_time = time.time()
    for step in range(max_steps):
        step_births = 0
        step_deaths = 0
        
        # 1. Spawn
        if np.random.random() < spawn_rate:
            agent = FractalAgent(agent_id=f"spawn_{step}", energy=spawn_energy)
            reality.add_agent(agent, population_id=0)
            step_births += 1
            
        # 2. Agent Dynamics
        agents = reality.get_population_agents(0)
        current_pop = len(agents)
        
        # SOC Mechanism
        deviation = current_pop - target_pop
        adjustment = adaptive_gain * deviation
        current_e_consume = base_e_consume + adjustment
        current_e_consume = max(0.100, min(0.110, current_e_consume))
        
        history_e.append(current_e_consume)
        
        # Resource Inflow
        resource_inflow = 10.0
        energy_gain = resource_inflow / current_pop if current_pop > 0 else 0
        
        # Iterate
        for agent in list(agents):
            # Metabolism
            agent.energy -= current_e_consume
            agent.energy += energy_gain
            
            # Death
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
                step_deaths += 1
                continue
                
            # Reproduction
            if agent.energy > 1.5:
                agent.energy -= 0.5
                child = FractalAgent(
                    agent_id=f"rep_{step}_{agent.agent_id}",
                    energy=0.5
                )
                reality.add_agent(child, population_id=0)
                step_births += 1
                
        # Cap population (Safety)
        current_agents = reality.get_population_agents(0)
        if len(current_agents) > max_population:
            to_remove = len(current_agents) - max_population
            for _ in range(to_remove):
                victim = current_agents[np.random.randint(len(current_agents))]
                reality.remove_agent(victim.agent_id, 0)
                step_deaths += 1 # Count culls as deaths for activity
        
        population = len(reality.get_population_agents(0))
        history_pop.append(population)
        history_activity.append(step_births + step_deaths)
        
        if population == 0:
            break
            
    runtime = time.time() - start_time
    
    reality.close()
    
    return {
        "seed": seed,
        "final_population": history_pop[-1] if history_pop else 0,
        "mean_population": np.mean(history_pop),
        "mean_e": np.mean(history_e),
        "activity_distribution": dict(Counter(history_activity)),
        "steps_survived": len(history_pop),
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 283: SOC AVALANCHE ANALYSIS")
    print("=================================")
    
    # Parameters from Cycle 282 Success
    base_e = 0.1
    gain = 0.0001
    target_pop = 50
    
    seeds = [1001, 1002, 1003] # Few long runs
    results = []
    
    print(f"Config: Base E={base_e}, Gain={gain}, Target={target_pop}, Steps=10000")
    print("Hypothesis: Activity distribution should follow Power Law P(s) ~ s^-alpha")
    print("---------------------------------")
    
    aggregated_activity = Counter()
    
    for seed in seeds:
        print(f"Running Seed {seed}...", end="", flush=True)
        res = run_experiment(seed, base_e, gain, target_pop)
        results.append(res)
        
        # Aggregate activity
        for size, count in res['activity_distribution'].items():
            aggregated_activity[int(size)] += count
            
        print(f" Done. Pop={res['mean_population']:.1f}, E={res['mean_e']:.5f}")
        
    # Analysis
    print("\n--- AVALANCHE SIZE DISTRIBUTION ---")
    sorted_sizes = sorted(aggregated_activity.keys())
    
    # Simple text histogram & Power Law check
    print(f"{'Size (s)':<10} | {'Count (N)':<10} | {'log(s)':<10} | {'log(N)':<10}")
    print("-" * 50)
    
    log_s = []
    log_N = []
    
    for s in sorted_sizes:
        if s == 0: continue
        count = aggregated_activity[s]
        ls = np.log10(s)
        ln = np.log10(count)
        log_s.append(ls)
        log_N.append(ln)
        print(f"{s:<10} | {count:<10} | {ls:.2f}       | {ln:.2f}")
        
    # Estimate Slope (Alpha)
    if len(log_s) > 2:
        # Simple linear regression on log-log data
        slope, intercept = np.polyfit(log_s, log_N, 1)
        alpha = -slope
        print("-" * 50)
        print(f"Estimated Power Law Exponent (alpha): {alpha:.4f}")
        
        if 1.5 < alpha < 3.0:
            print(">>> RESULT: CONSISTENT WITH SOC (1.5 < alpha < 3.0)")
        else:
            print(">>> RESULT: DEVIATION FROM STANDARD SOC")
            
    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c283_avalanche_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
