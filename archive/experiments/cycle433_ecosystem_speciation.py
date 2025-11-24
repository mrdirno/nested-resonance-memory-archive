"""
Cycle 433: The Ecosystem (Speciation)
Role: The Ecologist
Responsibility: Demonstrate evolutionary divergence into distinct niches.
"""
import random
import numpy as np

class EcoAgent:
    def __init__(self, agent_id, generation=0, parents=None):
        self.id = agent_id
        self.energy = 20
        self.alive = True
        
        if parents:
            p1, p2 = parents
            self.speed = (p1.speed + p2.speed) / 2.0 + random.gauss(0, 0.05)
            self.strength = (p1.strength + p2.strength) / 2.0 + random.gauss(0, 0.05)
        else:
            self.speed = random.random()
            self.strength = random.random()
            
        # Normalize to enforce trade-off (sum approx 1.0)
        total = self.speed + self.strength
        if total > 0:
            self.speed /= total
            self.strength /= total

    def forage(self, resource_type):
        # Non-linear return to force specialization: reward = trait^2 * multiplier
        if resource_type == "BLUE":
            return (self.speed ** 2) * 25
        else: # RED
            return (self.strength ** 2) * 25

def run_experiment():
    print("Cycle 433: Ecosystem Speciation Test")
    print("====================================")
    
    population = [EcoAgent(i) for i in range(40)]
    next_id = 40
    
    for gen in range(20):
        # Resource Phase
        blue_harvest = []
        red_harvest = []
        
        for agent in population:
            if not agent.alive: continue
            
            # Random encounter
            res_type = random.choice(["BLUE", "RED"])
            energy_gain = agent.forage(res_type)
            
            agent.energy += energy_gain
            agent.energy -= 10 # Metabolic cost
            
            if agent.energy <= 0:
                agent.alive = False
            
            # Track stats
            if agent.alive:
                if agent.speed > agent.strength:
                    blue_harvest.append(agent.speed)
                else:
                    red_harvest.append(agent.strength)

        # Selection & Reproduction
        survivors = [a for a in population if a.alive]
        if len(survivors) < 2:
            print("Extinction.")
            break
            
        # Reproduction (Asexual/Random pairing for simplicity in niches)
        # To encourage speciation, maybe they mate with similar?
        # For now, random mating to see if selection alone drives it.
        new_borns = []
        survivors.sort(key=lambda a: a.energy, reverse=True)
        parents = survivors[:len(survivors)//2] # Top 50%
        
        while len(population) + len(new_borns) < 40:
            if len(parents) < 2: break
            p1 = random.choice(parents)
            # Assortative Mating: Choose p2 close to p1
            candidates = sorted(parents, key=lambda x: abs(x.speed - p1.speed))
            # Pick from top 3 most similar (excluding self if possible)
            p2 = candidates[1] if len(candidates) > 1 and candidates[0] == p1 else candidates[0]
            
            new_borns.append(EcoAgent(next_id, gen+1, (p1, p2)))
            next_id += 1
            p1.energy -= 10
            p2.energy -= 10
            
        population = survivors + new_borns
        
        # Report
        avg_speed = sum(a.speed for a in survivors)/len(survivors)
        # Count Specialists
        speedsters = sum(1 for a in survivors if a.speed > 0.8)
        strongmen = sum(1 for a in survivors if a.strength > 0.8)
        generalists = len(survivors) - speedsters - strongmen
        
        print(f"Gen {gen}: Pop {len(survivors)} | Speedsters {speedsters} | Strongmen {strongmen} | Generalists {generalists}")

    print("\n--- Speciation Result ---")
    if speedsters > 5 and strongmen > 5:
        print("SUCCESS: Bimodal distribution achieved (Speciation).")
    elif speedsters > 30 or strongmen > 30:
        print("PARTIAL: One species dominated (Drift/Luck).")
    else:
        print("FAIL: Generalists prevailed.")

if __name__ == "__main__":
    run_experiment()
