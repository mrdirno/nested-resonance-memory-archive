import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3240: TRAFFIC SIGNAL CONTROL BCP
# -----------------------------------------------------------------------------
# Domain: Smart Cities
# Goal: Optimize traffic flow through an intersection.
# Hypothesis: BCP (Queue-Length Predictive Control) reduces wait time vs 
#             Fixed-Time or Actuated (Sensor-based) control.
# -----------------------------------------------------------------------------

class Lane:
    def __init__(self, id):
        self.id = id
        self.queue = []
        self.arrival_rate = 0.2
        
    def tick(self):
        if random.random() < self.arrival_rate:
            self.queue.append(1) # Car

class Intersection:
    def __init__(self):
        # 4 Lanes: N, S, E, W
        # Phases: 0=NS Green, 1=EW Green
        self.lanes = [Lane(i) for i in range(4)]
        self.phase = 0
        self.phase_timer = 0
        self.switch_cost = 5 # Lost time (Yellow/Red)
        self.switching = False
        self.switch_timer = 0
        
    def step(self):
        # Inflow
        for l in self.lanes: l.tick()
        
        # Switching logic
        if self.switching:
            self.switch_timer -= 1
            if self.switch_timer <= 0:
                self.switching = False
                self.phase = 1 - self.phase # Toggle
                self.phase_timer = 0
            return 0 # No flow during switch
            
        # Outflow
        self.phase_timer += 1
        throughput = 0
        
        active_lanes = [0, 1] if self.phase == 0 else [2, 3]
        for idx in active_lanes:
            if self.lanes[idx].queue:
                self.lanes[idx].queue.pop(0)
                throughput += 1
                
        return throughput

    def switch(self):
        if not self.switching:
            self.switching = True
            self.switch_timer = self.switch_cost

class Controller:
    def control(self, intersection):
        raise NotImplementedError

class FixedController(Controller):
    def __init__(self, interval=30):
        self.interval = interval
        
    def control(self, intersection):
        if intersection.phase_timer >= self.interval:
            intersection.switch()

class ActuatedController(Controller):
    def control(self, intersection):
        # Switch if current lanes empty AND other lanes have cars
        # Min green time 10
        if intersection.phase_timer < 10: return
        
        curr = [0, 1] if intersection.phase == 0 else [2, 3]
        other = [2, 3] if intersection.phase == 0 else [0, 1]
        
        curr_q = sum(len(intersection.lanes[i].queue) for i in curr)
        other_q = sum(len(intersection.lanes[i].queue) for i in other)
        
        if curr_q == 0 and other_q > 0:
            intersection.switch()
        # Max green time 60
        elif intersection.phase_timer >= 60:
            intersection.switch()

class BCPController(Controller):
    def control(self, intersection):
        # BCP: Minimize Total System Entropy (Queue Length squared)
        # Predict growth of queues
        # Cost of switching is delay (5 ticks of zero flow)
        
        # Lookahead: 
        # Option A: Keep Green. Benefit = Outflow - Inflow. Cost = 0.
        # Option B: Switch. Benefit = Future Outflow (Other). Cost = Switch Time.
        
        if intersection.phase_timer < 10: return # Min green constraint
        
        curr = [0, 1] if intersection.phase == 0 else [2, 3]
        other = [2, 3] if intersection.phase == 0 else [0, 1]
        
        q_curr = sum(len(intersection.lanes[i].queue) for i in curr)
        q_other = sum(len(intersection.lanes[i].queue) for i in other)
        
        # Pressure
        # If we stay: q_curr drops, q_other rises
        # If we switch: Both rise for 5 ticks, then q_other drops
        
        # Simple Pressure Difference Logic (BackPressure)
        # Threshold = Cost of Switching equivalent in queue buildup
        
        pressure_diff = q_other - q_curr
        
        # If pressure difference > Threshold, switch
        # Threshold roughly proportional to inflow * switch_time
        threshold = (0.2 * 4) * 5 * 1.5 # Heuristic
        
        if pressure_diff > threshold:
            intersection.switch()

def run_simulation(controller_cls, steps=1000):
    intersection = Intersection()
    if controller_cls == FixedController: controller = FixedController()
    elif controller_cls == ActuatedController: controller = ActuatedController()
    else: controller = BCPController()
    
    total_wait = 0
    
    for _ in range(steps):
        intersection.step()
        controller.control(intersection)
        
        # Wait time = Sum of all queues
        total_wait += sum(len(l.queue) for l in intersection.lanes)
        
    return total_wait

def main():
    print("======================================================================")
    print("CYCLE 3240: TRAFFIC SIGNAL CONTROL BCP")
    print("======================================================================")
    
    steps = 2000
    
    fixed_wait = run_simulation(FixedController, steps)
    print(f"Fixed Time Wait: {fixed_wait}")
    
    act_wait = run_simulation(ActuatedController, steps)
    print(f"Actuated Wait:   {act_wait}")
    
    bcp_wait = run_simulation(BCPController, steps)
    print(f"BCP Wait:        {bcp_wait}")
    
    # Compare against Actuated (Standard Smart)
    improvement = ((act_wait - bcp_wait) / act_wait) * 100
    print("-" * 60)
    print(f"Improvement vs Actuated: {improvement:.2f}%")
    
    if bcp_wait < act_wait:
        print("RESULT: SUCCESS. Pressure-based control optimized flow.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3240_traffic_control.json", "w") as f:
        json.dump({"fixed": fixed_wait, "actuated": act_wait, "bcp": bcp_wait, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
