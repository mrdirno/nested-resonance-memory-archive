"""
Cycle 416: The Autonomous Scientist
Role: The Theorist
Responsibility: Formulate and test hypotheses about the relationship between system parameters and performance.
"""
import random
import numpy as np
import json

class Hypothesis:
    def __init__(self, name, prediction_rule):
        self.name = name
        self.prediction_rule = prediction_rule # Function: (params) -> predicted_fitness
        self.evidence = []
        self.confidence = 0.5

    def evaluate(self, params, actual_fitness):
        predicted = self.prediction_rule(params)
        error = abs(predicted - actual_fitness)
        
        # Update confidence (Simple Bayesian-like update)
        if error < 0.1:
            self.confidence = min(0.99, self.confidence * 1.1)
            return True # Supported
        else:
            self.confidence = max(0.01, self.confidence * 0.9)
            return False # Refuted

class HypothesisEngine:
    def __init__(self):
        self.hypotheses = []
        self.observations = []

    def observe(self, params, fitness):
        self.observations.append({"params": params, "fitness": fitness})
        
        # Evaluate existing hypotheses
        for h in self.hypotheses:
            h.evaluate(params, fitness)

    def generate_hypothesis(self):
        # Simple rule mining: Check correlation between Mutation Rate and Fitness
        if len(self.observations) < 5:
            return None

        # Extract data
        mrs = [o["params"]["mutation_rate"] for o in self.observations]
        fits = [o["fitness"] for o in self.observations]
        
        # Check for linear correlation
        correlation = np.corrcoef(mrs, fits)[0, 1]
        
        if correlation > 0.5:
            name = "Higher Mutation -> Higher Fitness"
            # Simple linear model: Fitness = 0.5 + MR
            rule = lambda p: 0.5 + p["mutation_rate"]
            h = Hypothesis(name, rule)
            self.hypotheses.append(h)
            return h
            
        elif correlation < -0.5:
            name = "Lower Mutation -> Higher Fitness"
            # Simple linear model: Fitness = 1.0 - MR
            rule = lambda p: 1.0 - p["mutation_rate"]
            h = Hypothesis(name, rule)
            self.hypotheses.append(h)
            return h
            
        return None

def run_experiment():
    print("Cycle 416: Hypothesis Generation Test")
    print("=====================================")
    
    scientist = HypothesisEngine()
    
    # Scenario 1: Exploration Phase (High MR is better)
    # We simulate a complex landscape where mutation helps
    print("\n--- Scenario 1: Complex Landscape (Mutation helps) ---")
    for i in range(10):
        mr = random.uniform(0.0, 0.5)
        # Truth: Fitness = 0.5 + MR + noise
        fitness = 0.5 + mr + random.uniform(-0.05, 0.05)
        scientist.observe({"mutation_rate": mr}, fitness)
        
    # Check if hypothesis was generated
    h = scientist.generate_hypothesis()
    if h:
        print(f"Generated Hypothesis: {h.name} (Confidence: {h.confidence:.2f})")
        if "Higher Mutation" in h.name:
            print("SUCCESS: Correctly identified positive correlation.")
        else:
            print("FAIL: Incorrect hypothesis.")
    else:
        print("FAIL: No hypothesis generated.")

    # Scenario 2: Convergence Phase (Low MR is better)
    # We reset and simulate a smooth landscape where mutation hurts
    print("\n--- Scenario 2: Smooth Landscape (Mutation hurts) ---")
    scientist = HypothesisEngine() # Reset
    for i in range(10):
        mr = random.uniform(0.0, 0.5)
        # Truth: Fitness = 1.0 - MR + noise
        fitness = 1.0 - mr + random.uniform(-0.05, 0.05)
        scientist.observe({"mutation_rate": mr}, fitness)
        
    # Check if hypothesis was generated
    h = scientist.generate_hypothesis()
    if h:
        print(f"Generated Hypothesis: {h.name} (Confidence: {h.confidence:.2f})")
        if "Lower Mutation" in h.name:
            print("SUCCESS: Correctly identified negative correlation.")
        else:
            print("FAIL: Incorrect hypothesis.")
    else:
        print("FAIL: No hypothesis generated.")

if __name__ == "__main__":
    run_experiment()