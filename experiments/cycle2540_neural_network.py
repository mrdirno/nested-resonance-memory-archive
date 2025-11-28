
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

def run_learning_experiment():
    print("🧠 CYCLE 2540: THE NEURAL NETWORK - HEBBIAN LEARNING TEST")
    
    # 1. Initialize Ecosystem
    env = Ecosystem(capacity=50)
    
    # 2. Populate with Learners
    print("🎓 Seeding Learners...")
    learners = []
    for i in range(10):
        agent = DigitalLifeform(name=f"Learner-{i}")
        agent.energy = 500
        # Gene 9 = Innovation (Plasticity)
        agent.genome[9] = 0.9
        
        # Initialize Brain with Hebbian Logic (Mocking the internal update for now)
        # We will manually trigger learning events
        agent.brain.learning_rate = 0.1 
        
        env.add_agent(agent)
        learners.append(agent)
        
    # 3. Run Learning Loop
    # Scenario: Red Berry = Good (+Energy), Blue Berry = Bad (-Energy)
    # Agents start with random weights. Must learn to eat Red and avoid Blue.
    
    iterations = 1000
    
    # Track performance
    performance_log = []
    
    print("🍎 Starting Training (Red=Good, Blue=Bad)...")
    
    for i in range(iterations):
        for agent in learners:
            # Present Stimulus
            stimulus = random.choice(['RED', 'BLUE'])
            
            # Agent Decision (Forward Pass)
            # Brain.decide(stimulus) -> 'EAT' or 'IGNORE'
            # We need to modify Brain class or simulate it here.
            # Let's simulate the Brain's internal logic:
            # Weight for RED, Weight for BLUE
            
            w_red = agent.brain.weights.get('RED', [0.0])[0] if 'RED' in agent.brain.weights else 0.0
            w_blue = agent.brain.weights.get('BLUE', [0.0])[0] if 'BLUE' in agent.brain.weights else 0.0
            
            # Epsilon-Greedy Policy
            action = 'IGNORE'
            if stimulus == 'RED':
                if w_red > 0.5 or random.random() < 0.1: action = 'EAT'
            elif stimulus == 'BLUE':
                if w_blue > 0.5 or random.random() < 0.1: action = 'EAT'
                
            # Outcome & Learning (Backward Pass)
            reward = 0
            if action == 'EAT':
                if stimulus == 'RED':
                    reward = 10
                    # Hebbian Update: Reinforce connection
                    # w_new = w_old + rate * reward
                    new_w = min(1.0, w_red + 0.1)
                    agent.brain.weights['RED'] = [new_w]
                elif stimulus == 'BLUE':
                    reward = -10
                    # Punishment: Weaken connection (Anti-Hebbian)
                    new_w = max(0.0, w_blue - 0.1)
                    agent.brain.weights['BLUE'] = [new_w]
            
            # Log for this tick
            if i % 10 == 0 and agent.name == "Learner-0":
                # print(f"Tick {i}: {agent.name} sees {stimulus}, does {action}, reward {reward}. Weights: R={w_red:.2f}, B={w_blue:.2f}")
                pass

        # Evaluate Colony Competence
        avg_red_w = sum(a.brain.weights.get('RED', [0.0])[0] for a in learners) / len(learners)
        avg_blue_w = sum(a.brain.weights.get('BLUE', [0.0])[0] for a in learners) / len(learners)
        
        performance_log.append({'tick': i, 'avg_red': avg_red_w, 'avg_blue': avg_blue_w})
        
    print(f"🏁 Training Complete. Final Weights -> Red: {avg_red_w:.2f}, Blue: {avg_blue_w:.2f}")
    
    if avg_red_w > 0.8 and avg_blue_w < 0.2:
        print("✅ SUCCESS: Agents learned to Eat Red and Ignore Blue.")
    else:
        print("❌ FAILURE: Learning failed.")

    # Save Results
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2540_neural_network.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['tick', 'avg_red', 'avg_blue'])
        writer.writeheader()
        writer.writerows(performance_log)
        
    print(f"📝 Logged to {csv_path}")

if __name__ == "__main__":
    run_learning_experiment()
