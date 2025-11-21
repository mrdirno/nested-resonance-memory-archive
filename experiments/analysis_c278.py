#!/usr/bin/env python3
import json
import numpy as np
import sys
from scipy.optimize import curve_fit

def power_law(x, a, b):
    return a * np.power(x, b)

def analyze_c278():
    print("ANALYZING CYCLE 278: CRITICAL PHENOMENA II (SUB-SATURATION)")
    print("===========================================================")
    
    try:
        with open('experiments/results/c278_critical_phenomena_sub_saturation_results.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: Results file not found.")
        return

    results = data['results']
    
    # Group by frequency
    freq_data = {}
    for r in results:
        f = r['frequency']
        if f not in freq_data:
            freq_data[f] = {'pop': [], 'tau': []}
        freq_data[f]['pop'].append(r['final_population'])
        freq_data[f]['tau'].append(r['equilibration_time'])

    print(f"{'FREQ (%)':<10} | {'MEAN POP':<10} | {'MEAN TAU':<10} | {'VAR POP':<10}")
    print("-" * 50)

    x_vals = []
    y_pop = []
    y_tau = []
    y_var = []

    for f in sorted(freq_data.keys()):
        pops = freq_data[f]['pop']
        taus = freq_data[f]['tau']
        
        mean_pop = np.mean(pops)
        mean_tau = np.mean(taus)
        var_pop = np.var(pops)
        
        x_vals.append(f)
        y_pop.append(mean_pop)
        y_tau.append(mean_tau)
        y_var.append(var_pop)
        
        print(f"{f*100:<10.4f} | {mean_pop:<10.1f} | {mean_tau:<10.1f} | {var_pop:<10.2f}")

    # Estimate Critical Frequency (Peak Variance)
    max_var_idx = np.argmax(y_var)
    f_crit = x_vals[max_var_idx]
    print("-" * 50)
    print(f"ESTIMATED F_CRIT: {f_crit*100:.4f}%")

    # Calculate Exponents near F_crit
    # nu_E: Energy/Pop scaling ~ |f - f_crit|^nu_E
    # nu_tau: Time scaling ~ |f - f_crit|^nu_tau
    # nu_sigma: Variance scaling ~ |f - f_crit|^nu_sigma
    
    # For sub-saturation, we might just look at scaling with f if f_crit ~ 0
    
    try:
        # Fit Tau ~ f^-z
        popt_tau, _ = curve_fit(power_law, x_vals, y_tau, maxfev=2000)
        z = -popt_tau[1]
        print(f"Critical Slowing Down (z): {z:.4f}")
        
        # Fit Pop ~ f^beta
        popt_pop, _ = curve_fit(power_law, x_vals, y_pop, maxfev=2000)
        beta = popt_pop[1]
        print(f"Order Parameter (beta): {beta:.4f}")
        
    except Exception as e:
        print(f"Fitting Error: {e}")

if __name__ == "__main__":
    analyze_c278()
