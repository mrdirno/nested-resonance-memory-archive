#!/usr/bin/env python3
"""
CYCLE 2568: The Starving Philosopher
=====================================
Empirically demonstrate that ignorance can be an economically optimal strategy under scarcity.

Hypothesis:
    An agent that selects its perceptual scale by minimizing a computational potential
    will voluntarily increase prediction error E_pred in order to reduce metabolic cost
    E_comp when its energy reserves e_buffer fall below a critical threshold.

Control Law:
    V(s) = E_pred(s) + λ(e_buffer) * β * E_comp(s)

    where λ(e_buffer) = k / (ε + e_buffer)  [metabolic pressure]

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Config:
    """Experiment parameters from spec."""
    # Simulation
    T: int = 1000  # Total time steps

    # Scales (window sizes / downsampling factors)
    scales: List[int] = None

    # Signal parameters
    A_trend: float = 10.0      # Macro trend amplitude
    A_detail: float = 2.0      # Micro detail amplitude
    omega_low: float = 0.02    # Low angular frequency (slow trend)
    omega_high: float = 0.3    # High angular frequency (fast nuances)
    sigma_noise: float = 0.5   # White noise std dev

    # Metabolic parameters
    k: float = 50.0            # Sensitivity constant for λ (increased)
    epsilon: float = 1.0       # Prevents division by zero
    beta: float = 1e-4         # Normalizer (increased for clearer effect)

    # Hysteresis
    gamma: float = 5.0         # Switching threshold (increased to prevent oscillation)

    # Energy dynamics
    e_buffer_init: float = 100.0  # Initial energy
    drain_rate: float = 0.25      # Energy drain per step in Phase 2

    # Phase boundaries
    phase1_end: int = 400      # Golden Age ends
    phase2_end: int = 800      # Collapse ends, Dark Age begins

    def __post_init__(self):
        if self.scales is None:
            self.scales = [1, 5, 10, 50]


# ============================================================================
# SIGNAL GENERATION
# ============================================================================

def generate_signal(t: np.ndarray, cfg: Config) -> np.ndarray:
    """
    Generate composite signal Y(t) = trend + detail + noise.

    Y(t) = A_trend * sin(ω_low * t) + A_detail * sin(ω_high * t) + N(0, σ)
    """
    trend = cfg.A_trend * np.sin(cfg.omega_low * t)
    detail = cfg.A_detail * np.sin(cfg.omega_high * t)
    noise = np.random.normal(0, cfg.sigma_noise, len(t))
    return trend + detail + noise


# ============================================================================
# SCALE-DEPENDENT PREDICTION
# ============================================================================

def get_scaled_view(signal: np.ndarray, scale: int, t: int) -> np.ndarray:
    """
    Get a scale-specific view of the signal history.
    Scale acts as a rolling window / smoothing factor.
    """
    start = max(0, t - scale * 10)  # Look back proportional to scale
    window = signal[start:t+1]

    if scale == 1:
        return window
    else:
        # Downsample by averaging groups of 'scale' points
        if len(window) < scale:
            return window
        trimmed_len = (len(window) // scale) * scale
        trimmed = window[:trimmed_len]
        return trimmed.reshape(-1, scale).mean(axis=1)


def predict_next(view: np.ndarray) -> float:
    """
    Simple linear predictor: extrapolate from last two points.
    Falls back to last value if insufficient history.
    """
    if len(view) < 2:
        return view[-1] if len(view) > 0 else 0.0

    # Linear extrapolation
    delta = view[-1] - view[-2]
    return view[-1] + delta


def compute_prediction_error(signal: np.ndarray, scale: int, t: int) -> float:
    """
    Compute one-step prediction error at given scale.
    """
    if t < 2:
        return 0.0

    view = get_scaled_view(signal, scale, t-1)
    prediction = predict_next(view)

    # For coarse scales, compare against smoothed actual
    if scale > 1:
        actual_view = get_scaled_view(signal, scale, t)
        actual = actual_view[-1] if len(actual_view) > 0 else signal[t]
    else:
        actual = signal[t]

    return (prediction - actual) ** 2


def compute_compute_cost(scale: int, base_flops: float = 1e5) -> float:
    """
    Compute cost is inversely proportional to scale.
    Fine scale (s=1) = max cost, Coarse scale (s=50) = low cost.
    """
    return base_flops / scale


# ============================================================================
# METABOLIC PRESSURE
# ============================================================================

def compute_lambda(e_buffer: float, k: float, epsilon: float) -> float:
    """
    Metabolic pressure: λ(e_buffer) = k / (ε + e_buffer)

    - Abundance (large e_buffer): λ ≈ 0, cost is cheap
    - Starvation (small e_buffer): λ is large, cost dominates
    """
    return k / (epsilon + e_buffer)


# ============================================================================
# POTENTIAL AND SCALE SELECTION
# ============================================================================

def compute_potential(
    E_pred: float,
    E_comp: float,
    lambda_: float,
    beta: float
) -> float:
    """
    V(s) = E_pred(s) + λ(e_buffer) * β * E_comp(s)
    """
    return E_pred + lambda_ * beta * E_comp


def select_scale(
    signal: np.ndarray,
    t: int,
    current_scale: int,
    e_buffer: float,
    cfg: Config
) -> Tuple[int, float, float, float]:
    """
    Select optimal scale by minimizing potential V(s).
    Returns: (selected_scale, E_pred, E_comp, V)
    """
    lambda_ = compute_lambda(e_buffer, cfg.k, cfg.epsilon)

    best_scale = current_scale
    best_V = float('inf')
    best_E_pred = 0
    best_E_comp = 0

    # Current scale potential
    E_pred_curr = compute_prediction_error(signal, current_scale, t)
    E_comp_curr = compute_compute_cost(current_scale)
    V_curr = compute_potential(E_pred_curr, E_comp_curr, lambda_, cfg.beta)

    for scale in cfg.scales:
        E_pred = compute_prediction_error(signal, scale, t)
        E_comp = compute_compute_cost(scale)
        V = compute_potential(E_pred, E_comp, lambda_, cfg.beta)

        if scale == current_scale:
            # No switching cost for staying
            if V < best_V:
                best_V = V
                best_scale = scale
                best_E_pred = E_pred
                best_E_comp = E_comp
        else:
            # Apply hysteresis: only switch if improvement > Γ
            if V_curr - V > cfg.gamma:
                if V < best_V:
                    best_V = V
                    best_scale = scale
                    best_E_pred = E_pred
                    best_E_comp = E_comp

    # If no switch was beneficial, stay with current
    if best_scale == current_scale or best_V >= V_curr:
        best_scale = current_scale
        best_V = V_curr
        best_E_pred = E_pred_curr
        best_E_comp = E_comp_curr

    return best_scale, best_E_pred, best_E_comp, best_V


# ============================================================================
# ENERGY DYNAMICS
# ============================================================================

def update_energy(e_buffer: float, t: int, cfg: Config) -> float:
    """
    Update energy buffer based on simulation phase.

    Phase 1 (Golden Age):   Constant high energy
    Phase 2 (Collapse):     Linear drain
    Phase 3 (Dark Age):     Near-zero asymptote
    """
    if t <= cfg.phase1_end:
        # Golden Age: abundant energy
        return cfg.e_buffer_init
    elif t <= cfg.phase2_end:
        # Collapse: drain energy
        return max(cfg.epsilon, e_buffer - cfg.drain_rate)
    else:
        # Dark Age: minimal energy
        return max(cfg.epsilon, e_buffer - cfg.drain_rate * 0.1)


# ============================================================================
# MAIN SIMULATION
# ============================================================================

def run_simulation(cfg: Config, seed: int = 42) -> dict:
    """
    Run the Starving Philosopher experiment.
    """
    np.random.seed(seed)

    # Generate time and signal
    t_array = np.arange(cfg.T)
    signal = generate_signal(t_array, cfg)

    # Initialize logging arrays
    log = {
        't': [],
        'e_buffer': [],
        'lambda': [],
        'scale': [],
        'E_pred': [],
        'E_comp': [],
        'V': [],
        'prediction': [],
        'signal': signal.tolist()
    }

    # Initial state
    current_scale = cfg.scales[0]  # Start with finest scale
    e_buffer = cfg.e_buffer_init

    for t in range(cfg.T):
        # Update energy
        e_buffer = update_energy(e_buffer, t, cfg)
        lambda_ = compute_lambda(e_buffer, cfg.k, cfg.epsilon)

        # Select scale
        scale, E_pred, E_comp, V = select_scale(
            signal, t, current_scale, e_buffer, cfg
        )
        current_scale = scale

        # Compute prediction for visualization
        if t > 0:
            view = get_scaled_view(signal, scale, t-1)
            pred = predict_next(view)
        else:
            pred = signal[0]

        # Log
        log['t'].append(t)
        log['e_buffer'].append(e_buffer)
        log['lambda'].append(lambda_)
        log['scale'].append(scale)
        log['E_pred'].append(E_pred)
        log['E_comp'].append(E_comp)
        log['V'].append(V)
        log['prediction'].append(pred)

    return log


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_results(log: dict, cfg: Config, output_path: str):
    """
    Generate the three-panel figure as specified.
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    t = np.array(log['t'])

    # -------------------------------------------------------------------------
    # Panel 1: Metabolism
    # -------------------------------------------------------------------------
    ax1 = axes[0]
    ax1_twin = ax1.twinx()

    # Energy buffer (green)
    line1 = ax1.plot(t, log['e_buffer'], 'g-', linewidth=2, label='Energy Buffer')
    ax1.set_ylabel('Energy Buffer (e)', color='green')
    ax1.tick_params(axis='y', labelcolor='green')
    ax1.set_ylim(0, cfg.e_buffer_init * 1.1)

    # Metabolic pressure (red dashed)
    line2 = ax1_twin.plot(t, log['lambda'], 'r--', linewidth=2, label='Metabolic Pressure λ')
    ax1_twin.set_ylabel('Metabolic Pressure (λ)', color='red')
    ax1_twin.tick_params(axis='y', labelcolor='red')

    # Phase annotations
    ax1.axvline(cfg.phase1_end, color='gray', linestyle=':', alpha=0.7)
    ax1.axvline(cfg.phase2_end, color='gray', linestyle=':', alpha=0.7)
    ax1.text(cfg.phase1_end/2, cfg.e_buffer_init * 0.9, 'Golden Age', ha='center', fontsize=10)
    ax1.text((cfg.phase1_end + cfg.phase2_end)/2, cfg.e_buffer_init * 0.9, 'Collapse', ha='center', fontsize=10)
    ax1.text((cfg.phase2_end + cfg.T)/2, cfg.e_buffer_init * 0.9, 'Dark Age', ha='center', fontsize=10)

    ax1.set_title('Panel 1: Metabolism - Energy vs Metabolic Pressure', fontsize=12, fontweight='bold')

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center right')

    # -------------------------------------------------------------------------
    # Panel 2: Signal and Prediction
    # -------------------------------------------------------------------------
    ax2 = axes[1]

    signal = np.array(log['signal'])
    prediction = np.array(log['prediction'])

    ax2.plot(t, signal, 'gray', alpha=0.5, linewidth=0.5, label='Raw Signal Y(t)')
    ax2.plot(t, prediction, 'b-', linewidth=1.5, label='Agent Prediction')

    # Highlight regions
    ax2.axvspan(0, cfg.phase1_end, alpha=0.1, color='green', label='Fine tracking')
    ax2.axvspan(cfg.phase2_end, cfg.T, alpha=0.1, color='red', label='Coarse tracking')

    ax2.axvline(cfg.phase1_end, color='gray', linestyle=':', alpha=0.7)
    ax2.axvline(cfg.phase2_end, color='gray', linestyle=':', alpha=0.7)

    ax2.set_ylabel('Signal Value')
    ax2.set_title('Panel 2: Signal and Prediction - Detail Loss Under Scarcity', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right')

    # -------------------------------------------------------------------------
    # Panel 3: Lens and Potential
    # -------------------------------------------------------------------------
    ax3 = axes[2]
    ax3_twin = ax3.twinx()

    # Scale (black step function)
    line3 = ax3.step(t, log['scale'], 'k-', linewidth=2, where='post', label='Perceptual Scale s')
    ax3.set_ylabel('Scale (s)', color='black')
    ax3.set_ylim(0, max(cfg.scales) * 1.2)
    ax3.set_yticks(cfg.scales)

    # Potential (faint red)
    line4 = ax3_twin.plot(t, log['V'], 'r-', alpha=0.5, linewidth=1, label='Potential V(s)')
    ax3_twin.set_ylabel('Potential V(s)', color='red')
    ax3_twin.tick_params(axis='y', labelcolor='red')

    ax3.axvline(cfg.phase1_end, color='gray', linestyle=':', alpha=0.7)
    ax3.axvline(cfg.phase2_end, color='gray', linestyle=':', alpha=0.7)

    # Find switch point
    scales = np.array(log['scale'])
    switch_points = np.where(np.diff(scales) != 0)[0]
    for sp in switch_points:
        ax3.axvline(sp, color='orange', linestyle='--', alpha=0.8)
        ax3.annotate(f'Switch @ t={sp}', xy=(sp, scales[sp+1]),
                     xytext=(sp+50, scales[sp+1]*1.1),
                     fontsize=9, color='orange',
                     arrowprops=dict(arrowstyle='->', color='orange'))

    ax3.set_xlabel('Time Step (t)')
    ax3.set_title('Panel 3: Lens Selection - Ignorance as Optimal Strategy', fontsize=12, fontweight='bold')

    lines = line3 + line4
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc='center right')

    # -------------------------------------------------------------------------
    # Final layout
    # -------------------------------------------------------------------------
    plt.tight_layout()

    # Add main title
    fig.suptitle('CYCLE 2568: The Starving Philosopher\n'
                 '"Perception is a function of budget, not just a passive mirror of the world"',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Figure saved: {output_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run experiment and generate output."""
    print("=" * 70)
    print("CYCLE 2568: The Starving Philosopher")
    print("Demonstrating: Ignorance as Economically Optimal Strategy")
    print("=" * 70)

    # Configuration
    cfg = Config()

    print(f"\nParameters:")
    print(f"  T = {cfg.T} steps")
    print(f"  Scales = {cfg.scales}")
    print(f"  Phase 1 (Golden Age): 0-{cfg.phase1_end}")
    print(f"  Phase 2 (Collapse): {cfg.phase1_end}-{cfg.phase2_end}")
    print(f"  Phase 3 (Dark Age): {cfg.phase2_end}-{cfg.T}")
    print(f"  Hysteresis Γ = {cfg.gamma}")

    # Run simulation
    print("\nRunning simulation...")
    log = run_simulation(cfg)

    # Analyze results
    scales = np.array(log['scale'])
    switch_points = np.where(np.diff(scales) != 0)[0]

    print(f"\nResults:")
    print(f"  Initial scale: {scales[0]}")
    print(f"  Final scale: {scales[-1]}")
    print(f"  Scale switches: {len(switch_points)}")

    for sp in switch_points:
        print(f"    t={sp}: {scales[sp]} → {scales[sp+1]} "
              f"(e_buffer={log['e_buffer'][sp]:.1f}, λ={log['lambda'][sp]:.2f})")

    # Validate hypothesis
    if scales[0] < scales[-1]:
        print("\n✓ HYPOTHESIS VALIDATED:")
        print("  Agent voluntarily increased perceptual scale (became 'more ignorant')")
        print("  under metabolic pressure to minimize computational potential.")
    else:
        print("\n✗ HYPOTHESIS NOT VALIDATED:")
        print("  Agent did not switch to coarser scale under scarcity.")

    # Generate figure
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/data/figures"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "cycle2568_starving_philosopher.png")

    print(f"\nGenerating figure...")
    plot_results(log, cfg, output_path)

    print("\n" + "=" * 70)
    print("INTERPRETATION:")
    print("-" * 70)
    print("Under ABUNDANCE: Agent uses fine lens, tracks complex reality")
    print("Under SCARCITY: Agent becomes 'ignorant' of high-frequency structure")
    print("The transition is NOT arbitrary - it's where V(s) is minimized")
    print("by giving up detail. Perception is a function of BUDGET.")
    print("=" * 70)

    return log


if __name__ == "__main__":
    main()
