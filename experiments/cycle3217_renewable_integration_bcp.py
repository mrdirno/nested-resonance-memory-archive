import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3217: RENEWABLE INTEGRATION BCP
# -----------------------------------------------------------------------------
# Domain: Energy
# Goal: Apply Adaptive BCP Forecasting to Grid Allocation.
# Hypothesis: Accurate demand prediction (Cycle 3216) fixes the outage problem 
#             observed in Cycle 3215.
# -----------------------------------------------------------------------------

class GridNode:
    def __init__(self, node_id, demand_profile):
        self.id = node_id
        self.demand_profile = demand_profile 
        self.time = 0
        self.current_demand = 0
        self.received_power = 0
        
    def tick(self):
        self.time += 1
        base = 10
        noise = random.gauss(0, 2)
        
        if self.demand_profile == 'stable':
            self.current_demand = max(1, base + noise)
        elif self.demand_profile == 'drifting':
            # Sine wave drift
            self.current_demand = max(1, base + noise + (math.sin(self.time * 0.1) * 5))
        elif self.demand_profile == 'spike':
            if random.random() < 0.1:
                self.current_demand = max(1, base * 2 + noise)
            else:
                self.current_demand = max(1, base + noise)
                
        self.received_power = 0

    def check_status(self):
        if self.received_power < self.current_demand * 0.95:
            return "OUTAGE"
        return "OK"

class BCPForecaster:
    def __init__(self):
        self.mu = 10.0
        self.learning_rate = 0.2
        
    def predict(self):
        return self.mu
    
    def update(self, actual):
        error = actual - self.mu
        self.mu += self.learning_rate * error

class Controller:
    def __init__(self, total_capacity):
        self.total_capacity = total_capacity

    def distribute(self, nodes):
        raise NotImplementedError

class ReactiveController(Controller):
    def distribute(self, nodes):
        total_demand = sum(n.current_demand for n in nodes)
        if total_demand <= self.total_capacity:
            for n in nodes: n.received_power = n.current_demand
        else:
            ratio = self.total_capacity / total_demand
            for n in nodes: n.received_power = n.current_demand * ratio

class SmartBCPController(Controller):
    def __init__(self, total_capacity, nodes):
        super().__init__(total_capacity)
        # Maintain a forecaster for EACH node
        self.forecasters = {n.id: BCPForecaster() for n in nodes}
        
    def distribute(self, nodes):
        # 1. Predict Demand
        predictions = {}
        total_predicted = 0
        for n in nodes:
            pred = self.forecasters[n.id].predict()
            predictions[n.id] = max(0.1, pred) # Safety floor
            total_predicted += pred
            
        # 2. Allocate based on PREDICTION (Simulating Day-Ahead Market)
        # Note: In this simulation, we allocate based on prediction, 
        # but if we have excess capacity at the moment of truth, we use it.
        # The constraint is: We commit to the allocation based on prediction.
        
        if total_predicted <= self.total_capacity:
            # Abundance (Predicted)
            ratio = 1.0
        else:
            # Scarcity (Predicted)
            ratio = self.total_capacity / total_predicted
            
        # 3. Real-time adjustment (The "Grid Physics")
        # We allocate specific capacity limits to nodes.
        current_load = 0
        
        for n in nodes:
            # We allocate capacity based on prediction
            allocated_cap = predictions[n.id] * ratio
            
            # Node takes what it needs UP TO allocation
            used = min(allocated_cap, n.current_demand)
            n.received_power = used
            
            # Update Forecaster with ACTUAL demand (Learning loop)
            self.forecasters[n.id].update(n.current_demand)

def run_simulation(controller_cls, steps=1000):
    nodes = [
        GridNode(1, 'stable'),
        GridNode(2, 'drifting'),
        GridNode(3, 'drifting'),
        GridNode(4, 'spike'),
        GridNode(5, 'spike'),
    ]
    
    # Capacity constraint
    if controller_cls == SmartBCPController:
        controller = SmartBCPController(65, nodes)
    else:
        controller = controller_cls(total_capacity=65)
        
    total_outages = 0
    
    for _ in range(steps):
        for n in nodes: n.tick()
        
        controller.distribute(nodes)
        
        for n in nodes:
            if n.check_status() == "OUTAGE":
                total_outages += 1
                
    return total_outages

def main():
    print("======================================================================")
    print("CYCLE 3217: RENEWABLE INTEGRATION BCP")
    print("======================================================================")
    
    steps = 2000
    
    reactive_outages = run_simulation(ReactiveController, steps)
    print(f"Reactive Outages: {reactive_outages}")
    
    bcp_outages = run_simulation(SmartBCPController, steps)
    print(f"Smart BCP Outages: {bcp_outages}")
    
    improvement = 0
    if reactive_outages > 0:
        improvement = ((reactive_outages - bcp_outages) / reactive_outages) * 100
        
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_outages < reactive_outages:
        print("RESULT: SUCCESS. Smart BCP outperforms Reactive control.")
    else:
        print("RESULT: FAILURE. Prediction errors caused misallocation.")
        
    print("======================================================================")
    
    # Save results
    with open("results/cycle3217_renewable_integration.json", "w") as f:
        json.dump({"improvement": improvement, "reactive": reactive_outages, "bcp": bcp_outages}, f)

if __name__ == "__main__":
    main()
