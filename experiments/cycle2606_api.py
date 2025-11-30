#!/usr/bin/env python3
"""
Experiment: Cycle 2606 - The API
Goal: Implement a lightweight JSON REST API using http.server to expose Hive state.
"""

import http.server
import socketserver
import json
import sys
import threading
import time
import random
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Reuse Hive Logic
sys.path.append(str(Path(__file__).parent))
try:
    from cycle2602_hive import Vector2, HiveAgent
    from cycle2600_protocol import AgentMessage, MessageType
except ImportError:
    sys.exit(1)

# Global Shared State (Simulated Database)
class SharedState:
    def __init__(self):
        self.agents = [HiveAgent(f"drone_{i}", Vector2(random.uniform(0, 100), random.uniform(0, 100))) for i in range(5)]
        self.target = Vector2(50.0, 50.0)
        self.lock = threading.Lock()

    def update(self):
        """Advance simulation one step."""
        with self.lock:
            broadcasts = []
            for agent in self.agents:
                msg = agent.update(self.target)
                if msg: broadcasts.append(msg)
            
            for msg in broadcasts:
                for agent in self.agents:
                    agent.receive_message(msg)

    def get_snapshot(self):
        """Return JSON-serializable state."""
        with self.lock:
            return {
                "timestamp": time.time(),
                "target": {"x": self.target.x, "y": self.target.y},
                "agents": [
                    {
                        "id": a.agent_id,
                        "x": a.position.x,
                        "y": a.position.y,
                        "knowing": bool(a.known_target)
                    } for a in self.agents
                ]
            }

    def set_target(self, x, y):
        with self.lock:
            self.target = Vector2(x, y)
            # Reset agent knowledge to simulate re-tasking
            for a in self.agents:
                a.known_target = None

STATE = SharedState()

class ApiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            data = STATE.get_snapshot()
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return
            
        elif parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"HELIOS-ONE Hive API Online. Endpoints: /status, /target (POST)")
            return

        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/target':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                x = float(data.get('x', 0))
                y = float(data.get('y', 0))
                
                STATE.set_target(x, y)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "new_target": {"x": x, "y": y}}).encode('utf-8'))
                
            except ValueError:
                self.send_error(400, "Invalid JSON or coordinates")
            return
            
        self.send_error(404)

    def log_message(self, format, *args):
        return # Silence console logging

def run_simulation_loop():
    """Background thread to keep the simulation alive."""
    while True:
        STATE.update()
        time.sleep(0.1)

def main():
    port = 8081
    print(f"Cycle 2606: The API - Starting server on port {port}...")
    
    # Start Sim Thread
    sim_thread = threading.Thread(target=run_simulation_loop, daemon=True)
    sim_thread.start()
    
    # Start HTTP Server
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('', port), ApiHandler) as httpd:
        print("Server running. Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server.")

if __name__ == "__main__":
    main()
