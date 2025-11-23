"""
HELIOS Type 3 OS - Web Interface Server
Exposes the Universal Operator via a REST API and serves the 3D visualization.
Upgraded for Real-Time Streaming (Phase 12).
"""
import os
import logging
import os
import logging
# import eventlet # Disabled due to Python 3.13 compatibility issues
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from src.helios.operator import UniversalOperator
from src.helios.nlp import NaturalLanguageInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'helios_secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize Operator and NLP
logger.info("Initializing Universal Operator...")
operator = UniversalOperator(resolution_mm=4.0) # Low res for interactive speed
nlp = NaturalLanguageInterface()
logger.info("Operator Online.")

# Background Thread for State Updates
def background_thread():
    """Emits the state of the system to all clients at 60Hz."""
    logger.info("Starting Background Stream...")
    while True:
        socketio.sleep(0.016) # ~60 FPS
        
        objects = []
        for obj_id, data in operator.active_objects.items():
            objects.append({
                "id": obj_id,
                "type": data['type'],
                "location": data['location']
            })
            
        # Get Field Slice (Z=50%)
        # Note: This might be heavy. If laggy, reduce frequency or resolution.
        field_slice = operator.get_field_slice(0.5)
            
        socketio.emit('state_update', {
            'objects': objects,
            'field': field_slice
        })

@app.route('/')
def index():
    """Serve the main interface."""
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def execute_command():
    """Execute a natural language command."""
    data = request.json
    command_text = data.get('command')
    
    if not command_text:
        return jsonify({"error": "No command provided"}), 400

    logger.info(f"Received command: {command_text}")
    
    try:
        intent = nlp.parse(command_text)
        action = intent.get('action')
        response_data = {"status": "success", "intent": intent}

        if action == 'create':
            shape = intent['shape']
            loc = intent['location']
            obj_id = operator.create_object(shape, loc)
            response_data["message"] = f"Created {shape} at {loc} (ID: {obj_id})"
            response_data["object_id"] = obj_id
            
        elif action == 'move':
            obj_id = intent['id']
            target = intent['target']
            operator.move_object(obj_id, target)
            response_data["message"] = f"Moved object {obj_id} to {target}"
            
        elif action == 'delete':
            obj_id = intent['id']
            if operator.delete_object(obj_id):
                response_data["message"] = f"Deleted object {obj_id}"
            else:
                response_data["status"] = "error"
                response_data["message"] = f"Object {obj_id} not found"
                
        elif action == 'load':
             filename = intent['filename']
             try:
                 obj_id, count = operator.create_from_file(filename)
                 response_data["message"] = f"Loaded {filename} (ID: {obj_id}, Points: {count})"
                 response_data["object_id"] = obj_id
             except Exception as e:
                 response_data["status"] = "error"
                 response_data["message"] = str(e)
                 
        elif action == 'animate':
            # Handle animation command
            # animate <id> to <mesh> [frames]
            # We need to parse this manually or update NLP
            # For now, let's assume the NLP handles it or we parse it here if 'animate' action exists
            # The current NLP might not support 'animate' yet.
            # Let's add basic support if intent has it.
            if 'target_mesh' in intent:
                obj_id = intent['id']
                mesh = intent['target_mesh']
                frames = intent.get('duration', 10)
                # We need to run this async or it blocks!
                # For now, synchronous is fine for demo
                phases = operator.animate_object(obj_id, mesh, frames)
                response_data["message"] = f"Animation compiled ({len(phases)} frames)."
            else:
                 response_data["message"] = "Animation command parsed but missing parameters."

        elif action == 'status':
             response_data["message"] = f"System Active. {len(operator.active_objects)} objects online."

        elif action == 'unknown':
            response_data["status"] = "error"
            response_data["message"] = f"Unknown command: {command_text}"
            
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/state', methods=['GET'])
def get_state():
    """Return the current state (Legacy Polling Fallback)."""
    objects = []
    for obj_id, data in operator.active_objects.items():
        objects.append({
            "id": obj_id,
            "type": data['type'],
            "location": data['location']
        })
    return jsonify({"objects": objects})

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")
    # Start background thread if not running
    # Note: In production, use a more robust way to ensure single thread
    # For this dev server, it's fine.
    # We'll use a global flag or just start it.
    # socketio.start_background_task(background_thread) is idempotent-ish if we check
    pass

if __name__ == '__main__':
    # Start the background task
    socketio.start_background_task(background_thread)
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
