"""
Cycle 2566: The Dictionary (Gate 194)
Goal: Observe the emergence of a shared language.
Mechanism:
1. Initialize 10 Agents.
2. Place Food in the center.
3. Agents wander, find food, label it.
4. Others verify and reinforce.
5. Track dominant label for 'FOOD'.
"""

import time
import random
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2566: The Dictionary ---")
    
    ecosystem = Ecosystem(capacity=20, width=20, height=20)
    
    # 1. Initialize Population (High Innovation for Language)
    population = []
    for i in range(10):
        agent = DigitalLifeform(name=f"Speaker-{i}")
        while len(agent.genome) < 11: agent.genome.append(0.5)
        agent.genome[9] = 0.95 # High Innovation
        agent.energy = 500
        # Start them near the center but scattered
        agent.x = random.randint(8, 12)
        agent.y = random.randint(8, 12)
        ecosystem.add_agent(agent)
        population.append(agent)
        
    # 2. Create "Real" Food Source (Implicitly via scan logic)
    # The agents need to perceive 'FOOD'.
    # In `scan()`, they look for agents with "Food" in name.
    # Let's add a dummy agent named "FoodSource".
    food = DigitalLifeform(name="FoodSource")
    food.x = 10
    food.y = 10
    food.energy = 10000 # Infinite food
    food.is_prey = True # Edible
    ecosystem.add_agent(food)
    
    print("Population Initialized. Food Source at (10, 10).")
    
    # 3. Simulation Loop
    ticks = 200
    
    for t in range(ticks):
        # Update Ecosystem (includes sense -> scan -> act)
        ecosystem.update()
        
        # Telemetry: What labels exist for FOOD?
        label_counts = {}
        
        for agent in population:
            # Check vocabulary for 'FOOD'
            # Structure: {label: {type: strength}}
            # We want to know which label is strongest for 'FOOD' for this agent
            
            best_label = agent.brain.get_label('FOOD')
            if best_label:
                label_counts[best_label] = label_counts.get(best_label, 0) + 1
                
        if t % 10 == 0:
            print(f"[EXP] Tick {t}: Food Labels: {label_counts}")
            
    # 4. Final Result
    print("\n--- Final Consensus ---")
    print(f"Food Labels: {label_counts}")
    
    if label_counts:
        winner = max(label_counts, key=label_counts.get)
        count = label_counts[winner]
        print(f"Dominant Label: '{winner}' with {count}/10 agents.")
        
        if count >= 5:
            print("SUCCESS: Majority consensus achieved.")
        else:
            print("FAILURE: Fragmentation (Tower of Babel).")
    else:
        print("FAILURE: No labels invented.")

if __name__ == "__main__":
    run_experiment()
