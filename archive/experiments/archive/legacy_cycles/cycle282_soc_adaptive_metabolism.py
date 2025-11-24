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

def run_experiment(seed, base_e_consume, adaptive_gain, target_pop):
    """
    Runs a single experiment with adaptive metabolic cost (SOC).
    E_consume(t) = Base_E + Gain * (Population(t) - Target_Pop)
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c282_SOC_seed{seed}.db",
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001  # 0.01%
    initial_energy = 1.0
    spawn_energy = 0.5
    max_population = 1000
    
    # Initialize Agents
    # Start with a healthy population
    # CRITICAL FIX: Randomize initial energy to prevent synchronized death
    for i in range(100):
        init_e = np.random.uniform(0.8, 1.2) # Diversity
        agent = FractalAgent(agent_id=f"init_{i}", energy=init_e)
        reality.add_agent(agent, population_id=0)
    
    # Run Simulation
    max_steps = 2000 # Longer run to allow convergence
    history_pop = []
    history_e = []
    
    np.random.seed(seed)
    
    current_e_consume = base_e_consume
    
    start_time = time.time()
    for step in range(max_steps):
        # 1. Spawn (External inflow)
        if np.random.random() < spawn_rate:
            agent = FractalAgent(agent_id=f"spawn_{step}", energy=spawn_energy)
            reality.add_agent(agent, population_id=0)
            
        # 2. Agent Dynamics
        agents = reality.get_population_agents(0)
        current_pop = len(agents)
        
        # --- SOC MECHANISM: ADAPTIVE METABOLISM ---
        # E(t) = E_base + Gain * (P(t) - P_target)
        # If Pop > Target, E increases (Kill more)
        # If Pop < Target, E decreases (Save more)
        
        deviation = current_pop - target_pop
        adjustment = adaptive_gain * deviation
        current_e_consume = base_e_consume + adjustment
        
        # Clamp to critical range [0.100, 0.110] to avoid wild swings
        # We want to see if it can find the "sweet spot" (0.1045)
        current_e_consume = max(0.100, min(0.110, current_e_consume))
        
        history_e.append(current_e_consume)
        
        # Resource Inflow
        resource_inflow = 10.0
        energy_gain = resource_inflow / current_pop if current_pop > 0 else 0
        
        # Iterate over copy
        for agent in list(agents):
            # Metabolism (Adaptive)
            agent.energy -= current_e_consume
            
            # Resource Gain
            agent.energy += energy_gain
            
            # Death
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
                continue
                
            # Reproduction
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
        history_pop.append(population)
        
        # Early exit if collapsed
        if population == 0:
            break
            
    runtime = time.time() - start_time
    
    # Calculate Metrics
    final_pop = history_pop[-1] if history_pop else 0
    mean_pop = np.mean(history_pop[-500:]) if len(history_pop) >= 500 else final_pop
    variance_pop = np.var(history_pop[-500:]) if len(history_pop) >= 500 else 0.0
    mean_e = np.mean(history_e[-500:]) if len(history_e) >= 500 else current_e_consume
    
    reality.close()
    
    return {
        "seed": seed,
        "target_pop": target_pop,
        "base_e": base_e_consume,
        "gain": adaptive_gain,
        "final_population": final_pop,
        "mean_population": mean_pop,
        "variance_population": variance_pop,
        "mean_final_e_consume": mean_e,
        "steps_survived": len(history_pop),
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 282: SELF-ORGANIZED CRITICALITY (Adaptive Metabolism) - SWEEP")
    print("===================================================================")
    
    # Parameter Sweep
    base_e_values = [0.100, 0.102, 0.104] # Start safe or near-critical
    gains = [0.0001, 0.0005, 0.001, 0.005] # Vary feedback strength
    target_pop = 50
    
    seeds = range(900, 905) # 5 seeds per condition (Quick sweep)
    
    results = []
    
    total_runs = len(base_e_values) * len(gains) * len(seeds)
    current_run = 0
    
    print(f"Target Pop: {target_pop}")
    print(f"Sweeping Base E: {base_e_values}")
    print(f"Sweeping Gains: {gains}")
    print("-----------------------------------------------------------")
    
    for base_e in base_e_values:
        for gain in gains:
            print(f"\nTesting Base E={base_e}, Gain={gain}")
            condition_results = []
            for seed in seeds:
                current_run += 1
                print(f"[{current_run}/{total_runs}] Seed={seed}...", end="", flush=True)
                
                res = run_experiment(seed, base_e, gain, target_pop)
                results.append(res)
                condition_results.append(res)
                
                status = "Collapsed" if res['final_population'] == 0 else f"Stable ({res['mean_population']:.1f})"
                print(f"  ✓ {status}, E_final={res['mean_final_e_consume']:.5f}")
            
            # Condition Summary
            survivors = [r for r in condition_results if r['final_population'] > 0]
            survival_rate = len(survivors) / len(seeds)
            if survivors:
                mean_pop = np.mean([r['mean_population'] for r in survivors])
                mean_e = np.mean([r['mean_final_e_consume'] for r in survivors])
                print(f"  >>> Summary: Survival={survival_rate*100:.0f}%, Pop={mean_pop:.1f}, E={mean_e:.5f}")
            else:
                print(f"  >>> Summary: Survival=0%")

    # Save Results
    os.makedirs("experiments/results", exist_ok=True)
    output_file = "experiments/results/c282_soc_sweep_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n===========================================================")
    print(f"CAMPAIGN COMPLETE. Results saved to {output_file}")

if __name__ == "__main__":
    main()
