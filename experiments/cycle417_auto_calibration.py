"""
Cycle 417: The Self-Correcting Laboratory (Automated Calibration)
Role: Self-Calibrating Coordinator
Responsibility: Detect miscalibration and automatically perform adjustments.
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
PERSISTENCE_THRESHOLD = 0.7 # If fitness drops below 70% of recent peak, re-initialize
FITNESS_HISTORY_LENGTH = 5  # Number of recent best fitnesses to consider for peak
CALIBRATION_CHECK_INTERVAL = 100 # Check every X generations

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
CALIBRATION_OFFSET_X = 0.0 # Global calibration offset for mock
CALIBRATION_OFFSET_Y = 0.0
CALIBRATION_OFFSET_Z = 0.0


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
    def __init__(self):
        self.cap = None
        self.is_mock = True
        self.current_mock_fitness = 5.0 # Starting mock fitness
        self.perturbation_timer = 0
        self.perturbation_interval = random.randint(30, 80) # Perturb every X generations (mock)
        
        # Mock actual particle position for calibration feedback
        self.mock_particle_pos = {"x": 0.0, "y": 0.0, "z": 50.0}
        self.misalignment_level = 0.0 # Simulates drift/miscalibration
        
    def auto_connect(self):
        """Attempt to find a camera."""
        try:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.is_mock = False
                print("[Camera] Connected to Video Device 0.")
                return True
        except Exception as e:
            print(f"[Camera] Connection failed: {e}")
            
        print("[Camera] No camera found. Using Mock Vision.")
        self.is_mock = True
        return False
        
    def get_fitness_score(self):
        """
        Capture an image and analyze levitation stability/quality.
        Returns a float score (Higher is better).
        """
        if self.is_mock:
            # Simulate current best solution's ability to hold the particle near TARGET_POINT
            # Add calibration offset to the particle's "true" position
            simulated_x = TARGET_POINT["x"] + CALIBRATION_OFFSET_X + self.misalignment_level
            simulated_y = TARGET_POINT["y"] + CALIBRATION_OFFSET_Y + self.misalignment_level
            simulated_z = TARGET_POINT["z"] + CALIBRATION_OFFSET_Z
            
            distance_to_target = np.sqrt(
                (simulated_x - TARGET_POINT["x"])**2 +
                (simulated_y - TARGET_POINT["y"])**2 +
                (simulated_z - TARGET_POINT["z"])**2
            )
            
            # Fitness is inversely proportional to distance (closer is better)
            # Add some base fitness and noise
            fitness = max(0.1, 100.0 / (1.0 + distance_to_target) + random.uniform(-2.0, 2.0))
            
            # Simulate external perturbation affecting misalignment
            self.perturbation_timer += 1
            if self.perturbation_timer > self.perturbation_interval:
                self.misalignment_level += random.uniform(-2.0, 2.0) # Random drift
                self.perturbation_timer = 0
                self.perturbation_interval = random.randint(30, 80)
            
            return fitness
            
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

    def get_particle_position(self):
        """Mock method to return observed particle position relative to camera frame."""
        if self.is_mock:
            # Simulate particle position based on target and calibration offset
            # A fixed pattern should ideally result in a fixed observed position
            observed_x = TARGET_POINT["x"] + CALIBRATION_OFFSET_X + self.misalignment_level + random.uniform(-0.5, 0.5)
            observed_y = TARGET_POINT["y"] + CALIBRATION_OFFSET_Y + self.misalignment_level + random.uniform(-0.5, 0.5)
            observed_z = TARGET_POINT["z"] + CALIBRATION_OFFSET_Z + random.uniform(-0.5, 0.5)
            return {"x": observed_x, "y": observed_y, "z": observed_z}
        
        # Real camera logic would involve computer vision for particle tracking
        return {"x": 0.0, "y": 0.0, "z": 0.0} # Placeholder
        

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
            
    def get_highest_fitness_solution(self):
        """Retrieves the solution with the highest recorded fitness."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT target_x, target_y, target_z, best_genome, best_fitness FROM solutions ORDER BY best_fitness DESC LIMIT 1"
            )
            result = cursor.fetchone()
            if result:
                target_point = {"x": result[0], "y": result[1], "z": result[2]}
                best_genome = json.loads(result[3])
                best_fitness = result[4]
                return target_point, best_genome, best_fitness
            return None, None, None

