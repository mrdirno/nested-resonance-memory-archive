"""
Cycle 407: The Hive Mind (Distributed Genetic Algorithm)
Role: Evolutionary Coordinator
Responsibility: Evolve a population of Acoustic Trap solutions using the Swarm for fitness evaluation.
"""
import asyncio
import websockets
import json
import random
import numpy as np
import time

# --- GA Parameters ---
POPULATION_SIZE = 20
GENERATIONS = 100
MUTATION_RATE = 0.1
ELITISM_COUNT = 2

# --- Simulation Constants ---
NUM_EMITTERS = 64  # Example array size
TARGET_POINT = {"x": 0, "y": 0, "z": 50} # Levitation target (mm)

# --- Global State ---
CONNECTED_WORKERS = set()
TASK_QUEUE = asyncio.Queue()
RESULTS_BUFFER = {} # task_id -> fitness
CURRENT_GENERATION = 0
POPULATION = [] # List of genomes (each genome is a list of phases)

def init_population():
    """Create initial random population."""
    pop = []
    for _ in range(POPULATION_SIZE):
        # Genome: List of phases [0, 2pi]
        genome = [random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)]
        pop.append(genome)
    return pop

async def evaluate_generation(population):
    """
    Distribute the entire population to workers for evaluation.
    Returns a list of (genome, fitness) tuples.
    """
    global RESULTS_BUFFER
    RESULTS_BUFFER = {}
    
    print(f"[GA] Evaluating Generation {CURRENT_GENERATION} ({len(population)} individuals)...")
    
    # 1. Queue all tasks
    for i, genome in enumerate(population):
        task_id = f"gen{CURRENT_GENERATION}_ind{i}"
        
        # Construct Emitters payload (simplified geometry for now)
        # In reality, we'd map these phases to actual transducer positions.
        # For this test, we just send the phases and let the worker assume a geometry 
        # OR we send the full geometry. Let's send a mock geometry.
        emitters_payload = []
        for idx, phase in enumerate(genome):
            # Mock 8x8 grid
            row = idx // 8
            col = idx % 8
            emitters_payload.append({
                "x": (col - 3.5) * 10, 
                "y": (row - 3.5) * 10, 
                "z": 0, 
                "phase": phase
            })
            
        task = {
            "id": task_id,
            "emitters": emitters_payload,
            "targets": [TARGET_POINT]
        }
        await TASK_QUEUE.put(task)
        
    # 2. Wait for results
    # We need to wait until we have results for ALL tasks (or timeout)
    start_time = time.time()
    while len(RESULTS_BUFFER) < len(population):
        if time.time() - start_time > 30: # Timeout
            print("[GA] Timeout waiting for generation results.")
            break
        await asyncio.sleep(0.1)
        
    # 3. Compile Fitness
    scored_population = []
    for i, genome in enumerate(population):
        task_id = f"gen{CURRENT_GENERATION}_ind{i}"
        fitness = RESULTS_BUFFER.get(task_id, -1000.0) # Default bad fitness
        scored_population.append((genome, fitness))
        
    return scored_population

def evolve(scored_population):
    """
    Create next generation via Selection, Crossover, Mutation.
    """
    # Sort by fitness (Descending)
    scored_population.sort(key=lambda x: x[1], reverse=True)
    
    best_genome, best_fitness = scored_population[0]
    print(f"[GA] Gen {CURRENT_GENERATION} Best Fitness: {best_fitness:.4f}")
    
    next_gen = []
    
    # Elitism
    for i in range(ELITISM_COUNT):
        next_gen.append(scored_population[i][0])
        
    # Breeding
    while len(next_gen) < POPULATION_SIZE:
        # Tournament Selection
        parent1 = tournament_select(scored_population)
        parent2 = tournament_select(scored_population)
        
        # Crossover
        child = crossover(parent1, parent2)
        
        # Mutation
        child = mutate(child)
        
        next_gen.append(child)
        
    return next_gen

def tournament_select(scored_pop, k=3):
    candidates = random.sample(scored_pop, k)
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def crossover(p1, p2):
    point = random.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:]

def mutate(genome):
    for i in range(len(genome)):
        if random.random() < MUTATION_RATE:
            genome[i] += random.gauss(0, 0.5) # Perturb phase
            genome[i] %= (2 * np.pi)
    return genome

# --- WebSocket Infrastructure ---

async def distributor():
    while True:
        if not TASK_QUEUE.empty() and CONNECTED_WORKERS:
            task = await TASK_QUEUE.get()
            # Simple Round Robin or Random
            worker = random.choice(list(CONNECTED_WORKERS))
            
            payload = json.dumps({
                "type": "compute_task",
                "task_id": task["id"],
                "emitters": task["emitters"],
                "targets": task["targets"]
            })
            
            try:
                await worker.send(payload)
                # print(f"[Distributor] Sent {task['id']}")
            except:
                print(f"[Distributor] Worker failed. Re-queueing {task['id']}")
                await TASK_QUEUE.put(task)
        await asyncio.sleep(0.01)

async def handler(websocket):
    CONNECTED_WORKERS.add(websocket)
    print(f"[Server] Worker Connected. Total: {len(CONNECTED_WORKERS)}")
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "result":
                # Calculate Fitness from Result
                # Fitness = Potential at target (Mock: we want to MINIMIZE potential for a trap, 
                # but let's say we want to MAXIMIZE it for a focus for simplicity, or use -Potential)
                # The worker returns 'u' (potential).
                
                # Let's say we want a FOCUS (High Intensity)
                results = data["results"]
                # Sum of intensities (mock 'u' is potential)
                total_u = sum(r.get("u", 0) for r in results)
                
                # Store fitness
                RESULTS_BUFFER[data["task_id"]] = total_u
                
            elif data["type"] == "ready":
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_WORKERS.remove(websocket)
        print(f"[Server] Worker Disconnected. Total: {len(CONNECTED_WORKERS)}")

async def main():
    global CURRENT_GENERATION, POPULATION
    
    print("Starting Hive Mind Coordinator (Cycle 407)...")
    server = await websockets.serve(handler, "localhost", 8765)
    print("WebSocket Server listening on ws://localhost:8765")
    
    asyncio.create_task(distributor())
    
    # Wait for at least one worker
    print("[GA] Waiting for workers...")
    while not CONNECTED_WORKERS:
        await asyncio.sleep(1)
    print("[GA] Worker detected. Starting Evolution.")
    
    POPULATION = init_population()
    
    for gen in range(GENERATIONS):
        CURRENT_GENERATION = gen
        scored_pop = await evaluate_generation(POPULATION)
        POPULATION = evolve(scored_pop)
        await asyncio.sleep(0.1)
        
    print("[GA] Evolution Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
