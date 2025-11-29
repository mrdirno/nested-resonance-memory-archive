import random

# ======================================================================
# CYCLE 3226: SPECTRUM MANAGEMENT AS BCP
# ======================================================================
# Hypothesis: Dynamic Spectrum Access is BCP.
#   V(channel) = Quality(SNR) - lambda(Contention) * Switching_Cost
#   High lambda -> Stay on channel (tolerate noise).
#   Low lambda -> Switch to best channel.
# ======================================================================

def run_experiment():
    print("CYCLE 3226: Spectrum Management as BCP")
    
    T = 100
    channels = 10
    users = 20 # More users than channels -> Scarcity
    
    # State
    # interference[channel]
    
    total_throughput_bcp = 0
    total_throughput_fixed = 0
    
    # BCP Users
    user_channels = [random.randint(0, channels-1) for _ in range(users)]
    
    # Fixed Users (Static assignment)
    fixed_channels = [i % channels for i in range(users)]
    
    for t in range(T):
        # Environment: Interference fluctuates
        noise = [random.random() * 0.5 for _ in range(channels)]
        
        # --- BCP Logic ---
        # Calculate Lambda (Contention per channel)
        # Real system: Measure Packet Error Rate
        
        # Local decision for User 0 (Agent)
        # Current Channel
        curr = user_channels[0]
        
        # Evaluate all channels
        # V = (1 - Noise) - lambda * Switch_Cost
        # Lambda? Global congestion? Or simply Local Cost?
        # Let's say lambda is fixed "Laziness" or "Cost Sensitivity".
        lamb = 0.1 
        switch_cost = 0.5
        
        best_v = -1
        best_c = curr
        
        for c in range(channels):
            congestion = user_channels.count(c) # How many others?
            snr = 1.0 - noise[c] - (congestion * 0.1)
            
            gain = max(0, snr)
            cost = switch_cost if c != curr else 0
            
            v = gain - lamb * cost
            
            if v > best_v:
                best_v = v
                best_c = c
                
        user_channels[0] = best_c
        
        # Throughput Calculation
        # BCP
        cong = user_channels.count(user_channels[0])
        th = max(0, 1.0 - noise[user_channels[0]] - (cong * 0.1))
        total_throughput_bcp += th
        
        # Fixed
        cong_f = fixed_channels.count(fixed_channels[0])
        th_f = max(0, 1.0 - noise[fixed_channels[0]] - (cong_f * 0.1))
        total_throughput_fixed += th
        
    print(f"BCP Throughput: {total_throughput_bcp:.2f}")
    print(f"Fixed Throughput: {total_throughput_fixed:.2f}")
    
    if total_throughput_bcp > total_throughput_fixed:
        print("VERIFIED: BCP Spectrum Access outperforms Fixed.")
        return True
    else:
        print("FAILED: No improvement.")
        return False

if __name__ == "__main__":
    run_experiment()