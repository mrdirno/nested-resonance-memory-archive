import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
try:
    from core.agent import BCPAgent
except ImportError:
    # Fallback if running isolated
    class BCPAgent:
        def __init__(self, budget=100.0, k=1.0, epsilon=0.1):
            self.budget = budget
            self.k = k
            self.epsilon = epsilon
        @property
        def lambda_val(self):
            return self.k / (self.epsilon + max(0.0, self.budget))
        def evaluate(self, gain, cost):
            return gain - (self.lambda_val * cost)

def run_experiment():
    print("Running BCP Regeneration Experiment...")
    agent = BCPAgent(budget=10.0)
    
    # Scenario: High Cost, High Gain
    gain = 100.0
    cost = 5.0
    
    val = agent.evaluate(gain, cost)
    print(f"Budget: {agent.budget}, Lambda: {agent.lambda_val:.2f}")
    print(f"Action(G={gain}, C={cost}) -> Value: {val:.2f}")
    
    if val > 0:
        print("Action TAKEN.")
    else:
        print("Action REJECTED.")

if __name__ == "__main__":
    run_experiment()