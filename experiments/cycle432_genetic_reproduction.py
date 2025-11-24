"""
Cycle 432: The Species (Genetic Reproduction)
Role: The Biologist
Responsibility: Implement evolutionary dynamics (Selection, Reproduction, Mutation) to optimize the population over time.
"""
import random
import numpy as np

class BioAgent:
    def __init__(self, agent_id, generation=0, parents=None):
        self.id = agent_id
        self.generation = generation
        self.parents = parents
        self.energy = 10 # Starting energy
        self.alive = True
        
        # Genetics
        if parents:
            # Crossover
            p1, p2 = parents
            self.skill = (p1.skill + p2.skill) / 2.0
            self.social_weight = (p1.social_weight + p2.social_weight) / 2.0
            # Mutation
            self.skill += random.gauss(0, 0.05)
            self.social_weight += random.gauss(0, 0.05)
            # Clamp
            self.skill = max(0.0, min(1.0, self.skill))
            self.social_weight = max(0.0, min(1.0, self.social_weight))
        else:
            # Genesis
            self.skill = random.random()
            self.social_weight = random.random()

    def work(self):
        # Higher skill = Higher efficiency (Less energy cost for same output value)
        # Cost = 10 - (Skill * 5). Min cost 5.
        cost = 10 - (self.skill * 5)
        
        if self.energy < cost:
            self.alive = False
            return 0 # Output value
            
        self.energy -= cost
        # Output Value = 10 (Fixed for simplicity, so net gain depends on cost)
        return 10 

    def eat(self, value):
        self.energy += value

def run_experiment():
    print("Cycle 432: Genetic Reproduction Test")
    print("====================================")
    
    # 1. Genesis Population
    population = [BioAgent(i) for i in range(20)]
    next_id = 20
    
    avg_skill_history = []
    
    for gen in range(10):
        print(f"\n--- Generation {gen} (Pop: {len(population)}) ---")
        
        # A. Work Phase
        productivity = 0
        for agent in population:
            if agent.alive:
                output = agent.work()
                # Simplified economy: You eat what you kill (or sell)
                # Profit = Output - Cost (Implicit in energy check)
                # Here, we just give them the revenue:
                agent.eat(8) # Revenue > Cost for high skill, < Cost for low skill?
                # Wait, max cost is 10, min is 5.
                # If Revenue is 8:
                #   Skill 0.0 (Cost 10) -> Net -2 -> Death
                #   Skill 1.0 (Cost 5)  -> Net +3 -> Growth
                
        # B. Selection (Death)
        # Agents with low energy die
        for agent in population:
            if agent.energy <= 0:
                agent.alive = False
                
        survivors = [a for a in population if a.alive]
        avg_skill = sum(a.skill for a in survivors) / len(survivors) if survivors else 0
        avg_skill_history.append(avg_skill)
        print(f"Survivors: {len(survivors)} | Avg Skill: {avg_skill:.3f}")
        
        if len(survivors) < 2:
            print("Extinction Event.")
            break
            
        # C. Reproduction
        new_borns = []
        # Top 50% reproduce
        survivors.sort(key=lambda a: a.energy, reverse=True)
        parents_pool = survivors[:len(survivors)//2]
        
        while len(population) + len(new_borns) < 20: # Maintain pop size
            if len(parents_pool) < 2: break
            p1 = random.choice(parents_pool)
            p2 = random.choice(parents_pool)
            if p1 != p2:
                child = BioAgent(next_id, generation=gen+1, parents=(p1, p2))
                new_borns.append(child)
                next_id += 1
                # Reproduction cost
                p1.energy -= 10
                p2.energy -= 10
                
        population = survivors + new_borns
        
    print("\n--- Evolution Summary ---")
    print(f"Initial Skill: {avg_skill_history[0]:.3f}")
    print(f"Final Skill:   {avg_skill_history[-1]:.3f}")
    
    if avg_skill_history[-1] > avg_skill_history[0]:
        print("SUCCESS: Evolution optimized the population for efficiency.")
    else:
        print("FAIL: No evolutionary gain.")

if __name__ == "__main__":
    run_experiment()