class MetaController:
    def __init__(self):
        self.stagnation_counter = 0
        self.current_mutation_rate = MUTATION_RATE
        self.fitness_history = []
        
    def adapt(self, current_fitness):
        self.fitness_history.append(current_fitness)
        if len(self.fitness_history) > 5:
            self.fitness_history.pop(0)
            
            if max(self.fitness_history) - min(self.fitness_history) < 0.01:
                self.stagnation_counter += 1
            else:
                self.stagnation_counter = 0
                
        if self.stagnation_counter > 3:
            self.current_mutation_rate = min(0.5, self.current_mutation_rate * 1.5)
            self.stagnation_counter = 0
        elif len(self.fitness_history) > 2 and self.fitness_history[-1] > self.fitness_history[-2]:
            self.current_mutation_rate = max(0.01, self.current_mutation_rate * 0.95)
            
        return self.current_mutation_rate

class HypothesisEngine:
    def __init__(self, knowledge_graph_interface):
        self.memory = knowledge_graph_interface

    def generate_hypothesis(self):
        """
        Generates a simple hypothesis based on the knowledge graph.
        Hypothesis: "The highest fitness achieved so far is at this specific target point."
        """
        target_point, genome, fitness = self.memory.get_highest_fitness_solution()
        
        if target_point:
            hypothesis = {
                "type": "optimal_target_point",
                "description": f"Hypothesize that the optimal levitation position is around {target_point}, where a fitness of {fitness:.4f} was achieved.",
                "test_parameters": {
                    "target_point": target_point,
                    "initial_genome": genome # Suggest seeding with this genome
                }
            }
            print(f"[HypothesisEngine] Generated: {hypothesis['description']}")
            return hypothesis
        
        print("[HypothesisEngine] No solutions in knowledge graph to generate hypothesis.")
        return None

