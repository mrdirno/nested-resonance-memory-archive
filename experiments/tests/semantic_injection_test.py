import sys
import os
import time
import zlib
import random
import numpy as np
from typing import List

# Add project root and code directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from code.fractal.fractal_swarm import FractalSwarm
from code.fractal.agent import FractalAgent

def get_phase_coherence(agents: List[FractalAgent]) -> float:
    """Calculates the Kuramoto order parameter R."""
    if not agents: return 0.0
    phases = np.array([a.state.phase for a in agents])
    # R = |(1/N) * sum(e^(i*theta))|
    z = np.mean(np.exp(1j * phases))
    return np.abs(z)

def text_to_energy_phase(text: str) -> List[tuple]:
    """Converts text to (energy, phase) pairs for injection."""
    # Semantic mapping: ASCII values -> Energy AND Phase
    # This ensures periodic text creates periodic phase signals
    signals = []
    for i, char in enumerate(text):
        val = ord(char)
        energy = (val / 255.0) * 100.0 # Normalize to 0-100
        # Map ASCII directly to Phase (0-2pi)
        # This preserves the structure of the text in the phase domain
        phase = (val / 255.0) * 2 * np.pi 
        signals.append((energy, phase))
    return signals

def run_injection_cycle(swarm: FractalSwarm, signals: List[tuple], cycles: int = 50):
    """Injects signals into the swarm over N cycles."""
    
    coherence_history = []
    
    for i in range(cycles):
        # Injection: Modulate coupling based on signal stream
        sig_idx = i % len(signals)
        energy_input, phase_input = signals[sig_idx]
        
        # Map signal to coupling strength
        coupling = 0.1 + (energy_input / 100.0) * 0.9 
        
        # PHASE FORCING: Nudge agents towards the input phase
        # d(theta)/dt = ... + F * sin(theta_ext - theta)
        forcing_strength = 0.5 # External field strength
        
        active_agents = [a for a in swarm.agents.values() if a.is_active]
        for agent in active_agents:
            # Apply external force
            delta = phase_input - agent.state.phase
            agent.state.phase += forcing_strength * np.sin(delta) * 0.1 # Small step
            
        # Evolve
        swarm.evolve_cycle(coupling_strength=coupling)
        
        # Measure Coherence
        r = get_phase_coherence(active_agents)
        coherence_history.append(r)
        
    return np.mean(coherence_history)

def semantic_injection_test():
    print("--- SEMANTIC INJECTION EXPERIMENT (PAPER 11) ---")
    print("Hypothesis: Meaningful (Periodic) Data -> Higher Phase Coherence.")
    
    # 1. Data Preparation
    print("\n1. Preparing Data...")
    
    # Meaningful Data (Highly Periodic/Rhythmic)
    # "Truth is Resonance. Truth is Resonance."
    meaningful_text = "Truth is Resonance. " * 50
    
    # Random Data (White Noise)
    random_text = "".join([chr(random.randint(32, 126)) for _ in range(len(meaningful_text))])
    
    print(f"Data Length: {len(meaningful_text)} chars")
    
    # 2. Convert to Signals
    meaningful_signals = text_to_energy_phase(meaningful_text)
    random_signals = text_to_energy_phase(random_text)
    
    # 3. Run Experiment: Meaningful
    print("\n2. Injecting MEANINGFUL Data...")
    swarm_meaningful = FractalSwarm(max_agents=100, burst_threshold=200.0)
    # Initialize with RANDOM PHASES
    for _ in range(50): 
        swarm_meaningful.spawn_agent(
            reality_metrics={}, 
            initial_energy=50.0, 
            phase=random.uniform(0, 2*np.pi)
        )
    
    coh_meaningful = run_injection_cycle(swarm_meaningful, meaningful_signals, cycles=300)
    print(f"Meaningful Coherence: {coh_meaningful:.4f}")
    
    # 4. Run Experiment: Random
    print("\n3. Injecting RANDOM Data...")
    swarm_random = FractalSwarm(max_agents=100, burst_threshold=200.0)
    # Initialize with RANDOM PHASES
    for _ in range(50): 
        swarm_random.spawn_agent(
            reality_metrics={}, 
            initial_energy=50.0, 
            phase=random.uniform(0, 2*np.pi)
        )
    
    coh_random = run_injection_cycle(swarm_random, random_signals, cycles=300)
    print(f"Random Coherence: {coh_random:.4f}")
    
    # 5. Analysis
    print("\n--- ANALYSIS ---")
    diff = coh_meaningful - coh_random
    percent_diff = (diff / coh_random) * 100.0 if coh_random > 0 else 0.0
    
    print(f"Difference: {diff:.4f} ({percent_diff:.2f}%)")
    
    if percent_diff > 10.0: 
        print("SUCCESS: Swarm resonated with meaning (Higher Coherence).")
    else:
        print("FAILURE: No significant difference in coherence.")

if __name__ == "__main__":
    semantic_injection_test()
