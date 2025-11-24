
import sys
import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) # Remove root from path to be safe
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) # Need root to import code.*

from src.fractal.fractal_swarm import FractalSwarm
from src.fractal.agent import FractalAgent

def debug_swarm():
    print("--- DEBUG SWARM ---")
    import inspect
    print(f"FractalAgent Source: {inspect.getfile(FractalAgent)}")
    print(f"FractalAgent Init Signature: {inspect.signature(FractalAgent.__init__)}")
    
    swarm = FractalSwarm()
    # agent = FractalAgent(energy=100.0) # Commented out to allow inspection
    agent = FractalAgent() # Try default init
    agent.state.energy = 100.0 # Manually set
    swarm.agents[agent.agent_id] = agent
    
    print(f"Agent Energy: {agent.state.energy}")
    print("Calling energy_pooling_cycle...")
    swarm.energy_pooling_cycle([agent], sharing_fraction=0.2)
    print(f"Agent Energy after pooling: {agent.state.energy}")

if __name__ == "__main__":
    debug_swarm()
