import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3230: CLIMATE MODELING BCP
# -----------------------------------------------------------------------------
# Domain: Environmental
# Goal: Predict future state of a chaotic system (Lorenz-like).
# Hypothesis: BCP (Ensemble Kalman Filter) outperforms Single Deterministic Model.
# -----------------------------------------------------------------------------

class ChaoticSystem:
    def __init__(self, x=1.0, y=1.0, z=1.0):
        self.state = [x, y, z]
        # Lorenz parameters
        self.sigma = 10.0
        self.rho = 28.0
        self.beta = 8.0 / 3.0
        self.dt = 0.01
        
    def step(self):
        x, y, z = self.state
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        
        self.state[0] += dx * self.dt
        self.state[1] += dy * self.dt
        self.state[2] += dz * self.dt
        
        # Add process noise (Real world uncertainty)
        self.state[0] += random.gauss(0, 0.1)
        self.state[1] += random.gauss(0, 0.1)
        self.state[2] += random.gauss(0, 0.1)
        
        return self.state

class DeterministicModel:
    def __init__(self, start_state):
        self.state = list(start_state)
        self.sigma = 10.0
        self.rho = 28.0
        self.beta = 8.0 / 3.0
        self.dt = 0.01
        
    def predict(self, steps=1):
        # Predicts WITHOUT noise (Idealized)
        s = list(self.state)
        for _ in range(steps):
            x, y, z = s
            dx = self.sigma * (y - x)
            dy = x * (self.rho - z) - y
            dz = x * y - self.beta * z
            s[0] += dx * self.dt
            s[1] += dy * self.dt
            s[2] += dz * self.dt
        self.state = s
        return s

    def update(self, observation):
        # Naive update: Reset state to observation
        self.state = list(observation)

class EnsembleBCPModel:
    def __init__(self, start_state, members=10):
        self.members = []
        for _ in range(members):
            # Initialize members with slight perturbation
            s = [x + random.gauss(0, 0.5) for x in start_state]
            self.members.append(DeterministicModel(s))
            
    def predict(self, steps=1):
        # Run all members
        predictions = []
        for m in self.members:
            predictions.append(m.predict(steps))
            
        # Return Mean
        avg = [sum(p[i] for p in predictions)/len(predictions) for i in range(3)]
        return avg
    
    def update(self, observation):
        # Ensemble Kalman Filter (simplified)
        # 1. Calculate Kalman Gain based on variance of ensemble
        # (Here simplified: Nudge members towards observation based on spread)
        
        obs_x, obs_y, obs_z = observation
        
        for m in self.members:
            # Nudge
            # This prevents collapse while correcting drift
            m.state[0] += 0.5 * (obs_x - m.state[0]) + random.gauss(0, 0.1)
            m.state[1] += 0.5 * (obs_y - m.state[1]) + random.gauss(0, 0.1)
            m.state[2] += 0.5 * (obs_z - m.state[2]) + random.gauss(0, 0.1)

def calculate_error(s1, s2):
    return math.sqrt(sum((s1[i] - s2[i])**2 for i in range(3)))

def run_simulation(model_cls, steps=500):
    truth = ChaoticSystem()
    # Burn in
    for _ in range(100): truth.step()
    
    model = model_cls(truth.state)
    
    total_error = 0
    
    # Predict 10 steps ahead at each point
    lookahead = 10
    
    for t in range(steps):
        # True future (for validation)
        # We need a clone of truth to peek ahead without advancing simulation
        # But since truth has noise, we can't perfectly predict.
        # We compare Model Prediction vs Actual Future Observation
        
        current_truth = list(truth.state)
        
        # Step Truth
        obs = truth.step()
        
        # Model predicts next step (1 step lookahead error)
        pred = model.predict(steps=1)
        
        err = calculate_error(pred, obs)
        total_error += err
        
        # Update model with observation
        model.update(obs)
        
    return total_error / steps

def main():
    print("======================================================================")
    print("CYCLE 3230: CLIMATE MODELING BCP")
    print("======================================================================")
    
    steps = 1000
    
    # Deterministic
    det_err = run_simulation(DeterministicModel, steps)
    print(f"Deterministic Error: {det_err:.4f}")
    
    # BCP (Ensemble)
    bcp_err = run_simulation(EnsembleBCPModel, steps)
    print(f"BCP Ensemble Error:  {bcp_err:.4f}")
    
    improvement = ((det_err - bcp_err) / det_err) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_err < det_err:
        print("RESULT: SUCCESS. Ensemble averaging reduced chaos drift.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3230_climate_modeling.json", "w") as f:
        json.dump({"deterministic": det_err, "bcp": bcp_err, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
