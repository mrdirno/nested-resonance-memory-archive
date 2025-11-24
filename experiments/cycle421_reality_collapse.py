"""
Cycle 421: The Observer (Reality Collapse)
Role: Observer & Model Updater
Responsibility: Measure discrepancy between Dream and Reality, and update the internal model to minimize future error.
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
WAVE_NUMBER = 2 * np.pi / 8.6

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
        # Force Mock for Verification of Logic
        self.is_mock = True
        return False
        
    def get_fitness_score(self, target_point):
        if self.is_mock:
            dist = math.sqrt(target_point['x']**2 + target_point['y']**2 + target_point['z']**2)
            z_penalty = max(0, (target_point['z'] - 40) / 10.0)
            difficulty = 1.0 + (dist / 50.0) + z_penalty
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
                CREATE TABLE IF NOT EXISTS observed_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_num INTEGER,
                    shape_type TEXT,
                    predicted_fitness REAL,
                    actual_fitness REAL,
                    error REAL,
                    model_scale_before REAL,
                    model_scale_after REAL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_observation(self, cycle, shape_data, pred, actual, error, scale_before, scale_after):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO observed_cycles (cycle_num, shape_type, predicted_fitness, actual_fitness, error, model_scale_before, model_scale_after) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cycle, shape_data['type'], pred, actual, error, scale_before, scale_after)
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
        self.emitters = []
        for x in range(8):
            for y in range(8):
                self.emitters.append({"x": (x-3.5)*10, "y": (y-3.5)*10, "z": 0})
        
        # Tunable Model Parameter
        # Initial guess: 6.4 (from previous cycle observation)
        self.amplitude_scale = 6.4 

    def simulate_field(self, phases, target_point):
        complex_pressure = complex(0, 0)
        for i, emitter in enumerate(self.emitters):
            dx = target_point['x'] - emitter['x']
            dy = target_point['y'] - emitter['y']
            dz = target_point['z'] - emitter['z']
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            phase = phases[i]
            kd = WAVE_NUMBER * dist
            complex_pressure += cmath.exp(complex(0, phase + kd))
        amplitude = abs(complex_pressure)
        return amplitude

    async def hallucinate(self, shape, generations=10):
        pop = [[random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)] for _ in range(POPULATION_SIZE)]
        best_fitness = 0.0
        
        for _ in range(generations):
            scored_pop = []
            for genome in pop:
                raw_amp = self.simulate_field(genome, shape['target'])
                # Apply Model Scaling
                fitness = raw_amp / self.amplitude_scale
                scored_pop.append((genome, fitness))
            
            scored_pop.sort(key=lambda x: x[1], reverse=True)
            best_fitness = max(best_fitness, scored_pop[0][1])
            
            new_pop = [scored_pop[0][0], scored_pop[1][0]]
            while len(new_pop) < POPULATION_SIZE:
                parent = random.choice(scored_pop[:5])[0]
                child = [p + random.gauss(0, 0.5) for p in parent]
                new_pop.append(child)
            pop = new_pop
            
        return best_fitness

class Observer:
    def __init__(self, dream_engine):
        self.dream_engine = dream_engine
        self.learning_rate = 0.1

    def observe_and_update(self, predicted_fitness, actual_fitness):
        """
        Updates the DreamEngine's amplitude_scale based on the error.
        If Actual < Predicted, our scale is too small (dividing by too small number? No wait).
        Fitness = Raw / Scale.
        If Fitness_Pred > Fitness_Actual:
           Raw/Scale_Old > Fitness_Actual
           Scale_Old < Raw/Fitness_Actual
           We need to INCREASE Scale to reduce Predicted Fitness.
        """
        
        # Simple update rule:
        # Target Scale = Raw_Amp / Actual_Fitness (approx)
        # But we don't have Raw_Amp easily here without re-simulating.
        # Let's use the ratio.
        # Pred = Raw / Scale
        # Actual = Raw / New_Scale
        # => New_Scale = Raw / Actual = (Pred * Scale) / Actual
        
        if actual_fitness < 0.001: return 0.0 # Avoid div by zero
        
        target_scale = (predicted_fitness * self.dream_engine.amplitude_scale) / actual_fitness
        
        # Smooth update
        old_scale = self.dream_engine.amplitude_scale
        new_scale = (1 - self.learning_rate) * old_scale + (self.learning_rate) * target_scale
        
        self.dream_engine.amplitude_scale = new_scale
        return abs(predicted_fitness - actual_fitness)

# Instantiate Global Objects
HARDWARE = SerialInterface()
EYES = CameraInterface()
MEMORY = KnowledgeGraphInterface()
DESIGNER = GenerativeDesigner()
CURATOR = AestheticCurator()
DREAMER = DreamEngine()
OBSERVER = Observer(DREAMER)

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
    
    print("Starting The Observer (Cycle 421)...")
    print(f"Initial Model Scale: {DREAMER.amplitude_scale:.4f}")
    
    num_cycles = 5
    
    for cycle in range(num_cycles):
        print(f"\n=== Wake-Sleep Cycle {cycle+1}/{num_cycles} ===")
        
        # 1. Generate & Curate
        batch = DESIGNER.generate_batch(batch_size=10)
        scored_batch = []
        for shape in batch:
            scores = CURATOR.evaluate(shape)
            scored_batch.append((shape, scores))
        scored_batch.sort(key=lambda x: x[1]['interest'], reverse=True)
        top_candidate = scored_batch[0] # Take top 1
        shape, scores = top_candidate
        
        print(f"[DESIGNER] Selected: {shape['params']['mode']} (Interest: {scores['interest']:.2f})")
        
        # 2. Dream
        predicted_fitness = await DREAMER.hallucinate(shape)
        print(f"[DREAMER] Predicted Fitness: {predicted_fitness:.4f}")
        
        # 3. Realize
        print("[REALIZER] Attempting physical realization...")
        population = init_population()
        best_fitness_for_shape = 0
        
        for gen in range(GENERATIONS_PER_SHAPE):
            scored_pop = await evaluate_generation_physically(population, shape['target'])
            population, best_genome, best_fitness = evolve(scored_pop, MUTATION_RATE)
            best_fitness_for_shape = max(best_fitness_for_shape, best_fitness)
            
        print(f"[REALIZER] Actual Fitness: {best_fitness_for_shape:.4f}")
        
        # 4. Observe & Update
        scale_before = DREAMER.amplitude_scale
        error = OBSERVER.observe_and_update(predicted_fitness, best_fitness_for_shape)
        scale_after = DREAMER.amplitude_scale
        
        print(f"[OBSERVER] Error: {error:.4f}")
        print(f"[OBSERVER] Updated Model Scale: {scale_before:.4f} -> {scale_after:.4f}")
        
        MEMORY.save_observation(cycle, shape, predicted_fitness, best_fitness_for_shape, error, scale_before, scale_after)
        
    print("Cycle 421 Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
