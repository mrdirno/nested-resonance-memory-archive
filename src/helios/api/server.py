"""
HELIOS Bridge API (Gate 5.1)
A simple REST endpoint to expose the Fabricator to the outside world.
Gate 5.1 Compliant.
Updated Cycle 2393: Gate 17 (FPGA Integration)
"""

import os
import threading
import time
import logging
import numpy as np

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("Loading modules...")
try:
    from flask import Flask, request, jsonify, render_template, Response
    from flask_socketio import SocketIO, emit
    from werkzeug.utils import secure_filename
    import cv2
    from src.helios.fabricator import Fabricator
    from src.helios.sdr_bridge import SDRInterface
    from src.fpga.driver import GorkovAccelerator # Gate 17
    print("Modules loaded successfully.")
except Exception as e:
    print(f"IMPORT ERROR: {e}")
    exit(1)

app = Flask(__name__, template_folder="../ui/templates", static_folder="../ui/static")
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'data/models')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ... (Camera Class remains unchanged) ...
class Camera:
    def __init__(self):
        self.cap = None
        self.virtual = False
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open video device")
        except Exception:
            print("Camera not found. Using Virtual Camera.")
            self.virtual = True

    def get_frame(self):
        if not self.virtual and self.cap:
            ret, frame = self.cap.read()
            if ret:
                ret, jpeg = cv2.imencode('.jpg', frame)
                return jpeg.tobytes()
        
        # Virtual Camera (Static Noise or Pattern)
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        t = time.time()
        cx = int(320 + 100 * np.sin(t))
        cy = int(240 + 100 * np.cos(t))
        cv2.circle(img, (cx, cy), 20, (0, 255, 0), -1)
        cv2.putText(img, "VIRTUAL CAMERA", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()

camera = Camera()

def gen_frames():
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        time.sleep(0.05) # Limit FPS

# Global Instances
try:
    fabricator = Fabricator(virtual=True)
    sdr = SDRInterface()
    sdr.connect()
    
    # Gate 17: Accelerator Initialization
    # Check if we have the LUT for accurate simulation
    lut_path = "FPGA/verilog/src/sine_lut.mem"
    if os.path.exists(lut_path):
        accelerator = GorkovAccelerator(simulation_mode=True, lut_path=lut_path)
    else:
        accelerator = GorkovAccelerator(simulation_mode=True) # Fallback to math.sin
        
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

# ... (Routes /video_feed, /upload, /, /status, /tune, /connect remain similar) ...

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a 3D model file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and file.filename.endswith('.obj'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({
            "status": "success", 
            "message": f"File saved to {filepath}",
            "filename": filename,
            "path": filepath
        })
    else:
        return jsonify({"error": "Invalid file type (only .obj allowed)"}), 400

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    """Returns the current status of the hardware."""
    hw_status = "online" if fabricator.array.connected else "offline"
    hw_mode = "virtual" if isinstance(fabricator.array, type(fabricator.array)) else "physical"
    sdr_mode = "virtual" if sdr.virtual else "physical"
    acc_mode = "simulated" if accelerator.simulation_mode else "hardware"
    
    return jsonify({
        "status": hw_status,
        "mode": hw_mode,
        "sdr": sdr_mode,
        "accelerator": acc_mode,
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
            
            # Emit to frontend (Gate 5.3 + 5.2)
            socketio.emit('field_update', {
                'phases': phases,
                'traps': instruction_set.get('traps', [])
            })
            
            # Now run the physical loop (blocking)
            fabricator.materialize(mesh_path, duration=duration)
            
            return jsonify({"status": "complete"})
        else:
             return jsonify({"error": "Compilation failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/simulate', methods=['POST'])
def simulate():
    """
    Gate 17: Trigger FPGA Simulation (or Hardware Execution).
    Payload: {"phases": [0, 100, ...], "target": [x, y, z]}
    """
    data = request.json
    phases = data.get('phases') # Expecting list of 64 ints (0-1023)
    target = data.get('target') # Expecting [x, y, z]
    
    if not phases or len(phases) != 64:
        return jsonify({"error": "Invalid phases. Must be list of 64."} ), 400
    
    if not target or len(target) != 3:
        target = [0, 0, 0] # Default to origin
        
    try:
        accelerator.load_phases(phases)
        accelerator.set_target(target[0], target[1], target[2])
        accelerator.run()
        result = accelerator.read_result()
        
        return jsonify({
            "status": "success",
            "potential": result,
            "mode": "simulation" if accelerator.simulation_mode else "hardware"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("SERVER STARTING ON PORT 5001...", flush=True)
    try:
        # Re-enable socketio.run with explicit threading mode
        socketio.run(app, host='127.0.0.1', port=5001, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"SERVER CRASHED: {e}", flush=True)