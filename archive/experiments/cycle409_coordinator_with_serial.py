"""
Cycle 409: The First Physical Link
Role: Hardware-Aware Coordinator
Responsibility: Extend the GA Coordinator to speak Serial.
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

class SerialInterface:
    def __init__(self):
        self.port = None
        self.is_mock = True
        
    def auto_connect(self):
        """Attempt to find and connect to the FPGA controller."""
        ports = list(serial.tools.list_ports.comports())
        print(f"[Serial] Scanning {len(ports)} ports...")
        
        target_port = None
        # Heuristic: Look for USB Serial devices
        for p in ports:
            if "USB" in p.description or "ACM" in p.device:
                target_port = p.device
                break
                
        if target_port:
            try:
                self.port = serial.Serial(target_port, 115200, timeout=0.1)
                self.is_mock = False
                print(f"[Serial] Connected to {target_port}")
                # Handshake
                self.port.write(b"READY\n")
                return True
            except Exception as e:
                print(f"[Serial] Connection failed: {e}")
        
        print("[Serial] No hardware found. Using Mock Interface.")
        self.is_mock = True
        return False

    def send_phases(self, phases):
        """Send a list of 64 phases (0-2pi) to the hardware."""
        if self.is_mock:
            # Mock Latency
            # print(f"[Serial-Mock] Sent {len(phases)} phases.")
            return
            
        if not self.port or not self.port.is_open:
            return

        # Protocol: Start Byte (0xFF), 64 bytes (0-255 map to 0-2pi), Checksum
        try:
            data = bytearray([0xFF])
            for p in phases:
                # Map 0-2pi to 0-255
                val = int((p / (2 * np.pi)) * 255) % 256
                data.append(val)
            
            # Simple Checksum
            checksum = sum(data[1:]) % 256
            data.append(checksum)
            
            self.port.write(data)
            # print(f"[Serial] Sent frame.")
        except Exception as e:
            print(f"[Serial] Write Error: {e}")

# Instantiate Global Serial Interface
HARDWARE = SerialInterface()

def init_population():
    pop = []
    for _ in range(POPULATION_SIZE):
        genome = [random.uniform(0, 2 * np.pi) for _ in range(NUM_EMITTERS)]
        pop.append(genome)
    return pop

async def evaluate_generation(population):
    global RESULTS_BUFFER
    RESULTS_BUFFER = {}
    
    print(f"[GA] Evaluating Gen {CURRENT_GENERATION}...")
    
    for i, genome in enumerate(population):
        task_id = f"gen{CURRENT_GENERATION}_ind{i}"
        
        emitters_payload = []
        for idx, phase in enumerate(genome):
            row = idx // 8
            col = idx % 8
            emitters_payload.append({
                "x": (col - 3.5) * 10, 
                "y": (row - 3.5) * 10, 
                "z": 0, 
                "phase": phase
            })
            
        task = {
            "id": task_id,
            "emitters": emitters_payload,
            "targets": [TARGET_POINT]
        }
        await TASK_QUEUE.put(task)
        
    start_time = time.time()
    while len(RESULTS_BUFFER) < len(population):
        if time.time() - start_time > 30:
            print("[GA] Timeout.")
            break
        await asyncio.sleep(0.1)
        
    scored_population = []
    for i, genome in enumerate(population):
        task_id = f"gen{CURRENT_GENERATION}_ind{i}"
        fitness = RESULTS_BUFFER.get(task_id, -1000.0)
        scored_population.append((genome, fitness))
        
    return scored_population

def evolve(scored_population):
    scored_population.sort(key=lambda x: x[1], reverse=True)
    best_genome = copy.deepcopy(scored_population[0][0])
    best_fitness = scored_population[0][1]
    print(f"[GA] Gen {CURRENT_GENERATION} Best Fitness: {best_fitness:.4f}")
    
    # --- PHYSICAL INJECTION ---
    # Send the best genome to the hardware immediately
    HARDWARE.send_phases(best_genome)
    # --------------------------
    
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

async def distributor():
    while True:
        if not TASK_QUEUE.empty() and CONNECTED_WORKERS:
            task = await TASK_QUEUE.get()
            worker = random.choice(list(CONNECTED_WORKERS))
            payload = json.dumps({
                "type": "compute_task",
                "task_id": task["id"],
                "emitters": task["emitters"],
                "targets": task["targets"]
            })
            try:
                await worker.send(payload)
            except:
                await TASK_QUEUE.put(task)
        await asyncio.sleep(0.01)

async def handler(websocket):
    CONNECTED_WORKERS.add(websocket)
    print(f"[Server] Worker Connected.")
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "result":
                results = data["results"]
                total_u = sum(r.get("u", 0) for r in results)
                RESULTS_BUFFER[data["task_id"]] = total_u
    except:
        pass
    finally:
        CONNECTED_WORKERS.remove(websocket)

async def main():
    global CURRENT_GENERATION, POPULATION
    
    # Init Hardware
    HARDWARE.auto_connect()
    
    print("Starting Hardware-Aware Coordinator (Cycle 409)...")
    server = await websockets.serve(handler, "localhost", 8765)
    asyncio.create_task(distributor())
    
    print("[GA] Waiting for workers...")
    while not CONNECTED_WORKERS:
        await asyncio.sleep(1)
    
    POPULATION = init_population()
    
    for gen in range(GENERATIONS):
        CURRENT_GENERATION = gen
        scored_pop = await evaluate_generation(POPULATION)
        POPULATION, best_genome, best_fitness = evolve(scored_pop)
        await broadcast_ga_status(CURRENT_GENERATION, best_fitness, np.array(best_genome).tolist())
        await asyncio.sleep(0.1)
        
    print("[GA] Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")