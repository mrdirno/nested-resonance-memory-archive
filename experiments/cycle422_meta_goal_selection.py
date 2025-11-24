"""
Cycle 422: The Strategist (Meta-Goal Selection)
Role: The Captain
Responsibility: Adjust high-level goals (Curator Weights) based on system performance (Mood).
"""
import random

class Strategist:
    def __init__(self):
        self.history = []
        self.mood = "Neutral"
        self.weights = {"symmetry": 0.5, "complexity": 0.5, "novelty": 0.5}

    def update(self, fitness):
        self.history.append(fitness)
        if len(self.history) > 5:
            self.history.pop(0)
        
        self._assess_mood()
        self._set_weights()
        
        print(f"[STRATEGIST] Fitness: {fitness:.2f} -> Mood: {self.mood} -> Weights: {self.weights}")

    def _assess_mood(self):
        avg_fitness = sum(self.history) / len(self.history)
        
        if avg_fitness > 8.0:
            self.mood = "Bored"
        elif avg_fitness < 4.0:
            self.mood = "Frustrated"
        else:
            self.mood = "Flow"

    def _set_weights(self):
        if self.mood == "Bored":
            # High success -> Seek Novelty & Complexity
            self.weights = {"symmetry": 0.1, "complexity": 0.8, "novelty": 0.9}
        elif self.mood == "Frustrated":
            # Low success -> Seek Safety (Symmetry)
            self.weights = {"symmetry": 0.9, "complexity": 0.1, "novelty": 0.1}
        else:
            # Flow -> Balance
            self.weights = {"symmetry": 0.5, "complexity": 0.5, "novelty": 0.5}

def run_experiment():
    print("Cycle 422: Meta-Goal Selection Test")
    print("===================================")
    
    strat = Strategist()
    
    # Scenario 1: High Success (Boredom)
    print("\n--- Scenario 1: Success Streak ---")
    for _ in range(5):
        strat.update(9.0)
        
    if strat.weights['novelty'] > 0.8:
        print("SUCCESS: System prioritized Novelty due to Boredom.")
    else:
        print("FAIL: System failed to adapt to success.")

    # Scenario 2: Failure Streak (Frustration)
    print("\n--- Scenario 2: Failure Streak ---")
    for _ in range(5):
        strat.update(2.0)
        
    if strat.weights['symmetry'] > 0.8:
        print("SUCCESS: System prioritized Symmetry due to Frustration.")
    else:
        print("FAIL: System failed to adapt to failure.")

if __name__ == "__main__":
    run_experiment()