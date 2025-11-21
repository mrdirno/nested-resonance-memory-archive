import sys
import os
import time
import json
import sqlite3
import numpy as np
from scipy.signal import periodogram

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, RealityInterface

def run_experiment(seed, condition):
    """
    Runs an experiment to measure resonance entrainment.
    Conditions: 'sub' (E=0.100), 'super' (E=0.110), 'soc' (Adaptive).
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c287_Resonance_{condition}_seed{seed}.db",
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
    global_energy_signal = []
    
    # Drive Parameters
    drive_period = 5
    drive_freq = 1.0 / drive_period
    
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
            
    # --- Phase 2: Stimulation (Global Drive) ---
    # No specific input node - drive the entire field
        
    for step in range(stabilization_steps, total_steps):
        # Generate Signal
        t = step - stabilization_steps
        signal_val = 0.5 * np.sin(2 * np.pi * t / drive_period)
        
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
        
        total_energy = 0
        
        for agent in list(agents):
            # Global Drive: All agents feel the field
            agent.energy += signal_val * 0.1 # Weak global coupling
            
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
            
            total_energy += agent.energy
                
        # Cap
        current_agents = reality.get_population_agents(0)
        if len(current_agents) > max_population:
            to_remove = len(current_agents) - max_population
            for _ in range(to_remove):
                victim = current_agents[np.random.randint(len(current_agents))]
                reality.remove_agent(victim.agent_id, 0)
                
        # Record Global Energy
        global_energy_signal.append(total_energy)
        
        # DEBUG
        if step % 100 == 0:
            print(f"Step {step}: Signal={signal_val:.4f}, TotalE={total_energy:.4f}, Pop={len(current_agents)}")
            
        if len(reality.get_population_agents(0)) == 0:
            break

    runtime = time.time() - start_time
    reality.close()
    
    # Calculate Entrainment Score (PSD at drive freq)
    entrainment_score = 0
    if len(global_energy_signal) > 200:
        # Use last 500 steps
        sig = np.array(global_energy_signal[-500:])
        # Detrend
        sig = sig - np.mean(sig)
        
        f, Pxx = periodogram(sig)
        
        # Find power near drive freq
        idx = np.argmin(np.abs(f - drive_freq))
        power_at_freq = Pxx[idx]
        total_power = np.sum(Pxx)
        
        if total_power > 0:
            entrainment_score = power_at_freq / total_power
    
    return {
        "seed": seed,
        "condition": condition,
        "entrainment_score": entrainment_score,
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 287: RESONANCE ENTRAINMENT")
    print("================================")
    print("Hypothesis: SOC state is most susceptible to entrainment.")
    
    conditions = ['sub', 'super', 'soc']
    seeds = range(400, 410) # 10 seeds per condition
    
    results = []
    
    print(f"{'Condition':<10} | {'Mean Entrainment Score':<25} | {'Std Dev':<15}")
    print("-" * 60)
    
    for cond in conditions:
        cond_results = []
        for seed in seeds:
            res = run_experiment(seed, cond)
            cond_results.append(res)
            results.append(res)
            
        # Stats
        scores = [r['entrainment_score'] for r in cond_results]
        
        if scores:
            mean_score = np.mean(scores)
            std_score = np.std(scores)
        else:
            mean_score = 0
            std_score = 0
        
        print(f"{cond:<10} | {mean_score:.4f}                    | {std_score:.4f}")
        
    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c287_resonance_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n================================")
    print("CAMPAIGN COMPLETE.")

if __name__ == "__main__":
    main()
