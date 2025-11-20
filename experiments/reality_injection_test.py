import sys
import os
import time
import psutil
import numpy as np
from typing import Dict, List

# Add project root and code directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from code.fractal.fractal_swarm import FractalSwarm
from code.fractal.agent import FractalAgent

def reality_injection_test():
    print("--- REALITY INJECTION EXPERIMENT (PAPER 10) ---")
    print("Hypothesis: External Entropy (Reality) stabilizes Swarm Dynamics.")
    
    # 1. Configuration
    config = {
        "cycles": 500,
        "agent_count": 100,
        "base_coupling": 0.1,
        "base_resource": 1.0
    }
    
    # 2. Initialize Swarm
    swarm = FractalSwarm(max_agents=1000, burst_threshold=200.0)
    
    for i in range(config["agent_count"]):
        swarm.spawn_agent(reality_metrics={}, initial_energy=100.0)
        
    print(f"Initial State: {len(swarm.agents)} agents")
    
    # 3. Run Simulation with Reality Injection
    history = []
    
    # 3. Run Simulation with Reality Injection
    history = []
    
    print("Injecting Wall Clock Time Signal (Open System)...")
    start_wall_time = time.time()
    
    for cycle in range(config["cycles"]):
        # --- REALITY INJECTION ---
        # Use Wall Clock Time (External) instead of Cycle Count (Internal)
        current_time = time.time() - start_wall_time
        
        # Create a signal based on REAL TIME (0.5 Hz oscillation)
        # This couples the simulation speed to the physical clock
        reality_signal = 0.5 + 0.4 * np.sin(current_time * np.pi) 
        
        # Map to Swarm Parameters
        coupling_strength = reality_signal
        
        # Log Injection
        if cycle % 50 == 0:
            print(f"Cycle {cycle}: Time={current_time:.2f}s -> Signal={reality_signal:.2f}")
            
        # Apply Pooling
        active_agents = [a for a in swarm.agents.values() if a.is_active]
        if active_agents:
            swarm.energy_pooling_cycle(active_agents, sharing_fraction=0.2)
            
        # Evolve with Injected Parameters
        metrics = swarm.evolve_cycle(coupling_strength=coupling_strength)
        
        # Record Metrics
        history.append({
            "cycle": cycle,
            "time": current_time,
            "signal": reality_signal,
            "agents": metrics["active_agents"],
            "energy": metrics["total_energy"]
        })
        
        # Sleep slightly to ensure time passes (simulating computation cost)
        time.sleep(0.01)

    # 4. Analysis
    print("\n--- ANALYSIS ---")
    agents = [h["agents"] for h in history]
    energies = [h["energy"] for h in history]
    signals = [h["signal"] for h in history]
    
    # Correlation
    corr_agents = np.corrcoef(signals, agents)[0, 1]
    corr_energy = np.corrcoef(signals, energies)[0, 1]
    
    print(f"Correlation (Signal vs Agents): {corr_agents:.4f}")
    print(f"Correlation (Signal vs Energy): {corr_energy:.4f}")
    
    final_pop = agents[-1]
    print(f"Final Population: {final_pop}")
    
    # Success if EITHER agents OR energy correlates
    if abs(corr_agents) > 0.1 or abs(corr_energy) > 0.1:
        print("SUCCESS: Swarm dynamics are coupled to Wall Clock Time.")
    else:
        print("FAILURE: No significant coupling observed.")

if __name__ == "__main__":
    reality_injection_test()
