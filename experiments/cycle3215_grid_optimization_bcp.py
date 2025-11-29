import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3215: GRID OPTIMIZATION BCP
# -----------------------------------------------------------------------------
# Domain: Energy
# Goal: Optimize grid load balancing using BCP principles.
# Hypothesis: BCP (predictive metabolic pressure) reduces outage rates compared 
#             to Reactive (threshold-based) control.
# -----------------------------------------------------------------------------

class GridNode:
    def __init__(self, node_id, demand_profile):
        self.id = node_id
        self.demand_profile = demand_profile # 'stable', 'volatile', 'spike'
        self.current_demand = 0
        self.received_power = 0
        self.outage_count = 0

    def tick(self, time_step):
        # Simulate demand
        base = 10
        noise = random.uniform(-2, 2)
        
        if self.demand_profile == 'stable':
            self.current_demand = base + noise
        elif self.demand_profile == 'volatile':
            self.current_demand = base + noise + (math.sin(time_step * 0.5) * 5)
        elif self.demand_profile == 'spike':
            if random.random() < 0.1:
                self.current_demand = base * 3 # Spike
            else:
                self.current_demand = base + noise
        
        self.received_power = 0 # Reset for distribution step

    def check_status(self):
        if self.received_power < self.current_demand * 0.95: # 5% tolerance
            self.outage_count += 1
            return "OUTAGE"
        return "OK"

class Controller:
    def __init__(self, total_capacity):
        self.total_capacity = total_capacity

    def distribute(self, nodes, time_step):
        raise NotImplementedError

class ReactiveController(Controller):
    def distribute(self, nodes, time_step):
        # Simple equal distribution, then re-allocate? 
        # No, standard is "Request based" up to capacity.
        
        total_demand = sum(n.current_demand for n in nodes)
        
        if total_demand <= self.total_capacity:
            # Everyone gets what they want
            for n in nodes:
                n.received_power = n.current_demand
        else:
            # Brownout: Proportional reduction
            ratio = self.total_capacity / total_demand
            for n in nodes:
                n.received_power = n.current_demand * ratio

class BCPController(Controller):
    def distribute(self, nodes, time_step):
        # BCP Logic: Forecast demand based on "Metabolic Pressure"
        # We reserve a "Buffer" based on volatility estimation.
        
        predictions = {}
        total_predicted = 0
        
        for n in nodes:
            # BCP Prediction: 
            # If volatile, predict higher (Risk Aversion).
            # If stable, predict mean.
            
            if n.demand_profile == 'stable':
                pred = 10.0 # Prior knowledge
            elif n.demand_profile == 'volatile':
                # Anticipate the sine wave + margin
                pred = 10.0 + 5.0 + 2.0 # Max + margin
            elif n.demand_profile == 'spike':
                # Hedging: Don't cover full spike (too expensive), but keep reserve
                pred = 15.0 
            
            predictions[n.id] = pred
            total_predicted += pred
            
        # Allocation
        if total_predicted <= self.total_capacity:
            # We have excess, so we can actually allocate exactly what they *currently* need
            # effectively matching the Reactive case in abundance, 
            # BUT we can pre-allocate (simulated here by just meeting demand)
             for n in nodes:
                n.received_power = n.current_demand
        else:
            # Scarcity: BCP Allocation
            # Prioritize 'stable' (Low Cost/Risk) or 'spike' (High Cost)?
            # BCP says: Minimize total system entropy (Outages).
            # We allocate weighted by "Criticality" (assumed equal) 
            # but we use the PREDICTED ratios, not current demand.
            
            ratio = self.total_capacity / total_predicted
            for n in nodes:
                # We give them their share of the capacity based on RISK profile
                allocated = predictions[n.id] * ratio
                # But they can't use more than they need (physics)
                used = min(allocated, n.current_demand)
                n.received_power = used
                
                # If they needed more than allocated, it's a blackout.
                # If they needed less, the power is "wasted" (or saved, but here strictly allocated)

def run_simulation(controller_type, steps=100):
    nodes = [
        GridNode(1, 'stable'),
        GridNode(2, 'stable'),
        GridNode(3, 'volatile'),
        GridNode(4, 'volatile'),
        GridNode(5, 'spike'),
    ]
    
    # Capacity is tight: Avg demand is ~55. Max is much higher.
    # Set capacity to 60 (slightly above average, but below peaks)
    controller = controller_type(total_capacity=60)
    
    total_outages = 0
    
    for t in range(steps):
        for n in nodes:
            n.tick(t)
            
        controller.distribute(nodes, t)
        
        for n in nodes:
            if n.check_status() == "OUTAGE":
                total_outages += 1
                
    return total_outages

def main():
    print("======================================================================")
    print("CYCLE 3215: GRID OPTIMIZATION BCP")
    print("======================================================================")
    
    steps = 1000
    
    # Run Reactive
    reactive_outages = run_simulation(ReactiveController, steps)
    print(f"Reactive Controller Outages: {reactive_outages}")
    
    # Run BCP
    bcp_outages = run_simulation(BCPController, steps)
    print(f"BCP Controller Outages:      {bcp_outages}")
    
    # Compare
    improvement = 0
    if reactive_outages > 0:
        improvement = ((reactive_outages - bcp_outages) / reactive_outages) * 100
        
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_outages < reactive_outages:
        print("RESULT: SUCCESS. BCP logic reduced outages via risk-aware allocation.")
    else:
        print("RESULT: FAILURE. BCP did not outperform reactive baseline.")
        
    print("======================================================================")
    
    # Save results
    results = {
        "steps": steps,
        "reactive_outages": reactive_outages,
        "bcp_outages": bcp_outages,
        "improvement_percent": improvement
    }
    
    with open("results/cycle3215_grid_optimization.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
