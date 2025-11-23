"""
Cycle 415: The Learning Loop (Meta-Adaptation)
Role: Meta-Cognitive Coordinator
Responsibility: Adapt learning strategy based on performance history.
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
import cv2
import sqlite3

# --- GA Parameters (Initial) ---
POPULATION_SIZE = 20
GENERATIONS_PER_CYCLE = 50
MUTATION_RATE = 0.1
ELITISM_COUNT = 2

# --- Persistence Parameters ---
PERSISTENCE_THRESHOLD = 0.7
FITNESS_HISTORY_LENGTH = 5

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
BEST_FITNESS_HISTORY = []

# --- Hardware Interfaces ---

class SerialInterface:
    def __init__(self):
        self.port = None
        self.is_mock = True
        
    def auto_connect(self):
        ports = list(serial.tools.list_ports.comports())
        target_port = None
        for p in ports:
            if "USB" in p.description or "ACM" in p.device:
                target_port = p.device
                break
        if target_port:
            try:
                self.port = serial.Serial(target_port, 115200, timeout=0.1)
                self.is_mock = False
                self.port.write(b"READY\n")
                return True
            except:
                pass
        self.is_mock = True
        return False

    def send_phases(self, phases):
        if self.is_mock or not self.port or not self.port.is_open:
            return
        try:
            data = bytearray([0xFF])
            for p in phases:
                val = int((p / (2 * np.pi)) * 255) % 256
                data.append(val)
            checksum = sum(data[1:]) % 256
            data.append(checksum)
            self.port.write(data)
        except:
            pass

class CameraInterface:
    def __init__(self):
        self.cap = None
        self.is_mock = True
        self.current_mock_fitness = 5.0
        self.perturbation_timer = 0
        self.perturbation_interval = random.randint(30, 80)
        
    def auto_connect(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.is_mock = False
                return True
        except:
            pass
        self.is_mock = True
        return False
        
    def get_fitness_score(self):
        if self.is_mock:
            if CURRENT_GENERATION < GENERATIONS_PER_CYCLE / 2:
                self.current_mock_fitness += random.uniform(0.1, 0.5)
            else:
                self.perturbation_timer += 1
                if self.perturbation_timer > self.perturbation_interval:
                    self.current_mock_fitness *= random.uniform(0.5, 0.9)
                    self.perturbation_timer = 0
                    self.perturbation_interval = random.randint(30, 80)
            return max(0.1, self.current_mock_fitness + random.uniform(-0.5, 0.5))
            
        if not self.cap or not self.cap.isOpened():
            return 0.0
        ret, frame = self.cap.read()
        if not ret:
            return 0.0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0.0
        largest_contour = max(contours, key=cv2.contourArea)
        return cv2.contourArea(largest_contour)

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

    def load_best_solution(self, target_point, tolerance=0.5):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
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
                return json.loads(result[0]), result[1]
            return None, None

class MetaController:
    def __init__(self):
        self.stagnation_counter = 0
        self.current_mutation_rate = MUTATION_RATE
        self.fitness_history = []
        
    def adapt(self, current_fitness):
        self.fitness_history.append(current_fitness)
        if len(self.fitness_history) > 5:
            self.fitness_history.pop(0)
            
            # Check for stagnation (last 5 fitness values are very close)
            if max(self.fitness_history) - min(self.fitness_history) < 0.01:
                self.stagnation_counter += 1
            else:
                self.stagnation_counter = 0
                
        # Adapt Strategy
        if self.stagnation_counter > 3:
            # Increase exploration
            self.current_mutation_rate = min(0.5, self.current_mutation_rate * 1.5)
            print(f"[META] Stagnation detected. Boosting Mutation Rate to {self.current_mutation_rate:.3f}")
            self.stagnation_counter = 0 # Reset to give it time to work
        elif len(self.fitness_history) > 2 and self.fitness_history[-1] > self.fitness_history[-2]:
            # Performance improving, gradually cool down
            self.current_mutation_rate = max(0.01, self.current_mutation_rate * 0.95)
            
        return self.current_mutation_rate

# Instantiate Global Objects
HARDWARE = SerialInterface()
EYES = CameraInterface()
MEMORY = KnowledgeGraphInterface()
META = MetaController()

def init_population():
    pop = []
    for _ in range(POPULATION_SIZE):
        genome = [random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)]
        pop.append(genome)
    return pop

async def evaluate_genome_physically(genome):
    HARDWARE.send_phases(genome)
    await asyncio.sleep(0.05) # Faster cycle
    fitness = EYES.get_fitness_score()
    return fitness

async def evaluate_generation_physically(population):
    scored_population = []
    for i, genome in enumerate(population):
        fitness = await evaluate_genome_physically(genome)
        scored_population.append((genome, fitness))
    return scored_population

def evolve(scored_population, mutation_rate):
    scored_population.sort(key=lambda x: x[1], reverse=True)
    best_genome = copy.deepcopy(scored_population[0][0])
    best_fitness = scored_population[0][1]
    
    HARDWARE.send_phases(best_genome)
    
    next_gen = []
    for i in range(ELITISM_COUNT):
        next_gen.append(scored_population[i][0])
        
    while len(next_gen) < POPULATION_SIZE:
        parent1 = tournament_select(scored_population)
        parent2 = tournament_select(scored_population)
        child = mutate(crossover(parent1, parent2), mutation_rate)
        next_gen.append(child)
        
    return next_gen, best_genome, best_fitness

def tournament_select(scored_pop, k=3):
    candidates = random.sample(scored_pop, k)
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def crossover(p1, p2):
    point = random.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:]

def mutate(genome, rate):
    for i in range(len(genome)):
        if random.random() < rate:
            genome[i] += random.gauss(0, 0.5)
            genome[i] %= (2 * np.pi)
    return genome

async def broadcast_ga_status(generation, best_fitness, best_genome, mutation_rate):
    if not CONNECTED_WORKERS:
        return
    status_payload = json.dumps({
        "type": "ga_status",
        "generation": generation,
        "best_fitness": best_fitness,
        "best_genome": best_genome,
        "mutation_rate": mutation_rate # Added metric
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
    
    HARDWARE.auto_connect()
    EYES.auto_connect()
    
    print("Starting Meta-Cognitive Coordinator (Cycle 415)...")
    server = await websockets.serve(handler, "localhost", 8765)
    
    POPULATION = init_population()
    CURRENT_GENERATION = 0
    BEST_FITNESS_HISTORY = []

    loaded_genome, loaded_fitness = MEMORY.load_best_solution(TARGET_POINT)
    if loaded_genome and loaded_fitness is not None:
        POPULATION[0] = loaded_genome
        BEST_FITNESS_HISTORY.append(loaded_fitness)
        print(f"[KnowledgeGraph] Seeded GA. Fitness: {loaded_fitness:.4f}")
    
    while True:
        print(f"\n--- Cycle {CURRENT_GENERATION // GENERATIONS_PER_CYCLE + 1} ---")
        
        for gen in range(GENERATIONS_PER_CYCLE):
            CURRENT_GENERATION += 1
            
            TARGET_POINT["x"] += TARGET_VELOCITY["x"]
            TARGET_POINT["y"] += TARGET_VELOCITY["y"]
            TARGET_POINT["z"] += TARGET_VELOCITY["z"]
            
            scored_pop = await evaluate_generation_physically(POPULATION)
            
            # Meta-Adaptation
            best_fitness_in_gen = max(p[1] for p in scored_pop)
            current_mr = META.adapt(best_fitness_in_gen)
            
            POPULATION, best_genome, best_fitness = evolve(scored_pop, current_mr)
            
            await broadcast_ga_status(CURRENT_GENERATION, best_fitness, np.array(best_genome).tolist(), current_mr)
            
            MEMORY.save_solution(TARGET_POINT, CURRENT_GENERATION, best_fitness, best_genome)
            
            # Perturbation detection
            BEST_FITNESS_HISTORY.append(best_fitness)
            if len(BEST_FITNESS_HISTORY) > FITNESS_HISTORY_LENGTH:
                BEST_FITNESS_HISTORY.pop(0)
                recent_peak = max(BEST_FITNESS_HISTORY)
                if best_fitness < recent_peak * PERSISTENCE_THRESHOLD:
                    print(f"[PERTURBATION] Fitness dropped. Resetting strategy.")
                    # Instead of full reset, maybe just boost mutation?
                    # For now, standard reset but keep best
                    POPULATION = init_population()
                    POPULATION[0] = best_genome # Keep memory
                    META.current_mutation_rate = 0.5 # Panic mode (High Exploration)
            
    print("Stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")