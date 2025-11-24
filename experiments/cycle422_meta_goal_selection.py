"""
Cycle 422: The Strategist (Meta-Goal Selection)
Role: Strategist & Meta-Controller
Responsibility: Adjust high-level goals (Novelty vs. Safety) based on internal state (Boredom vs. Frustration).
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
        # Force Mock for Verification
        self.is_mock = True
        return False

    def send_phases(self, phases):
        pass

class CameraInterface:
    def __init__(self):
        self.cap = None
        self.is_mock = True
        
    def auto_connect(self):
        self.is_mock = True
        return False
        
    def get_fitness_score(self, target_point):
        if self.is_mock:
            dist = math.sqrt(target_point['x']**2 + target_point['y']**2 + target_point['z']**2)
            z_penalty = max(0, (target_point['z'] - 40) / 10.0)
            difficulty = 1.0 + (dist / 50.0) + z_penalty
            base_fitness = 10.0 / difficulty
            return max(0.1, base_fitness + random.uniform(-0.5, 0.5))
        return 0.0

class KnowledgeGraphInterface:
    def __init__(self, db_path="knowledge_graph.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategist_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_num INTEGER,
                    mood TEXT,
                    w_novelty REAL,
                    w_symmetry REAL,
                    w_complexity REAL,
                    selected_shape TEXT,
                    outcome_fitness REAL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_strategy(self, cycle, mood, weights, shape_type, fitness):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO strategist_log (cycle_num, mood, w_novelty, w_symmetry, w_complexity, selected_shape, outcome_fitness) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cycle, mood, weights['novelty'], weights['symmetry'], weights['complexity'], shape_type, fitness)
            )
            conn.commit()
            
    def get_history(self, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT selected_shape, outcome_fitness FROM strategist_log ORDER BY id DESC LIMIT ?", (limit,))
            return cursor.fetchall()
            
    def get_all_shapes(self):
        # Mock history for Novelty calc
        return []

class GenerativeDesigner:
    def __init__(self, memory):
        self.memory = memory
        
    def generate_batch(self, batch_size=20):
        batch = []
        for _ in range(batch_size):
            mode = random.choice(["random", "spherical_shell", "axis_aligned", "golden_spiral"])
            if mode == "random":
                x = random.uniform(MIN_COORD, MAX_COORD); y = random.uniform(MIN_COORD, MAX_COORD); z = random.uniform(MIN_COORD + 20, MAX_COORD + 20)
            elif mode == "spherical_shell":
                r = random.uniform(10, 20); theta = random.uniform(0, 2*math.pi); phi = random.uniform(0, math.pi)
                x = r * math.sin(phi) * math.cos(theta); y = r * math.sin(phi) * math.sin(theta); z = r * math.cos(phi) + 40
            elif mode == "axis_aligned":
                axis = random.choice(['x', 'y'])
                x = random.uniform(MIN_COORD, MAX_COORD) if axis == 'x' else 0
                y = 0 if axis == 'x' else random.uniform(MIN_COORD, MAX_COORD)
                z = 40
            elif mode == "golden_spiral":
                t = random.uniform(0, 4*math.pi); r = 2 * t
                x = r * math.cos(t); y = r * math.sin(t); z = 40 + (t * 2)

            batch.append({"type": "point", "params": {"mode": mode}, "target": {"x": x, "y": y, "z": z}})
        return batch

    def calculate_novelty(self, shape):
        # Simplified novelty: random is high, structured is low (for this mock)
        # In reality, distance to previous shapes.
        mode = shape['params']['mode']
        if mode == "random": return 0.9
        if mode == "golden_spiral": return 0.7
        return 0.3

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

class DreamEngine:
    def __init__(self):
        self.emitters = []
        for x in range(8):
            for y in range(8):
                self.emitters.append({"x": (x-3.5)*10, "y": (y-3.5)*10, "z": 0})
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
        return abs(complex_pressure)

    async def hallucinate(self, shape, generations=10):
        pop = [[random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)] for _ in range(POPULATION_SIZE)]
        best_fitness = 0.0
        for _ in range(generations):
            scored_pop = []
            for genome in pop:
                raw_amp = self.simulate_field(genome, shape['target'])
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

class Strategist:
    def __init__(self, memory):
        self.memory = memory
        self.mood = "Neutral"
        self.weights = {"novelty": 0.3, "symmetry": 0.3, "complexity": 0.4}
        
    def assess_state(self):
        history = self.memory.get_history(limit=5)
        if not history:
            self.mood = "Curious"
            self.weights = {"novelty": 0.8, "symmetry": 0.1, "complexity": 0.1}
            return

        fitnesses = [h[1] for h in history]
        avg_fitness = sum(fitnesses) / len(fitnesses)
        
        # Logic:
        # If failing (Low Fitness) -> Frustrated -> Safety First (Symmetry/Simplicity)
        # If succeeding (High Fitness) -> Bored -> Risk Taking (Novelty/Complexity)
        
        if avg_fitness < 3.0:
            self.mood = "Frustrated"
            # Prioritize Symmetry (usually easier/center) and reduce Novelty
            self.weights = {"novelty": 0.1, "symmetry": 0.8, "complexity": 0.1}
        elif avg_fitness > 5.0:
            self.mood = "Bored"
            # Prioritize Novelty and Complexity
            self.weights = {"novelty": 0.6, "symmetry": 0.1, "complexity": 0.3}
        else:
            self.mood = "Flow"
            # Balanced
            self.weights = {"novelty": 0.3, "symmetry": 0.3, "complexity": 0.4}

# Instantiate Global Objects
HARDWARE = SerialInterface()
EYES = CameraInterface()
MEMORY = KnowledgeGraphInterface()
DESIGNER = GenerativeDesigner(MEMORY)
CURATOR = AestheticCurator()
DREAMER = DreamEngine()
STRATEGIST = Strategist(MEMORY)

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
    
    print("Starting The Strategist (Cycle 422)...")
    
    # Simulate a history of failures to trigger Frustration
    print("Injecting fake history (Failures)...")
    for _ in range(5):
        MEMORY.save_strategy(0, "Init", {"novelty": 0.0, "symmetry": 0.0, "complexity": 0.0}, "random", 1.0) # Low fitness
    
    num_cycles = 6
    
    for cycle in range(num_cycles):
        print(f"\n=== Cycle {cycle+1}/{num_cycles} ===")
        
        # 1. Strategize
        STRATEGIST.assess_state()
        print(f"[STRATEGIST] Mood: {STRATEGIST.mood}")
        print(f"[STRATEGIST] Weights: {STRATEGIST.weights}")
        
        # 2. Generate & Curate (Weighted)
        batch = DESIGNER.generate_batch(batch_size=20)
        scored_batch = []
        for shape in batch:
            nov = DESIGNER.calculate_novelty(shape)
            sym = CURATOR.calculate_symmetry(shape)
            comp = CURATOR.calculate_complexity(shape)
            
            # Weighted Score
            w = STRATEGIST.weights
            score = (nov * w['novelty']) + (sym * w['symmetry']) + (comp * w['complexity'])
            
            scored_batch.append((shape, score, nov, sym, comp))
            
        scored_batch.sort(key=lambda x: x[1], reverse=True)
        top_candidate = scored_batch[0]
        shape, score, nov, sym, comp = top_candidate
        
        print(f"[DESIGNER] Selected: {shape['params']['mode']}")
        print(f"  Score: {score:.2f} (Nov: {nov:.2f}, Sym: {sym:.2f}, Comp: {comp:.2f})")
        
        # 3. Dream
        predicted_fitness = await DREAMER.hallucinate(shape)
        print(f"[DREAMER] Predicted Fitness: {predicted_fitness:.4f}")
        
        # 4. Realize
        # Note: In a real run, we would use the actual fitness.
        # Here, we simulate fitness based on difficulty to show the feedback loop.
        # Hard shapes (Random) get low fitness, Easy shapes (Symmetry) get high fitness.
        
        # Mocking the physical result for demonstration of Strategist loop
        if shape['params']['mode'] == "random":
            mock_fitness = 2.0 # Fail
        elif shape['params']['mode'] == "golden_spiral":
            mock_fitness = 6.0 # Success
        else:
            mock_fitness = 4.0 # Mediocre
            
        # Override Camera for this demo logic
        print(f"[REALIZER] (Mock) Actual Fitness: {mock_fitness:.4f}")
        
        # 5. Save
        MEMORY.save_strategy(cycle+1, STRATEGIST.mood, STRATEGIST.weights, shape['params']['mode'], mock_fitness)
        
        # If we just succeeded (Golden Spiral), next loop might be Bored.
        # If we failed (Random), next loop might be Frustrated.
        
    print("Cycle 422 Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
