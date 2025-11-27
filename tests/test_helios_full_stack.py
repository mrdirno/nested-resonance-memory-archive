
import sys
import os
import pytest
import json
import io
import numpy as np

# Add root to path
sys.path.append(os.getcwd())

from src.helios.api.server import app
import src.helios.api.server as server_module

@pytest.fixture
def client(monkeypatch):
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = '/tmp/helios_full_stack_test'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Mock SocketIO to capture emits
    mock_emit_calls = []
    def _mock_emit(event, data):
        mock_emit_calls.append((event, data))
    monkeypatch.setattr(server_module.socketio, 'emit', _mock_emit)
    
    # Inject the mock calls list into app config for retrieval in test
    app.config['MOCK_EMITS'] = mock_emit_calls
    
    # Ensure Fabricator is connected
    server_module.fabricator.connect()
    
    with app.test_client() as client:
        yield client
    
    server_module.fabricator.disconnect()

def test_full_stack_materialization(client):
    """
    Gate 6.1: Verify UI -> API -> Compiler -> Solver -> Fabricator -> Virtual Array pipeline.
    """
    # 1. Upload .obj
    # Minimal cube OBJ
    obj_content = b"""
v 0 0 0
v 1 0 0
v 0 1 0
v 0 0 1
f 1 2 3
"""
    data = {'file': (io.BytesIO(obj_content), 'cube.obj')}
    response = client.post('/upload', data=data)
    assert response.status_code == 200
    upload_resp = json.loads(response.data)
    mesh_path = upload_resp['path']
    
    # 2. Trigger Materialization
    # duration=0.1 to keep test fast
    payload = {"mesh_path": mesh_path, "duration": 0.1}
    response = client.post('/materialize', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 200
    
    # 3. Verify Socket Emission (Visualizer)
    emits = app.config['MOCK_EMITS']
    found_update = False
    for event, data in emits:
        if event == 'field_update':
            found_update = True
            assert 'phases' in data
            assert 'traps' in data
            # We expect *some* phases and traps
            assert len(data['phases']) == 64 # Default 8x8
            # Traps might be empty if threshold is high or solver is weird, 
            # but let's check type at least
            assert isinstance(data['traps'], list)
            break
    assert found_update, "No field_update emitted"
    
    # 4. Verify Fabricator/HAL State (Physical Actuation)
    # The fabricator is global in server_module
    fab = server_module.fabricator
    # Check if VirtualArray received phases
    # VirtualArray.phases is init to zeros. If updated, mean/sum should change (unless all 0).
    # Random/Solved phases are usually not all exactly 0.0
    current_phases = fab.array.phases
    assert np.any(current_phases != 0), "HAL phases were not updated (still zero)"
    
    print("Full Stack Integration Verified.")
