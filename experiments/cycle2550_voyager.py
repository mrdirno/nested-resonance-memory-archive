"""
Cycle 2550: The Voyager (Gate 178)
Experiment: Data Visualization.
Goal: Analyze the 'migrants.jsonl' file and report statistics about the agents who left the simulation.
"""

import json
import statistics
from pathlib import Path

def run_voyager_analysis():
    print("🔭 CYCLE 2550: THE VOYAGER - DIASPORA ANALYSIS")
    
    migrants_file = Path("migrants.jsonl")
    if not migrants_file.exists():
        print("❌ Error: migrants.jsonl not found.")
        return

    agents = []
    with open(migrants_file, 'r') as f:
        for line in f:
            if line.strip():
                agents.append(json.loads(line))
                
    count = len(agents)
    print(f"📊 Total Migrants: {count}")
    
    if count == 0:
        return

    # Analyze Genomes
    # Genome[9] = Innovation
    innovations = [a['genome'][9] for a in agents]
    avg_innovation = statistics.mean(innovations)
    
    print(f"🧠 Average Innovation: {avg_innovation:.4f}")
    print(f"🧬 Lineages: {set(a['lineage'] for a in agents)}")
    
    # Analyze Brain Weights (Cognitive diversity)
    # Just sample one
    sample_brain = agents[0]['brain']
    print(f"🤖 Sample Brain Weights (Traveler-0): {sample_brain}")
    
    print("✅ ANALYSIS COMPLETE.")

if __name__ == "__main__":
    run_voyager_analysis()
