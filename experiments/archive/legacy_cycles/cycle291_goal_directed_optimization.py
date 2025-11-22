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
    Runs an experiment to test Goal-Directed Optimization.
    System uses Perturb-and-Observe (Hill Climbing) to maximize a Reward Function.
    Reward = Variance * Stability
    Stability = 1 / (1 + Volatility of Variance)
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c291_GoalOpt_seed{seed}.db",
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001
    spawn_energy = 0.5
    max_population = 200 
    
    # Optimizer Parameters
    window_size = 50
    perturbation_step = 0.0005
    
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
    history_reward = []
    
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
        
        # --- Goal-Directed Optimization Loop ---
        if len(history_pop) >= window_size * 2 and step % window_size == 0:
            # Calculate Reward over last window
            recent_pop = history_pop[-window_size:]
            variance = np.var(recent_pop)
            
            # Calculate Stability (Inverse of Variance Volatility)
            # We need variance of variance? Or just change in variance?
            # Let's use change in variance from previous window
            prev_pop = history_pop[-2*window_size:-window_size]
            prev_variance = np.var(prev_pop)
            
            variance_change = abs(variance - prev_variance)
            stability = 1.0 / (1.0 + variance_change)
            
            # Reward Function: Maximize Variance but keep it Stable
            reward = variance * stability
            history_reward.append(reward)
            
            # Perturb-and-Observe Logic
            if last_reward != -1.0:
                delta_reward = reward - last_reward
                
                if delta_reward > 0:
                    # Keep going in same direction
                    pass
                else:
                    # Reverse direction
                    direction *= -1
            
            last_reward = reward
            
            # Apply Perturbation
            current_e_consume += direction * perturbation_step
            
            # Clamp
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
    final_pop = history_pop[-1]
    initial_e = history_e[0]
    
    return {
        "seed": seed,
        "initial_e": initial_e,
        "final_e": final_e,
        "mean_e_stable": mean_e_last_500,
        "final_pop": final_pop,
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 291: GOAL-DIRECTED OPTIMIZATION")
    print("=====================================")
    print("Hypothesis: System can autonomously maximize Complexity Reward.")
    print("Reward = Variance * Stability")
    
    seeds = range(800, 810) # 10 seeds
    
    results = []
    
    print(f"{'Seed':<10} | {'Initial E':<15} | {'Final E':<15} | {'Mean E (Last 500)':<20}")
    print("-" * 70)
    
    for seed in seeds:
        res = run_experiment(seed)
        results.append(res)
        print(f"{seed:<10} | {res['initial_e']:.5f}          | {res['final_e']:.5f}          | {res['mean_e_stable']:.5f}")
            
    # Stats
    final_es = [r['final_e'] for r in results]
    
    print("-" * 70)
    print(f"{'MEAN':<10} | {'N/A':<15} | {np.mean(final_es):.5f}")
    print(f"{'STD':<10} | {'N/A':<15} | {np.std(final_es):.5f}")
    print(f"CRITICAL TARGET: 0.1045")
        
    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c291_goalopt_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n=====================================")
    print("CAMPAIGN COMPLETE.")

if __name__ == "__main__":
    main()
