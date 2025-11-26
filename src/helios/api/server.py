"""
HELIOS Bridge API (Gate 5.1)
A simple REST endpoint to expose the Fabricator to the outside world.
Gate 5.1 Compliant.
"""

import os
import threading
import time
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("Loading modules...")
try:
    from flask import Flask, request, jsonify, render_template
    from flask_socketio import SocketIO, emit
    from src.helios.fabricator import Fabricator
    from src.helios.sdr_bridge import SDRInterface
    print("Modules loaded successfully.")
except Exception as e:
    print(f"IMPORT ERROR: {e}")
    exit(1)

app = Flask(__name__, template_folder="../ui/templates", static_folder="../ui/static")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global Instances
try:
    fabricator = Fabricator(virtual=True)
    sdr = SDRInterface()
    sdr.connect()
except Exception as e:
    print(f"INIT ERROR: {e}")

# Background RF Streamer
def rf_stream():
    while True:
        if sdr.connected:
            psd = sdr.get_psd()
            try:
                socketio.emit('rf_update', {'psd': psd, 'center_freq': sdr.center_freq})
            except Exception as e:
                pass
        time.sleep(0.1) # 10Hz update rate

rf_thread = threading.Thread(target=rf_stream)
rf_thread.daemon = True
rf_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    """Returns the current status of the hardware."""
    hw_status = "online" if fabricator.array.connected else "offline"
    hw_mode = "virtual" if isinstance(fabricator.array, type(fabricator.array)) else "physical"
    sdr_mode = "virtual" if sdr.virtual else "physical"
    
    return jsonify({
        "status": hw_status,
        "mode": hw_mode,
        "sdr": sdr_mode,
        "freq": sdr.center_freq
    })

@app.route('/tune', methods=['POST'])
def tune():
    """Tunes the SDR to a new center frequency."""
    data = request.json
    freq = data.get('freq')
    if freq and not sdr.virtual:
        try:
            sdr.sdr.center_freq = float(freq)
            sdr.center_freq = float(freq)
            return jsonify({"status": "tuned", "freq": freq})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"status": "virtual_mode_or_invalid"}), 200

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
        # Compile first to get instruction set
        instruction_set = fabricator.compiler.compile_object(mesh_path)
        
        if instruction_set:
            # Extract phases
            num_emitters = len(instruction_set['emitters'])
            phases = [0.0] * num_emitters
            for emitter in instruction_set['emitters']:
                phases[emitter['id']] = emitter['phase']
            
            # Emit to frontend (Gate 5.3)
            socketio.emit('phase_update', {'phases': phases})
            
            # Now run the physical loop (blocking)
            fabricator.materialize(mesh_path, duration=duration)
            
            return jsonify({"status": "complete"})
        else:
             return jsonify({"error": "Compilation failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("SERVER STARTING ON PORT 5001...", flush=True)
    try:
        # Re-enable socketio.run with explicit threading mode
        socketio.run(app, host='127.0.0.1', port=5001, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"SERVER CRASHED: {e}", flush=True)
