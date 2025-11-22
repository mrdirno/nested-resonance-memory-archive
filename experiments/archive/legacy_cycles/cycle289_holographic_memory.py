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

def run_experiment(seed):
    """
    Runs an experiment to measure holographic memory (frequency multiplexing).
    Injects two orthogonal frequencies: f1=0.1, f2=0.2.
    Checks for spectral peaks at f1, f2 and absence of intermodulation.
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c289_Holographic_seed{seed}.db",
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001
    spawn_energy = 0.5
    max_population = 200 
    
    # SOC Parameters (Fixed to Critical State)
    base_e_soc = 0.1
    gain_soc = 0.0001
    target_pop_soc = 50
    
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
    
    current_e_consume = base_e_soc
    
    # Signal Tracking
    global_energy_signal = []
    
    # Drive Parameters
    f1 = 0.1
    f2 = 0.2
    amplitude = 0.5
    
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
            
    # --- Phase 2: Stimulation (Holographic Multiplexing) ---
    for step in range(stabilization_steps, total_steps):
        # Generate Signal
        t = step - stabilization_steps
        
        # Composite Signal: S(t) = A*sin(2pi*f1*t) + A*sin(2pi*f2*t)
        s1 = amplitude * np.sin(2 * np.pi * f1 * t)
        s2 = amplitude * np.sin(2 * np.pi * f2 * t)
        total_signal = s1 + s2
        
        # Spawn
        if np.random.random() < spawn_rate:
            agent = FractalAgent(agent_id=f"spawn_{step}", energy=spawn_energy)
            reality.add_agent(agent, population_id=0)
            
        agents = reality.get_population_agents(0)
        current_pop = len(agents)
        
        # SOC Logic
        deviation = current_pop - target_pop_soc
        adjustment = gain_soc * deviation
        current_e_consume = base_e_soc + adjustment
        current_e_consume = max(0.100, min(0.110, current_e_consume))
            
        resource_inflow = 10.0
        energy_gain = resource_inflow / current_pop if current_pop > 0 else 0
        
        total_energy = 0
        
        for agent in list(agents):
            # Global Drive
            agent.energy += total_signal * 0.1 # Weak global coupling
            
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
            
        if len(reality.get_population_agents(0)) == 0:
            break

    runtime = time.time() - start_time
    reality.close()
    
    # Calculate Spectral Power
    p_f1 = 0
    p_f2 = 0
    p_intermod = 0 # f1 + f2 = 0.3
    
    if len(global_energy_signal) > 200:
        # Use last 500 steps
        sig = np.array(global_energy_signal[-500:])
        # Detrend
        sig = sig - np.mean(sig)
        
        f, Pxx = periodogram(sig)
        
        # Find power at frequencies
        idx_f1 = np.argmin(np.abs(f - f1))
        idx_f2 = np.argmin(np.abs(f - f2))
        idx_im = np.argmin(np.abs(f - (f1 + f2)))
        
        p_f1 = Pxx[idx_f1]
        p_f2 = Pxx[idx_f2]
        p_intermod = Pxx[idx_im]
    
    return {
        "seed": seed,
        "power_f1": p_f1,
        "power_f2": p_f2,
        "power_intermod": p_intermod,
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 289: HOLOGRAPHIC ASSOCIATIVE MEMORY")
    print("=========================================")
    print("Hypothesis: SOC supports frequency multiplexing (Orthogonality).")
    
    seeds = range(600, 610) # 10 seeds
    
    results = []
    
    print(f"{'Seed':<10} | {'Power f1 (0.1)':<15} | {'Power f2 (0.2)':<15} | {'Intermod (0.3)':<15}")
    print("-" * 65)
    
    for seed in seeds:
        res = run_experiment(seed)
        results.append(res)
        print(f"{seed:<10} | {res['power_f1']:.4f}          | {res['power_f2']:.4f}          | {res['power_intermod']:.4f}")
            
    # Stats
    p1 = [r['power_f1'] for r in results]
    p2 = [r['power_f2'] for r in results]
    pim = [r['power_intermod'] for r in results]
    
    print("-" * 65)
    print(f"{'MEAN':<10} | {np.mean(p1):.4f}          | {np.mean(p2):.4f}          | {np.mean(pim):.4f}")
    print(f"{'STD':<10} | {np.std(p1):.4f}          | {np.std(p2):.4f}          | {np.std(pim):.4f}")
        
    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c289_holographic_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n=========================================")
    print("CAMPAIGN COMPLETE.")

if __name__ == "__main__":
    main()
