"""
Cycle 2501: The Silk Road (Gate 129)
Experiment: Trade and Reputation.
Goal: Compare Tribal Stagnation vs. Cosmopolitan Growth.
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

def run_trade_war():
    print("🐫 CYCLE 2501: THE SILK ROAD - TRADE WAR")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=300, prey_capacity=300, predator_capacity=0)
    duration = 2000
    
    # Seed 2 Groups
    # Group A: Tribalists (Low Trust, High Cannibalism)
    print("🌱 Seeding Tribalists...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Tribal-{i}", lineage_id="Tribal")
        agent.energy = 100
        # Genome: [..., Cannibalism(0.8), Trust(0.1)]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.5, 0.5, 0.5, 0.8, 0.1] 
        env.add_agent(agent)
        
    # Group B: Cosmopolitans (High Trust, Low Cannibalism)
    print("🌱 Seeding Cosmopolitans...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Cosmo-{i}", lineage_id="Cosmo")
        agent.energy = 100
        # Genome: [..., Cannibalism(0.1), Trust(0.9)]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.5, 0.5, 0.5, 0.1, 0.9]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2501_trade_war.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_tribal", "pop_cosmo", "avg_nrg_tribal", "avg_nrg_cosmo", "trades"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            trades = 0
            
            # Environmental Stress: Low Food
            if env.agents:
                # Feed 10% of agents
                lucky_ones = random.sample(env.agents, max(1, int(len(env.agents) * 0.1)))
                for a in lucky_ones:
                    a.energy += 30
            
            # Manual Intent Injection (Simulation Control)
            for agent in env.agents:
                # If agent has high trust and low energy, it tries to 'trade' (beg)
                # genesis.py act() now sets this automatically based on gene 8
                pass
                
            # Execute Trades (Simulation Logic)
            # We need to facilitate the meeting of agents
            # Random pairings
            random.shuffle(env.agents)
            pairs = zip(env.agents[::2], env.agents[1::2])
            
            for a1, a2 in pairs:
                # If a1 wants to trade, it asks a2
                if a1.intent == 'trade':
                    if a1.trade(a2):
                        trades += 1
                # If a2 wants to trade, it asks a1
                if a2.intent == 'trade':
                    if a2.trade(a1):
                        trades += 1
                        
                # Hunting logic (Tribalists might hunt)
                if a1.intent == 'hunt':
                    a1.hunt(a2)
                if a2.intent == 'hunt':
                    a2.hunt(a1)
            
            env.update()
            
            # Stats
            tribals = [a for a in env.agents if a.lineage_id == "Tribal"]
            cosmos = [a for a in env.agents if a.lineage_id == "Cosmo"]
            
            pop_tribal = len(tribals)
            pop_cosmo = len(cosmos)
            
            avg_nrg_tribal = 0
            if tribals: avg_nrg_tribal = sum(a.energy for a in tribals) / len(tribals)
            
            avg_nrg_cosmo = 0
            if cosmos: avg_nrg_cosmo = sum(a.energy for a in cosmos) / len(cosmos)
            
            writer.writerow([tick, pop_tribal, pop_cosmo, f"{avg_nrg_tribal:.1f}", f"{avg_nrg_cosmo:.1f}", trades])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Tribal={pop_tribal} ({avg_nrg_tribal:.1f}), Cosmo={pop_cosmo} ({avg_nrg_cosmo:.1f}), Trades={trades}")
            
            if len(env.agents) == 0:
                print("💀 EXTINCTION.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: Tribal={pop_tribal}, Cosmo={pop_cosmo}")

if __name__ == "__main__":
    run_trade_war()
