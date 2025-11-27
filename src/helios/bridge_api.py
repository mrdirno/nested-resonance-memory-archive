"""
HELIOS Bridge API (Gate 5.1)
Exposes the Fabricator via a Flask REST API.

Principle: PRIN-ACCESSIBILITY
Author: MOG (Cycle 2352)
"""

from flask import Flask, request, jsonify
from src.helios.fabricator import Fabricator
from src.fpga.driver import GorkovAccelerator
import os

app = Flask(__name__)
fab = Fabricator() # Default to Virtual/Mock
# Initialize Accelerator (Simulation Mode for Mac Host)
accel = GorkovAccelerator(simulation_mode=True, lut_path="FPGA/verilog/src/sine_lut.mem")

UPLOAD_FOLDER = "workspace/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/status', methods=['GET'])
def status():
    return jsonify(fab.array.get_status())

@app.route('/fabricate', methods=['POST'])
def fabricate():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Parse options
        material = request.form.get('material', 'AIR_STP')
        duration = int(request.form.get('duration', 5))
        
        # Trigger Fabrication
        try:
            fab.fabricate(filepath, material, duration)
            return jsonify({"status": "success", "message": f"Fabricated {file.filename}"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/simulate', methods=['POST'])
def simulate():
    """
    Trigger FPGA Simulation (Gorkov Potential).
    Input: JSON { "target": [x, y, z], "phases": [p0, p1, ... p63] }
    Output: JSON { "potential": <int> }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
        
    target = data.get('target', [0, 0, 0])
    phases = data.get('phases', [0]*64)
    
    if len(phases) != 64:
        return jsonify({"error": "Phases must be length 64"}), 400
        
    try:
        # Load Data
        accel.load_phases(phases)
        accel.set_target(*target)
        
        # Run Simulation
        accel.run()
        
        # Read Result
        result = accel.read_result()
        
        return jsonify({
            "status": "success",
            "potential": result,
            "mode": "simulation" if accel.simulation_mode else "hardware"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
