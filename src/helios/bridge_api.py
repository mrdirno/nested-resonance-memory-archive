"""
HELIOS Bridge API (Gate 5.1)
Exposes the Fabricator via a Flask REST API.

Principle: PRIN-ACCESSIBILITY
Author: MOG (Cycle 2352)
"""

from flask import Flask, request, jsonify
from src.helios.fabricator import Fabricator
import os

app = Flask(__name__)
fab = Fabricator() # Default to Virtual/Mock

UPLOAD_FOLDER = "workspace/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/status', methods=['GET'])
def status():
    return jsonify(fab.driver.get_status())

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
