import sys
import os
import time
import json
import sqlite3
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, RealityInterface

def run_experiment(seed, condition):
    """
    Runs an experiment to measure memory retention (relaxation time) after perturbation.
    Conditions: 'sub' (E=0.100), 'super' (E=0.110), 'soc' (Adaptive).
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c284_Memory_{condition}_seed{seed}.db",
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001
    spawn_energy = 0.5
    max_population = 1000
    
    # SOC Parameters
    base_e_soc = 0.1
    gain_soc = 0.0001
    target_pop_soc = 50
    
    # Fixed Parameters
    if condition == 'sub':
        base_e = 0.100
    elif condition == 'super':
        base_e = 0.110
    else:
        base_e = base_e_soc # Initial
        
    # Initialize Agents with Diversity
    np.random.seed(seed)
    for i in range(100):
        init_e = np.random.uniform(0.8, 1.2)
        agent = FractalAgent(agent_id=f"init_{i}", energy=init_e)
        reality.add_agent(agent, population_id=0)
    
    # Run Simulation
    stabilization_steps = 500
    post_injection_steps = 500
    total_steps = stabilization_steps + post_injection_steps
    
    history_energy_mean = []
    
    current_e_consume = base_e
    
    start_time = time.time()
    
    # --- Phase 1: Stabilization ---
    for step in range(stabilization_steps):
        # Spawn
        if np.random.random() < spawn_rate:
            agent = FractalAgent(agent_id=f"spawn_{step}", energy=spawn_energy)
            reality.add_agent(agent, population_id=0)
            
        # Agent Dynamics
        agents = reality.get_population_agents(0)
        current_pop = len(agents)
        
        # SOC Logic
        if condition == 'soc':
            deviation = current_pop - target_pop_soc
            adjustment = gain_soc * deviation
            current_e_consume = base_e_soc + adjustment
            current_e_consume = max(0.100, min(0.110, current_e_consume))
        
        # Resource Inflow
        resource_inflow = 10.0
        energy_gain = resource_inflow / current_pop if current_pop > 0 else 0
        
        current_step_energies = []
        
        for agent in list(agents):
            agent.energy -= current_e_consume
            agent.energy += energy_gain
            
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
                continue
            
            if agent.energy > 1.5:
                agent.energy -= 0.5
                child = FractalAgent(agent_id=f"rep_{step}_{agent.agent_id}", energy=0.5)
                reality.add_agent(child, population_id=0)
            
            current_step_energies.append(agent.energy)
            
        # Cap
        current_agents = reality.get_population_agents(0)
        if len(current_agents) > max_population:
            to_remove = len(current_agents) - max_population
            for _ in range(to_remove):
                victim = current_agents[np.random.randint(len(current_agents))]
                reality.remove_agent(victim.agent_id, 0)
        
        # Record Metric
        if current_step_energies:
            history_energy_mean.append(np.mean(current_step_energies))
        else:
            history_energy_mean.append(0)
            
        if len(reality.get_population_agents(0)) == 0:
            break
            
    # Calculate Baseline
    if len(history_energy_mean) >= 100:
        baseline_mean = np.mean(history_energy_mean[-100:])
        baseline_std = np.std(history_energy_mean[-100:])
    else:
        baseline_mean = 0
        baseline_std = 0
        
    # --- Phase 2: Injection ---
    # Inject High Energy Signal
    # 10 agents with Energy = 10.0 (Massive perturbation)
    for i in range(10):
        agent = FractalAgent(agent_id=f"signal_{i}", energy=10.0)
        reality.add_agent(agent, population_id=0)
        
    # --- Phase 3: Relaxation ---
    retention_steps = 0
    signal_detected = True
    
    for step in range(stabilization_steps, total_steps):
        # Same Dynamics Loop...
        # (Duplicated for simplicity of flow control)
        
        if np.random.random() < spawn_rate:
            agent = FractalAgent(agent_id=f"spawn_{step}", energy=spawn_energy)
            reality.add_agent(agent, population_id=0)
            
        agents = reality.get_population_agents(0)
        current_pop = len(agents)
        
        if condition == 'soc':
            deviation = current_pop - target_pop_soc
            adjustment = gain_soc * deviation
            current_e_consume = base_e_soc + adjustment
            current_e_consume = max(0.100, min(0.110, current_e_consume))
            
        resource_inflow = 10.0
        energy_gain = resource_inflow / current_pop if current_pop > 0 else 0
        
        current_step_energies = []
        
        for agent in list(agents):
            agent.energy -= current_e_consume
            agent.energy += energy_gain
            
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
                continue
            
            if agent.energy > 1.5:
                agent.energy -= 0.5
                child = FractalAgent(agent_id=f"rep_{step}_{agent.agent_id}", energy=0.5)
                reality.add_agent(child, population_id=0)
                
            current_step_energies.append(agent.energy)
            
        current_agents = reality.get_population_agents(0)
        if len(current_agents) > max_population:
            to_remove = len(current_agents) - max_population
            for _ in range(to_remove):
                victim = current_agents[np.random.randint(len(current_agents))]
                reality.remove_agent(victim.agent_id, 0)
                
        # Check Signal Retention
        if current_step_energies:
            current_mean = np.mean(current_step_energies)
            # Signal is considered "retained" if mean is > baseline + 2*std
            threshold = baseline_mean + 2 * baseline_std
            
            if signal_detected:
                if current_mean > threshold:
                    retention_steps += 1
                else:
                    # Signal lost
                    signal_detected = False
        else:
            signal_detected = False
            
        if len(reality.get_population_agents(0)) == 0:
            break

    runtime = time.time() - start_time
    reality.close()
    
    return {
        "seed": seed,
        "condition": condition,
        "baseline_mean": baseline_mean,
        "baseline_std": baseline_std,
        "retention_steps": retention_steps,
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 284: CRITICAL MEMORY CAPACITY")
    print("===================================")
    print("Hypothesis: SOC state maximizes signal retention time.")
    
    conditions = ['sub', 'super', 'soc']
    seeds = range(100, 110) # 10 seeds per condition
    
    results = []
    
    print(f"{'Condition':<10} | {'Mean Retention (Steps)':<25} | {'Survival Rate':<15}")
    print("-" * 60)
    
    for cond in conditions:
        cond_results = []
        for seed in seeds:
            res = run_experiment(seed, cond)
            cond_results.append(res)
            results.append(res)
            
        # Stats
        retention_times = [r['retention_steps'] for r in cond_results]
        mean_retention = np.mean(retention_times)
        std_retention = np.std(retention_times)
        
        # Survival (Did it collapse?)
        # Note: Super-critical usually collapses, so retention might be 0 or low
        
        print(f"{cond:<10} | {mean_retention:.1f} +/- {std_retention:.1f}          | N/A")
        
    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c284_memory_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n===================================")
    print("CAMPAIGN COMPLETE.")

if __name__ == "__main__":
    main()
