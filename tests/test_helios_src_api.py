
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
