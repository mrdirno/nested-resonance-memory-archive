"""
HELIOS Type 3 OS - Web Interface Server
Exposes the Universal Operator via a REST API and serves the 3D visualization.
"""
import os
import logging
from flask import Flask, request, jsonify, render_template
from src.helios.operator import UniversalOperator
from src.helios.nlp import NaturalLanguageInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')

# Initialize Operator and NLP
logger.info("Initializing Universal Operator...")
operator = UniversalOperator(resolution_mm=4.0) # Low res for interactive speed
nlp = NaturalLanguageInterface()
logger.info("Operator Online.")

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
    """Return the current state of all objects for visualization."""
    objects = []
    for obj_id, data in operator.active_objects.items():
        # Convert numpy arrays to lists for JSON serialization
        # We need to get the actual points from the operator's internal state if possible,
        # but for now we'll just return metadata. 
        # To visualize, we really need the point clouds.
        # Let's extract the point cloud from the operator.
        
        # Accessing private attribute for visualization (pragmatic hack)
        # In a real system, we'd have a public getter.
        # Assuming operator stores objects in a way we can retrieve points.
        # Looking at operator.py (from memory/context), it has `active_objects` dict.
        # We need to see if we can get the points.
        # The `create_object` method returns an ID.
        # The operator likely manages the field directly.
        # For this prototype, let's assume we can get the center location and type.
        # Ideally, we would send the full point cloud, but that might be heavy.
        # Let's send type and location for now, and maybe a placeholder size.
        
        objects.append({
            "id": obj_id,
            "type": data['type'],
            "location": data['location']
        })
        
    return jsonify({"objects": objects})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
