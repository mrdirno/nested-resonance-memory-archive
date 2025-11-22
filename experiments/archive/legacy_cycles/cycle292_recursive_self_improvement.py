import sys
import os
import time
import json
import sqlite3
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, RealityInterface

def run_experiment(seed):
    """
    Runs an experiment to test Recursive Self-Improvement (Meta-Learning).
    System optimizes E_consume using Perturb-and-Observe.
    AND optimizes its own Learning Rate (Step Size) based on performance.
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c292_MetaOpt_seed{seed}.db",
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001
    spawn_energy = 0.5
    max_population = 200 
    
    # Optimizer Parameters
    window_size = 50
    
    # Meta-Learning State
    current_step_size = 0.001 # Start relatively high
    min_step_size = 0.0001
    max_step_size = 0.005
    
    reward_history = [] # List of (reward, direction_sign)
    
    # Initial State (Random Start)
    np.random.seed(seed)
    current_e_consume = np.random.uniform(0.100, 0.110)
    
    # Initialize Agents
    for i in range(100):
        init_e = np.random.uniform(0.8, 1.2)
        agent = FractalAgent(agent_id=f"init_{i}", energy=init_e)
        reality.add_agent(agent, population_id=0)
    
    # Run Simulation
    total_steps = 2500
    
    history_pop = []
    history_e = []
    history_step_size = []
    
    # Optimization State
    last_reward = -1.0
    direction = 1 # +1 or -1
    
    start_time = time.time()
    
    for step in range(total_steps):
        # Spawn
        if np.random.random() < spawn_rate:
            agent = FractalAgent(agent_id=f"spawn_{step}", energy=spawn_energy)
            reality.add_agent(agent, population_id=0)
            
        # Agent Dynamics
        agents = reality.get_population_agents(0)
        current_pop = len(agents)
        history_pop.append(current_pop)
        
        # --- Recursive Optimization Loop ---
        if len(history_pop) >= window_size * 2 and step % window_size == 0:
            # 1. Calculate Reward
            recent_pop = history_pop[-window_size:]
            variance = np.var(recent_pop)
            
            prev_pop = history_pop[-2*window_size:-window_size]
            prev_variance = np.var(prev_pop)
            
            variance_change = abs(variance - prev_variance)
            stability = 1.0 / (1.0 + variance_change)
            
            reward = variance * stability
            
            # 2. Meta-Learning (Tune Step Size)
            if last_reward != -1.0:
                delta_reward = reward - last_reward
                
                # Track improvement sign
                reward_sign = 1 if delta_reward > 0 else -1
                reward_history.append(reward_sign)
                
                # Look at recent history (last 3 updates)
                if len(reward_history) >= 3:
                    recent_signs = reward_history[-3:]
                    
                    # If consistently improving (+, +, +), Accelerate
                    if all(s > 0 for s in recent_signs):
                        current_step_size *= 1.2
                        
                    # If oscillating (+, -, + or -, +, -), Dampen
                    # Simple check: if signs are not all same, dampen?
                    # Or specifically check for oscillation.
                    # Let's just say if we had a negative result recently, dampen.
                    elif any(s < 0 for s in recent_signs):
                         current_step_size *= 0.8
                
                # Clamp Step Size
                current_step_size = max(min_step_size, min(max_step_size, current_step_size))
                
                # 3. Base Optimization (Tune E)
                if delta_reward > 0:
                    # Keep direction
                    pass
                else:
                    # Reverse direction
                    direction *= -1
            
            last_reward = reward
            history_step_size.append(current_step_size)
            
            # Apply Perturbation
            current_e_consume += direction * current_step_size
            
            # Clamp E
            current_e_consume = max(0.100, min(0.110, current_e_consume))
            
        history_e.append(current_e_consume)
        
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

    runtime = time.time() - start_time
    reality.close()
    
    # Metrics
    final_e = history_e[-1]
    mean_e_last_500 = np.mean(history_e[-500:]) if len(history_e) > 500 else final_e
    final_step_size = history_step_size[-1] if history_step_size else current_step_size
    initial_step_size = 0.001
    
    return {
        "seed": seed,
        "final_e": final_e,
        "mean_e_stable": mean_e_last_500,
        "final_step_size": final_step_size,
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 292: RECURSIVE SELF-IMPROVEMENT")
    print("=====================================")
    print("Hypothesis: System can optimize its own Learning Rate.")
    print("Initial Step Size: 0.001")
    
    seeds = range(900, 910) # 10 seeds
    
    results = []
    
    print(f"{'Seed':<10} | {'Final E':<15} | {'Final Step Size':<20} | {'Mean E (Last 500)':<20}")
    print("-" * 75)
    
    for seed in seeds:
        res = run_experiment(seed)
        results.append(res)
        print(f"{seed:<10} | {res['final_e']:.5f}          | {res['final_step_size']:.6f}             | {res['mean_e_stable']:.5f}")
            
    # Stats
    final_es = [r['final_e'] for r in results]
    final_steps = [r['final_step_size'] for r in results]
    
    print("-" * 75)
    print(f"{'MEAN':<10} | {np.mean(final_es):.5f}          | {np.mean(final_steps):.6f}")
    print(f"{'STD':<10} | {np.std(final_es):.5f}          | {np.std(final_steps):.6f}")
    print(f"CRITICAL TARGET: 0.1045")
        
    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c292_metaopt_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n=====================================")
    print("CAMPAIGN COMPLETE.")

if __name__ == "__main__":
    main()
