"""
Cycle 412: The Living Lab (Persistent Autonomy)
Role: Autopoietic Coordinator
Responsibility: Run indefinitely, self-optimizing and recovering from perturbations.
"""
import asyncio
import websockets
import json
import random
import numpy as np
import time
import copy
import serial
import serial.tools.list_ports
import cv2  # For the Camera Interface

# --- GA Parameters ---
POPULATION_SIZE = 20
GENERATIONS_PER_CYCLE = 50 # Run for a set number of generations, then re-evaluate/check
MUTATION_RATE = 0.1
ELITISM_COUNT = 2

# --- Persistence Parameters ---
PERSISTENCE_THRESHOLD = 0.7 # If fitness drops below 70% of recent peak, re-initialize
FITNESS_HISTORY_LENGTH = 5  # Number of recent best fitnesses to consider for peak

# --- Simulation Constants ---
NUM_EMITTERS = 64
TARGET_POINT = {"x": 0, "y": 0, "z": 50}
TARGET_VELOCITY = {"x": 0.1, "y": 0.1, "z": 0}

# --- Global State ---
CONNECTED_WORKERS = set()
TASK_QUEUE = asyncio.Queue()
RESULTS_BUFFER = {}
CURRENT_GENERATION = 0
POPULATION = []
SERIAL_PORT = None
BEST_FITNESS_HISTORY = [] # To track recent fitness peaks

import sqlite3 # New import
# --- Hardware Interfaces ---

class SerialInterface:
    def __init__(self):
        self.port = None
        self.is_mock = True
        
    def auto_connect(self):
        """Attempt to find and connect to the FPGA controller."""
        ports = list(serial.tools.list_ports.comports())
        print(f"[Serial] Scanning {len(ports)} ports...")
        
        target_port = None
        for p in ports:
            if "USB" in p.description or "ACM" in p.device:
                target_port = p.device
                break
                
        if target_port:
            try:
                self.port = serial.Serial(target_port, 115200, timeout=0.1)
                self.is_mock = False
                print(f"[Serial] Connected to {target_port}")
                self.port.write(b"READY\n")
                return True
            except Exception as e:
                print(f"[Serial] Connection failed: {e}")
        
        print("[Serial] No hardware found. Using Mock Serial.")
        self.is_mock = True
        return False

    def send_phases(self, phases):
        """Send a list of 64 phases (0-2pi) to the hardware."""
        if self.is_mock:
            return
            
        if not self.port or not self.port.is_open:
            return

        try:
            data = bytearray([0xFF])
            for p in phases:
                val = int((p / (2 * np.pi)) * 255) % 256
                data.append(val)
            checksum = sum(data[1:]) % 256
            data.append(checksum)
            self.port.write(data)
        except Exception as e:
            print(f"[Serial] Write Error: {e}")

class CameraInterface:
    # ... (existing CameraInterface code) ...

class KnowledgeGraphInterface:
    def __init__(self, db_path="knowledge_graph.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_x REAL,
                    target_y REAL,
                    target_z REAL,
                    generation INTEGER,
                    best_fitness REAL,
                    best_genome TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_solution(self, target_point, generation, best_fitness, best_genome):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO solutions (target_x, target_y, target_z, generation, best_fitness, best_genome) VALUES (?, ?, ?, ?, ?, ?)",
                (target_point["x"], target_point["y"], target_point["z"], generation, best_fitness, json.dumps(best_genome))
            )
            conn.commit()
        print(f"[KnowledgeGraph] Saved solution for target {target_point} with fitness {best_fitness:.4f}")

    def load_best_solution(self, target_point, tolerance=0.5):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Find solutions near the target point
            cursor.execute(
                """
                SELECT best_genome, best_fitness FROM solutions
                WHERE ABS(target_x - ?) < ? AND ABS(target_y - ?) < ? AND ABS(target_z - ?) < ?
                ORDER BY best_fitness DESC
                LIMIT 1
                """,
                (target_point["x"], tolerance, target_point["y"], tolerance, target_point["z"], tolerance)
            )
            result = cursor.fetchone()
            if result:
                genome = json.loads(result[0])
                fitness = result[1]
                print(f"[KnowledgeGraph] Loaded best solution for target {target_point} with fitness {fitness:.4f}")
                return genome, fitness
            return None, None
            
# Instantiate Global Hardware
HARDWARE = SerialInterface()
EYES = CameraInterface()
MEMORY = KnowledgeGraphInterface() # New global instance

def init_population():
    pop = []
    for _ in range(POPULATION_SIZE):
        genome = [random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)]
        pop.append(genome)
    return pop

async def evaluate_genome_physically(genome):
    HARDWARE.send_phases(genome)
    await asyncio.sleep(0.1) 
    fitness = EYES.get_fitness_score()
    return fitness

