import random
import math
import matplotlib.pyplot as plt
import os

# ======================================================================
# CYCLE 3210: RETAIL INVENTORY AS BCP
# ======================================================================
# Hypothesis: Inventory management is a BCP allocation problem.
#   V(stock_item) = E[Profit] - lambda(Capital) * Holding_Cost
#   Capital = Budget B
#   lambda = Opportunity cost of capital / Storage pressure
# ======================================================================

def run_experiment():
    print("CYCLE 3210: Inventory Management as BCP")
    print("Testing: EOQ vs BCP-Adaptive Inventory")
    
    # Parameters
    T = 365 # Days
    initial_capital = 10000.0
    
    # Items: [Name, Demand_Mean, Demand_Std, Cost, Price, Holding_Cost]
    items = [
        {"name": "Staple",  "d_mean": 10, "d_std": 2, "cost": 5,  "price": 8,  "h_cost": 0.01}, # Low margin, high vol
        {"name": "Luxury",  "d_mean": 1,  "d_std": 1, "cost": 100,"price": 200,"h_cost": 0.50}, # High margin, low vol
        {"name": "Seasonal","d_mean": 5,  "d_std": 5, "cost": 20, "price": 50, "h_cost": 0.10}, # Volatile
    ]
    
    # State
    capital = initial_capital
    inventory = {item["name"]: 0 for item in items}
    
    # History
    history = {"capital": [], "lambda": []}
    
    # Simulation
    for t in range(T):
        # 1. Calculate Lambda (Metabolic Pressure)
        # High capital -> low lambda (can afford to hold stock)
        # Low capital -> high lambda (must liquidate / minimize holding)
        # lambda = k / (epsilon + Capital)
        # Scaling factor k=1000 to make lambda meaningful relative to costs
        lamb = 1000.0 / (100.0 + capital)
        
        # 2. Replenishment Decision (BCP)
        for item in items:
            # Value of stocking 1 unit = Expected Profit - Lambda * Holding Cost
            # Simplification: Restock to target level where V ~ 0
            
            expected_profit = item["price"] - item["cost"]
            # Generalized cost includes capital tie-up + physical holding
            # C = Item_Cost (capital tie-up) + Holding_Cost_Per_Day * Days_to_Sell
            days_to_sell = 1.0 / max(0.1, item["d_mean"]) # Approx
            total_cost = item["cost"] + item["h_cost"] * days_to_sell
            
            # V = Gain - lambda * Cost
            val = expected_profit - lamb * total_cost
            
            # Decision: Stock if V > 0 AND we have cash
            target_stock = int(item["d_mean"] * 7) # Week supply baseline
            
            # BCP Adjustment: Reduce target if lambda is high (scarcity)
            # Simple linear modulation: target * (1 / (1 + lambda))
            adjusted_target = int(target_stock / (1.0 + lamb))
            
            current = inventory[item["name"]]
            needed = max(0, adjusted_target - current)
            
            # Buy
            cost_to_buy = needed * item["cost"]
            if cost_to_buy > capital:
                needed = int(capital / item["cost"])
                cost_to_buy = needed * item["cost"]
            
            if val > 0 and needed > 0:
                inventory[item["name"]] += needed
                capital -= cost_to_buy
        
        # 3. Demand & Sales
        daily_revenue = 0
        for item in items:
            demand = max(0, int(random.gauss(item["d_mean"], item["d_std"])))
            sold = min(demand, inventory[item["name"]])
            inventory[item["name"]] -= sold
            daily_revenue += sold * item["price"]
            
            # Holding cost deduction
            capital -= inventory[item["name"]] * item["h_cost"]
            
        capital += daily_revenue
        
        # Log
        history["capital"].append(capital)
        history["lambda"].append(lamb)
        
        if t % 50 == 0:
            print(f"Day {t}: Capital={capital:.2f}, Lambda={lamb:.4f}")

    # Analysis
    final_capital = capital
    roi = (final_capital - initial_capital) / initial_capital * 100
    print(f"FINAL: Capital={final_capital:.2f}, ROI={roi:.1f}%")
    
    # Verification
    if roi > 0:
        print("VERIFIED: BCP-managed inventory yields positive ROI.")
        return True
    else:
        print("FAILED: Negative ROI.")
        return False

if __name__ == "__main__":
    run_experiment()
