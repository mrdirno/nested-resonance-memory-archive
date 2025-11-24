#!/usr/bin/env python3
import json
import numpy as np
import sys
from scipy.optimize import curve_fit

def power_law(x, a, b):
    return a * np.power(x, b)

def analyze_c276():
    print("ANALYZING CYCLE 276: TOPOLOGY UNIVERSALITY")
    print("==========================================")
    
    try:
        with open('experiments/results/c276_universality_topology_results.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: Results file not found.")
        return

    results = data['results']
    
    # Group by topology
    topologies = {}
    for r in results:
        topo = r['topology']
        if topo not in topologies:
            topologies[topo] = {'f': [], 'pop': []}
        topologies[topo]['f'].append(r['frequency'])
        topologies[topo]['pop'].append(r['final_population'])

    print(f"{'TOPOLOGY':<20} | {'BETA':<10} | {'R^2':<10} | {'STATUS'}")
    print("-" * 60)

    for topo, vals in topologies.items():
        # Calculate mean population for each frequency
        freq_map = {}
        for f, p in zip(vals['f'], vals['pop']):
            if f not in freq_map:
                freq_map[f] = []
            freq_map[f].append(p)
        
        x_data = []
        y_data = []
        
        for f in sorted(freq_map.keys()):
            mean_pop = np.mean(freq_map[f])
            # Order parameter Psi = (Pop - Pop_crit) / Pop_crit ? 
            # Or simply Psi ~ f^beta
            # In C276 we assume Psi ~ f^beta
            
            if f > 0: # Avoid log(0)
                x_data.append(f)
                y_data.append(mean_pop)
        
        # Fit Power Law: y = a * x^b
        try:
            popt, pcov = curve_fit(power_law, x_data, y_data, maxfev=2000)
            beta = popt[1]
            
            # Calculate R^2
            residuals = y_data - power_law(x_data, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y_data - np.mean(y_data))**2)
            r_squared = 1 - (ss_res / ss_tot)
            
            status = "UNIVERSAL" if 0.45 <= beta <= 0.55 else "DEVIANT"
            print(f"{topo:<20} | {beta:.4f}     | {r_squared:.4f}     | {status}")
            
        except Exception as e:
            print(f"{topo:<20} | ERROR      | N/A        | {str(e)}")

if __name__ == "__main__":
    analyze_c276()
