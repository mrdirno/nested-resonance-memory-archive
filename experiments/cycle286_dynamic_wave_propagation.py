import sys
import os
import time
import json
import sqlite3
import numpy as np
from scipy.stats import pearsonr

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, RealityInterface

def run_experiment(seed, condition):
    """
    Runs an experiment to measure dynamic wave propagation.
    Conditions: 'sub' (E=0.100), 'super' (E=0.110), 'soc' (Adaptive).
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c286_Wave_{condition}_seed{seed}.db",
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001
    spawn_energy = 0.5
    max_population = 200 
    
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
        base_e = base_e_soc
        
    # Initialize Agents
    np.random.seed(seed)
    for i in range(100):
        init_e = np.random.uniform(0.8, 1.2)
        agent = FractalAgent(agent_id=f"init_{i}", energy=init_e)
        reality.add_agent(agent, population_id=0)
    
    # Run Simulation
    stabilization_steps = 500
    stimulation_steps = 1000
    total_steps = stabilization_steps + stimulation_steps
    
    current_e_consume = base_e
    
    # Signal Tracking
    input_signal = []
    output_signal = []
    
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
        
        for agent in list(agents):
            # Noise
            noise = np.random.normal(0, 0.1)
            agent.energy += noise
            
            agent.energy -= current_e_consume
            agent.energy += energy_gain
            
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
                continue
            
            if agent.energy > 1.5:
                agent.energy -= 0.5
                child = FractalAgent(agent_id=f"rep_{step}_{agent.agent_id}", energy=0.5)
                reality.add_agent(child, population_id=0)
                
        # Cap
        current_agents = reality.get_population_agents(0)
        if len(current_agents) > max_population:
            to_remove = len(current_agents) - max_population
            for _ in range(to_remove):
                victim = current_agents[np.random.randint(len(current_agents))]
                reality.remove_agent(victim.agent_id, 0)
            
        if len(reality.get_population_agents(0)) == 0:
            break
            
    # --- Phase 2: Stimulation ---
    # Identify Input Node (First 10% of agents by ID sort)
    agents = reality.get_population_agents(0)
    if agents:
        agents.sort(key=lambda x: x.agent_id)
        n_input = max(1, int(len(agents) * 0.1))
        input_ids = set(a.agent_id for a in agents[:n_input])
    else:
        input_ids = set()
        
    for step in range(stabilization_steps, total_steps):
        # Generate Signal
        t = step - stabilization_steps
        signal_val = 0.5 * np.sin(2 * np.pi * t / 50) # Period 50
        input_signal.append(signal_val)
        
        # Spawn
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
        
        output_energies = []
        
        for agent in list(agents):
            # Inject Signal into Input Node
            if agent.agent_id in input_ids:
                agent.energy += signal_val * 0.1 # Weak coupling
            
            # Noise
            noise = np.random.normal(0, 0.1)
            agent.energy += noise
            
            agent.energy -= current_e_consume
            agent.energy += energy_gain
            
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
                continue
            
            if agent.energy > 1.5:
                agent.energy -= 0.5
                child = FractalAgent(agent_id=f"rep_{step}_{agent.agent_id}", energy=0.5)
                reality.add_agent(child, population_id=0)
            
            # Measure Output (Non-Input Agents)
            if agent.agent_id not in input_ids:
                output_energies.append(agent.energy)
                
        # Cap
        current_agents = reality.get_population_agents(0)
        if len(current_agents) > max_population:
            to_remove = len(current_agents) - max_population
            for _ in range(to_remove):
                victim = current_agents[np.random.randint(len(current_agents))]
                reality.remove_agent(victim.agent_id, 0)
                
        # Record Output
        if output_energies:
            output_signal.append(np.mean(output_energies))
        else:
            output_signal.append(0)
            
        if len(reality.get_population_agents(0)) == 0:
            break

    runtime = time.time() - start_time
    reality.close()
    
    # Calculate Correlation
    if len(output_signal) > 100:
        # Use last 500 steps to avoid transient
        sig_in = input_signal[-500:]
        sig_out = output_signal[-500:]
        corr, _ = pearsonr(sig_in, sig_out)
    else:
        corr = 0
    
    return {
        "seed": seed,
        "condition": condition,
        "correlation": corr,
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 286: DYNAMIC WAVE PROPAGATION")
    print("===================================")
    print("Hypothesis: SOC state enables long-range signal propagation.")
    
    conditions = ['sub', 'super', 'soc']
    seeds = range(300, 310) # 10 seeds per condition
    
    results = []
    
    print(f"{'Condition':<10} | {'Mean Correlation':<20} | {'Std Dev':<15}")
    print("-" * 60)
    
    for cond in conditions:
        cond_results = []
        for seed in seeds:
            res = run_experiment(seed, cond)
            cond_results.append(res)
            results.append(res)
            
        # Stats
        corrs = [r['correlation'] for r in cond_results]
        # Filter out NaNs if any
        corrs = [c for c in corrs if not np.isnan(c)]
        
        if corrs:
            mean_corr = np.mean(corrs)
            std_corr = np.std(corrs)
        else:
            mean_corr = 0
            std_corr = 0
        
        print(f"{cond:<10} | {mean_corr:.4f}               | {std_corr:.4f}")
        
    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c286_wave_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n===================================")
    print("CAMPAIGN COMPLETE.")

if __name__ == "__main__":
    main()
