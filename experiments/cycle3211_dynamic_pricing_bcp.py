import random
import math

# ======================================================================
# CYCLE 3211: DYNAMIC PRICING AS BCP
# ======================================================================
# Hypothesis: Pricing is a BCP allocation of demand.
#   Price P adjusts to balance flow rate against budget pressure.
#   High Lambda (Scarcity) -> High Price (Harvest value, reduce replacement risk)
#   Low Lambda (Abundance) -> Low Price (Maximize flow, liquidity)
# ======================================================================

def run_experiment():
    print("CYCLE 3211: Dynamic Pricing as BCP")
    
    # Simulation Parameters
    T = 365
    initial_stock = 1000
    initial_cash = 1000.0
    base_cost = 10.0
    
    # Demand Curve: D = A * P^(-Elasticity)
    A = 5000
    Elasticity = 2.0
    
    # State
    stock = initial_stock
    cash = initial_cash
    
    history = []
    
    for t in range(T):
        # 1. Replenishment (Simplified)
        # Supplier arrives every 10 days
        if t % 10 == 0 and cash > base_cost * 100:
            buy_qty = 100
            stock += buy_qty
            cash -= buy_qty * base_cost
            
        # 2. Calculate Lambda (Scarcity Pressure)
        # Lambda depends on Cash (need liquidity) AND Stock (need shelf space/turnover)
        # For pricing, Scarcity of STOCK increases price. Scarcity of CASH decreases price (fire sale)?
        # Wait. BCP: V(sale) = Price - Cost - lambda * Replacement_Difficulty
        
        # Let's model Lambda as "Pressure to Acquire Cash"
        # Low cash -> High lambda -> "Must sell now" -> Lower Price? 
        # OR Low stock -> High lambda_stock -> "Must conserve stock" -> Higher Price.
        
        # Let's use Dual Lambda:
        lambda_cash = 1000.0 / (100.0 + cash) # Need for money
        lambda_stock = 100.0 / (1.0 + stock)  # Need for conservation
        
        # Pricing Heuristic via BCP:
        # Target Price = Base_Price * (1 + Markup)
        # Markup scales with lambda_stock (scarcity premium)
        # Markup reduces with lambda_cash (liquidity discount)
        
        base_price = base_cost * 1.5 # 50% margin baseline
        
        # BCP Equation:
        # Price = Base * (1 + k_stock * lambda_stock - k_cash * lambda_cash)
        k_stock = 10.0
        k_cash = 5.0
        
        price_mult = 1.0 + (k_stock * lambda_stock) - (k_cash * lambda_cash)
        price = max(base_cost, base_price * price_mult) # Floor at cost
        
        # 3. Market Demand
        demand = int(A * (price ** -Elasticity))
        sales = min(stock, demand)
        
        revenue = sales * price
        stock -= sales
        cash += revenue
        
        if t % 50 == 0:
            print(f"Day {t}: Stock={stock}, Cash={cash:.2f}, Price={price:.2f}")
            
    print(f"FINAL: Stock={stock}, Cash={cash:.2f}")
    
    if cash > initial_cash:
        print("VERIFIED: BCP Dynamic Pricing generates profit.")
        return True
    else:
        print("FAILED: Loss incurred.")
        return False

if __name__ == "__main__":
    run_experiment()
