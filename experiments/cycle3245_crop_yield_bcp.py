import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3245: CROP YIELD PREDICTION BCP
# -----------------------------------------------------------------------------
# Domain: Agriculture
# Goal: Predict crop yield based on weather and soil data.
# Hypothesis: BCP (Bayesian Regression) outperforms Linear Regression.
# -----------------------------------------------------------------------------

class Field:
    def __init__(self, id):
        self.id = id
        self.soil_quality = random.uniform(0.5, 1.0)
        self.weather_impact = 0.0 # Unobserved latent
        self.true_yield = 0.0
        
    def grow(self):
        # Yield = Soil * Weather + Noise
        # Weather is common across fields but varies by year
        self.weather_impact = random.uniform(0.8, 1.2)
        self.true_yield = (self.soil_quality * self.weather_impact * 100.0) + random.gauss(0, 5)
        return self.true_yield

class Predictor:
    def predict(self, field):
        raise NotImplementedError
    def update(self, field, actual):
        pass

class LinearPredictor(Predictor):
    def __init__(self):
        self.slope = 100.0 # Guess
        self.intercept = 0.0
        self.learning_rate = 0.01
        
    def predict(self, field):
        return (self.slope * field.soil_quality) + self.intercept
        
    def update(self, field, actual):
        pred = self.predict(field)
        error = actual - pred
        # GD
        self.slope += self.learning_rate * error * field.soil_quality
        self.intercept += self.learning_rate * error

class BCPPredictor(Predictor):
    def __init__(self):
        # Bayesian Linear Regression (Simplified)
        # Prior: slope ~ N(100, 10), intercept ~ N(0, 5)
        self.mu_slope = 100.0
        self.sigma_slope = 10.0
        self.mu_int = 0.0
        self.sigma_int = 5.0
        self.noise_sigma = 5.0 # Observation noise
        
    def predict(self, field):
        # Predictive Mean
        return (self.mu_slope * field.soil_quality) + self.mu_int
        
    def update(self, field, actual):
        # Update belief based on likelihood
        # This is a simplified Kalman update for parameters
        
        x = field.soil_quality
        y = actual
        
        # Prediction
        pred = self.predict(field)
        error = y - pred
        
        # Uncertainty of prediction
        pred_var = (x**2 * self.sigma_slope) + self.sigma_int + self.noise_sigma
        
        # Kalman Gain
        k_slope = (self.sigma_slope * x) / pred_var
        k_int = self.sigma_int / pred_var
        
        # Update Mean
        self.mu_slope += k_slope * error
        self.mu_int += k_int * error
        
        # Update Variance (Reduction)
        self.sigma_slope *= (1 - k_slope * x)
        self.sigma_int *= (1 - k_int)

def run_simulation(predictor_cls, steps=100):
    predictor = predictor_cls()
    total_error_sq = 0
    
    for _ in range(steps):
        f = Field(0)
        actual = f.grow()
        
        pred = predictor.predict(f)
        error = actual - pred
        total_error_sq += error**2
        
        predictor.update(f, actual)
        
    return math.sqrt(total_error_sq / steps)

def main():
    print("======================================================================")
    print("CYCLE 3245: CROP YIELD PREDICTION BCP")
    print("======================================================================")
    
    steps = 1000
    
    lin_rmse = run_simulation(LinearPredictor, steps)
    print(f"Linear Regression RMSE: {lin_rmse:.4f}")
    
    bcp_rmse = run_simulation(BCPPredictor, steps)
    print(f"BCP Bayesian RMSE:      {bcp_rmse:.4f}")
    
    improvement = ((lin_rmse - bcp_rmse) / lin_rmse) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_rmse < lin_rmse:
        print("RESULT: SUCCESS. Bayesian updating converged faster.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3245_crop_yield.json", "w") as f:
        json.dump({"linear": lin_rmse, "bcp": bcp_rmse, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
