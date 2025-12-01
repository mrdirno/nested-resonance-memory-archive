import math

class BCPAgent:
    def __init__(self, budget=100.0, k=1.0, epsilon=0.1):
        self.budget = budget
        self.k = k
        self.epsilon = epsilon
        
    @property
    def lambda_val(self):
        return self.k / (self.epsilon + max(0.0, self.budget))
        
    def evaluate(self, gain, cost):
        # The Universal Equation
        return gain - (self.lambda_val * cost)
        
    def act(self, cost):
        if self.budget >= cost:
            self.budget -= cost
            return True
        return False