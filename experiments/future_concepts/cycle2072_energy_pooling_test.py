"""
Cycle 2072: Energy Pooling Test
================================
Can resource sharing prevent localized collapse?

From C2071: Swarm vs Monolith was inconclusive at low stress.
Hypothesis: Under localized energy starvation (some ants starve), 
pooling energy allows the swarm to survive where individuals would die.

Design:
- Swarm of 4 agents.
- Uneven energy drain (one agent drained 4x faster).
- Condition A: No Pooling (Independence).
- Condition B: Pooling (Redistribution).
- Metric: Survival rate of the collective memory.
"""

import numpy as np
import json
from datetime import datetime

class EnergyPooling:
    def __init__(self):
        self.num_agents = 4
        self.initial_energy = 100.0
        self.critical_threshold = 10.0
        self.num_cycles = 200
        self.num_trials = 20

    def run_trial(self, pooling, seed):
        np.random.seed(seed)
        
        energies = np.full(self.num_agents, self.initial_energy)
        alive = np.ones(self.num_agents, dtype=bool)
        
        # Drain rates: Agent 0 is the "stressed" one
        drain_rates = np.array([4.0, 1.0, 1.0, 1.0])
        
        survival_time = self.num_cycles
        
        for cycle in range(self.num_cycles):
            # 1. Apply Drain
            energies[alive] -= drain_rates[alive]
            
            # 2. Pooling Logic
            if pooling and np.any(alive):
                total_energy = np.sum(energies[alive])
                avg_energy = total_energy / np.sum(alive)
                energies[alive] = avg_energy
            
            # 3. Check Survival
            dead_now = energies <= self.critical_threshold
            if np.any(dead_now & alive):
                alive[dead_now] = False
                
                # If Agent 0 dies, the specific "view" is lost
                if dead_now[0]:
                    survival_time = cycle
                    break
                    
            if not np.any(alive):
                break
                
        return survival_time

    def run_experiment(self):
        results = {"conditions": []}
        
        print(f"{'Condition':<12} {'Avg Survival':<15} {'Survival %':<12}")
        print("---------------------------------------------")
        
        for pooling in [False, True]:
            survivals = []
            full_survival_count = 0
            
            for t in range(self.num_trials):
                s_time = self.run_trial(pooling, t*100)
                survivals.append(s_time)
                if s_time == self.num_cycles:
                    full_survival_count += 1
            
            avg_survival = np.mean(survivals)
            survival_pct = full_survival_count / self.num_trials
            
            cond_name = "Pooling" if pooling else "No Pooling"
            
            results["conditions"].append({
                "pooling": pooling,
                "avg_survival": avg_survival,
                "survival_pct": survival_pct
            })
            
            print(f"{cond_name:<12} {avg_survival:<15.1f} {survival_pct*100:<12.0f}%")
            
        return results

    def analyze(self, results):
        conds = results["conditions"]
        no_pool = [c for c in conds if not c["pooling"]][0]
        pool = [c for c in conds if c["pooling"]][0]
        
        gain = pool["avg_survival"] - no_pool["avg_survival"]
        
        findings = []
        if gain > 20:
            status = "CONFIRMED"
            findings.append(f"Pooling extends survival by {gain:.1f} cycles.")
        else:
            status = "FALSIFIED"
            findings.append("Pooling provided no significant benefit.")
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2072: Energy Pooling Test")
    print("Hypothesis: Resource sharing prevents localized collapse.")
    print("="*60)
    
    exp = EnergyPooling()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2072_energy_pooling.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
