"""
Cycle 402: The Coordinator Server
Role: The Central Nervous System of the Autopoietic Lab.
Responsibility: Manages global state, distributing compute shards to workers (browsers), and aggregating results.
Technology: Python + WebSockets (FastAPI/Uvicorn proxy logic for prototype).
"""
import asyncio
import websockets
import json
import time
import random
import numpy as np

# Global State
CONNECTED_WORKERS = set()
GLOBAL_POTENTIAL = {} # Voxel -> Potential
TASK_QUEUE = asyncio.Queue()

# Simulation Parameters
BOX_DIM = 100.0
RESOLUTION = 4.0 # mm
GRID_SIZE = int(BOX_DIM / RESOLUTION)

async def register(websocket):
    CONNECTED_WORKERS.add(websocket)
    print(f"Worker connected. Total: {len(CONNECTED_WORKERS)}")
    try:
        await websocket.wait_closed()
    finally:
        CONNECTED_WORKERS.remove(websocket)
        print(f"Worker disconnected. Total: {len(CONNECTED_WORKERS)}")

async def distributor():
    """
    Distributes compute tasks to available workers.
    """
    while True:
        if not TASK_QUEUE.empty() and CONNECTED_WORKERS:
            task = await TASK_QUEUE.get()
            worker = random.choice(list(CONNECTED_WORKERS)) # Simple load balancing
            
            payload = json.dumps({
                "type": "compute_task",
                "task_id": task["id"],
                "emitters": task["emitters"],
                "targets": task["targets"]
            })
            
            try:
                await worker.send(payload)
                print(f"Dispatched Task {task['id']} to worker.")
            except:
                print(f"Worker failed. Re-queueing Task {task['id']}.")
                await TASK_QUEUE.put(task)
                
        await asyncio.sleep(0.1)

async def handler(websocket):
    # Register worker
    CONNECTED_WORKERS.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "result":
                # Process Result
                task_id = data["task_id"]
                results = data["results"]
                print(f"Received results for Task {task_id}: {len(results)} points.")
                
                # Aggregate (Mock)
                # In production, we'd sum potentials or update the GA population.
                pass
                
            elif data["type"] == "ready":
                print("Worker ready for tasks.")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_WORKERS.remove(websocket)

async def main():
    print("Starting Autopoietic Coordinator (Cycle 402)...")
    
    # Start Server
    server = await websockets.serve(handler, "localhost", 8765)
    print("WebSocket Server listening on ws://localhost:8765")
    
    # Start Distributor
    asyncio.create_task(distributor())
    
    # Mock Task Generator (to simulate workload)
    async def generate_mock_work():
        task_id = 0
        while True:
            if CONNECTED_WORKERS:
                # Create a dummy task
                task = {
                    "id": task_id,
                    "emitters": [{"x":0, "y":0, "z":0, "phase": 0.0}], # Simplified
                    "targets": [{"x": 50, "y": 50, "z": 50}]
                }
                await TASK_QUEUE.put(task)
                task_id += 1
                if task_id > 5: break # Just a few for the test
            await asyncio.sleep(1)
            
    asyncio.create_task(generate_mock_work())
    
    # Keep alive
    await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")
