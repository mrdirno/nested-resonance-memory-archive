
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
        self.position = 0.0 # Assets held
        self.belief = 100.0
        
    def decide_trade(self, current_price):
        # Returns signed volume (Buy > 0, Sell < 0)
        # Simple: Bet 10% of Capital per trade
        diff = self.belief - current_price
        confidence = math.tanh(diff / 10.0)
        
        # Bet size in dollars
        bet_size = self.capital * 0.1 * confidence
        
        # Volume = Dollars / Price
        if current_price <= 0.1: current_price = 0.1
        volume = bet_size / current_price
        return volume

def run_arbitrage_experiment():
    print("⚖️ CYCLE 2560: THE ARBITRAGEUR - MARKET CORRECTION")
    print("   (Wealth Transfer from Noise to Signal)")
    
    TRUE_VALUE = 100.0
    market_price = 100.0
    
    traders = []
    # Whales (Noise)
    for i in range(5):
        t = Trader(f"Whale-{i}", 10000)
        t.belief = 200.0 # Persistent Bull Bubble
        traders.append(t)
        
    # Arbitrageur (Smart)
    arb = Trader("Arbitrageur", 1000)
    arb.belief = TRUE_VALUE # Knows truth
    traders.append(arb)
    
    duration = 200
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2560_arbitrage.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "price", "arb_capital", "whale_capital"])
        
        for tick in range(1, duration + 1):
            
            # 1. Matching Engine (Simplified)
            total_volume = 0
            net_volume = 0
            
            orders = []
            for t in traders:
                vol = t.decide_trade(market_price)
                orders.append((t, vol))
                net_volume += vol
                total_volume += abs(vol)
                
            # 2. Price Impact
            # Price moves by Net Volume / Liquidity
            # Liquidity factor
            impact = net_volume * 0.1
            old_price = market_price
            market_price += impact
            if market_price < 1.0: market_price = 1.0
            
            # 3. PnL Settlement (Mark to Market)
            # Traders bought/sold at Old Price.
            # Their portfolio value changes as Price moves to New Price.
            # PnL = Position * (NewPrice - OldPrice)
            # Wait, logic check:
            # If I bought 1 unit at 100, and price goes to 110, I made 10.
            # If I bought 1 unit, I spent 100 cash. My asset value is 110. Net Wealth = -100 + 110 = 10 gain.
            
            # Let's track Wealth directly.
            # Wealth = Cash + (Position * Price)
            # But our simple model just updates Capital based on Trade PnL?
            # Let's update Capital based on the *Trade just executed*.
            # If I buy, I swap Cash for Asset.
            # Then Asset revalues.
            
            for t, vol in orders:
                # Execute Trade
                cost = vol * old_price
                t.capital -= cost # Spend cash
                t.position += vol # Get asset
                
                # Mark to Market
                asset_value = t.position * market_price
                
                # To measure "Capital" for next bet, we assume they can leverage their assets
                # Or we just track Net Worth
                net_worth = t.capital + asset_value
                
                # Bankruptcy Check
                if net_worth <= 0:
                    t.capital = 0
                    t.position = 0
                    
            # Calculate totals
            arb_wealth = arb.capital + (arb.position * market_price)
            whale_wealth = sum([t.capital + (t.position * market_price) for t in traders if "Whale" in t.name])
            
            writer.writerow([tick, f"{market_price:.2f}", f"{arb_wealth:.2f}", f"{whale_wealth:.2f}"])
            
            if tick % 20 == 0:
                print(f"   Tick {tick}: Price={market_price:.2f} ArbWealth={arb_wealth:.0f} WhaleWealth={whale_wealth:.0f}")
                
            # Reset Arbitrageur belief (always knows truth)
            arb.belief = TRUE_VALUE

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_arbitrage_experiment()
