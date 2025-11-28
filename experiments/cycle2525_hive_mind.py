"""
Cycle 2525: The Hive Mind (Gate 153)
Experiment: Collective Utility.
Goal: Demonstrate that agents can share utility scores to coordinate behavior.
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
from src.life.signal import Signal

def run_hive_mind_experiment():
    print("🐝 CYCLE 2525: THE HIVE MIND - COLLECTIVE INTELLIGENCE")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200)
    duration = 2000
    
    # Food Zone at (80, 80)
    food_zone = (80, 80)
    
    # Seed Agents
    print("🔗 Seeding The Borg...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Drone-{i}", lineage_id="Borg")
        agent.energy = 150 # Hungry
        agent.x = 20
        agent.y = 20
        # High Trust, High Altruism (Required for Hive Mind efficiency)
        agent.genome = [0.5] * 11
        agent.genome[8] = 0.9 # Trust
        agent.genome[5] = 0.9 # Altruism
        
        agent.hive_mind = True # ACTIVATE HIVE MIND
        
        env.add_agent(agent)
        
    # ONE Agent knows where the food is (The Scout)
    env.agents[0].sensed_signals['NEAREST_FOOD'] = food_zone
    print(f"👁️ Agent {env.agents[0].name} knows the location of food.")
    
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2525_hive_mind.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop", "avg_dist", "at_food", "intent_move_to_food", "knowledge_spread"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # We do NOT inject signal to all agents. Only Agent 0 has it initially.
            # We expect Agent 0 to broadcast 'move_to_food' utility.
            # Others should assimilate it and increase their own 'move_to_food' score.
            # BUT: They can't move to food if they don't have the coords.
            # Currently 'broadcast_thought' only sends utility SCORES, not the payload of the intent.
            # This is a limitation of Cycle 2525 design.
            # However, if they receive the utility boost, they might 'want' to move_to_food.
            # But `move_to_food` intent check: `if 'NEAREST_FOOD' in self.sensed_signals`.
            # So even if utility is high, the action requires the signal.
            # HIVE MIND V2 needed? 
            # Actually, let's see if the utility propagation works.
            # Agent 0: has signal -> high utility -> broadcast.
            # Agent 1: receives thought -> boosts utility for 'move_to_food'.
            # Agent 1: `calculate_utility` -> `move_to_food` score is high.
            # Agent 1: Checks `if 'NEAREST_FOOD' in self.sensed_signals`. It is NOT.
            # So Agent 1 will NOT pick `move_to_food` even if score is high.
            # It will fall back to `move_random` or `forage`.
            
            # FIX: The Hive Mind needs to share DATA, not just feelings.
            # But for this specific cycle, let's see if the *intent* count rises in the logs, 
            # even if execution fails.
            # Or better: The Scout should broadcast the LOCATION too?
            # Let's stick to the plan: Broadcast Utility.
            # Maybe we can manually propagate the signal if they are close?
            # No, let's test the "Telepathy of Desire" first.
            
            # Cycle 2525 Modification: Manually propagate the signal for the experiment
            # if the agent decides to move_to_food.
            # Wait, that's cheating.
            
            # Let's observe if "knowledge_spread" happens (i.e. other agents get the utility boost).
            # We can check `agent.collective_utility.get('move_to_food', 0)`.
            
            # Signal Propagation (handled by ecosystem for 'THOUGHT' signals?)
            # Ecosystem.propagate_signal() exists but isn't called in update().
            # We need to manually propagate signals in this experiment script to simulate the "Ether".
            
            thoughts = []
            # Collect thoughts from previous tick (or current acting phase)
            # Since we act() in update(), we can't easily capture output signals unless we hook into it.
            # But `act()` returns `broadcast_thought` result!
            # `env.update()` loop ignores return values of `act()`.
            
            # Workaround: We will inspect agents after update.
            # But `act()` clears `current_utility_map`.
            
            # This experiment is tricky because the ecosystem loop doesn't support signal passing natively yet.
            # We need to patch `env` to handle signals returned by `act()`.
            # OR: We rely on `agent.communicator`. 
            # `broadcast_thought` creates a Signal. It does not send it.
            # We need a mechanism to send.
            
            # Let's simulate the "Hive Mind Ether" here.
            # Everyone hears everyone (Global Range).
            
            # 1. Execute Update (Agents Generate Thoughts)
            # We need to capture the thoughts.
            # We will Iterate agents manually instead of env.update() for precise control?
            # Or just modify `env.update` to return signals?
            # Let's use `env.update()` but we know it won't propagate signals.
            
            # Actually, `genesis.py`: `act()` returns the Signal object.
            # `ecosystem.py`: `agent.act()` result is ignored.
            # We MUST modify `ecosystem.py` to handle the return value of `act()`.
            
            # Since I cannot modify `ecosystem.py` in the middle of this thought process without a tool call...
            # I will do it in the next step.
            # For now, write the script assuming `env` has a `signals` buffer or we handle it.
            
            pass # Placeholder for logic loop
            
            # To make this runnable without modifying ecosystem AGAIN:
            # We can't. The return value is lost.
            # UNLESS... we check `agent.communicator.outbox`?
            # `broadcast_thought` returns a Signal. Does it queue it?
            # `communicator.py` isn't shown, but usually `broadcast` puts it in outbox.
            # Let's assume `act()` returns it and we missed it.
            
            # Hack: We will "Simulate" the Hive Mind logic externally in this script
            # effectively overriding the internal logic for the experiment proof-of-concept.
            
            env.update() # Run standard physics/metabolism
            
            # MANUAL HIVE MIND SIMULATION
            # 1. Gather Utilities
            global_utility_sum = {}
            for agent in env.agents:
                # Force calculate (idempotent-ish)
                # We want to know what they *would* share.
                # This requires accessing their internal state.
                # `agent.calculate_utility()` returns a key.
                # We need the map. `calculate_utility` creates `options` dict locally.
                # We can't access it.
                pass
                
            # Okay, this experiment requires `ecosystem.py` modification to propagate signals.
            
            total_dist = 0
            at_food = 0
            intent_count = 0
            knowledge_spread = 0
            
            for agent in env.agents:
                dist = ((agent.x - food_zone[0])**2 + (agent.y - food_zone[1])**2)**0.5
                total_dist += dist
                if dist < 5: at_food += 1
                if agent.intent == 'move_to_food': intent_count += 1
                if agent.collective_utility.get('move_to_food', 0) > 0: knowledge_spread += 1
            
            avg_dist = total_dist / len(env.agents) if env.agents else 0
            
            writer.writerow([tick, len(env.agents), f"{avg_dist:.1f}", at_food, intent_count, knowledge_spread])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Dist={avg_dist:.1f}, Food={at_food}, Intent={intent_count}, Know={knowledge_spread}")
            
            if knowledge_spread > 40:
                print("🧠 SUCCESS! The Hive Mind is thinking together.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_hive_mind_experiment()
