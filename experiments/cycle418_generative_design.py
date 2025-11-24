"""
Cycle 418: The Creative Machine (Generative Design)
Role: Generative Designer & Optimizer
Responsibility: Invent new target shapes, assess novelty, and attempt physical realization.
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
# Bounding box for generation
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
        self.current_mock_fitness = 5.0
        
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
        # In a real scenario, this would measure how close the particle is to the target_point.
        # For mock, we simulate "realizability" - some shapes are harder than others.
        if self.is_mock:
            # Distance from center makes it harder
            dist = math.sqrt(target_point['x']**2 + target_point['y']**2 + target_point['z']**2)
            difficulty = 1.0 + (dist / 50.0)
            base_fitness = 10.0 / difficulty
            return max(0.1, base_fitness + random.uniform(-0.5, 0.5))
            
        if not self.cap or not self.cap.isOpened():
            return 0.0
        ret, frame = self.cap.read()
        if not ret:
            return 0.0
        # Placeholder for real CV logic
        return 0.0

class KnowledgeGraphInterface:
    def __init__(self, db_path="knowledge_graph.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS creations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shape_type TEXT,
                    parameters TEXT,
                    target_x REAL,
                    target_y REAL,
                    target_z REAL,
                    novelty_score REAL,
                    realizability_score REAL,
                    best_genome TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_creation(self, shape_data, novelty, realizability, genome):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO creations (shape_type, parameters, target_x, target_y, target_z, novelty_score, realizability_score, best_genome) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (shape_data['type'], json.dumps(shape_data['params']), shape_data['target']['x'], shape_data['target']['y'], shape_data['target']['z'], novelty, realizability, json.dumps(genome))
            )
            conn.commit()
            
    def get_history(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT target_x, target_y, target_z FROM creations")
            return cursor.fetchall()

class GenerativeDesigner:
    def __init__(self, memory_interface):
        self.memory = memory_interface
        
    def generate_shape(self):
        """Procedurally generates a new target point/shape."""
        # Simple generator: Random point within bounds, but with some structure
        # e.g., favoring shells or axes
        
        mode = random.choice(["random", "spherical_shell", "axis_aligned"])
        
        if mode == "random":
            x = random.uniform(MIN_COORD, MAX_COORD)
            y = random.uniform(MIN_COORD, MAX_COORD)
            z = random.uniform(MIN_COORD + 20, MAX_COORD + 20) # Levitation height offset
        elif mode == "spherical_shell":
            r = random.uniform(10, 20)
            theta = random.uniform(0, 2*math.pi)
            phi = random.uniform(0, math.pi)
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi) + 40 # Center at z=40
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
                
        return {
            "type": "point",
            "params": {"mode": mode},
            "target": {"x": x, "y": y, "z": z}
        }

    def calculate_novelty(self, new_shape):
        """Calculates distance to nearest neighbor in history."""
        history = self.memory.get_history()
        if not history:
            return 1.0 # Maximum novelty if no history
            
        target = new_shape['target']
        min_dist = float('inf')
        
        for h in history:
            d = math.sqrt((target['x'] - h[0])**2 + (target['y'] - h[1])**2 + (target['z'] - h[2])**2)
            if d < min_dist:
                min_dist = d
                
        # Normalize novelty (e.g., sigmoid or bounded)
        # Here, just raw distance
        return min_dist

# Instantiate Global Objects
HARDWARE = SerialInterface()
EYES = CameraInterface()
MEMORY = KnowledgeGraphInterface()
DESIGNER = GenerativeDesigner(MEMORY)

def init_population():
    pop = []
    for _ in range(POPULATION_SIZE):
        genome = [random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)]
        pop.append(genome)
    return pop

async def evaluate_genome_physically(genome, target_point):
    HARDWARE.send_phases(genome)
    await asyncio.sleep(0.02) # Fast update
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
    
    print("Starting The Creative Machine (Cycle 418)...")
    
    creation_count = 0
    
    while creation_count < 5: # Generate 5 shapes for this cycle
        creation_count += 1
        print(f"\n--- Creation {creation_count} ---")
        
        # 1. Generate
        shape = DESIGNER.generate_shape()
        novelty = DESIGNER.calculate_novelty(shape)
        print(f"[DESIGNER] Generated: {shape['params']['mode']} at {shape['target']}")
        print(f"[DESIGNER] Novelty Score: {novelty:.4f}")
        
        # 2. Realize (Optimize)
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
        
        # 3. Save
        MEMORY.save_creation(shape, novelty, best_fitness_for_shape, best_genome_for_shape)
        print("[MEMORY] Creation saved.")
        
    print("Cycle 418 Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
