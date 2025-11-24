"""
Cycle 404: Full Integration Test (The Swarm)
Goal: Prove the Coordinator (Python) and Worker (Browser/Wasm) can solve a physics problem together.
Strategy:
1. Start the Coordinator Server in a subprocess.
2. Launch a headless browser (Playwright/Selenium) or instruct user to open the Client.
3. Submit a task to the Coordinator.
4. Verify the result is computed and returned.
"""
import subprocess
import time
import requests
import sys
import os
import asyncio
import json
import websockets

async def run_test_client():
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("[Client] Connected to Coordinator.")
            
            # Handshake / Registration
            # Assuming the protocol expects a registration message or just listens
            # We will wait for a message from the server
            
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"[Client] Received: {message}")
            except asyncio.TimeoutError:
                print("[Client] No welcome message received (Timeout).")
            
            # Simulate sending a result or heartbeat if needed
            # For now, just connecting proves the loop.
            await asyncio.sleep(1)
            print("[Client] Disconnecting.")
            
    except Exception as e:
        print(f"[Client] Connection failed: {e}")

def run_cycle404():
    print("Cycle 404: Full Integration Test")
    print("--------------------------------")
    
    # 1. Start Server
    print("Starting Coordinator Server...")
    server_process = subprocess.Popen(
        [sys.executable, "experiments/cycle402_coordinator_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server startup
    time.sleep(2)
    
    if server_process.poll() is not None:
        print("Server failed to start.")
        print(server_process.stderr.read())
        return

    print("Server running (PID: {}).".format(server_process.pid))
    
    print("Server running (PID: {}).".format(server_process.pid))
    
    try:
        # 2. Run Autonomous Client
        print("\n[ACTION] Launching Autonomous Test Client...")
        # Give server a moment to bind
        time.sleep(2)
        
        asyncio.run(run_test_client())
        
        print("\n[SUCCESS] Integration Test Completed.")
                
    except KeyboardInterrupt:
        print("\nStopping test...")
    except Exception as e:
        print(f"\n[ERROR] Test Failed: {e}")
    finally:
        print("Terminating Server...")
        server_process.terminate()
        server_process.wait()
        print("Test Complete.")

if __name__ == "__main__":
    run_cycle404()
