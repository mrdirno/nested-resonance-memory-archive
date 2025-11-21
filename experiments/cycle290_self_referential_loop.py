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
    Runs an experiment to test Self-Referential Feedback.
    System monitors population variance and adjusts E_consume to maintain a target variance.
    Target Variance: 10.0 (Empirically chosen for criticality).
    """
    # Initialize Reality
    reality = RealityInterface(
        db_path=f"experiments/results/c290_SelfRef_seed{seed}.db",
        n_populations=1
    )
    
    # Configure Simulation Parameters
    spawn_rate = 0.0001
    spawn_energy = 0.5
    max_population = 200 
    
    # Feedback Loop Parameters
    target_variance = 10.0
    feedback_gain = 0.00005 # Slow, stable learning rate
    window_size = 50
    
    # Initial State (Sub-Critical)
    current_e_consume = 0.100 
    
    # Initialize Agents
    np.random.seed(seed)
    for i in range(100):
        init_e = np.random.uniform(0.8, 1.2)
        agent = FractalAgent(agent_id=f"init_{i}", energy=init_e)
        reality.add_agent(agent, population_id=0)
    
    # Run Simulation
    total_steps = 2000
    
    history_pop = []
    history_e = []
    history_variance = []
    
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
        
        # --- Self-Referential Feedback Loop ---
        if len(history_pop) >= window_size:
            # Observe Self (Variance over window)
            recent_pop = history_pop[-window_size:]
            current_variance = np.var(recent_pop)
            history_variance.append(current_variance)
            
            # Control Law
            # If Variance < Target (Too Stable) -> Decrease Stress (Allow more chaos) -> Wait, actually...
            # High Stress (E=0.110) -> Collapse (Low Variance, 0 pop) OR High Variance (if oscillating)?
            # Low Stress (E=0.100) -> Saturation (Low Variance, Max pop).
            # Critical (E=0.1045) -> High Variance (Avalanches).
            
            # So:
            # If Variance < Target -> We are likely Saturated (E too low) OR Collapsed (E too high).
            # This is non-monotonic. We need a directional heuristic or "Gradient Descent".
            
            # Simplified Heuristic for this cycle:
            # Assume we start at Sub-Critical (E=0.100, Saturated, Low Variance).
            # We want to increase E until Variance peaks.
            # If Variance < Target, Increase E (Add Stress).
            # If Variance > Target, Decrease E (Reduce Stress).
            
            error = target_variance - current_variance
            # If error > 0 (Variance too low), we want to move towards criticality.
            # Since we start at E=0.100 (Sub), we need to INCREASE E to get to 0.1045.
            # So Positive Error -> Positive Adjustment.
            
            adjustment = feedback_gain * error
            current_e_consume += adjustment
            
            # Clamp to safe range
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
    
    return {
        "seed": seed,
        "final_e": final_e,
        "mean_e_stable": mean_e_last_500,
        "final_pop": final_pop,
        "runtime_seconds": runtime
    }

def main():
    print("CYCLE 290: SELF-REFERENTIAL FEEDBACK LOOP")
    print("=========================================")
    print("Hypothesis: System can self-tune to criticality (E~0.1045) via Variance Feedback.")
    print("Starting E: 0.100 (Sub-Critical)")
    print("Target Variance: 10.0")
    
    seeds = range(700, 710) # 10 seeds
    
    results = []
    
    print(f"{'Seed':<10} | {'Final E':<15} | {'Mean E (Last 500)':<20} | {'Final Pop':<10}")
    print("-" * 65)
    
    for seed in seeds:
        res = run_experiment(seed)
        results.append(res)
        print(f"{seed:<10} | {res['final_e']:.5f}          | {res['mean_e_stable']:.5f}               | {res['final_pop']:<10}")
            
    # Stats
    final_es = [r['final_e'] for r in results]
    
    print("-" * 65)
    print(f"{'MEAN':<10} | {np.mean(final_es):.5f}")
    print(f"{'STD':<10} | {np.std(final_es):.5f}")
    print(f"CRITICAL TARGET: 0.1045")
        
    # Save
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c290_selfref_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\n=========================================")
    print("CAMPAIGN COMPLETE.")

if __name__ == "__main__":
    main()
