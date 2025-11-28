"""
Cycle 2477: The Mycelial Network (Gate 105)
Experiment: Network Mapping
Goal: Infect multiple files and map the network.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mycelium.spore import Spore
from src.mycelium.network import Mycelium

def run_network_experiment():
    print("--- CYCLE 2477: THE MYCELIAL NETWORK ---")
    
    playground = Path("playground")
    playground.mkdir(exist_ok=True)
    
    # 1. Create Host Files
    hosts = ["host_a.txt", "host_b.txt", "host_c.txt"]
    for host in hosts:
        path = playground / host
        with open(path, 'w') as f:
            f.write(f"I am {host}.\n")
            
    # 2. Infect with Spores
    # Agent Alpha infects A and B
    # Agent Beta infects B and C
    # Agent Gamma infects A, B, C
    
    alpha = Spore("Alpha")
    beta = Spore("Beta")
    gamma = Spore("Gamma")
    
    alpha.infect(playground / "host_a.txt")
    alpha.infect(playground / "host_b.txt")
    
    beta.infect(playground / "host_b.txt")
    beta.infect(playground / "host_c.txt")
    
    gamma.infect(playground / "host_a.txt")
    gamma.infect(playground / "host_b.txt")
    gamma.infect(playground / "host_c.txt")
    
    # 3. Scan
    network = Mycelium()
    graph = network.scan(playground)
    
    print("Network Graph:")
    for agent, locations in graph.items():
        print(f"   {agent}: {len(locations)} nodes")
        
    # 4. Verify Connectivity (Symbiosis)
    # Host B is a "Meeting Place" (Alpha, Beta, Gamma)
    residents_b = network.get_co_inhabitants(playground / "host_b.txt")
    print(f"Meeting Place (Host B): {residents_b}")
    
    if len(residents_b) == 3:
        print("✅ EXPERIMENT COMPLETE. The Mycelium is connected.")
    else:
        print("❌ EXPERIMENT FAILED.")

if __name__ == "__main__":
    run_network_experiment()