class CalibrationModule:
    def __init__(self, serial_interface, camera_interface, memory_interface):
        self.HARDWARE = serial_interface
        self.EYES = camera_interface
        self.MEMORY = memory_interface
        self.calibration_check_timer = 0
        self.reference_fitness = None # Store expected fitness for calibration checks

    async def check_for_miscalibration(self, current_best_fitness):
        """
        Periodically checks for miscalibration by comparing current performance to expected.
        Returns True if miscalibration is suspected.
        """
        global CURRENT_GENERATION, CALIBRATION_CHECK_INTERVAL

        self.calibration_check_timer += 1
        if self.calibration_check_timer < CALIBRATION_CHECK_INTERVAL:
            return False

        self.calibration_check_timer = 0 # Reset timer

        # Load the historically best solution (or a predefined calibration pattern)
        # For simplicity, let's just use the highest fitness solution from memory
        ref_target, ref_genome, ref_fitness = self.MEMORY.get_highest_fitness_solution()

        if ref_target is None:
            print("[Calibration] No reference solution in memory for calibration check.")
            return False

        # Apply the reference solution and get its current fitness
        print(f"[Calibration] Checking for miscalibration with reference target {ref_target}...")
        
        # Temporarily set TARGET_POINT to reference target for physical evaluation
        # This is a simplification; ideally, we'd have a dedicated calibration phase
        original_target_point = dict(TARGET_POINT) # Make a copy
        TARGET_POINT.update(ref_target) 

        # Evaluate the reference genome physically
        self.HARDWARE.send_phases(ref_genome)
        await asyncio.sleep(0.5) # Give hardware time to settle
        observed_fitness = self.EYES.get_fitness_score()
        
        TARGET_POINT.update(original_target_point) # Restore original target

        print(f"[Calibration] Reference Fitness (Expected: {ref_fitness:.4f}, Observed: {observed_fitness:.4f})")

        # If observed fitness is significantly lower than expected, suspect miscalibration
        if observed_fitness < ref_fitness * PERSISTENCE_THRESHOLD:
            print("[Calibration] MISCALIBRATION DETECTED!")
            return True
        
        print("[Calibration] No miscalibration detected.")
        return False

    async def perform_calibration(self):
        """
        Executes an automated calibration routine.
        For now, this will be a mock adjustment of global offsets.
        """
        global CALIBRATION_OFFSET_X, CALIBRATION_OFFSET_Y, CALIBRATION_OFFSET_Z
        print("[Calibration] Performing automated calibration routine...")

        # 1. Send a known, simple pattern to the hardware (e.g., all zeros phase for a flat field)
        flat_field_genome = [0.0] * NUM_EMITTERS
        self.HARDWARE.send_phases(flat_field_genome)
        await asyncio.sleep(1.0) # Wait for physical response

        # 2. Observe the physical response (e.g., where the particle actually is)
        observed_pos = self.EYES.get_particle_position()
        
        # Expected position for a flat field (this needs to be defined based on hardware setup)
        # For mock: assume it should be at (0,0,50) when no actual pattern is applied, but with some inherent offset
        expected_pos_flat_field = {"x": 0.0, "y": 0.0, "z": 50.0} 

        # 3. Calculate discrepancy and adjust global calibration offsets
        CALIBRATION_OFFSET_X = expected_pos_flat_field["x"] - observed_pos["x"]
        CALIBRATION_OFFSET_Y = expected_pos_flat_field["y"] - observed_pos["y"]
        CALIBRATION_OFFSET_Z = expected_pos_flat_field["z"] - observed_pos["z"] # Not yet used in fitness mock

        print(f"[Calibration] Adjusted offsets: X={CALIBRATION_OFFSET_X:.4f}, Y={CALIBRATION_OFFSET_Y:.4f}")
        print("[Calibration] Calibration complete.")
        # Reset misalignment for mock camera interface after calibration
        self.EYES.misalignment_level = 0.0


# Instantiate Global Objects
HARDWARE = SerialInterface()
EYES = CameraInterface()
MEMORY = KnowledgeGraphInterface()
META = MetaController()
HYPOTHESIS = HypothesisEngine(MEMORY) 
CALIBRATION = CalibrationModule(HARDWARE, EYES, MEMORY) # New instance

def init_population():
    pop = []
    for _ in range(POPULATION_SIZE):
        genome = [random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)]
        pop.append(genome)
    return pop