async def evaluate_generation_physically(population):
    print(f"[GA] Physically Evaluating Gen {CURRENT_GENERATION}...")
    scored_population = []
    
    for i, genome in enumerate(population):
        fitness = await evaluate_genome_physically(genome)
        scored_population.append((genome, fitness))
        
    return scored_population

def evolve(scored_population):
    scored_population.sort(key=lambda x: x[1], reverse=True)
    best_genome = copy.deepcopy(scored_population[0][0])
    best_fitness = scored_population[0][1]
    print(f"[GA] Gen {CURRENT_GENERATION} Best Physical Fitness: {best_fitness:.4f}")
    
    # Update fitness history
    BEST_FITNESS_HISTORY.append(best_fitness)
    if len(BEST_FITNESS_HISTORY) > FITNESS_HISTORY_LENGTH:
        BEST_FITNESS_HISTORY.pop(0) # Keep history length
    
    # Keep the best solution active while we compute the next generation
    HARDWARE.send_phases(best_genome)
    
    next_gen = []
    for i in range(ELITISM_COUNT):
        next_gen.append(scored_population[i][0])
        
    while len(next_gen) < POPULATION_SIZE:
        parent1 = tournament_select(scored_population)
        parent2 = tournament_select(scored_population)
        child = mutate(crossover(parent1, parent2))
        next_gen.append(child)
        
    return next_gen, best_genome, best_fitness

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
            genome[i] += random.gauss(0, 0.5)
            genome[i] %= (2 * np.pi)
    return genome

async def broadcast_ga_status(generation, best_fitness, best_genome):
    if not CONNECTED_WORKERS:
        return
    status_payload = json.dumps({
        "type": "ga_status",
        "generation": generation,
        "best_fitness": best_fitness,
        "best_genome": best_genome
    })
    for worker in list(CONNECTED_WORKERS):
        try:
            await worker.send(status_payload)
        except:
            pass

async def handler(websocket):
    CONNECTED_WORKERS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CONNECTED_WORKERS.remove(websocket)

async def main():
    global CURRENT_GENERATION, POPULATION, BEST_FITNESS_HISTORY
    
    # Init Hardware
    HARDWARE.auto_connect()
    EYES.auto_connect()
    
    print("Starting Living Lab Coordinator (Cycle 412)...")
    print(f"Hardware: {'REAL' if not HARDWARE.is_mock else 'MOCK'}")
    print(f"Vision:   {'REAL' if not EYES.is_mock else 'MOCK'}")
    
    server = await websockets.serve(handler, "localhost", 8765)
    
    print("[GA] Starting Physical Optimization Loop.")
    
    POPULATION = init_population()
    CURRENT_GENERATION = 0
    BEST_FITNESS_HISTORY = []

    # Try to load a known solution from the knowledge graph
    loaded_genome, loaded_fitness = MEMORY.load_best_solution(TARGET_POINT)
    if loaded_genome and loaded_fitness is not None:
        POPULATION[0] = loaded_genome # Seed the best individual
        BEST_FITNESS_HISTORY.append(loaded_fitness)
        print(f"[KnowledgeGraph] Seeded GA with loaded solution (Fitness: {loaded_fitness:.4f}).")
    
    while True: # Infinite loop for persistent autonomy
        print(f"\n--- Starting Optimization Cycle {CURRENT_GENERATION // GENERATIONS_PER_CYCLE + 1} ---")
        
        for gen in range(GENERATIONS_PER_CYCLE):
            CURRENT_GENERATION += 1 # Increment global generation counter
            
            # --- Environmental Drift ---
            TARGET_POINT["x"] += TARGET_VELOCITY["x"]
            TARGET_POINT["y"] += TARGET_VELOCITY["y"]
            TARGET_POINT["z"] += TARGET_VELOCITY["z"]
            # ---------------------------
            
            scored_pop = await evaluate_generation_physically(POPULATION)
            POPULATION, best_genome, best_fitness = evolve(scored_pop)
            
            await broadcast_ga_status(CURRENT_GENERATION, best_fitness, np.array(best_genome).tolist())
            
            # Save the best solution to the knowledge graph
            MEMORY.save_solution(TARGET_POINT, CURRENT_GENERATION, best_fitness, best_genome)
            
            # Perturbation detection and recovery
            if len(BEST_FITNESS_HISTORY) >= FITNESS_HISTORY_LENGTH:
                recent_peak_fitness = max(BEST_FITNESS_HISTORY)
                if best_fitness < recent_peak_fitness * PERSISTENCE_THRESHOLD:
                    print(f"[PERTURBATION] Fitness dropped (Current: {best_fitness:.4f}, Peak: {recent_peak_fitness:.4f}). Re-initializing GA.")
                    POPULATION = init_population()
                    BEST_FITNESS_HISTORY = [] # Clear history to allow new peak
                    # No need to break, just continue the loop, next iteration will be gen 0 of new pop
            
    print("[GA] Optimization Complete.") # This line won't be reached in persistent mode

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
