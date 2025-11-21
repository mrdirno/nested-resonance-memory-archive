import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# Constants
RESULTS_FILE = Path("experiments/results/c277_critical_phenomena_results.json")
OUTPUT_DIR = Path("experiments/analysis/c277")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def analyze_critical_phenomena():
    print(f"Loading results from {RESULTS_FILE}...")
    with open(RESULTS_FILE, 'r') as f:
        data = json.load(f)

    f_crit = data['config']['f_crit_hier']
    results = data['results']

    # Group by frequency
    freq_data = {}
    for r in results:
        if 'error' in r:
            continue
        f_val = r['frequency']
        if f_val not in freq_data:
            freq_data[f_val] = {'pop': [], 'tau': []}
        
        freq_data[f_val]['pop'].append(r['final_population'])
        if r['equilibration_time'] > 0:
            freq_data[f_val]['tau'].append(r['equilibration_time'])

    # Prepare data for fitting
    epsilon = []
    energy_min = [] # Inverse of population ~ energy
    variance = []
    relaxation_time = []

    print("\nProcessing data points:")
    print(f"{'Freq (%)':<10} {'Epsilon':<10} {'Mean Pop':<10} {'Variance':<10} {'Mean Tau':<10}")
    
    sorted_freqs = sorted(freq_data.keys())
    
    for f_val in sorted_freqs:
        pops = np.array(freq_data[f_val]['pop'])
        taus = np.array(freq_data[f_val]['tau'])
        
        if len(pops) == 0:
            continue

        # Calculate reduced frequency distance (epsilon)
        # We look at approach from above f_crit (f > f_crit)
        if f_val <= f_crit:
            continue
            
        eps = (f_val - f_crit) / f_crit
        
        mean_pop = np.mean(pops)
        var_pop = np.var(pops, ddof=1)
        mean_tau = np.mean(taus) if len(taus) > 0 else np.nan

        epsilon.append(eps)
        # Order parameter M ~ Population. Susceptibility ~ Variance.
        # Energy gap ~ 1/Population? Or is Population the order parameter?
        # In NRM, Population N ~ Energy/Cost. 
        # Criticality usually implies Divergence of Correlation Length/Time/Susceptibility.
        
        # We test:
        # 1. Susceptibility (Variance of N) ~ epsilon^-gamma
        # 2. Relaxation Time (tau) ~ epsilon^-nu_tau
        # 3. Order Parameter (N) ~ epsilon^beta (usually goes to 0) OR epsilon^-alpha (diverges?)
        # In our case, N diverges as f -> f_crit (from above). 
        # So we expect N ~ epsilon^-nu_E (Divergence)
        
        energy_min.append(mean_pop) 
        variance.append(var_pop)
        relaxation_time.append(mean_tau)

        print(f"{f_val*100:<10.3f} {eps:<10.4f} {mean_pop:<10.1f} {var_pop:<10.1f} {mean_tau:<10.1f}")

    # Convert to numpy arrays
    epsilon = np.array(epsilon)
    energy_min = np.array(energy_min)
    variance = np.array(variance)
    relaxation_time = np.array(relaxation_time) # Might contain NaNs

    # Fit Power Laws (Log-Log Regression)
    # y = A * x^k  => log(y) = k * log(x) + log(A)
    # We expect k to be negative for divergence (e.g. -gamma)
    
    results_summary = {}

    def fit_power_law(x, y, name):
        # Filter NaNs and Zeros
        mask = (x > 0) & (y > 0) & np.isfinite(y)
        x_fit = x[mask]
        y_fit = y[mask]
        
        if len(x_fit) < 3:
            print(f"Not enough data to fit {name}")
            return None
            
        slope, intercept, r_value, p_value, std_err = stats.linregress(np.log(x_fit), np.log(y_fit))
        exponent = -slope # We define exponent as positive value in epsilon^-nu
        
        print(f"\n{name} Scaling:")
        print(f"  Exponent: {exponent:.4f} (Slope: {slope:.4f})")
        print(f"  R-squared: {r_value**2:.4f}")
        
        plt.figure()
        plt.loglog(x_fit, y_fit, 'bo', label='Data')
        plt.loglog(x_fit, np.exp(intercept) * x_fit**slope, 'r-', label=f'Fit (exp={exponent:.2f})')
        plt.xlabel('Reduced Frequency $\epsilon = (f - f_c)/f_c$')
        plt.ylabel(name)
        plt.title(f'{name} Critical Scaling\nExponent = {exponent:.3f}, $R^2$ = {r_value**2:.3f}')
        plt.legend()
        plt.grid(True, which="both", ls="-")
        plt.savefig(OUTPUT_DIR / f"c277_{name.lower().replace(' ', '_')}_scaling.png")
        plt.close()
        
        return {"exponent": exponent, "r_squared": r_value**2, "slope": slope}

    results_summary['population_divergence'] = fit_power_law(epsilon, energy_min, "Population Divergence")
    results_summary['susceptibility'] = fit_power_law(epsilon, variance, "Susceptibility (Variance)")
    
    # For tau, we might have NaNs if system didn't equilibrate
    results_summary['relaxation_time'] = fit_power_law(epsilon, relaxation_time, "Relaxation Time")

    # Save summary
    with open(OUTPUT_DIR / "c277_analysis_summary.json", 'w') as f:
        json.dump(results_summary, f, indent=2)
        
    print(f"\nAnalysis complete. Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    analyze_critical_phenomena()
