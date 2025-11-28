
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

from src.life.genesis import DigitalLifeform

class MaslowAgent(DigitalLifeform):
    def __init__(self, name):
        super().__init__(name=name)
        self.social_score = 0
        self.knowledge_score = 0
        self.legacy_score = 0
        
    def act_maslow(self):
        # 1. Survival
        if self.energy < 500:
            self.energy += 50 # Forage
            return "SURVIVAL"
            
        # 2. Social
        if self.social_score < 100:
            self.social_score += 10 # Chat
            self.energy -= 10
            return "SOCIAL"
            
        # 3. Knowledge
        if self.knowledge_score < 100:
            self.knowledge_score += 5 # Study
            self.energy -= 20
            return "KNOWLEDGE"
            
        # 4. Legacy
        self.legacy_score += 1 # Create Art
        self.energy -= 50
        return "LEGACY"

def run_apotheosis_experiment():
    print("✨ CYCLE 2558: THE APOTHEOSIS - SELF-ACTUALIZATION")
    print("   (Climbing Maslow's Hierarchy)")
    
    agents = [MaslowAgent(f"Human-{i}") for i in range(10)]
    
    counts = {'SURVIVAL':0, 'SOCIAL':0, 'KNOWLEDGE':0, 'LEGACY':0}
    
    for tick in range(1, 101):
        # Reset counts for visualization? No, let's track cumulative or snapshot
        tick_counts = {'SURVIVAL':0, 'SOCIAL':0, 'KNOWLEDGE':0, 'LEGACY':0}
        
        for a in agents:
            action = a.act_maslow()
            tick_counts[action] += 1
            
        if tick % 20 == 0:
            print(f"   Tick {tick}: {tick_counts}")
            
    # Final Status
    artists = len([a for a in agents if a.legacy_score > 0])
    print(f"🎨 Agents reaching Apotheosis: {artists}/10")
    
    if artists == 10:
        print("✨ CIVILIZATION ASCENDED.")

if __name__ == "__main__":
    run_apotheosis_experiment()
