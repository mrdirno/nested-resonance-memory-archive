"""
Cycle 421: The Observer (Reality Collapse)
Role: The Scientist
Responsibility: Compare Prediction vs. Observation and update the internal model (minimize free energy).
"""
import random
import time

class DreamEngine:
    def __init__(self):
        # Internal Model Parameters
        self.bias = 5.0
        self.weight_sym = 2.0
        self.weight_comp = -0.5
    
    def predict(self, sym, comp):
        return max(0.1, self.bias + (sym * self.weight_sym) + (comp * self.weight_comp))

class Observer:
    def __init__(self, dream_engine):
        self.dream_engine = dream_engine
        self.learning_rate = 0.1
        
    def observe_and_update(self, predicted, actual, sym, comp):
        error = actual - predicted
        squared_error = error ** 2
        
        print(f"[OBSERVER] Pred: {predicted:.2f} | Actual: {actual:.2f} | Error: {error:.2f}")
        
        # Simple Gradient Descent to update weights
        # d(Error^2)/dw = 2 * Error * d(Error)/dw
        # d(Error)/dw = -d(Predicted)/dw
        
        # Update Bias
        grad_bias = -2 * error * 1.0
        self.dream_engine.bias -= self.learning_rate * grad_bias * 0.1 # Dampened
        
        # Update Sym Weight
        grad_sym = -2 * error * sym
        self.dream_engine.weight_sym -= self.learning_rate * grad_sym
        
        # Update Comp Weight
        grad_comp = -2 * error * comp
        self.dream_engine.weight_comp -= self.learning_rate * grad_comp
        
        return squared_error

def run_experiment():
    print("Cycle 421: Reality Collapse Test")
    print("===============================")
    
    dreamer = DreamEngine()
    observer = Observer(dreamer)
    
    # Simulate a "Real World" where Symmetry is actually BAD (Penalty)
    # Real Physics: Fitness = 5.0 - (Sym * 2.0) ... opposite of initial belief
    
    print(f"Initial Model: Bias={dreamer.bias:.2f}, W_Sym={dreamer.weight_sym:.2f}")
    
    for i in range(10):
        # 1. Encounter a shape
        sym = random.random()
        comp = random.random()
        
        # 2. Dream
        prediction = dreamer.predict(sym, comp)
        
        # 3. Act (Simulate Reality)
        reality = 5.0 - (sym * 2.0) # True physics
        
        # 4. Observe & Learn
        loss = observer.observe_and_update(prediction, reality, sym, comp)
        
        print(f"Cycle {i}: Loss {loss:.4f}")
        
    print(f"\nFinal Model: Bias={dreamer.bias:.2f}, W_Sym={dreamer.weight_sym:.2f}")
    
    if dreamer.weight_sym < 1.0:
        print("SUCCESS: System learned that Symmetry weight should be lower.")
    else:
        print("FAIL: System failed to adapt internal model.")

if __name__ == "__main__":
    run_experiment()