import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# Constants
RESULTS_FILE = Path("experiments/results/c278_critical_phenomena_sub_saturation_results.json")
OUTPUT_DIR = Path("experiments/analysis/c278")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def analyze_sub_saturation():
    print(f"Loading results from {RESULTS_FILE}...")
    with open(RESULTS_FILE, 'r') as f:
        data = json.load(f)

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

    # Prepare data for plotting
    frequencies = []
    mean_pops = []
    var_pops = []
    survival_probs = []

    print("\nProcessing data points:")
    print(f"{'Freq (%)':<10} {'Mean Pop':<10} {'Variance':<10} {'Survival %':<10}")
    
    sorted_freqs = sorted(freq_data.keys())
    
    f_crit_candidate = None

    for f_val in sorted_freqs:
        pops = np.array(freq_data[f_val]['pop'])
        
        if len(pops) == 0:
            continue

        mean_pop = np.mean(pops)
        var_pop = np.var(pops, ddof=1) if len(pops) > 1 else 0.0
        survival_count = np.sum(pops > 0)
        survival_prob = survival_count / len(pops)

        frequencies.append(f_val)
        mean_pops.append(mean_pop)
        var_pops.append(var_pop)
        survival_probs.append(survival_prob)

        print(f"{f_val*100:<10.4f} {mean_pop:<10.2f} {var_pop:<10.2f} {survival_prob*100:<10.0f}%")

        # Identify candidate critical point (first frequency with >50% survival or significant population)
        if f_crit_candidate is None and survival_prob > 0.5:
            f_crit_candidate = f_val

    frequencies = np.array(frequencies)
    mean_pops = np.array(mean_pops)
    var_pops = np.array(var_pops)
    survival_probs = np.array(survival_probs)

    # Plot Population vs Frequency
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies * 100, mean_pops, 'bo-', label='Mean Population')
    plt.xlabel('Frequency (%)')
    plt.ylabel('Mean Population')
    plt.title('Cycle 278: Population vs Frequency (Sub-Saturation)')
    plt.grid(True)
    plt.legend()
    plt.savefig(OUTPUT_DIR / "c278_population_vs_frequency.png")
    plt.close()

    # Plot Survival Probability vs Frequency
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies * 100, survival_probs * 100, 'ro-', label='Survival Probability')
    plt.xlabel('Frequency (%)')
    plt.ylabel('Survival Probability (%)')
    plt.title('Cycle 278: Survival Probability vs Frequency')
    plt.grid(True)
    plt.legend()
    plt.savefig(OUTPUT_DIR / "c278_survival_vs_frequency.png")
    plt.close()

    print(f"\nCandidate Critical Point (Survival > 50%): {f_crit_candidate}")

    results_summary = {
        "f_crit_candidate": f_crit_candidate,
        "frequencies": frequencies.tolist(),
        "mean_pops": mean_pops.tolist(),
        "survival_probs": survival_probs.tolist()
    }

    # Save summary
    with open(OUTPUT_DIR / "c278_analysis_summary.json", 'w') as f:
        json.dump(results_summary, f, indent=2)
        
    print(f"\nAnalysis complete. Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    analyze_sub_saturation()
