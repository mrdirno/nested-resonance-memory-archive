"""
Cycle 457: The Unified Agent (Integration)
Role: The Integrator
Responsibility: Merge Economics, Aesthetics, and Psychology into a single agent model.
"""
import random
import numpy as np

class UnifiedAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.wealth = 10.0
        self.stress = 0.0
        self.alive = True
        
        # Strategy Genes
        self.work_ethic = random.random() # 0 to 1. High = More Work, Less Art.
        self.artistic_need = random.random() # 0 to 1. High = Needs more Art to reduce stress.
        
    def step(self):
        if not self.alive: return
        
        # 1. Action Decision (Work vs Art)
        # Energy is limited. Agent splits effort based on work_ethic.
        
        # WORK Phase
        work_output = self.work_ethic * 5.0 # Revenue
        self.wealth += work_output
        
        # ART Phase
        art_output = (1.0 - self.work_ethic) # Time left for art
        
        # 2. Metabolism (Cost of Living)
        self.wealth -= 2.0
        if self.wealth < 0:
            self.alive = False
            return "STARVED"
            
        # 3. Psychology (Stress Accumulation)
        # Stress builds up naturally.
        # Art reduces stress.
        # If Work Ethic is high, Art is low, so Stress might build if Artistic Need is high.
        
        stress_buildup = self.artistic_need * 2.0 # High need = fast buildup
        stress_relief = art_output * 2.0 # Art relieves stress
        
        # Suppression Penalty (OSD/RES0X):
        # If you NEED art but WORK instead, the unexpressed potential becomes Load (Stress).
        suppression = max(0, self.artistic_need - art_output) * 5.0
        
        self.stress += stress_buildup + suppression - stress_relief
        self.stress = max(0, self.stress)
        
        if self.stress > 20.0:
            self.alive = False
            return "BURNOUT"
            
        return "ALIVE"

def run_experiment():
    print("Cycle 457: Unified Agent Simulation")
    print("===================================")
    
    population = [UnifiedAgent(i) for i in range(100)]
    ROUNDS = 50
    
    stats = {"ALIVE": [], "STARVED": [], "BURNOUT": []}
    
    for r in range(ROUNDS):
        statuses = []
        for agent in population:
            res = agent.step()
            statuses.append(res)
            
        alive_count = sum(1 for s in statuses if s == "ALIVE" or s == "ALIVE") # Fixed logic? Wait.
        # Agents marked dead return their death cause ONCE, then stop stepping?
        # My Agent.step returns immediately if not alive.
        # So we need to check agent.alive status.
        
        alive = [a for a in population if a.alive]
        dead = [a for a in population if not a.alive]
        
        # Analyze Dead
        starved = 0
        burnout = 0
        # We need to track death cause better. 
        # Ideally store it on agent. But for now, infer from state?
        # If wealth < 0 -> Starved. If stress > 20 -> Burnout.
        
        for d in dead:
            if d.wealth < 0: starved += 1
            elif d.stress > 20: burnout += 1
            
        print(f"Round {r}: Alive {len(alive)} | Starved {starved} | Burnout {burnout}")
        
        if len(alive) == 0:
            break
            
    # Analyze Survivors
    survivors = [a for a in population if a.alive]
    if survivors:
        avg_work = sum(a.work_ethic for a in survivors) / len(survivors)
        avg_need = sum(a.artistic_need for a in survivors) / len(survivors)
        print("\n--- Survivor Profile ---")
        print(f"Avg Work Ethic: {avg_work:.2f}")
        print(f"Avg Art Need:   {avg_need:.2f}")
        
        if avg_work > 0.4 and avg_work < 0.8:
            print("RESULT: Balance prevailed. Extremes died.")
        elif avg_work >= 0.8:
            print("RESULT: Workaholics prevailed (Low artistic need).")
        else:
            print("RESULT: Artists prevailed (Low metabolic cost?).")
    else:
        print("RESULT: Extinction.")

if __name__ == "__main__":
    run_experiment()
