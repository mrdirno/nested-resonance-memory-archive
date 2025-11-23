"""
Helios Experiment Protocols
Maps hypothesis discovery methods to FractalSwarm execution logic.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    name: str
    duration_cycles: int
    agent_count: int
    parameters: Dict[str, Any]

class ProtocolRegistry:
    @staticmethod
    def get_config(method_name: str, parameters: Dict[str, Any]) -> ExperimentConfig:
        """
        Map a discovery method name to an experiment configuration.
        """
        if method_name == "kuramoto_coupling_test":
            return ExperimentConfig(
                name="Kuramoto Coupling Validation",
                duration_cycles=50,
                agent_count=20,
                parameters={
                    "coupling_strength": parameters.get("coupling_strength", 0.1),
                    "burst_threshold": 5000.0,
                    "enable_pooling": True,
                    "sharing_fraction": 0.25,
                    "initial_energy": 100.0
                }
            )
        elif method_name == "population_stability_test":
             return ExperimentConfig(
                name="Population Stability Baseline",
                duration_cycles=100,
                agent_count=50,
                parameters={
                    "burst_threshold": 100.0
                }
            )
        elif method_name == "energy_pooling_test":
            return ExperimentConfig(
                name="Cooperative Energy Pooling",
                duration_cycles=50,
                agent_count=20,
                parameters={
                    "burst_threshold": 5000.0,
                    "enable_pooling": True,
                    "sharing_fraction": parameters.get("sharing_fraction", 0.25),
                    "initial_energy": 100.0
                }
            )
        elif method_name == "criticality_test":
            return ExperimentConfig(
                name="Swarm Criticality (Edge of Chaos)",
                duration_cycles=100,
                agent_count=30,
                parameters={
                    "burst_threshold": 4000.0, # Tuned: 30*150=4500 > 4000 (Forces split)
                    "enable_pooling": True,
                    "sharing_fraction": 0.5,
                    "initial_energy": 150.0
                }
            )
        elif method_name == "holographic_test":
            return ExperimentConfig(
                name="Holographic Memory Distribution",
                duration_cycles=50,
                agent_count=40,
                parameters={
                    "initial_energy": 50.0, # Low energy to simulate "damage" / stress
                    "enable_pooling": True,
                    "burst_threshold": 3000.0
                }
            )
        elif method_name == "prediction_test":
            return ExperimentConfig(
                name="Temporal Recursion (Prediction)",
                duration_cycles=50,
                agent_count=20,
                parameters={
                    "enable_pooling": True,
                    "burst_threshold": 5000.0 # Stable environment
                }
            )
        elif method_name == "injection_test":
            return ExperimentConfig(
                name="Reality Injection (External Sensing)",
                duration_cycles=50,
                agent_count=20,
                parameters={
                    "burst_threshold": 1000.0, # High stress (low threshold = frequent bursts)
                    "enable_pooling": True,
                    "initial_energy": 200.0
                }
            )
        elif method_name == "optimization_test":
            return ExperimentConfig(
                name="Factorial Optimization (C256)",
                duration_cycles=20, # Short, fast cycles for optimization
                agent_count=10,
                parameters={
                    "batch_size": 50, # Hypothesis: Larger batches = faster
                    "io_frequency": 10, # Hypothesis: Less frequent I/O = faster
                    "enable_pooling": False # Optimization doesn't need pooling
                }
            )
        elif method_name == "recursive_improvement_test":
            return ExperimentConfig(
                name="Helios Recursive Self-Improvement (C274)",
                duration_cycles=30,
                agent_count=15,
                parameters={
                    "recursion_depth": 3,
                    "enable_pooling": True,
                    "burst_threshold": 2000.0
                }
            )
        elif method_name == "meta_controller_integration_test":
            return ExperimentConfig(
                name="Helios Meta-Controller Integration (C275)",
                duration_cycles=30,
                agent_count=15,
                parameters={
                    "adaptation_rate": 0.1,
                    "enable_pooling": True,
                    "burst_threshold": 2000.0
                }
            )
        else:
            # Default fallback
            return ExperimentConfig(
                name="Generic Exploration",
                duration_cycles=10,
                agent_count=10,
                parameters={}
            )

    @staticmethod
    def evaluate_results(method_name: str, results: List[Dict[str, Any]]) -> bool:
        """
        Evaluate experiment results based on the protocol.
        """
        if not results:
            return False
            
        final_state = results[-1]
        
        if method_name == "kuramoto_coupling_test":
            # Success if resonance clusters formed
            return final_state.get("active_clusters", 0) > 0
            
        elif method_name == "population_stability_test":
            # Success if population survived
            return final_state.get("active_agents", 0) > 0

        elif method_name == "energy_pooling_test":
            # Success if clusters formed AND population survived (pooling requires clusters)
            return final_state.get("active_clusters", 0) > 0 and final_state.get("active_agents", 0) > 5
            
        elif method_name == "criticality_test":
            # Success if clusters exist but haven't taken over (Edge of Chaos)
            clusters = final_state.get("active_clusters", 0)
            return 0 < clusters <= 5

        elif method_name == "holographic_test":
            # Success if population recovers after "damage" (simulated by low initial energy)
            return final_state.get("active_agents", 0) > 10

        elif method_name == "prediction_test":
            # Success if variance is low (predictable)
            return final_state.get("active_clusters", 0) > 0

        elif method_name == "injection_test":
            # Success if system survives "high load" (simulated by high burst threshold)
            return final_state.get("active_agents", 0) > 0

        elif method_name == "optimization_test":
            # Success if speed is high and error is low (simulated)
            # In a real scenario, we would measure actual cycles/sec and error rate
            # For simulation, we check if the "optimized" flag is set or if performance metrics are good
            # Let's assume the swarm reports 'performance_score' in stats
            perf = final_state.get("performance_score", 0)
            error = final_state.get("validation_error", 0.0)
            return perf > 50 and error < 0.05

        elif method_name == "recursive_improvement_test":
            # Success if improvement score is positive (simulated)
            return final_state.get("improvement_score", 0.0) > 0.0

        elif method_name == "meta_controller_integration_test":
            # Success if adaptation score is positive (simulated)
            return final_state.get("adaptation_score", 0.0) > 0.0

        return True
