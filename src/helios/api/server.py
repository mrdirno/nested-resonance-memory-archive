"""
HELIOS Bridge API (Gate 5.1)
A simple REST endpoint to expose the Fabricator to the outside world.
Gate 5.1 Compliant.
"""

import os
from flask import Flask, request, jsonify
from src.helios.fabricator import Fabricator

app = Flask(__name__)

# Global Fabricator instance (default to virtual for safety)
fabricator = Fabricator(virtual=True)

@app.route('/status', methods=['GET'])
def status():
    """Returns the current status of the hardware."""
    if fabricator.array.connected:
        return jsonify({"status": "online", "mode": "virtual" if isinstance(fabricator.array, type(fabricator.array)) else "physical"})
    else:
        return jsonify({"status": "offline"})

@app.route('/connect', methods=['POST'])
def connect():
    """Connects to the hardware."""
    data = request.json or {}
    port = data.get('port')
    
    # If port is provided, try to switch to physical
    if port:
        # Re-init as physical if needed, simplified logic here
        pass 
        
    success = fabricator.connect()
    return jsonify({"success": success})

@app.route('/materialize', methods=['POST'])
def materialize():
    """
    Compiles and materializes a shape.
    Payload: {"mesh_path": "path/to/file.obj", "duration": 5}
    """
    data = request.json
    mesh_path = data.get('mesh_path')
    duration = data.get('duration', 5)
    
    if not mesh_path or not os.path.exists(mesh_path):
        return jsonify({"error": "Invalid mesh path"}), 400
        
    try:
        fabricator.materialize(mesh_path, duration=duration)
        return jsonify({"status": "complete"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
