import asyncio
import websockets
import json
import random

async def run_worker():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("[MockWorker] Connected.")
        await websocket.send(json.dumps({"type": "ready"}))
        
        try:
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "compute_task":
                    # print(f"[MockWorker] Received Task {data['task_id']}")
                    
                    # Simulate Compute
                    # Return a random fitness or one based on phase coherence
                    # For testing, just random
                    fitness = random.uniform(0, 100)
                    
                    result = {
                        "type": "result",
                        "task_id": data["task_id"],
                        "results": [{"u": fitness}]
                    }
                    await websocket.send(json.dumps(result))
        except websockets.exceptions.ConnectionClosed:
            print("[MockWorker] Connection Closed.")

if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        pass
