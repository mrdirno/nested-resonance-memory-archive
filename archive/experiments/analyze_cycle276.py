import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# Constants
RESULTS_FILE = Path("experiments/results/c276_universality_topology_results.json")
OUTPUT_DIR = Path("experiments/analysis/c276")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def analyze_topology_universality():
    print(f"Loading results from {RESULTS_FILE}...")
    with open(RESULTS_FILE, 'r') as f:
        data = json.load(f)

    results = data['results']

    # Group by Topology -> Frequency
    topo_data = {}
    
    for r in results:
        if 'error' in r:
            continue
            
        topo = r['topology']
        freq = r['frequency']
        pop = r['final_population']
        
        if topo not in topo_data:
            topo_data[topo] = {}
            
        if freq not in topo_data[topo]:
            topo_data[topo][freq] = []
            
        topo_data[topo][freq].append(pop)

    # Analyze each topology
    print("\n" + "="*80)
    print(f"{'TOPOLOGY':<20} {'BETA (Slope)':<15} {'R-SQUARED':<15} {'ALPHA (Intercept)':<15}")
    print("-" * 80)
    
    betas = []
    
    plt.figure(figsize=(12, 8))
    
    colors = {'FULLY_CONNECTED': 'blue', 'RING': 'green', 'STAR': 'red', 'RANDOM_GRAPH': 'purple'}
    
    for topo, freqs_dict in topo_data.items():
        sorted_freqs = sorted(freqs_dict.keys())
        
        x_vals = []
        y_vals = []
        y_errs = []
        
        for f_val in sorted_freqs:
            pops = np.array(freqs_dict[f_val])
            mean_pop = np.mean(pops)
            std_pop = np.std(pops, ddof=1)
            
            if mean_pop > 0:
                x_vals.append(f_val)
                y_vals.append(mean_pop)
                y_errs.append(std_pop)
                
        x_vals = np.array(x_vals)
        y_vals = np.array(y_vals)
        
        if len(x_vals) < 3:
            print(f"{topo:<20} {'Not enough data':<15}")
            continue
            
        # Fit Power Law: N = A * f^-beta  => log(N) = log(A) - beta * log(f)
        slope, intercept, r_value, p_value, std_err = stats.linregress(np.log(x_vals), np.log(y_vals))
        
        beta = -slope
        alpha_efficiency = np.exp(intercept) # This is roughly 'A'
        r_squared = r_value**2
        
        betas.append(beta)
        
        print(f"{topo:<20} {beta:<15.4f} {r_squared:<15.4f} {alpha_efficiency:<15.1f}")
        
        # Plot
        color = colors.get(topo, 'black')
        plt.loglog(x_vals, y_vals, 'o', color=color, label=f"{topo} (β={beta:.2f})")
        plt.loglog(x_vals, alpha_efficiency * x_vals**slope, '--', color=color, alpha=0.5)

    print("-" * 80)
    
    # Calculate Universality Statistics
    if betas:
        mean_beta = np.mean(betas)
        std_beta = np.std(betas, ddof=1)
        cv_beta = (std_beta / mean_beta) * 100
        
        print(f"\nUniversality Statistics:")
        print(f"Mean β: {mean_beta:.4f}")
        print(f"Std Dev: {std_beta:.4f}")
        print(f"CV: {cv_beta:.2f}%")
        
        if cv_beta < 15:
            print("✅ RESULT: Universality CONFIRMED (CV < 15%)")
        else:
            print("❌ RESULT: Universality REJECTED (CV > 15%)")
            
    plt.xlabel('Frequency (f)')
    plt.ylabel('Population (N)')
    plt.title('Cycle 276: Topology Universality Test\nScaling Law: $N \propto f^{-\\beta}$')
    plt.grid(True, which="both", ls="-")
    plt.legend()
    plt.savefig(OUTPUT_DIR / "c276_topology_scaling.png")
    plt.close()
    
    # Save Summary
    summary = {
        "mean_beta": mean_beta if betas else None,
        "std_beta": std_beta if betas else None,
        "cv_beta": cv_beta if betas else None,
        "topologies": {t: {} for t in topo_data.keys()} # Placeholder structure
    }
    
    with open(OUTPUT_DIR / "c276_analysis_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
        
    print(f"\nAnalysis complete. Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    analyze_topology_universality()
