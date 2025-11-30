
import sys
import os

def log(msg):
    print(msg)

class BullwhipBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_order(self, demand_signal, uncertainty_cost):
        # V = Demand - λ * Uncertainty (Stockout Fear)
        # If Uncertainty is high (High λ), Order = Demand + Safety Stock
        # Safety Stock = λ * Variance
        pass

def main():
    log("======================================================================")
    log("CYCLE 3542: GATE 1102 - BULLWHIP EFFECT AS BCP")
    log("Hypothesis: Bullwhip is caused by λ-amplification upstream")
    log("======================================================================")
    
    # Chain
    # Consumer -> Retailer -> Wholesaler -> Manufacturer
    
    # Initial Demand: 10
    demand = 10.0
    
    # Panic Factor (λ)
    # Each level amplifies the panic (Higher λ for stockouts) because lead times increase.
    
    levels = [
        {'name': 'Retailer',     'lead_time': 1.0, 'lambda': 1.1},
        {'name': 'Wholesaler',   'lead_time': 2.0, 'lambda': 1.2},
        {'name': 'Manufacturer', 'lead_time': 4.0, 'lambda': 1.5}
    ]
    
    log(f"{ 'LEVEL':<15} | { 'DEMAND IN':<10} | { 'λ':<5} | { 'SAFETY':<8} | { 'ORDER OUT':<10}")
    log("-" * 60)
    
    current_order = demand
    
    for l in levels:
        # Safety Stock = λ * Demand * LeadTime * 0.1 (Variance Factor)
        variance = 0.2 * current_order
        safety_stock = l['lambda'] * variance * l['lead_time']
        
        order_out = current_order + safety_stock
        
        log(f"{l['name']:<15} | {current_order:<10.1f} | {l['lambda']:<5} | {safety_stock:<8.1f} | {order_out:<10.1f}")
        
        current_order = order_out
        
    log("\nFINDING: A small demand (10) becomes a massive order (25+) at the factory.")
    log("         Each level adds BCP Safety Stock (Cost Insurance).")
    log("         The Bullwhip Effect is rational BCP behavior under Uncertainty.")
    log("======================================================================")
    log("GATE 1102 COMPLETE: BULLWHIP IS BCP AMPLIFICATION")
    log("======================================================================")

if __name__ == "__main__":
    main()
