import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3216: CONSUMPTION FORECASTING BCP
# -----------------------------------------------------------------------------
# Domain: Energy
# Goal: adaptive forecasting using Bayesian updates.
# Hypothesis: Dynamic updating (BCP) reduces prediction error vs Static average.
# -----------------------------------------------------------------------------

class Consumer:
    def __init__(self, behavior_type):
        self.behavior = behavior_type
        self.time = 0
        self.base = 10
        
    def get_demand(self):
        self.time += 1
        noise = random.gauss(0, 2)
        
        if self.behavior == 'drifting':
            # Demand slowly rises then falls
            trend = math.sin(self.time * 0.05) * 5
            return max(0, self.base + trend + noise)
        elif self.behavior == 'erratic':
            # Random jumps
            if random.random() < 0.1:
                return max(0, self.base + 15 + noise)
            return max(0, self.base + noise)
        else:
            return max(0, self.base + noise)

class Forecaster:
    def predict(self):
        raise NotImplementedError
    def update(self, actual):
        pass

class StaticForecaster(Forecaster):
    def __init__(self):
        self.prediction = 10.0 # Blind guess based on history
        
    def predict(self):
        return self.prediction

class BCPForecaster(Forecaster):
    def __init__(self):
        self.mu = 10.0
        self.sigma = 2.0
        self.learning_rate = 0.1
        
    def predict(self):
        # Predict mean
        return self.mu
    
    def update(self, actual):
        # Bayesian-like update (Kalman Filter simplified)
        # Error = Actual - Predicted
        error = actual - self.mu
        
        # Update mean towards error
        self.mu += self.learning_rate * error
        
        # Update sigma (variance estimation - not used for mean prediction but useful for risk)
        sq_error = error ** 2
        self.sigma += self.learning_rate * (sq_error - self.sigma)

def run_test(forecaster_cls, steps=1000):
    consumer = Consumer('drifting') # Test on non-stationary data
    forecaster = forecaster_cls()
    
    total_sq_error = 0
    
    for _ in range(steps):
        actual = consumer.get_demand()
        pred = forecaster.predict()
        
        error = actual - pred
        total_sq_error += error ** 2
        
        forecaster.update(actual)
        
    rmse = math.sqrt(total_sq_error / steps)
    return rmse

def main():
    print("======================================================================")
    print("CYCLE 3216: CONSUMPTION FORECASTING BCP")
    print("======================================================================")
    
    steps = 1000
    
    # Static
    static_rmse = run_test(StaticForecaster, steps)
    print(f"Static Forecaster RMSE: {static_rmse:.3f}")
    
    # BCP
    bcp_rmse = run_test(BCPForecaster, steps)
    print(f"BCP Forecaster RMSE:    {bcp_rmse:.3f}")
    
    # Compare
    improvement = ((static_rmse - bcp_rmse) / static_rmse) * 100
    
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if improvement > 0:
        print("RESULT: SUCCESS. Adaptive BCP reduced prediction error.")
    else:
        print("RESULT: FAILURE. BCP did not outperform baseline.")
        
    print("======================================================================")
    
    # Save results
    results = {
        "steps": steps,
        "static_rmse": static_rmse,
        "bcp_rmse": bcp_rmse,
        "improvement_percent": improvement
    }
    
    with open("results/cycle3216_forecasting.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
