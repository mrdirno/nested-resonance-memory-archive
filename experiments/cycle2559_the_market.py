
import sys
import os
import csv
import time
import random
import math
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Trader:
    def __init__(self, name, capital):
        self.name = name
        self.capital = capital
        self.belief = 100.0 # Estimated Price
        
    def trade(self, current_price):
        # Dampened Force Model
        # Force = Capital * tanh(Belief - Price) * scaling
        diff = self.belief - current_price
        
        # Saturation at diff=10
        activation = math.tanh(diff / 10.0)
        
        force = self.capital * activation * 0.01
        return force

def run_market_experiment():
    print("📈 CYCLE 2559: THE MARKET - FINANCIAL RESONANCE")
    print("   (Mapping NRM Physics to Price Discovery)")
    
    # 1. Setup
    TRUE_VALUE = 100.0
    market_price = 100.0
    
    traders = []
    # Informed Traders (Know Truth, Low Capital)
    for i in range(5):
        t = Trader(f"Informed-{i}", 1000)
        t.belief = TRUE_VALUE # They know!
        traders.append(t)
        
    # Noise Traders (Random Beliefs, High Capital)
    for i in range(5):
        t = Trader(f"Whale-{i}", 10000) # 10x Capital
        t.belief = random.uniform(50, 150) # Wrong!
        traders.append(t)
        
    duration = 100
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2559_the_market.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "true_value", "market_price", "dissonance"])
        
        for tick in range(1, duration + 1):
            
            # 1. Market Dynamics (Shock)
            if tick == 50:
                print("⚠️  SHOCK! TRUE VALUE DROPS TO 50!")
                TRUE_VALUE = 50.0
                # Informed update immediately
                for t in traders:
                    if "Informed" in t.name: t.belief = TRUE_VALUE
            
            # 2. Trading
            net_force = 0
            for t in traders:
                net_force += t.trade(market_price)
                
            # 3. Price Update
            market_price += net_force
            
            # 4. Whale Adaptation (Slow Learning)
            for t in traders:
                if "Whale" in t.name:
                    # Whales follow the trend (Momentum)
                    # t.belief = market_price # Simple follower
                    # Or partial correction towards price
                    t.belief += 0.1 * (market_price - t.belief)
            
            dissonance = abs(market_price - TRUE_VALUE)
            writer.writerow([tick, TRUE_VALUE, f"{market_price:.2f}", f"{dissonance:.2f}"])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Value={TRUE_VALUE} Price={market_price:.2f} Diss={dissonance:.2f}")

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_market_experiment()
