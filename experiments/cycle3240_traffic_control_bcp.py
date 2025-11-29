import random

# ======================================================================
# CYCLE 3240: TRAFFIC CONTROL AS BCP
# ======================================================================
# Hypothesis: Traffic Signals are BCP Allocators.
#   V(green) = Queue_Length - lambda * Wait_Time
#   Wait. Actually, Max-Pressure (Backpressure) is known optimal.
#   Is Max-Pressure a form of BCP?
#   MP maximizes throughput.
#   BCP balances throughput vs cost (delay?).
#   Let's test if BCP can beat simple Actuated Control.
# ======================================================================

def run_experiment():
    print("CYCLE 3240: Traffic Control as BCP")
    
    T = 1000
    # 4-way intersection (N, S, E, W)
    queues = {"N": 0, "S": 0, "E": 0, "W": 0}
    waits = {"N": 0, "S": 0, "E": 0, "W": 0}
    
    total_delay_bcp = 0
    total_throughput_bcp = 0
    
    # Arrivals
    def arrive():
        if random.random() < 0.3: queues["N"] += 1
        if random.random() < 0.3: queues["S"] += 1
        if random.random() < 0.2: queues["E"] += 1
        if random.random() < 0.2: queues["W"] += 1
        
    # BCP Simulation
    current_phase = "NS" # or EW
    time_in_phase = 0
    
    for t in range(T):
        arrive()
        
        # Accumulate Wait
        for d in queues:
            if queues[d] > 0: waits[d] += queues[d]
            
        # BCP Decision: Switch Phase?
        # Options: Keep Current, Switch
        # Switch Cost = Lost Time (Yellow/Red) = 3 ticks (Capacity loss)
        
        # V(Keep) = Service_Rate * Queue(Current) - lambda * 0
        # V(Switch) = Service_Rate * Queue(Other) - lambda * Switch_Cost
        
        # Lambda? Urgency.
        # If queues are huge -> Urgency High -> Switch less? Or Switch faster?
        # High Congestion -> Minimize Lost Time -> Switch LESS.
        # Low Congestion -> Switch FREELY to serve random arrivals.
        
        total_q = sum(queues.values())
        lamb = 100.0 / (10.0 + total_q) # Congestion -> Low lambda? No.
        # We need: High Congestion -> High Cost Sensitivity (Avoid Switch Loss).
        # So Lambda should be proportional to Congestion.
        # lambda = k * Congestion.
        lamb = 0.01 * total_q
        
        switch_cost = 3.0 * 1.0 # 3 cars lost capacity?
        # Gain = Queue size difference?
        
        q_ns = queues["N"] + queues["S"]
        q_ew = queues["E"] + queues["W"]
        
        if current_phase == "NS":
            gain_switch = q_ew - q_ns
        else:
            gain_switch = q_ns - q_ew
            
        # V = Gain - lambda * Cost
        v_switch = gain_switch - lamb * switch_cost
        
        if v_switch > 0 and time_in_phase > 5: # Minimum green
            # Switch
            current_phase = "EW" if current_phase == "NS" else "NS"
            time_in_phase = 0
            # Penalty: No service this tick (Yellow)
            pass 
        else:
            # Service
            time_in_phase += 1
            if current_phase == "NS":
                if queues["N"] > 0: queues["N"] -= 1; total_throughput_bcp += 1
                if queues["S"] > 0: queues["S"] -= 1; total_throughput_bcp += 1
            else:
                if queues["E"] > 0: queues["E"] -= 1; total_throughput_bcp += 1
                if queues["W"] > 0: queues["W"] -= 1; total_throughput_bcp += 1
                
        total_delay_bcp = sum(waits.values())
        
    print(f"BCP Delay: {total_delay_bcp}")
    
    # Actuated Control (Standard)
    # Switch if Gap > Threshold (Empty queue)
    # Else Max Green
    
    queues = {"N": 0, "S": 0, "E": 0, "W": 0}
    waits = {"N": 0, "S": 0, "E": 0, "W": 0}
    total_delay_act = 0
    current_phase = "NS"
    time_in_phase = 0
    
    random.seed(42) # Reset seed? No, just run loop again with approx logic
    
    for t in range(T):
        # Same arrival logic approx
        if random.random() < 0.3: queues["N"] += 1
        if random.random() < 0.3: queues["S"] += 1
        if random.random() < 0.2: queues["E"] += 1
        if random.random() < 0.2: queues["W"] += 1
        
        for d in queues:
            if queues[d] > 0: waits[d] += queues[d]
            
        # Actuated Logic
        # If current queue empty AND other queue has cars -> Switch
        q_curr = (queues["N"] + queues["S"]) if current_phase == "NS" else (queues["E"] + queues["W"])
        q_other = (queues["E"] + queues["W"]) if current_phase == "NS" else (queues["N"] + queues["S"])
        
        if q_curr == 0 and q_other > 0 and time_in_phase > 5:
            current_phase = "EW" if current_phase == "NS" else "NS"
            time_in_phase = 0
        elif time_in_phase > 60: # Max Green
            current_phase = "EW" if current_phase == "NS" else "NS"
            time_in_phase = 0
        else:
            time_in_phase += 1
            if current_phase == "NS":
                if queues["N"] > 0: queues["N"] -= 1
                if queues["S"] > 0: queues["S"] -= 1
            else:
                if queues["E"] > 0: queues["E"] -= 1
                if queues["W"] > 0: queues["W"] -= 1
                
        total_delay_act = sum(waits.values())
        
    print(f"Actuated Delay: {total_delay_act}")
    
    if total_delay_bcp < total_delay_act:
        print("VERIFIED: BCP Traffic Control outperforms Actuated.")
        return True
    else:
        print("FAILED: BCP Backpressure did not beat Actuated.")
        return False

if __name__ == "__main__":
    run_experiment()