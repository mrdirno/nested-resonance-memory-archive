import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from code.fractal.fractal_swarm import FractalSwarm
from code.fractal.agent import FractalAgent

# --- EXPERIMENT: CAUSAL INFERENCE ---
class CausalPilot:
    def __init__(self):
        self.observations = []
        self.interventions = {}
        
    def observe(self, k_val, flux_val, r_val):
        self.observations.append({'K': k_val, 'Flux': flux_val, 'R': r_val})
        
    def analyze_correlations(self):
        data = self.observations
        Ks = [d['K'] for d in data]
        Fluxs = [d['Flux'] for d in data]
        Rs = [d['R'] for d in data]
        
        corr_K_R = np.corrcoef(Ks, Rs)[0, 1]
        corr_Flux_R = np.corrcoef(Fluxs, Rs)[0, 1]
        
        return corr_K_R, corr_Flux_R
        
    def infer_causality(self, results_k, results_flux):
        # results_k: list of (k_val, resulting_R)
        # results_flux: list of (flux_val, resulting_R)
        
        # Calculate Causal Strength (Average Effect)
        # Effect = |R_high - R_low| / |Param_high - Param_low|
        
        # Analyze K intervention
        k_vals = [x[0] for x in results_k]
        r_vals_k = [x[1] for x in results_k]
        effect_k = (max(r_vals_k) - min(r_vals_k)) / (max(k_vals) - min(k_vals) + 1e-6)
        
        # Analyze Flux intervention
        flux_vals = [x[0] for x in results_flux]
        r_vals_flux = [x[1] for x in results_flux]
        effect_flux = (max(r_vals_flux) - min(r_vals_flux)) / (max(flux_vals) - min(flux_vals) + 1e-6)
        
        return effect_k, effect_flux

def run_swarm_step(k_param, flux_intervention=None):
    # Simulation of Swarm Physics
    # K is the True Driver of R.
    # Flux is a Confounder: In "Observation Mode", Flux = R + Noise.
    # In "Intervention Mode", Flux is forced to a value, but DOES NOT affect Physics.
    
    N_AGENTS = 50
    phases = np.random.uniform(0, 2*np.pi, N_AGENTS)
    velocities = np.random.normal(0, 0.1, N_AGENTS)
    
    # Run for some steps to settle
    for _ in range(50):
        # Kuramoto Dynamics
        z = np.exp(1j * phases)
        Z = np.sum(z) / N_AGENTS
        R = np.abs(Z)
        Psi = np.angle(Z)
        
        coupling = k_param * R * np.sin(Psi - phases)
        d_theta = velocities + coupling
        phases = (phases + d_theta * 0.1) % (2*np.pi)
        
    # Final State
    z = np.exp(1j * phases)
    R_final = np.abs(np.sum(z) / N_AGENTS)
    
    # Determine Flux Value
    if flux_intervention is not None:
        # DO(Flux = val) -> We force Flux, but it changes nothing in the physics above
        flux_val = flux_intervention
    else:
        # Observation Mode: Flux is caused by R (Reverse Causality / Confounder)
        flux_val = R_final * 10.0 + np.random.normal(0, 0.5)
        
    return R_final, flux_val

def causal_inference_test():
    print("\n--- PAPER 15: CAUSAL INFERENCE TEST ---")
    pilot = CausalPilot()
    
    # PHASE 1: OBSERVATION (The Illusion)
    print("\n[Phase 1] Observation: Collecting Data...")
    for _ in range(20):
        # Randomly vary K (the true cause)
        k = np.random.uniform(0, 2.0)
        r, flux = run_swarm_step(k_param=k, flux_intervention=None)
        pilot.observe(k, flux, r)
        
    corr_k, corr_flux = pilot.analyze_correlations()
    print(f"  Correlation(K, R):    {corr_k:.4f}")
    print(f"  Correlation(Flux, R): {corr_flux:.4f}")
    print("  >> Both variables appear highly correlated with Order.")
    
    # PHASE 2: INTERVENTION (The Do-Calculus)
    print("\n[Phase 2] Intervention: Pilot performs Do-Calculus...")
    
    # Intervene on K (DO(K))
    print("  >> Intervening on K (True Driver)...")
    results_k = []
    for k_val in [0.1, 1.0, 2.0]: # Low, Med, High
        # We force K, let Flux be whatever (natural)
        r, _ = run_swarm_step(k_param=k_val, flux_intervention=None)
        results_k.append((k_val, r))
        print(f"     DO(K={k_val}) -> R={r:.4f}")
        
    # Intervene on Flux (DO(Flux))
    print("  >> Intervening on Flux (Confounder)...")
    results_flux = []
    for flux_val in [1.0, 5.0, 10.0]: # Low, Med, High
        # We keep K constant (at medium) to isolate Flux effect
        # But we FORCE Flux to a value
        r, _ = run_swarm_step(k_param=1.0, flux_intervention=flux_val)
        results_flux.append((flux_val, r))
        print(f"     DO(Flux={flux_val}) -> R={r:.4f}")
        
    # PHASE 3: INFERENCE (The Conclusion)
    print("\n[Phase 3] Inference: Calculating Causal Strength...")
    effect_k, effect_flux = pilot.infer_causality(results_k, results_flux)
    
    print(f"  Causal Effect (dR/dK):    {effect_k:.4f}")
    print(f"  Causal Effect (dR/dFlux): {effect_flux:.4f}")
    
    if effect_k > 0.1 and effect_flux < 0.1:
        print("\nSUCCESS: Pilot correctly identified K as the Causal Driver.")
        print("Conclusion: Flux is a correlate, not a cause.")
    else:
        print("\nFAILURE: Pilot could not distinguish cause from correlate.")

if __name__ == "__main__":
    causal_inference_test()
