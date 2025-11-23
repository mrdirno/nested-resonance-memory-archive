import sys
import os
import time
import random
import numpy as np
from typing import List, Tuple
import scipy.signal

# Add project root and code directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.fractal.fractal_swarm import FractalSwarm
from src.fractal.agent import FractalAgent

def generate_signal_noise(cycles: int, target_freq: float, noise_level: float) -> Tuple[np.ndarray, np.ndarray]:
    """Generates a target sine wave with added noise."""
    # Use integer steps for time to match simulation steps
    t = np.arange(cycles)
    signal = np.sin(target_freq * t)
    noise = np.random.normal(0, noise_level, cycles)
    combined = signal + noise
    return combined, signal

def calculate_snr(signal: np.ndarray, noise: np.ndarray) -> float:
    """Calculates Signal-to-Noise Ratio in dB."""
    s_power = np.mean(signal ** 2)
    n_power = np.mean(noise ** 2)
    if n_power == 0: return 100.0
    return 10 * np.log10(s_power / n_power)

def get_swarm_phase(agents: List[FractalAgent]) -> float:
    """Calculates the mean phase of the swarm."""
    if not agents: return 0.0
    phases = np.array([a.state.phase for a in agents])
    # Mean phase vector
    z = np.mean(np.exp(1j * phases))
    return np.angle(z)

def spectral_filtering_test():
    print("--- SPECTRAL FILTERING EXPERIMENT (PAPER 11) ---")
    print("Hypothesis: Swarm Resonance Selectively Amplifies Target Frequency (Attention).")
    
    # Parameters
    CYCLES = 500
    TARGET_FREQ = 0.1 # Frequency relative to simulation step
    NOISE_LEVEL = 2.0 # High noise to test filtering
    
    # 1. Generate Input
    print(f"\n1. Generating Input (Target Freq={TARGET_FREQ}, Noise={NOISE_LEVEL})...")
    input_combined, input_clean = generate_signal_noise(CYCLES, TARGET_FREQ, NOISE_LEVEL)
    input_noise = input_combined - input_clean
    
    input_snr = calculate_snr(input_clean, input_noise)
    print(f"Input SNR: {input_snr:.2f} dB")
    
    # 2. Initialize Swarm
    print("\n2. Initializing Swarm...")
    swarm = FractalSwarm(max_agents=100, burst_threshold=200.0)
    # Initialize with random phases AND TUNED FREQUENCY
    
    for _ in range(50): 
        agent = swarm.spawn_agent(
            reality_metrics={}, 
            initial_energy=50.0, 
            phase=random.uniform(0, 2*np.pi)
        )
        if agent:
            # Set natural frequency to target frequency
            agent.state.velocity = TARGET_FREQ
        
    # 3. Run Injection
    print("\n3. Injecting Signal + Noise (PRC Method)...")
    swarm_output_phases = []
    order_parameters = []
    
    K = 0.5 # Coupling strength
    dt = 1.0 # Time step
    
    for i in range(CYCLES):
        signal_val = input_combined[i]
        
        active_agents = [a for a in swarm.agents.values() if a.is_active]
        
        # PRC INJECTION: Phase Response Curve
        # d(theta)/dt = omega + K * S(t) * cos(theta)
        
        for agent in active_agents:
            # Apply forcing term
            forcing = K * signal_val * np.cos(agent.state.phase)
            agent.state.phase += forcing * dt
            
        # Evolve (Natural Frequency)
        swarm.evolve_cycle(coupling_strength=0.5)
        
        # Measure Output Phase and Order Parameter
        if active_agents:
            phases = np.array([a.state.phase for a in active_agents])
            z = np.mean(np.exp(1j * phases))
            swarm_phase = np.angle(z)
            order_param = np.abs(z)
        else:
            swarm_phase = 0.0
            order_param = 0.0
            
        swarm_output_phases.append(swarm_phase)
        order_parameters.append(order_param)
        
    # 4. Analysis
    print("\n--- ANALYSIS ---")
    print(f"Mean Order Parameter: {np.mean(order_parameters):.4f}")
    
    # Convert Phase to Signal (Sine Wave) for comparison
    output_signal = np.sin(np.array(swarm_output_phases))
    
    # We need to extract the component at TARGET_FREQ from the output
    # Simple way: Correlate output with clean input sine wave
    correlation = np.corrcoef(input_clean, output_signal)[0, 1]
    print(f"Input-Output Correlation: {correlation:.4f}")
    
    # Estimate Output SNR
    f_in, Pxx_in = scipy.signal.periodogram(input_combined)
    f_out, Pxx_out = scipy.signal.periodogram(output_signal)
    
    f_clean, Pxx_clean = scipy.signal.periodogram(input_clean)
    target_idx = np.argmax(Pxx_clean)
    
    input_target_power = Pxx_in[target_idx]
    input_total_power = np.sum(Pxx_in)
    if input_total_power - input_target_power == 0:
        input_snr_spectral = 100.0
    else:
        input_snr_spectral = 10 * np.log10(input_target_power / (input_total_power - input_target_power))
    
    output_target_power = Pxx_out[target_idx]
    output_total_power = np.sum(Pxx_out)
    output_snr_spectral = 10 * np.log10(output_target_power / (output_total_power - output_target_power))
    
    print(f"Spectral Input SNR: {input_snr_spectral:.2f} dB")
    print(f"Spectral Output SNR: {output_snr_spectral:.2f} dB")
    
    gain = output_snr_spectral - input_snr_spectral
    print(f"SNR Gain: {gain:.2f} dB")
    
    if np.mean(order_parameters) > 0.8 and correlation > 0.9:
         print("SUCCESS: Swarm Locked to Signal (Zero Noise).")
    elif gain > 1.0:
        print("SUCCESS: Swarm amplified target signal (Filtering).")
    else:
        print("FAILURE: No significant locking or gain.")

if __name__ == "__main__":
    from typing import Tuple # Fix import
    spectral_filtering_test()
