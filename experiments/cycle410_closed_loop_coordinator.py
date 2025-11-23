"""
Cycle 410: The Physical Loop (Closed-Loop Optimization)
Role: Autopoietic Coordinator
Responsibility: Close the Brain -> Hands -> Reality -> Eyes -> Brain loop.
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
GENERATIONS = 100
MUTATION_RATE = 0.1
ELITISM_COUNT = 2

# --- Simulation Constants ---
NUM_EMITTERS = 64
TARGET_POINT = {"x": 0, "y": 0, "z": 50}

# --- Global State ---
CONNECTED_WORKERS = set()
TASK_QUEUE = asyncio.Queue()
RESULTS_BUFFER = {}
CURRENT_GENERATION = 0
POPULATION = []
SERIAL_PORT = None

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
        
    def auto_connect(self):
        """Attempt to find a camera."""
        try:
            # Try index 0 (default camera)
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
            # Mock: Return a random score biased towards improvement to simulate learning
            return random.uniform(0, 10) + (CURRENT_GENERATION * 0.1)
            
        if not self.cap or not self.cap.isOpened():
            return 0.0
            
        ret, frame = self.cap.read()
        if not ret:
            return 0.0
            
        # --- Vision Logic ---
        # 1. Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 2. Threshold to find the white particle
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        # 3. Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0.0 # No particle seen
            
        # 4. Score based on stability (e.g., circularity, centrality)
        # Simplified: Largest contour area = Stability
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        return area

# Instantiate Global Hardware
HARDWARE = SerialInterface()
EYES = CameraInterface()

def init_population():
    pop = []
    for _ in range(POPULATION_SIZE):
        genome = [random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)]
        pop.append(genome)
    return pop

async def evaluate_genome_physically(genome):
    """
    Inject a single genome into reality and measure the result.
    This replaces the parallel simulation loop for the physical run.
    """
    # 1. Inject (Hands)
    HARDWARE.send_phases(genome)
    
    # 2. Wait for physics (settling time)
    await asyncio.sleep(0.1) 
    
    # 3. Measure (Eyes)
    fitness = EYES.get_fitness_score()
    
    return fitness

async def evaluate_generation_physically(population):
    """
    Sequentially evaluate the population in the real world.
    NOTE: This is slow (serial execution), but grounded.
    """
    print(f"[GA] Physically Evaluating Gen {CURRENT_GENERATION}...")
    scored_population = []
    
    for i, genome in enumerate(population):
        fitness = await evaluate_genome_physically(genome)
        scored_population.append((genome, fitness))
        # Optional: Broadcast current progress to UI
        
    return scored_population

def evolve(scored_population):
    scored_population.sort(key=lambda x: x[1], reverse=True)
    best_genome = copy.deepcopy(scored_population[0][0])
    best_fitness = scored_population[0][1]
    print(f"[GA] Gen {CURRENT_GENERATION} Best Physical Fitness: {best_fitness:.4f}")
    
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
        "best_genome": best_genome # Already list
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
    global CURRENT_GENERATION, POPULATION
    
    # Init Hardware
    HARDWARE.auto_connect()
    EYES.auto_connect()
    
    print("Starting Autopoietic Coordinator (Cycle 410)...")
    print(f"Hardware: {'REAL' if not HARDWARE.is_mock else 'MOCK'}")
    print(f"Vision:   {'REAL' if not EYES.is_mock else 'MOCK'}")
    
    server = await websockets.serve(handler, "localhost", 8765)
    
    print("[GA] Starting Physical Optimization Loop.")
    
    POPULATION = init_population()
    
    for gen in range(GENERATIONS):
        CURRENT_GENERATION = gen
        
        # Use Physical Evaluation instead of Distributed Simulation
        scored_pop = await evaluate_generation_physically(POPULATION)
        
        POPULATION, best_genome, best_fitness = evolve(scored_pop)
        
        await broadcast_ga_status(CURRENT_GENERATION, best_fitness, np.array(best_genome).tolist())
        
        # No sleep needed here as physical eval takes time
        
    print("[GA] Optimization Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")