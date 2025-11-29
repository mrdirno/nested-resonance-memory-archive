import random
import json
import math

# -----------------------------------------------------------------------------
# CYCLE 3257: AD TECH BIDDING BCP
# -----------------------------------------------------------------------------
# Domain: Media
# Goal: Bid on ad slots to maximize conversions within budget.
# Hypothesis: BCP (Probabilistic Bidding) outperforms Fixed Bidding.
# -----------------------------------------------------------------------------

class Auction:
    def __init__(self):
        self.true_value = 0.0 # Hidden
        
    def run(self):
        self.true_value = random.uniform(0.1, 10.0) # Value of user
        return self.true_value

class Bidder:
    def bid(self, value_signal):
        raise NotImplementedError
    def feedback(self, win, cost, conversion_value):
        pass

class FixedBidder(Bidder):
    def bid(self, value_signal):
        return 2.0 # Always bid 2.0

class BCPBidder(Bidder):
    def __init__(self):
        # Track ROI
        self.roi_history = []
        self.bid_factor = 0.5 # Bid 50% of estimated value
        
    def bid(self, value_signal):
        # BCP: Bid = Estimated Value * P(Win) * ROI_Target
        # Here, signal is noisy estimate of value
        est_value = value_signal + random.gauss(0, 1.0)
        if est_value < 0: est_value = 0.1
        
        return est_value * self.bid_factor
        
    def feedback(self, win, cost, conversion_value):
        if win:
            roi = (conversion_value - cost) / cost if cost > 0 else 0
            self.roi_history.append(roi)
            
            # Adapt
            if roi > 1.0: # High ROI, bid more aggressively
                self.bid_factor += 0.01
            elif roi < 0.0: # Loss, bid less
                self.bid_factor -= 0.01

def run_simulation(bidder_cls, steps=1000):
    bidder = bidder_cls()
    budget = 1000.0
    revenue = 0.0
    
    for _ in range(steps):
        if budget <= 0: break
        
        auction = Auction()
        true_val = auction.run()
        
        # Signal (Noisy)
        signal = true_val + random.gauss(0, 0.5)
        
        my_bid = bidder.bid(signal)
        
        # Competitor (Random)
        comp_bid = random.uniform(0.1, 5.0)
        
        if my_bid > comp_bid:
            # Win (Second price)
            cost = comp_bid
            if budget >= cost:
                budget -= cost
                # Conversion? P(Conv) proportional to Value
                if random.random() < (true_val / 20.0): # Max val 10 -> 50% conv
                    conv_val = 10.0 # Standard payout
                    revenue += conv_val
                    bidder.feedback(True, cost, conv_val)
                else:
                    bidder.feedback(True, cost, 0.0)
            else:
                bidder.feedback(False, 0, 0)
        else:
            bidder.feedback(False, 0, 0)
            
    return revenue

def main():
    print("======================================================================")
    print("CYCLE 3257: AD TECH BIDDING BCP")
    print("======================================================================")
    
    steps = 2000
    
    fixed_rev = run_simulation(FixedBidder, steps)
    print(f"Fixed Revenue: {fixed_rev:.2f}")
    
    bcp_rev = run_simulation(BCPBidder, steps)
    print(f"BCP Revenue:   {bcp_rev:.2f}")
    
    improvement = ((bcp_rev - fixed_rev) / fixed_rev) * 100
    print("-" * 60)
    print(f"Improvement: {improvement:.2f}%")
    
    if bcp_rev > fixed_rev:
        print("RESULT: SUCCESS. Adaptive bidding maximized budget efficiency.")
    else:
        print("RESULT: FAILURE.")
        
    print("======================================================================")
    
    with open("results/cycle3257_ad_bidding.json", "w") as f:
        json.dump({"fixed": fixed_rev, "bcp": bcp_rev, "improvement": improvement}, f, indent=2)

if __name__ == "__main__":
    main()
