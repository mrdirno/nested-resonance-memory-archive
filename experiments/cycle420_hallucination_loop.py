"""
Cycle 420: The Dreamer (Hallucination Loop)
Role: Dreamer & Optimizer
Responsibility: Simulate potential futures (hallucinations) to predict realizability before physical execution.
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
import cmath

# --- GA Parameters ---
POPULATION_SIZE = 20
GENERATIONS_PER_SHAPE = 30
MUTATION_RATE = 0.1
ELITISM_COUNT = 2

# --- Simulation Constants ---
NUM_EMITTERS = 64
MIN_COORD = -20
MAX_COORD = 20
WAVE_NUMBER = 2 * np.pi / 8.6 # lambda ~ 8.6mm (40kHz)

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
        # Mock Reality:
        # Some shapes are "physically impossible" or hard.
        # Let's say targets with high Z are harder.
        # And targets far from center are harder.
        if self.is_mock:
            dist = math.sqrt(target_point['x']**2 + target_point['y']**2 + target_point['z']**2)
            z_penalty = max(0, (target_point['z'] - 40) / 10.0)
            difficulty = 1.0 + (dist / 50.0) + z_penalty
            base_fitness = 10.0 / difficulty
            
            # Add some noise/chaos
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
                CREATE TABLE IF NOT EXISTS dreamed_creations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shape_type TEXT,
                    parameters TEXT,
                    target_x REAL,
                    target_y REAL,
                    target_z REAL,
                    dream_fitness REAL,
                    actual_fitness REAL,
                    prediction_error REAL,
                    best_genome TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_dream(self, shape_data, dream_fitness, actual_fitness, genome):
        error = abs(dream_fitness - actual_fitness)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO dreamed_creations (shape_type, parameters, target_x, target_y, target_z, dream_fitness, actual_fitness, prediction_error, best_genome) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (shape_data['type'], json.dumps(shape_data['params']), shape_data['target']['x'], shape_data['target']['y'], shape_data['target']['z'], dream_fitness, actual_fitness, error, json.dumps(genome))
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
        x, y = shape['target']['x'], shape['target']['y']
        score = 0.0
        if abs(x) < 1.0: score += 0.5
        if abs(y) < 1.0: score += 0.5
        if abs(abs(x) - abs(y)) < 1.0: score += 0.3
        r = math.sqrt(x**2 + y**2)
        if abs(r - 15.0) < 2.0: score += 0.2
        return min(1.0, score)

    def calculate_complexity(self, shape):
        mode = shape['params']['mode']
        if mode == "random": return 0.1
        if mode == "axis_aligned": return 0.3
        if mode == "spherical_shell": return 0.5
        if mode == "golden_spiral": return 0.9
        return 0.0

    def evaluate(self, shape):
        sym = self.calculate_symmetry(shape)
        comp = self.calculate_complexity(shape)
        interest = (sym * 0.4) + (comp * 0.6)
        return {
            "symmetry": sym,
            "complexity": comp,
            "interest": interest
        }

class DreamEngine:
    def __init__(self):
        # Emitter positions (8x8 grid)
        self.emitters = []
        for x in range(8):
            for y in range(8):
                self.emitters.append({"x": (x-3.5)*10, "y": (y-3.5)*10, "z": 0})

    def simulate_field(self, phases, target_point):
        # Calculate acoustic pressure at target_point
        # P = sum(A * exp(i * (phi + k * d)))
        # Assuming A=1
        
        complex_pressure = complex(0, 0)
        
        for i, emitter in enumerate(self.emitters):
            dx = target_point['x'] - emitter['x']
            dy = target_point['y'] - emitter['y']
            dz = target_point['z'] - emitter['z']
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            phase = phases[i]
            # k * d
            kd = WAVE_NUMBER * dist
            
            complex_pressure += cmath.exp(complex(0, phase + kd))
            
        amplitude = abs(complex_pressure)
        return amplitude

    async def hallucinate(self, shape, generations=10):
        """Runs a fast internal simulation of the optimization process."""
        # Initialize random population
        pop = [[random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)] for _ in range(POPULATION_SIZE)]
        
        best_fitness = 0.0
        
        for _ in range(generations):
            scored_pop = []
            for genome in pop:
                # Simulate physics
                fitness = self.simulate_field(genome, shape['target'])
                # Normalize/Scale fitness to match "Reality" (Mock Camera) scale roughly
                # Reality is ~ 0-10. Simulation amplitude is ~ 0-64.
                # Let's scale it down.
                fitness = fitness / 6.4 
                scored_pop.append((genome, fitness))
            
            # Evolve (Simplified)
            scored_pop.sort(key=lambda x: x[1], reverse=True)
            best_fitness = max(best_fitness, scored_pop[0][1])
            
            # Simple elitism + mutation for next gen
            new_pop = [scored_pop[0][0], scored_pop[1][0]]
            while len(new_pop) < POPULATION_SIZE:
                parent = random.choice(scored_pop[:5])[0]
                child = [p + random.gauss(0, 0.5) for p in parent]
                new_pop.append(child)
            pop = new_pop
            
        return best_fitness

# Instantiate Global Objects
HARDWARE = SerialInterface()
EYES = CameraInterface()
MEMORY = KnowledgeGraphInterface()
DESIGNER = GenerativeDesigner()
CURATOR = AestheticCurator()
DREAMER = DreamEngine()

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
    
    print("Starting The Dreamer (Cycle 420)...")
    
    # 1. Generate Batch
    print("[DESIGNER] Generating candidate batch...")
    batch = DESIGNER.generate_batch(batch_size=20)
    
    # 2. Curate (Aesthetic Selection)
    print("[CURATOR] Evaluating aesthetics...")
    scored_batch = []
    for shape in batch:
        scores = CURATOR.evaluate(shape)
        scored_batch.append((shape, scores))
    
    scored_batch.sort(key=lambda x: x[1]['interest'], reverse=True)
    top_candidates = scored_batch[:5] # Take top 5 for Dreaming
    
    print(f"[CURATOR] Selected top {len(top_candidates)} candidates for Dreaming.")
    
    # 3. Dream (Internal Simulation)
    print("[DREAMER] Hallucinating outcomes...")
    dreamed_candidates = []
    for shape, scores in top_candidates:
        predicted_fitness = await DREAMER.hallucinate(shape)
        dreamed_candidates.append((shape, scores, predicted_fitness))
        print(f"  Dreamed {shape['params']['mode']}: Predicted Fitness = {predicted_fitness:.4f}")
        
    # Sort by Predicted Fitness
    dreamed_candidates.sort(key=lambda x: x[2], reverse=True)
    
    # Select Top 2 for Reality
    final_selection = dreamed_candidates[:2]
    print(f"[DREAMER] Selected top {len(final_selection)} for Physical Realization.")
    
    # 4. Realize (Physical Execution)
    for i, (shape, scores, predicted_fitness) in enumerate(final_selection):
        print(f"\n--- Realizing Selection #{i+1} ---")
        print(f"Target: {shape['target']}")
        print(f"Predicted Fitness: {predicted_fitness:.4f}")
        
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
                print(f"  Gen {gen}: Actual Fitness = {best_fitness:.4f}")
                
        print(f"[REALIZER] Optimization Complete. Actual Fitness: {best_fitness_for_shape:.4f}")
        print(f"[DREAMER] Prediction Error: {abs(predicted_fitness - best_fitness_for_shape):.4f}")
        
        # 5. Save
        MEMORY.save_dream(shape, predicted_fitness, best_fitness_for_shape, best_genome_for_shape)
        print("[MEMORY] Dream saved.")
        
    print("Cycle 420 Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
