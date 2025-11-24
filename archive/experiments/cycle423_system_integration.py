"""
Cycle 423: The Architect (System Integration)
Role: The Architect (Main Controller)
Responsibility: Orchestrate the entire lifecycle of autonomous discovery, creation, and self-correction.
Integrates: Calibration, Generative Design, Curation, Dreaming, Observation, and Strategy.
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
                CREATE TABLE IF NOT EXISTS architect_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_num INTEGER,
                    phase TEXT,
                    details TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def log_event(self, cycle, phase, details):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO architect_log (cycle_num, phase, details) VALUES (?, ?, ?)",
                (cycle, phase, json.dumps(details))
            )
            conn.commit()
            
    def get_recent_fitness(self, limit=5):
        # Mocking history for Strategist
        # In a real system, this would query the 'observed_cycles' or similar table
        return [random.uniform(3.0, 6.0) for _ in range(limit)]

# --- Components ---

class CalibrationModule:
    def check_health(self):
        # Simulating a health check
        drift = random.uniform(0, 0.05)
        if drift > 0.04:
            return False, drift
        return True, drift
        
    def recalibrate(self):
        # Simulating recalibration
        return True

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

class Observer:
    def __init__(self, dream_engine):
        self.dream_engine = dream_engine
        self.learning_rate = 0.1

    def observe_and_update(self, predicted_fitness, actual_fitness):
        if actual_fitness < 0.001: return 0.0
        target_scale = (predicted_fitness * self.dream_engine.amplitude_scale) / actual_fitness
        old_scale = self.dream_engine.amplitude_scale
        new_scale = (1 - self.learning_rate) * old_scale + (self.learning_rate) * target_scale
        self.dream_engine.amplitude_scale = new_scale
        return abs(predicted_fitness - actual_fitness)

class Strategist:
    def __init__(self, memory):
        self.memory = memory
        self.mood = "Neutral"
        self.weights = {"novelty": 0.3, "symmetry": 0.3, "complexity": 0.4}
        # Keep local history for simulation consistency
        self.history = []
        
    def record_outcome(self, fitness):
        self.history.append(fitness)
        if len(self.history) > 5:
            self.history.pop(0)
        
    def assess_state(self):
        if not self.history:
            self.mood = "Curious"
            self.weights = {"novelty": 0.8, "symmetry": 0.1, "complexity": 0.1}
            return

        avg_fitness = sum(self.history) / len(self.history)
        
        if avg_fitness < 3.0:
            self.mood = "Frustrated"
            self.weights = {"novelty": 0.1, "symmetry": 0.8, "complexity": 0.1}
        elif avg_fitness > 5.0:
            self.mood = "Bored"
            self.weights = {"novelty": 0.6, "symmetry": 0.1, "complexity": 0.3}
        else:
            self.mood = "Flow"
            self.weights = {"novelty": 0.3, "symmetry": 0.3, "complexity": 0.4}

# --- The Architect ---

class Architect:
    def __init__(self):
        self.memory = KnowledgeGraphInterface()
        self.calibration = CalibrationModule()
        self.designer = GenerativeDesigner(self.memory)
        self.curator = AestheticCurator()
        self.dreamer = DreamEngine()
        self.observer = Observer(self.dreamer)
        self.strategist = Strategist(self.memory)
        
        # Hardware
        self.hardware = SerialInterface()
        self.eyes = CameraInterface()
        
    async def wake_up(self):
        print("[ARCHITECT] Waking up...")
        self.hardware.auto_connect()
        self.eyes.auto_connect()
        
        # Check Health
        healthy, drift = self.calibration.check_health()
        if not healthy:
            print(f"[ARCHITECT] Drift detected ({drift:.4f}). Recalibrating...")
            self.calibration.recalibrate()
            print("[ARCHITECT] Recalibration complete.")
        else:
            print(f"[ARCHITECT] Systems nominal. Drift: {drift:.4f}")
            
    async def run_cycle(self, cycle_num):
        print(f"\n=== Cycle {cycle_num} ===")
        
        # 1. Strategize
        self.strategist.assess_state()
        print(f"[STRATEGIST] Mood: {self.strategist.mood} | Weights: {self.strategist.weights}")
        self.memory.log_event(cycle_num, "STRATEGY", {"mood": self.strategist.mood, "weights": self.strategist.weights})
        
        # 2. Imagine (Generate & Curate)
        batch = self.designer.generate_batch(batch_size=20)
        scored_batch = []
        for shape in batch:
            nov = self.designer.calculate_novelty(shape)
            sym = self.curator.calculate_symmetry(shape)
            comp = self.curator.calculate_complexity(shape)
            
            w = self.strategist.weights
            score = (nov * w['novelty']) + (sym * w['symmetry']) + (comp * w['complexity'])
            scored_batch.append((shape, score))
            
        scored_batch.sort(key=lambda x: x[1], reverse=True)
        top_candidates = scored_batch[:3] # Top 3 for Dreaming
        print(f"[ARCHITECT] Selected {len(top_candidates)} candidates for dreaming.")
        
        # 3. Dream
        dream_results = []
        for shape, score in top_candidates:
            pred_fitness = await self.dreamer.hallucinate(shape)
            dream_results.append((shape, pred_fitness))
            print(f"  Dreamed {shape['params']['mode']}: Pred Fitness {pred_fitness:.2f}")
            
        # Select Best Dream
        dream_results.sort(key=lambda x: x[1], reverse=True)
        best_dream = dream_results[0]
        target_shape, predicted_fitness = best_dream
        print(f"[ARCHITECT] Chosen Target: {target_shape['params']['mode']} (Pred: {predicted_fitness:.2f})")
        self.memory.log_event(cycle_num, "DREAM", {"target": target_shape['params']['mode'], "predicted": predicted_fitness})
        
        # 4. Act (Realize)
        print("[REALIZER] Attempting physical realization...")
        # Mocking the physical result based on difficulty
        if target_shape['params']['mode'] == "random":
            actual_fitness = 2.0 + random.uniform(-0.5, 0.5)
        elif target_shape['params']['mode'] == "golden_spiral":
            actual_fitness = 6.0 + random.uniform(-0.5, 0.5)
        else:
            actual_fitness = 4.0 + random.uniform(-0.5, 0.5)
            
        print(f"[REALIZER] Actual Fitness: {actual_fitness:.4f}")
        self.memory.log_event(cycle_num, "ACTION", {"actual": actual_fitness})
        
        # 5. Observe & Learn
        error = self.observer.observe_and_update(predicted_fitness, actual_fitness)
        print(f"[OBSERVER] Error: {error:.4f} | New Model Scale: {self.dreamer.amplitude_scale:.4f}")
        self.memory.log_event(cycle_num, "OBSERVATION", {"error": error, "new_scale": self.dreamer.amplitude_scale})
        
        # Update Strategist History
        self.strategist.record_outcome(actual_fitness)
        
        # 6. Sleep (Pause)
        await asyncio.sleep(0.1)

async def main():
    architect = Architect()
    await architect.wake_up()
    
    print("Starting Autonomous Loop...")
    for i in range(1, 11): # Run 10 cycles
        await architect.run_cycle(i)
        
    print("Autonomous Loop Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")