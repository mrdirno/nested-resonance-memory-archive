
import sys
import os
import csv
import time
import random
import math
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_urban_migration_experiment():
    print("🌆 CYCLE 2538: THE CITIZEN - URBAN MIGRATION TEST")
    
    # 1. Initialize Ecosystem
    # Larger map to distinguish Urban vs Rural
    width = 100
    height = 100
    env = Ecosystem(capacity=200, width=width, height=height)
    
    # 2. Construct THE CITY (Pre-built infrastructure)
    # City Center at (50, 50)
    city_x, city_y = 50, 50
    city_radius = 10
    
    print("🏗️ Constructing The City...")
    farms_built = 0
    for _ in range(20):
        # Cluster farms around the center
        fx = city_x + random.randint(-city_radius, city_radius)
        fy = city_y + random.randint(-city_radius, city_radius)
        
        # Add Farm Structure
        env.add_structure({'type': 'FARM', 'x': fx, 'y': fy, 'hp': 50, 'yield': 10})
        farms_built += 1
        
    print(f"✅ City Established: {farms_built} Farms at ({city_x}, {city_y}) +/- {city_radius}")
    
    # 3. Populate the Hinterlands (Rural Agents)
    # Agents start far away from the city
    print("👨‍🌾 Populating the Hinterlands...")
    population_size = 50
    for i in range(population_size):
        agent = DigitalLifeform(name=f"Citizen-{i}")
        
        # Spawn in rural areas (edges of map)
        if random.random() < 0.5:
            agent.x = random.randint(0, 20) if random.random() < 0.5 else random.randint(80, 100)
            agent.y = random.randint(0, 100)
        else:
            agent.x = random.randint(0, 100)
            agent.y = random.randint(0, 20) if random.random() < 0.5 else random.randint(80, 100)
            
        agent.energy = 100 # Moderate energy
        
        # Ensure they can move and sense
        # Gene 10 = Mobility
        agent.genome[10] = 0.8 
        
        env.add_agent(agent)
        
    # 4. Run Simulation & Track Migration
    duration = 200
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2538_urban_migration.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "avg_dist_to_city", "urban_pop", "rural_pop", "avg_energy_urban", "avg_energy_rural"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            env.update()
            
            # Analysis
            urban_pop = 0
            rural_pop = 0
            total_dist = 0
            urban_energy = 0
            rural_energy = 0
            
            agent_count = len(env.agents)
            if agent_count == 0:
                print("💀 Extinction.")
                break
                
            for agent in env.agents:
                dist = math.sqrt((agent.x - city_x)**2 + (agent.y - city_y)**2)
                total_dist += dist
                
                if dist <= city_radius + 5: # Urban + Suburbs
                    urban_pop += 1
                    urban_energy += agent.energy
                else:
                    rural_pop += 1
                    rural_energy += agent.energy
            
            avg_dist = total_dist / agent_count
            avg_e_urban = urban_energy / urban_pop if urban_pop > 0 else 0
            avg_e_rural = rural_energy / rural_pop if rural_pop > 0 else 0
            
            writer.writerow([tick, f"{avg_dist:.1f}", urban_pop, rural_pop, f"{avg_e_urban:.1f}", f"{avg_e_rural:.1f}"])
            
            if tick % 20 == 0:
                print(f"   Tick {tick}: Dist={avg_dist:.1f}, Urban={urban_pop} (E={avg_e_urban:.0f}), Rural={rural_pop} (E={avg_e_rural:.0f})")
                
            # Success Condition: Majority Urban
            if urban_pop > rural_pop * 2:
                print("🏙️ SUCCESS! Urbanization achieved.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_urban_migration_experiment()
