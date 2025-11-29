
import sys
import os
import json

# Ensure we can import the BCP library
sys.path.append(os.path.join(os.getcwd(), 'src'))

def log(msg):
    print(f"[CYCLE 3307] {msg}")

def run_storage_bcp(prices, efficiency):
    # Simple Algorithm: 
    # Find min price to buy, max price to sell.
    # Spread > Cost of Cycle?
    # Cost of Cycle = Buying Price + Opportunity Cost?
    # Arbitrage condition: P_sell * Eff > P_buy.
    
    # Let's maximize Profit = sum(discharge * P) - sum(charge * P).
    # Subject to constraints.
    
    # Heuristic BCP:
    # Mean Price P_avg.
    # If P < P_avg * Eff: Charge.
    # If P > P_avg / Eff: Discharge.
    
    p_avg = sum(prices) / len(prices)
    buy_thresh = p_avg * efficiency
    sell_thresh = p_avg / efficiency
    
    state_of_charge = 0.0 # 0 to 1.0 (100 MWh cap)
    max_cap = 100.0
    rate = 20.0 # MW per hour
    
    profit = 0.0
    actions = []
    
    for t, p in enumerate(prices):
        action = "IDLE"
        mw = 0.0
        
        if p < buy_thresh and state_of_charge < max_cap:
            # Charge
            mw = min(rate, max_cap - state_of_charge)
            state_of_charge += mw
            profit -= mw * p
            action = "CHARGE"
            
        elif p > sell_thresh and state_of_charge > 0:
            # Discharge
            mw = min(rate, state_of_charge)
            state_of_charge -= mw
            profit += mw * p * efficiency # Sell output (input equivalent? No, sell energy)
            # Wait, if we discharge X stored, we sell X * Eff?
            # Usually Eff is Round Trip. Let's apply on discharge.
            # output = mw * efficiency? Or is 'mw' the output?
            # Let's say we drain 'mw' from battery. Output to grid is 'mw * eff'.
            # Profit += (mw * eff) * p.
            profit += (mw * efficiency) * p
            action = "DISCHARGE"
            
        actions.append((t, p, action, mw))
        
    return profit, actions

def main():
    log("GATE 931: STORAGE ARBITRAGE AS BCP")
    
    # Duck Curve Prices (24h)
    # Night: 30
    # Morning Peak: 60
    # Solar Dip (Noon): 10
    # Evening Peak: 100
    
    prices = [30, 30, 30, 30, 40, 60, 60, 50, 30, 20, 10, 10, 10, 10, 20, 40, 80, 100, 100, 80, 60, 40, 30, 30]
    eff = 0.9
    
    profit, actions = run_storage_bcp(prices, eff)
    
    log(f"Total Profit: ${profit:.2f}")
    
    validation_score = 0
    
    # Check Noon (t=10,11,12,13) -> Should Charge
    noon_actions = [a[2] for a in actions[10:14]]
    if "CHARGE" in noon_actions:
        validation_score += 1
        log("VALID: Charges during Solar Dip.")
    else:
        log("INVALID: Missed solar dip.")
        
    # Check Evening (t=17,18,19) -> Should Discharge
    eve_actions = [a[2] for a in actions[17:20]]
    if "DISCHARGE" in eve_actions:
        validation_score += 1
        log("VALID: Discharges during Evening Peak.")
    else:
        log("INVALID: Missed peak.")
        
    # Check Profit
    if profit > 0:
        validation_score += 1
        log("VALID: Profitable arbitrage.")
    else:
        log("INVALID: Loss made.")
        
    # Output results
    output = {
        "cycle": 3307,
        "phase": 187,
        "gate": 931,
        "validation": validation_score/3.0
    }
    
    with open("data/results/cycle3307_storage_arbitrage.json", "w") as f:
        json.dump(output, f, indent=2)
        
    log("Gate 931 Complete.")

if __name__ == "__main__":
    main()
