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

def run_experiment(seed, logic_case):
    """
    Runs an experiment to measure resonant logic response.
    Logic Cases:
    - 'constructive': Phase 0 (Input 1, 1)
    - 'single': Single Source (Input 1, 0)
    - 'destructive': Phase Pi (Input 1, -1) -> Simulates cancellation
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c288_Logic_{logic_case}_seed{seed}.db",
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
    drive_period = 5
    drive_freq = 1.0 / drive_period
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
            
    # --- Phase 2: Stimulation (Resonant Logic) ---
    for step in range(stabilization_steps, total_steps):
        # Generate Signals
        t = step - stabilization_steps
        
        # Signal 1 (Always On)
        s1 = amplitude * np.sin(2 * np.pi * t / drive_period)
        
        # Signal 2 (Conditional)
        if logic_case == 'constructive':
            s2 = amplitude * np.sin(2 * np.pi * t / drive_period) # In-Phase
        elif logic_case == 'destructive':
            s2 = amplitude * np.sin(2 * np.pi * t / drive_period + np.pi) # Out-of-Phase
        else: # single
            s2 = 0
            
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
    
    # Calculate Response Amplitude at Drive Frequency
    response_amp = 0
    if len(global_energy_signal) > 200:
        # Use last 500 steps
        sig = np.array(global_energy_signal[-500:])
        # Detrend
        sig = sig - np.mean(sig)
        
        f, Pxx = periodogram(sig)
        
        # Find power near drive freq
        idx = np.argmin(np.abs(f - drive_freq))
        power_at_freq = Pxx[idx]
        
        # Amplitude is proportional to sqrt(Power)
        response_amp = np.sqrt(power_at_freq)
    
    return {
        "seed": seed,
        "logic_case": logic_case,
        "response_amp": response_amp,
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 288: RESONANT LOGIC GATES")
    print("===============================")
    print("Hypothesis: SOC supports constructive/destructive interference.")
    
    cases = ['single', 'constructive', 'destructive']
    seeds = range(500, 510) # 10 seeds per case
    
    results = []
    
    print(f"{'Case':<15} | {'Mean Amplitude':<20} | {'Std Dev':<15}")
    print("-" * 60)
    
    for case in cases:
        case_results = []
        for seed in seeds:
            res = run_experiment(seed, case)
            case_results.append(res)
            results.append(res)
            
        # Stats
        amps = [r['response_amp'] for r in case_results]
        
        if amps:
            mean_amp = np.mean(amps)
            std_amp = np.std(amps)
        else:
            mean_amp = 0
            std_amp = 0
        
        print(f"{case:<15} | {mean_amp:.4f}               | {std_amp:.4f}")
        
    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c288_logic_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n===============================")
    print("CAMPAIGN COMPLETE.")

if __name__ == "__main__":
    main()
