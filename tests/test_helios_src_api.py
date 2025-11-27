
import sys
import os
import pytest
import json
import io

# Add root to path
sys.path.append(os.getcwd())

# We need to mock the socketio run or ensure it doesn't block import
# server.py executes code at module level (rf_thread.start), which is fine.
# But we want to verify the app logic.

from src.helios.api.server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Use a temp dir for uploads in tests
    app.config['UPLOAD_FOLDER'] = '/tmp/helios_uploads_test'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.test_client() as client:
        yield client

def test_api_upload_file(client):
    """Verify uploading a .obj file."""
    data = {
        'file': (io.BytesIO(b'v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3'), 'test_triangle.obj')
    }
    
    # Note: Flask test client handles multipart boundary automatically
    # when data contains file objects. Do NOT set content_type manually string.
    response = client.post('/upload', data=data)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert "saved" in data["message"]
    assert data["filename"] == "test_triangle.obj"
    assert os.path.exists(data["path"])

def test_api_upload_no_file(client):
    """Verify handling of request with no file."""
    response = client.post('/upload', data={})
    assert response.status_code == 400

def test_api_upload_invalid_extension(client):
    """Verify rejection of non-obj files."""
    data = {
        'file': (io.BytesIO(b'evil script'), 'evil.exe')
    }
    response = client.post('/upload', data=data)
    assert response.status_code == 400

def test_api_materialize(client, monkeypatch):
    """Verify materialization triggers compilation and emission."""
    # Mock fabricator.compiler.compile_object to return a dummy instruction set
    # We need to patch the 'fabricator' instance in src.helios.api.server
    
    # Mock emission
    mock_emit = []
    def _mock_emit(event, data):
        mock_emit.append((event, data))
        
    import src.helios.api.server as server_module
    monkeypatch.setattr(server_module.socketio, 'emit', _mock_emit)
    
    # Mock fabricator.compiler.compile_object
    # The fabricator is global in server.py
    # We can mock the method on the instance
    
    def _mock_compile(mesh_path, material="AIR_STP"):
        return {
            "emitters": [{"id": 0, "phase": 1.57}],
            "traps": [[0.5, 0.5, 0.5]]
        }
        
    monkeypatch.setattr(server_module.fabricator.compiler, 'compile_object', _mock_compile)
    # Also mock materialize to avoid blocking sleep
    monkeypatch.setattr(server_module.fabricator, 'materialize', lambda m, duration: None)

    # Create a dummy file to pass validation
    with open(os.path.join(server_module.app.config['UPLOAD_FOLDER'], "test.obj"), "w") as f:
        f.write("dummy")

    payload = {"mesh_path": os.path.join(server_module.app.config['UPLOAD_FOLDER'], "test.obj"), "duration": 1}
    response = client.post('/materialize', 
                          data=json.dumps(payload),
                          content_type='application/json')
                          
    assert response.status_code == 200
    
    # Verify emit
    found_field_update = False
    for event, data in mock_emit:
        if event == 'field_update':
            found_field_update = True
            assert 'phases' in data
            assert 'traps' in data
            assert len(data['traps']) == 1
            break
    assert found_field_update

def test_api_video_feed(client):
    """Verify the video feed endpoint returns a multipart stream."""
    response = client.get('/video_feed')
    assert response.status_code == 200
    assert 'multipart/x-mixed-replace' in response.content_type
    # We can't easily check content without consuming the stream, 
    # but status and header confirm the route works.
