import sys
import os
import time
import json
import sqlite3
import numpy as np
from datetime import datetime

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, RealityInterface

def run_experiment(seed, e_consume):
    """
    Runs a single experiment with a specific metabolic cost (E_consume).
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c280_METABOLIC_{e_consume:.3f}_seed{seed}.db",
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001  # 0.01%
    initial_energy = 1.0
    spawn_energy = 0.5
    max_population = 1000
    
    # Initialize Agents
    # Start with a healthy population to test stability
    for i in range(100):
        agent = FractalAgent(agent_id=f"init_{i}", energy=initial_energy)
        reality.add_agent(agent, population_id=0)
    
    # Run Simulation
    max_steps = 1000
    history = []
    
    np.random.seed(seed)
    
    start_time = time.time()
    for step in range(max_steps):
        # 1. Spawn (External inflow)
        if np.random.random() < spawn_rate:
            agent = FractalAgent(agent_id=f"spawn_{step}", energy=spawn_energy)
            reality.add_agent(agent, population_id=0)
            
        # 2. Agent Dynamics (Metabolism, Death, Reproduction)
        agents = reality.get_population_agents(0)
        
        # Resource Inflow (Constant flux shared among agents)
        resource_inflow = 10.0
        n_agents = len(agents)
        energy_gain = resource_inflow / n_agents if n_agents > 0 else 0
        
        # Iterate over copy to allow modification
        for agent in list(agents):
            # Metabolism
            agent.energy -= e_consume
            
            # Resource Gain
            agent.energy += energy_gain
            
            # Death
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
                continue
                
            # Reproduction
            # If energy is high, reproduce
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
            # Random cull
            to_remove = len(current_agents) - max_population
            for _ in range(to_remove):
                victim = current_agents[np.random.randint(len(current_agents))]
                reality.remove_agent(victim.agent_id, 0)
        
        population = len(reality.get_population_agents(0))
        history.append(population)
        
        # Early exit if collapsed
        if population == 0:
            break
            
    runtime = time.time() - start_time
    
    # Calculate Metrics
    final_pop = history[-1] if history else 0
    mean_pop = np.mean(history[-100:]) if len(history) >= 100 else final_pop
    variance = np.var(history[-100:]) if len(history) >= 100 else 0.0
    
    reality.close()
    
    return {
        "e_consume": e_consume,
        "seed": seed,
        "final_population": final_pop,
        "mean_population": mean_pop,
        "variance": variance,
        "steps_survived": len(history),
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 280: FINE-GRAINED METABOLIC SWEEP (Critical Point Search)")
    print("===============================================================")
    
    # Parameter Sweep: E_consume from 0.10 to 0.20
    # We expect a transition somewhere in this range.
    e_consume_values = [0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20]
    seeds = range(700, 710) # 10 seeds per condition
    
    results = []
    
    total_experiments = len(e_consume_values) * len(seeds)
    current_exp = 0
    
    for e_val in e_consume_values:
        print(f"\nTesting E_consume = {e_val:.3f} (10 seeds)")
        print("----------------------------------------")
        
        condition_results = []
        
        for seed in seeds:
            current_exp += 1
            print(f"[{current_exp}/{total_experiments}] Running: E={e_val:.3f}, seed={seed}...", end="", flush=True)
            
            res = run_experiment(seed, e_val)
            results.append(res)
            condition_results.append(res)
            
            status = "Collapsed" if res['final_population'] == 0 else f"Saturated ({res['mean_population']:.1f})"
            print(f"  ✓ {status}, {res['runtime_seconds']:.1f}s")
            
        # Condition Summary
        mean_pop = np.mean([r['mean_population'] for r in condition_results])
        survival_rate = np.mean([1 if r['final_population'] > 0 else 0 for r in condition_results])
        print(f"Summary (E={e_val:.3f}): Mean Pop={mean_pop:.1f}, Survival={survival_rate*100:.0f}%")

    # Save Results
    os.makedirs("experiments/results", exist_ok=True)
    output_file = "experiments/results/c280_fine_grained_metabolic_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n===============================================================")
    print(f"CAMPAIGN COMPLETE. Results saved to {output_file}")

if __name__ == "__main__":
    main()
