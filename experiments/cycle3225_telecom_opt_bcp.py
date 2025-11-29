import random
import math

# ======================================================================
# CYCLE 3225: TELECOM NETWORK OPTIMIZATION AS BCP
# ======================================================================
# Hypothesis: Network routing is BCP.
#   V(packet) = Priority - lambda(Buffer_Occupancy) * Latency_Cost
#   High lambda -> Drop low priority (Active Queue Management)
#   Low lambda -> Queue everything
# ======================================================================

def run_experiment():
    print("CYCLE 3225: Network Optimization as BCP")
    
    T = 1000
    capacity = 10.0 # Packets per tick
    buffer_size = 50
    
    # Traffic: High Priority (Voice) vs Low Priority (Data)
    # Voice: Priority=10, Latency_Sensitive=High
    # Data: Priority=1, Latency_Sensitive=Low
    
    # BCP Queue
    queue = [] # (priority, arrival_time)
    dropped_voice = 0
    dropped_data = 0
    
    # Static Queue (FIFO with Tail Drop)
    static_queue = []
    s_dropped_voice = 0
    s_dropped_data = 0
    
    for t in range(T):
        # Arrivals
        # Burst traffic
        n_voice = random.choice([0, 1, 5])
        n_data = random.choice([0, 2, 10])
        
        # --- BCP LOGIC ---
        # Lambda = Stress = 1 / (epsilon + Free_Space)
        free_space = buffer_size - len(queue)
        lamb = 100.0 / (1.0 + max(0, free_space)) 
        
        # Admission Control
        for _ in range(n_voice):
            # V = Priority(10) - lambda * Cost(1)
            if 10 - lamb * 1.0 > 0:
                queue.append((10, t))
            else:
                dropped_voice += 1
                
        for _ in range(n_data):
            # V = Priority(1) - lambda * Cost(1)
            if 1 - lamb * 1.0 > 0:
                queue.append((1, t))
            else:
                dropped_data += 1
                
        # Service
        # Priority Queueing implied by BCP (Maximize V -> Serve High Val first)
        queue.sort(key=lambda x: x[0], reverse=True)
        queue = queue[:buffer_size] # Hard limit check
        
        serviced = 0
        while serviced < capacity and queue:
            queue.pop(0)
            serviced += 1
            
        # --- STATIC LOGIC (FIFO Tail Drop) ---
        for _ in range(n_voice):
            if len(static_queue) < buffer_size:
                static_queue.append((10, t))
            else:
                s_dropped_voice += 1
                
        for _ in range(n_data):
            if len(static_queue) < buffer_size:
                static_queue.append((1, t))
            else:
                s_dropped_data += 1
                
        s_serviced = 0
        while s_serviced < capacity and static_queue:
            static_queue.pop(0) # FIFO
            s_serviced += 1
            
    print(f"BCP: Dropped Voice={dropped_voice}, Dropped Data={dropped_data}")
    print(f"Static: Dropped Voice={s_dropped_voice}, Dropped Data={s_dropped_data}")
    
    # Verification
    # BCP should drop Data to save Voice.
    # Static drops both equally (proportional to arrival).
    
    if dropped_voice < s_dropped_voice:
        print("VERIFIED: BCP protects High Priority traffic.")
        return True
    else:
        print("FAILED: BCP did not improve Voice QoS.")
        return False

if __name__ == "__main__":
    run_experiment()