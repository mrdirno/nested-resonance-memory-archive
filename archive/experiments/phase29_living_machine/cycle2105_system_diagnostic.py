import sys
import os
import numpy as np
import traceback

# Add project root to path
sys.path.append(os.getcwd())

# Import Modules to Test
from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine
from src.fractal.evolved_agents import OptimizerAgent, calculate_fitness
from src.experiments.cycle2104_robust_and_gate import run_logic_test

def test_physics_core():
    print("[TEST] Physics Core (Fractal/Agent)... ", end="")
    try:
        agent = FractalAgent(agent_id="test_agent", energy=1.0, phase=0.0, position=np.array([0.0, 0.0, 0.0]))
        agent.update_energy(0.1)
        agent.move(np.array([1.0, 0.0, 0.0]))
        assert agent.state.energy == 1.1
        assert agent.state.position[0] == 1.0
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {repr(e)}")
        traceback.print_exc()
        return False

def test_composition_engine():
    print("[TEST] Composition Engine... ", end="")
    try:
        engine = CompositionEngine(resonance_threshold=0.1)
        a1 = FractalAgent(agent_id="a1", energy=1.0, phase=0.0, position=np.array([0.0, 0.0, 0.0]))
        a2 = FractalAgent(agent_id="a2", energy=1.0, phase=0.0, position=np.array([0.5, 0.0, 0.0])) # Close
        
        # Debug checks
        res = a1.calculate_resonance(a2)
        # print(f"DEBUG: Resonance {res}")
        
        clusters = engine.compose_all([a1, a2])
        # print(f"DEBUG: Clusters {clusters}")
        
        assert len(clusters) == 1, f"Expected 1 cluster, got {len(clusters)}"
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {repr(e)}")
        # traceback.print_exc()
        return False

def test_optimization_logic():
    print("[TEST] Optimization Logic... ", end="")
    try:
        center = np.array([0.0, 0.0, 0.0])
        blocks = [np.array([10.0, 0.0, 0.0])]
        fitness = calculate_fitness(blocks, 10.0, center)
        assert fitness == 0.0 # Perfect match
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {repr(e)}")
        traceback.print_exc()
        return False

def test_cognitive_logic():
    print("[TEST] Cognitive Logic (AND Gate)... ", end="")
    try:
        # Quick check of the logic gate function
        result = run_logic_test(np.pi, np.pi, "Bang-Bang") # Should be 1.0
        assert result == 1.0
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL: {repr(e)}")
        traceback.print_exc()
        return False

def run_diagnostic():
    print("MOG ONLINE: Cycle 2105 - System Diagnostic (Verbose)\n")
    
    results = [
        test_physics_core(),
        test_composition_engine(),
        test_optimization_logic(),
        test_cognitive_logic()
    ]
    
    if all(results):
        print("\nSYSTEM STATUS: 🟢 NOMINAL")
        print("All subsystems operational. Ready for Phase 29.")
    else:
        print("\nSYSTEM STATUS: 🔴 DEGRADED")
        print("Critical failures detected.")

if __name__ == "__main__":
    run_diagnostic()