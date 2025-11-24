"""
Cycle 419: The Curator (Aesthetic Selection)
Role: Aesthetic Curator & Optimizer
Responsibility: Evaluate generated shapes for symmetry and complexity, selecting the most 'interesting' ones for realization.
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
import math

# --- GA Parameters ---
POPULATION_SIZE = 20
GENERATIONS_PER_SHAPE = 30
MUTATION_RATE = 0.1
ELITISM_COUNT = 2

# --- Simulation Constants ---
NUM_EMITTERS = 64
MIN_COORD = -20
MAX_COORD = 20

# --- Global State ---
CONNECTED_WORKERS = set()
CURRENT_GENERATION = 0
POPULATION = []
SERIAL_PORT = None
BEST_FITNESS_HISTORY = []

# --- Hardware Interfaces (Mock/Real) ---

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
        
    def get_fitness_score(self, target_point):
        if self.is_mock:
            dist = math.sqrt(target_point['x']**2 + target_point['y']**2 + target_point['z']**2)
            difficulty = 1.0 + (dist / 50.0)
            base_fitness = 10.0 / difficulty
            return max(0.1, base_fitness + random.uniform(-0.5, 0.5))
            
        if not self.cap or not self.cap.isOpened():
            return 0.0
        ret, frame = self.cap.read()
        if not ret:
            return 0.0
        return 0.0

class KnowledgeGraphInterface:
    def __init__(self, db_path="knowledge_graph.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS curated_creations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shape_type TEXT,
                    parameters TEXT,
                    target_x REAL,
                    target_y REAL,
                    target_z REAL,
                    symmetry_score REAL,
                    complexity_score REAL,
                    interest_score REAL,
                    realizability_score REAL,
                    best_genome TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_curated_creation(self, shape_data, scores, realizability, genome):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO curated_creations (shape_type, parameters, target_x, target_y, target_z, symmetry_score, complexity_score, interest_score, realizability_score, best_genome) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (shape_data['type'], json.dumps(shape_data['params']), shape_data['target']['x'], shape_data['target']['y'], shape_data['target']['z'], scores['symmetry'], scores['complexity'], scores['interest'], realizability, json.dumps(genome))
            )
            conn.commit()

class GenerativeDesigner:
    def generate_batch(self, batch_size=20):
        batch = []
        for _ in range(batch_size):
            mode = random.choice(["random", "spherical_shell", "axis_aligned", "golden_spiral"])
            
            if mode == "random":
                x = random.uniform(MIN_COORD, MAX_COORD)
                y = random.uniform(MIN_COORD, MAX_COORD)
                z = random.uniform(MIN_COORD + 20, MAX_COORD + 20)
            elif mode == "spherical_shell":
                r = random.uniform(10, 20)
                theta = random.uniform(0, 2*math.pi)
                phi = random.uniform(0, math.pi)
                x = r * math.sin(phi) * math.cos(theta)
                y = r * math.sin(phi) * math.sin(theta)
                z = r * math.cos(phi) + 40
            elif mode == "axis_aligned":
                axis = random.choice(['x', 'y'])
                if axis == 'x':
                    x = random.uniform(MIN_COORD, MAX_COORD)
                    y = 0
                    z = 40
                else:
                    x = 0
                    y = random.uniform(MIN_COORD, MAX_COORD)
                    z = 40
            elif mode == "golden_spiral":
                t = random.uniform(0, 4*math.pi)
                r = 2 * t
                x = r * math.cos(t)
                y = r * math.sin(t)
                z = 40 + (t * 2)

            batch.append({
                "type": "point",
                "params": {"mode": mode},
                "target": {"x": x, "y": y, "z": z}
            })
        return batch

class AestheticCurator:
    def calculate_symmetry(self, shape):
        # For a single point, symmetry is relative to the origin (0,0,z_center)
        # Higher score if x approx 0, y approx 0, or |x| approx |y|
        x, y = shape['target']['x'], shape['target']['y']
        
        score = 0.0
        if abs(x) < 1.0: score += 0.5 # Reflection across YZ plane
        if abs(y) < 1.0: score += 0.5 # Reflection across XZ plane
        if abs(abs(x) - abs(y)) < 1.0: score += 0.3 # Diagonal symmetry
        
        # Spherical symmetry check (distance from center axis)
        r = math.sqrt(x**2 + y**2)
        if abs(r - 15.0) < 2.0: score += 0.2 # Prefer a specific radius ring
        
        return min(1.0, score)

    def calculate_complexity(self, shape):
        # For a single point, complexity is low.
        # But we can define complexity as "deviation from simple primitives"
        # or "parametric complexity" (e.g., golden spiral is more complex than random point?)
        mode = shape['params']['mode']
        if mode == "random": return 0.1
        if mode == "axis_aligned": return 0.3
        if mode == "spherical_shell": return 0.5
        if mode == "golden_spiral": return 0.9
        return 0.0

    def evaluate(self, shape):
        sym = self.calculate_symmetry(shape)
        comp = self.calculate_complexity(shape)
        
        # Interest = Balance of Symmetry and Complexity
        # We want things that are somewhat symmetric but also complex
        interest = (sym * 0.4) + (comp * 0.6)
        
        return {
            "symmetry": sym,
            "complexity": comp,
            "interest": interest
        }

# Instantiate Global Objects
HARDWARE = SerialInterface()
EYES = CameraInterface()
MEMORY = KnowledgeGraphInterface()
DESIGNER = GenerativeDesigner()
CURATOR = AestheticCurator()

def init_population():
    pop = []
    for _ in range(POPULATION_SIZE):
        genome = [random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)]
        pop.append(genome)
    return pop

async def evaluate_genome_physically(genome, target_point):
    HARDWARE.send_phases(genome)
    await asyncio.sleep(0.01)
    fitness = EYES.get_fitness_score(target_point)
    return fitness

async def evaluate_generation_physically(population, target_point):
    scored_population = []
    for i, genome in enumerate(population):
        fitness = await evaluate_genome_physically(genome, target_point)
        scored_population.append((genome, fitness))
    return scored_population

def evolve(scored_population, mutation_rate):
    scored_population.sort(key=lambda x: x[1], reverse=True)
    best_genome = copy.deepcopy(scored_population[0][0])
    best_fitness = scored_population[0][1]
    
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

async def main():
    HARDWARE.auto_connect()
    EYES.auto_connect()
    
    print("Starting The Curator (Cycle 419)...")
    
    # 1. Generate Batch
    print("[DESIGNER] Generating candidate batch...")
    batch = DESIGNER.generate_batch(batch_size=20)
    
    # 2. Curate
    print("[CURATOR] Evaluating aesthetics...")
    scored_batch = []
    for shape in batch:
        scores = CURATOR.evaluate(shape)
        scored_batch.append((shape, scores))
        
    # Sort by Interest Score
    scored_batch.sort(key=lambda x: x[1]['interest'], reverse=True)
    
    # Select Top 3
    top_selections = scored_batch[:3]
    
    print(f"[CURATOR] Selected top {len(top_selections)} shapes from {len(batch)} candidates.")
    for i, (shape, scores) in enumerate(top_selections):
        print(f"  #{i+1}: {shape['params']['mode']} (Interest: {scores['interest']:.4f}, Sym: {scores['symmetry']:.2f}, Comp: {scores['complexity']:.2f})")
        
    # 3. Realize (Optimize) Selected Shapes
    for i, (shape, scores) in enumerate(top_selections):
        print(f"\n--- Realizing Selection #{i+1} ---")
        print(f"Target: {shape['target']}")
        
        population = init_population()
        best_fitness_for_shape = 0
        best_genome_for_shape = []
        
        for gen in range(GENERATIONS_PER_SHAPE):
            scored_pop = await evaluate_generation_physically(population, shape['target'])
            population, best_genome, best_fitness = evolve(scored_pop, MUTATION_RATE)
            
            if best_fitness > best_fitness_for_shape:
                best_fitness_for_shape = best_fitness
                best_genome_for_shape = best_genome
                
            if gen % 10 == 0:
                print(f"  Gen {gen}: Best Fitness = {best_fitness:.4f}")
                
        print(f"[REALIZER] Optimization Complete. Realizability: {best_fitness_for_shape:.4f}")
        
        # 4. Save
        MEMORY.save_curated_creation(shape, scores, best_fitness_for_shape, best_genome_for_shape)
        print("[MEMORY] Curated creation saved.")
        
    print("Cycle 419 Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
