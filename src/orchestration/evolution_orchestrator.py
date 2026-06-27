import os
import sys
import json
import asyncio
from pathlib import Path
from google.antigravity import Agent, LocalAgentConfig, types

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_experiment_coordinator import DynamicExperimentCoordinator
from campaign_data_validator import CampaignDataValidator

def write_simulation_script(generation: int, code: str) -> str:
    """Writes the simulation script for a specific generation.
    
    Args:
        generation: The generation number to write code for.
        code: The complete python code for the simulation.
    """
    os.makedirs("experiments/evolution", exist_ok=True)
    filename = f"experiments/evolution/generation_{generation}.py"
    with open(filename, 'w') as f:
        f.write(code.strip())
    return f"Simulation successfully written to {filename}"

def run_simulation_with_coordinator(generation: int) -> str:
    """Executes the simulation script for a specific generation and uses the coordinator.
    
    Args:
        generation: The generation number to execute.
    """
    coordinator = DynamicExperimentCoordinator()
    exp = coordinator.add_experiment(
        name=f"Generation {generation}",
        script_name=f"generation_{generation}.py",
        results_name=f"gen_{generation}_metrics.json"
    )
    
    success = coordinator.launch_experiment(exp)
    if not success:
        return "Failed to launch experiment."
        
    status = coordinator.wait_for_completion(exp, timeout=120)
    
    if status == 'completed':
        # Get fitness score
        validator = CampaignDataValidator(results_dir=coordinator.results_dir)
        fitness = validator.get_fitness_score(generation)
        
        with open(exp.results_path, 'r') as f:
            metrics = json.load(f)
            
        return f"Execution completed. Fitness Score: {fitness:.2f}\nMetrics: {json.dumps(metrics, indent=2)}"
    else:
        return f"Experiment ended with status: {status}"

async def run_orchestration(start_generation: int, max_generations: int):
    # Initialize the Director agent configuration
    config = LocalAgentConfig(
        tools=[write_simulation_script, run_simulation_with_coordinator],
        capabilities=types.CapabilitiesConfig(enable_subagents=True),
        system_instructions=(
            "You are the Director of the Evolutionary Research Framework.\n"
            "Your task is to orchestrate a continuous research cycle.\n"
            "For each generation, you MUST use a subagent to design the new Python simulation script.\n"
            "The subagent should write a Python script simulating distributed workers optimizing resource constraints. "
            "It must save metrics to `data/results/gen_<num>_metrics.json`.\n"
            "Ensure the simulation saves 'worker_count', 'efficiency', and 'resource_utilization' into the JSON file.\n"
            "After the subagent returns the code, use the `write_simulation_script` tool to save it, "
            "then use `run_simulation_with_coordinator` to execute it.\n"
            "The coordinator will return a Fitness Score. Analyze this score.\n"
            "Instruct your subagent on how to improve the script for the next generation based on the fitness score.\n"
            "Continue this loop until the max generation is reached, then stop."
        )
    )
    
    async with Agent(config) as agent:
        print(f"\n🚀 Starting Closed-Loop Orchestration from generation {start_generation} to {max_generations}...\n")
        
        prompt = (
            f"Please begin the orchestration starting at generation {start_generation}. "
            f"Use your subagent to draft the first simulation script, then write and run it. "
            "Analyze the fitness results and iterate until generation {max_generations} is completed."
        )
        
        response = await agent.chat(prompt)
        async for chunk in response:
            print(chunk, end="", flush=True)
            
        print("\n\nOrchestration cycle complete.")

if __name__ == "__main__":
    # Ensure standard directories exist
    os.makedirs("experiments/evolution", exist_ok=True)
    os.makedirs("data/results", exist_ok=True)
    
    # Check for API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not set. Cannot run Antigravity SDK agents.")
        sys.exit(1)
        
    asyncio.run(run_orchestration(1, 3))
