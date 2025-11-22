import sys
import os
import time
import json
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, RealityInterface

class ParameterizedFractalAgent(FractalAgent):
    """
    Extended agent with individual metabolic rate.
    """
    def __init__(self, agent_id, population_id=0, energy=1.0, metabolic_rate=0.1):
        super().__init__(agent_id, population_id, energy)
        self.metabolic_rate = metabolic_rate

def run_experiment(seed, condition):
    """
    Runs a single experiment comparing parameter variance vs state variance.
    
    Conditions:
    - "STATE_VARIANCE": Uniform metabolic rate (0.105), Variable Energy (sigma=0.1)
    - "PARAM_VARIANCE": Variable metabolic rate (mean=0.105, sigma=0.01), Uniform Energy (1.0)
    - "BOTH": Both variable
    - "CONTROL": Neither (Uniform 0.105, Uniform 1.0) - Expect extinction
    """
    reality = RealityInterface(db_path=None, n_populations=1)
    
    # Simulation Constants
    N_AGENTS = 100
    MAX_STEPS = 5000
    RESOURCE_INFLOW = 10.0
    SPAWN_RATE = 0.0001
    MAX_POP = 1000
    
    # Baseline
    base_metabolic = 0.105
    base_energy = 1.0
    
    np.random.seed(seed)
    
    # Initialize Agents based on condition
    for i in range(N_AGENTS):
        if condition == "STATE_VARIANCE":
            e_init = np.clip(np.random.normal(base_energy, 0.1), 0.1, 2.0)
            met_rate = base_metabolic
        elif condition == "PARAM_VARIANCE":
            e_init = base_energy
            # Metabolic rate variance (std=0.01 -> 10% of mean)
            met_rate = np.clip(np.random.normal(base_metabolic, 0.01), 0.05, 0.2)
        elif condition == "BOTH":
            e_init = np.clip(np.random.normal(base_energy, 0.1), 0.1, 2.0)
            met_rate = np.clip(np.random.normal(base_metabolic, 0.01), 0.05, 0.2)
        else: # CONTROL
            e_init = base_energy
            met_rate = base_metabolic
            
        agent = ParameterizedFractalAgent(f"init_{i}", energy=e_init, metabolic_rate=met_rate)
        reality.add_agent(agent, 0)
        
    # Run
    history = []
    
    for step in range(MAX_STEPS):
        # Spawn (Inherits baseline traits for simplicity, or random?)
        # Let's say new spawns are baseline to test if initial population adapts
        if np.random.random() < SPAWN_RATE:
            # Spawns introduce noise? Let's say spawns are noisy too to maintain diversity potential
            spawn_met = np.clip(np.random.normal(base_metabolic, 0.01), 0.05, 0.2) if "PARAM" in condition else base_metabolic
            agent = ParameterizedFractalAgent(f"spawn_{step}", energy=0.5, metabolic_rate=spawn_met)
            reality.add_agent(agent, 0)
            
        agents = reality.get_population_agents(0)
        if not agents:
            break
            
        # Resource Distribution
        share = RESOURCE_INFLOW / len(agents)
        
        # Update
        for agent in list(agents):
            # Use agent's individual metabolic rate if it has one, else baseline
            cost = getattr(agent, 'metabolic_rate', base_metabolic)
            
            agent.energy -= cost
            agent.energy += share
            
            if agent.energy <= 0:
                reality.remove_agent(agent.agent_id, 0)
                continue
                
            if agent.energy > 1.5:
                agent.energy -= 0.5
                # Child inherits parent's metabolic rate (Heredity)
                child_met = getattr(agent, 'metabolic_rate', base_metabolic)
                
                child = ParameterizedFractalAgent(f"rep_{step}_{agent.agent_id}", energy=0.5, metabolic_rate=child_met)
                reality.add_agent(child, 0)
                
        # Cap
        current = reality.get_population_agents(0)
        if len(current) > MAX_POP:
            for _ in range(len(current) - MAX_POP):
                victim = current[np.random.randint(len(current))]
                reality.remove_agent(victim.agent_id, 0)
                
        history.append(len(current))
        
    final_pop = history[-1] if history else 0
    mean_pop = np.mean(history[-500:]) if len(history) > 500 else final_pop
    
    # Calculate final trait distribution if survived
    final_traits = []
    if final_pop > 0:
        agents = reality.get_population_agents(0)
        final_traits = [getattr(a, 'metabolic_rate', base_metabolic) for a in agents]
    
    reality.close()
    
    return {
        "condition": condition,
        "seed": seed,
        "final_pop": final_pop,
        "mean_pop": mean_pop,
        "survived": final_pop > 0,
        "mean_final_metabolic": np.mean(final_traits) if final_traits else 0.0,
        "std_final_metabolic": np.std(final_traits) if final_traits else 0.0
    }

def main():
    print("CYCLE 285: PARAMETER VARIANCE vs STATE VARIANCE")
    print("=============================================")
    print("Hypothesis: Parameter variance allows evolution (selection of efficient agents),")
    print("            whereas State variance is transient buffering.")
    
    conditions = ["CONTROL", "STATE_VARIANCE", "PARAM_VARIANCE", "BOTH"]
    seeds = range(1000, 1020) # 20 seeds
    
    results = []
    
    for cond in conditions:
        print(f"\nCondition: {cond}")
        batch_res = []
        for seed in seeds:
            res = run_experiment(seed, cond)
            batch_res.append(res)
            results.append(res)
            
        survival = sum(1 for r in batch_res if r['survived'])
        avg_pop = np.mean([r['final_pop'] for r in batch_res])
        avg_met = np.mean([r['mean_final_metabolic'] for r in batch_res if r['survived']]) if survival > 0 else 0.0
        
        print(f"  Survival: {survival}/20 ({survival/20*100:.0f}%)")
        print(f"  Mean Pop: {avg_pop:.1f}")
        if survival > 0 and cond in ["PARAM_VARIANCE", "BOTH"]:
            print(f"  Final Mean Metabolic Rate: {avg_met:.4f} (Started at 0.105)")
            # If < 0.105, evolution happened

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c285_param_vs_state.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
