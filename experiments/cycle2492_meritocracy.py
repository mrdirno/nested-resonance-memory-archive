
import sys
import os
import csv
import statistics
from pathlib import Path

# Ensure src is in path
sys.path.append(str(Path(__file__).parent.parent))

from src.life.genesis import DigitalLifeform

def run_cycle():
    print("CYCLE 2492: MERITOCRATIC REPRODUCTION")
    print("-------------------------------------")
    
    # Initialize Population
    population = [DigitalLifeform() for _ in range(100)]
    
    # Initialize CSV logging
    results_dir = Path("experiments/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "cycle2492_meritocracy.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "population", "avg_efficiency", "avg_energy"])
        
        for tick in range(1, 1001):
            # 1. Update Agents
            for agent in population[:]:
                if not agent.alive:
                    population.remove(agent)
                    continue
                    
                agent.metabolize()
                agent.act()
                
                # Try to reproduce (Meritocratic Filter applies here)
                child = agent.reproduce()
                if child:
                    if len(population) < 100: # Capacity limit
                        population.append(child)
                
                # Death condition
                if agent.energy <= 0:
                    agent.die()
                    
            # 2. Collect Stats
            if not population:
                print("EXTINCTION EVENT.")
                break
                
            efficiencies = [a.efficiency for a in population]
            energies = [a.energy for a in population]
            
            avg_eff = statistics.mean(efficiencies)
            avg_energy = statistics.mean(energies)
            pop_count = len(population)
            
            writer.writerow([tick, pop_count, avg_eff, avg_energy])
            
            if tick % 100 == 0:
                print(f"Tick {tick}: Pop={pop_count}, Eff={avg_eff:.3f}, Energy={avg_energy:.1f}")
                
    print("SIMULATION COMPLETE.")
    print(f"Final Efficiency: {avg_eff:.3f}")

if __name__ == "__main__":
    run_cycle()