async def evaluate_genome_physically(genome):
    HARDWARE.send_phases(genome)
    await asyncio.sleep(0.05)
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
        "mutation_rate": mutation_rate
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
    global CURRENT_GENERATION, POPULATION, BEST_FITNESS_HISTORY, TARGET_POINT
    global CALIBRATION_OFFSET_X, CALIBRATION_OFFSET_Y, CALIBRATION_OFFSET_Z
    
    HARDWARE.auto_connect()
    EYES.auto_connect()
    
    print("Starting Self-Correcting Lab Coordinator (Cycle 417)...")
    server = await websockets.serve(handler, "localhost", 8765)
    
    POPULATION = init_population()
    CURRENT_GENERATION = 0
    BEST_FITNESS_HISTORY = []

    # Initial seeding from Knowledge Graph
    loaded_genome, loaded_fitness = MEMORY.load_best_solution(TARGET_POINT)
    if loaded_genome and loaded_fitness is not None:
        POPULATION[0] = loaded_genome
        BEST_FITNESS_HISTORY.append(loaded_fitness)
        print(f"[KnowledgeGraph] Seeded GA. Fitness: {loaded_fitness:.4f}")
    
    while True:
        # Periodically check for miscalibration
        if await CALIBRATION.check_for_miscalibration(BEST_FITNESS_HISTORY[-1] if BEST_FITNESS_HISTORY else 0):
            await CALIBRATION.perform_calibration()
            # After calibration, restart the GA cycle to re-optimize with new offsets
            POPULATION = init_population()
            # Potentially re-load solution for current target to re-seed after calibration
            loaded_genome, loaded_fitness = MEMORY.load_best_solution(TARGET_POINT)
            if loaded_genome and loaded_fitness is not None:
                POPULATION[0] = loaded_genome
                BEST_FITNESS_HISTORY = [loaded_fitness]
            else:
                BEST_FITNESS_HISTORY = []
            CURRENT_GENERATION = 0 # Reset generation counter for new optimization cycle
            META.current_mutation_rate = MUTATION_RATE # Reset meta-controller
            print("[Calibration] Recalibration complete. Resuming optimization.")
            continue # Skip remaining GA logic for this iteration, start fresh
        
        # Generate Hypothesis
        if CURRENT_GENERATION % (GENERATIONS_PER_CYCLE * 2) == 0 and CURRENT_GENERATION > 0: # Periodically generate hypothesis
            hypothesis = HYPOTHESIS.generate_hypothesis()
            if hypothesis and hypothesis["type"] == "optimal_target_point":
                print(f"[SCIENTIST] Testing hypothesis: {hypothesis['description']}")
                TARGET_POINT = hypothesis["test_parameters"]["target_point"]
                POPULATION = init_population() # Reset population to test new target effectively
                if hypothesis["test_parameters"]["initial_genome"]:
                    POPULATION[0] = hypothesis["test_parameters"]["initial_genome"]
                # Clear history and re-initialize mock fitness for the new target
                BEST_FITNESS_HISTORY = [hypothesis["test_parameters"]["best_fitness"]]
                EYES.current_mock_fitness = hypothesis["test_parameters"]["best_fitness"] or 5.0 # Reset mock fitness
                EYES.perturbation_timer = 0 # Reset perturbation timer
                CURRENT_GENERATION = 0 # Reset generation counter for new optimization cycle
                META.current_mutation_rate = MUTATION_RATE # Reset meta-controller
                print(f"[SCIENTIST] Switched TARGET_POINT to {TARGET_POINT} and seeded GA.")
                continue # Skip remaining GA logic for this iteration, start fresh

        print(f"\n--- Cycle {CURRENT_GENERATION // GENERATIONS_PER_CYCLE + 1} ---")
        
        for gen in range(GENERATIONS_PER_CYCLE):
            CURRENT_GENERATION += 1
            
            TARGET_POINT["x"] += TARGET_VELOCITY["x"]
            TARGET_POINT["y"] += TARGET_VELOCITY["y"]
            TARGET_POINT["z"] += TARGET_VELOCITY["z"]
            
            scored_pop = await evaluate_generation_physically(POPULATION)
            
            best_fitness_in_gen = max(p[1] for p in scored_pop)
            current_mr = META.adapt(best_fitness_in_gen)
            
            POPULATION, best_genome, best_fitness = evolve(scored_pop, current_mr)
            
            await broadcast_ga_status(CURRENT_GENERATION, best_fitness, np.array(best_genome).tolist(), current_mr)
            
            MEMORY.save_solution(TARGET_POINT, CURRENT_GENERATION, best_fitness, best_genome)
            
            BEST_FITNESS_HISTORY.append(best_fitness)
            if len(BEST_FITNESS_HISTORY) > FITNESS_HISTORY_LENGTH:
                BEST_FITNESS_HISTORY.pop(0)
                recent_peak = max(BEST_FITNESS_HISTORY)
                if best_fitness < recent_peak * PERSISTENCE_THRESHOLD:
                    print(f"[PERTURBATION] Fitness dropped. Resetting strategy.")
                    POPULATION = init_population()
                    POPULATION[0] = best_genome
                    META.current_mutation_rate = 0.5
            
    print("Stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
