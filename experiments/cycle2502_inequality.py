"""
Cycle 2502: The Inequality (Gate 130)
Experiment: Trade in an unequal world.
Goal: Determine if Trade saves the poor without bankrupting the rich.
"""

import sys
import os
import csv
import time
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_inequality_experiment():
    print("⚖️ CYCLE 2502: THE INEQUALITY - TRADE VIABILITY")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed 2 Groups
    # Group A: The Rich (Cosmopolitans)
    # High Trust (0.9), High Initial Energy (500), Recurring Income
    print("🌱 Seeding The Rich...")
    for i in range(20): # Few rich
        agent = DigitalLifeform(name=f"Rich-{i}", lineage_id="Rich")
        agent.energy = 1000 
        # [..., Trust=0.9]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.5, 0.5, 0.1, 0.9]
        env.add_agent(agent)
        
    # Group B: The Poor (Tribalists)
    # Low Trust (0.1), Low Initial Energy (50), No Income
    print("🌱 Seeding The Poor...")
    for i in range(180): # Many poor
        agent = DigitalLifeform(name=f"Poor-{i}", lineage_id="Poor")
        agent.energy = 50
        # [..., Trust=0.1] - They DON'T trust strangers initially
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.5, 0.5, 0.1, 0.1]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2502_inequality.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_rich", "pop_poor", "avg_nrg_rich", "avg_nrg_poor", "trades"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            trades = 0
            
            # Income for the Rich (Simulating better territory/tech)
            # Give 10 energy per tick to Rich agents
            rich_agents = [a for a in env.agents if a.lineage_id == "Rich"]
            for a in rich_agents:
                a.energy += 10
                
            # No income for Poor agents (Starvation unless they trade/beg)
            
            # Execute Trades
            random.shuffle(env.agents)
            pairs = zip(env.agents[::2], env.agents[1::2])
            
            for a1, a2 in pairs:
                # Rich agents (Cosmo) are willing to trade/donate
                # Poor agents (Tribal) are suspicious, but desperate?
                # genesis.py: trade() checks if self.energy > 50 AND trust > 0.5.
                # Poor agents have Trust=0.1, so they won't initiate trade with strangers.
                # Rich agents have Trust=0.9, so they will initiate trade/donation.
                
                # A1 asks A2
                if a1.intent == 'trade':
                    if a1.trade(a2): trades += 1
                
                # A2 asks A1
                if a2.intent == 'trade':
                    if a2.trade(a1): trades += 1
            
            env.update()
            
            # Stats
            rich = [a for a in env.agents if a.lineage_id == "Rich"]
            poor = [a for a in env.agents if a.lineage_id == "Poor"]
            
            pop_rich = len(rich)
            pop_poor = len(poor)
            
            avg_nrg_rich = 0
            if rich: avg_nrg_rich = sum(a.energy for a in rich) / len(rich)
            
            avg_nrg_poor = 0
            if poor: avg_nrg_poor = sum(a.energy for a in poor) / len(poor)
            
            writer.writerow([tick, pop_rich, pop_poor, f"{avg_nrg_rich:.1f}", f"{avg_nrg_poor:.1f}", trades])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Rich={pop_rich} ({avg_nrg_rich:.1f}), Poor={pop_poor} ({avg_nrg_poor:.1f}), Trades={trades}")
            
            if len(env.agents) == 0:
                print("💀 EXTINCTION.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: Rich={pop_rich}, Poor={pop_poor}")

if __name__ == "__main__":
    run_inequality_experiment()
