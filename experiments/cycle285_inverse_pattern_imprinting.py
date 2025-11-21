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
    Runs an experiment to measure pattern persistence (Inverse Engineering).
    Conditions: 'sub' (E=0.100), 'super' (E=0.110), 'soc' (Adaptive).
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c285_Pattern_{condition}_seed{seed}.db",
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001
    spawn_energy = 0.5
    max_population = 200 # Reduced to force turnover in Sub
    
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
        
    # Initialize Agents with Diversity
    np.random.seed(seed)
    for i in range(100):
        init_e = np.random.uniform(0.8, 1.2)
        agent = FractalAgent(agent_id=f"init_{i}", energy=init_e)
        reality.add_agent(agent, population_id=0)
    
    # Run Simulation
    stabilization_steps = 500
    post_imprint_steps = 2000 # Increased duration
    total_steps = stabilization_steps + post_imprint_steps
    
    current_e_consume = base_e
    
    # Data for Pattern Tracking
    imprinted_cohort = {} # {agent_id: target_energy}
    history_correlation = []
    
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
            # Add Noise (Entropy)
            noise = np.random.normal(0, 10.0) # Extreme Noise
            agent.energy += noise
            
            # DEBUG
            if step % 100 == 0 and agent.agent_id == agents[0].agent_id:
                print(f"DEBUG: Step {step}, Agent {agent.agent_id}, Noise {noise:.4f}, Energy {agent.energy:.4f}, ID {id(agent)}")
            
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
            
    # --- Phase 2: Imprinting ---
    # Get current agents
    agents = reality.get_population_agents(0)
    if agents:
        # Sort by ID to have a deterministic order
        agents.sort(key=lambda x: x.agent_id)
        N = len(agents)
        
        # Imprint Sine Wave Pattern
        # E_i = 1.0 + 0.5 * sin(2*pi * i / N)
        for i, agent in enumerate(agents):
            target_e = 1.0 + 0.5 * np.sin(2 * np.pi * i / N)
            agent.energy = target_e # Force set
            imprinted_cohort[agent.agent_id] = target_e
            
    # --- Phase 3: Persistence ---
    persistence_steps = 0
    pattern_lost = False
    
    for step in range(stabilization_steps, total_steps):
        # Same Dynamics Loop...
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
        
        for agent in list(agents):
            # Add Noise (Entropy)
            noise = np.random.normal(0, 0.1) # Reasonable Noise
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
                
        current_agents = reality.get_population_agents(0)
        if len(current_agents) > max_population:
            to_remove = len(current_agents) - max_population
            for _ in range(to_remove):
                victim = current_agents[np.random.randint(len(current_agents))]
                reality.remove_agent(victim.agent_id, 0)
                
        # Measure Correlation
        current_survivors = []
        targets = []
        
        # Only check agents that were part of the imprinted cohort
        surviving_agents = [a for a in reality.get_population_agents(0) if a.agent_id in imprinted_cohort]
        
        if len(surviving_agents) > 2:
            for a in surviving_agents:
                current_survivors.append(a.energy)
                targets.append(imprinted_cohort[a.agent_id])
                
            # Pearson Correlation
            corr, _ = pearsonr(current_survivors, targets)
            history_correlation.append(corr)
            
            # DEBUG
            if step % 100 == 0:
                print(f"Step {step}: Corr={corr:.4f}, Survivors={len(surviving_agents)}, SampleE={surviving_agents[0].energy:.4f}")
            
            if not pattern_lost:
                if corr > 0.5: # Threshold for "Pattern Exists"
                    persistence_steps += 1
                else:
                    pattern_lost = True
        else:
            history_correlation.append(0)
            pattern_lost = True
            
        if len(reality.get_population_agents(0)) == 0:
            break

    runtime = time.time() - start_time
    reality.close()
    
    return {
        "seed": seed,
        "condition": condition,
        "persistence_steps": persistence_steps,
        "final_correlation": history_correlation[-1] if history_correlation else 0,
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 285: INVERSE PATTERN IMPRINTING")
    print("=====================================")
    print("Hypothesis: SOC state sustains imprinted patterns longer.")
    
    conditions = ['sub', 'super', 'soc']
    seeds = range(200, 210) # 10 seeds per condition
    
    results = []
    
    print(f"{'Condition':<10} | {'Mean Persistence (Steps)':<25} | {'Survival Rate':<15}")
    print("-" * 60)
    
    for cond in conditions:
        cond_results = []
        for seed in seeds:
            res = run_experiment(seed, cond)
            cond_results.append(res)
            results.append(res)
            
        # Stats
        persistence_times = [r['persistence_steps'] for r in cond_results]
        mean_persistence = np.mean(persistence_times)
        std_persistence = np.std(persistence_times)
        
        print(f"{cond:<10} | {mean_persistence:.1f} +/- {std_persistence:.1f}          | N/A")
        
    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c285_pattern_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n=====================================")
    print("CAMPAIGN COMPLETE.")

if __name__ == "__main__":
    main()
