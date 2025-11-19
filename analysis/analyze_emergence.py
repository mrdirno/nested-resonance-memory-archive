
import json
import os
import numpy as np

def analyze_emergence_results(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    history_summary = data.get('history_summary', [])
    print(f"Number of history entries loaded: {len(history_summary)}")
    analysis_summary = data.get('analysis', {})
    
    print("--- Emergence Analysis Report ---")
    print(f"Timestamp: {data.get('timestamp')}")
    print(f"Config: {data.get('config')}")
    print(f"Baseline Reality: {data.get('baseline_reality')}")
    print(f"Overall Analysis: {analysis_summary}")
    print("\n")

    if not history_summary:
        print("History summary is empty. No detailed analysis can be performed.")
        return

    # --- Deep Dive into Burst Distributions ---
    all_burst_cycles = []
    burst_counts = [] # Initialize burst_counts here
    for entry in history_summary:
        if entry.get('bursts', 0) > 0:
            all_burst_cycles.append((entry['cycle'], entry['bursts']))

    print("--- Burst Distribution Analysis ---")
    if all_burst_cycles:
        print(f"Total Bursts: {analysis_summary.get('total_bursts')}")
        print("Cycles with Bursts (Cycle, Count):")
        for cycle, count in all_burst_cycles:
            print(f"  Cycle {cycle}: {count} bursts")
        
        burst_counts = [count for _, count in all_burst_cycles]
        print(f"Average Bursts per active cycle: {np.mean(burst_counts):.2f}")
        print(f"Std Dev of Bursts per active cycle: {np.std(burst_counts):.2f}")
    else:
        print("No burst events recorded in history.")
    print("\n")

    # --- Cluster Stability Analysis ---
    active_clusters_per_cycle = [entry.get('active_clusters', 0) for entry in history_summary]
    
    print("--- Cluster Stability Analysis ---")
    if active_clusters_per_cycle:
        non_zero_clusters = [c for c in active_clusters_per_cycle if c > 0]
        if non_zero_clusters:
            print(f"Average Active Clusters (when > 0): {np.mean(non_zero_clusters):.2f}")
            print(f"Std Dev Active Clusters (when > 0): {np.std(non_zero_clusters):.2f}")
            print(f"Min Active Clusters (when > 0): {min(non_zero_clusters)}")
            print(f"Max Active Clusters (when > 0): {max(non_zero_clusters)}")
        else:
            print("No active clusters recorded throughout the history.")

        # Analyze changes in active_clusters
        cluster_changes = [abs(active_clusters_per_cycle[i] - active_clusters_per_cycle[i-1]) 
                           for i in range(1, len(active_clusters_per_cycle))]
        if cluster_changes:
            print(f"Average absolute change in active clusters per cycle: {np.mean(cluster_changes):.2f}")
            print(f"Max absolute change in active clusters per cycle: {max(cluster_changes)}")
    else:
        print("No cluster data available in history.")
    print("\n")

    # --- Quantifying Criticality ---
    # Criticality often involves power-law distributions in event sizes/durations,
    # or significant fluctuations and sensitivity to initial conditions.
    # From available data, we can look at the variance of burst counts and cluster changes.

    print("--- Criticality Indicators ---")
    # High variance in bursts and cluster changes can indicate criticality.
    burst_variance = np.var(burst_counts) if burst_counts else 0
    cluster_change_variance = np.var(cluster_changes) if cluster_changes else 0

    print(f"Variance of Burst Counts: {burst_variance:.2f}")
    print(f"Variance of Cluster Active Changes: {cluster_change_variance:.2f}")

    # Check for periods of collapse/resurgence
    active_agents_per_cycle = [entry.get('active_agents', 0) for entry in history_summary]
    if active_agents_per_cycle:
        initial_agents = active_agents_per_cycle[0]
        final_agents = active_agents_per_cycle[-1]
        
        if initial_agents > 0 and final_agents == 0:
            print("System appears to have collapsed (active agents went to 0).")
        elif initial_agents == 0 and final_agents > 0:
            print("System shows resurgence (active agents appeared).")
        elif np.mean(active_agents_per_cycle) > 0 and final_agents == 0:
            collapse_cycle = -1
            for i in range(len(active_agents_per_cycle) - 1, -1, -1):
                if active_agents_per_cycle[i] == 0 and active_agents_per_cycle[i-1] > 0:
                    collapse_cycle = history_summary[i]['cycle']
                    break
            if collapse_cycle != -1:
                print(f"System sustained agents for some time, then collapsed around cycle {collapse_cycle}.")
        else:
            print("System maintained a relatively stable agent count or fluctuated.")
    
    print(f"Stability Score (from overall analysis): {analysis_summary.get('stability_score')}")
    print("\n")


if __name__ == "__main__":
    emergence_file = os.path.join(os.getcwd(), 'fractal', 'emergence_results.json')
    if os.path.exists(emergence_file):
        analyze_emergence_results(emergence_file)
    else:
        print(f"Error: {emergence_file} not found.")
