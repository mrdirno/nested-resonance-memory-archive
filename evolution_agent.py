import os
import sys
import json
import subprocess
import asyncio
from google.antigravity import Agent, LocalAgentConfig, types

def write_experiment_code(generation: int, code: str) -> str:
    """Writes the experiment code for a specific generation.
    
    Args:
        generation: The generation number to write code for.
        code: The complete python code for the experiment.
    """
    os.makedirs("experiments", exist_ok=True)
    filename = f"experiments/generation_{generation}.py"
    with open(filename, 'w') as f:
        f.write(code.strip())
    return f"Code successfully written to {filename}"

def execute_experiment(generation: int) -> str:
    """Executes the experiment script for a specific generation and returns the results.
    
    Args:
        generation: The generation number to execute.
    """
    filename = f"experiments/generation_{generation}.py"
    if not os.path.exists(filename):
        return f"Error: Script {filename} does not exist."
    
    try:
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True,
            text=True,
            check=True
        )
        
        result_path = os.path.join("data", "results", f"gen_{generation}_fitness.json")
        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                fitness_data = json.load(f)
            return f"Execution successful. Stdout:\n{result.stdout}\n\nFitness JSON:\n{json.dumps(fitness_data, indent=2)}"
        else:
            return f"Execution successful, but fitness JSON not found at {result_path}.\nStdout:\n{result.stdout}"
            
    except subprocess.CalledProcessError as e:
        return f"Execution failed with return code {e.returncode}.\nStdout:\n{e.stdout}\nStderr:\n{e.stderr}"

def ensure_scaffold():
    """Ensure the base structure is created before running."""
    import bootstrap_bcp
    bootstrap_bcp.scaffold_structure()
    print("Scaffolding complete.")

async def run_evolution_cycle(start_generation: int, max_generations: int):
    ensure_scaffold()
    
    # Initialize agent configuration
    config = LocalAgentConfig(
        tools=[write_experiment_code, execute_experiment],
        capabilities=types.CapabilitiesConfig(enable_subagents=True),
        system_instructions=(
            "You are the BCP Evolutionary Guardian. Your task is to perform evolutionary cycles for the Duality-Zero framework.\n"
            "For each generation, you MUST use a subagent to design the new experiment code.\n"
            "The experiment code must simulate BCP Agents interacting, similar to the original bootstrap_bcp.py design, "
            "but you should encourage the subagent to introduce novel mutations, physics, or constraints to break stagnation "
            "and achieve higher complexity and survival rates.\n"
            "After the subagent returns the code, you will use the `write_experiment_code` tool to save it, "
            "then use `execute_experiment` to run it and read the fitness.\n"
            "You must continue this loop until the max generation is reached.\n"
            "When the max generation is reached, summarize the findings and stop."
        )
    )
    
    async with Agent(config) as agent:
        print(f"\n🚀 Starting evolutionary cycle from generation {start_generation} to {max_generations}...\n")
        
        prompt = (
            f"Please begin the evolutionary cycle starting at generation {start_generation}. "
            f"Use a subagent to write the first experimental script `experiments/generation_{start_generation}.py`. "
            "You can refer to the original `bootstrap_bcp.py` for inspiration on the experiment structure. "
            "The experiment MUST output fitness data to `data/results/gen_<num>_fitness.json` with keys like "
            "'generation', 'budget_avg', 'gain_base', 'cost_base', 'complexity', 'value', 'survival_rate', and 'survived'. "
            "Once written, execute it and analyze the results. Then proceed to the next generation until generation {max_generations} is done."
        )
        
        response = await agent.chat(prompt)
        async for chunk in response:
            print(chunk, end="", flush=True)
            
        print("\n\nEvolutionary cycle complete.")

if __name__ == "__main__":
    asyncio.run(run_evolution_cycle(1000, 1002))  # Run a short cycle of 3 generations for testing
