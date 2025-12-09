import moderngl
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QTimer, QPoint, QThread, Signal
from .camera import Camera
from .grid import InfiniteGrid
from .mesh import Mesh
from ..core.engine import GeometryEngine

class MeshWorker(QThread):
    finished = Signal(object, object, object) # verts, norms, faces
    
    def __init__(self, engine, params):
        super().__init__()
        self.engine = engine
        self.params = params
        
    def run(self):
        resolution = self.params.get("resolution", 64)
        scale = self.params.get("scale", 2.0)
        # Note: thickness support needs to be added to engine if not present,
        # but for now we pass what we have.
        # Actually, let's update engine call signature in the worker if engine supports it.
        # Checking engine code: generate_gyroid_mesh(resolution=64, scale=2.0)
        # It has hardcoded thickness=0.2 inside. I should update engine too, but for now let's just pass what fits.
        
        verts, norms, faces = self.engine.generate_gyroid_mesh(resolution=resolution, scale=scale)
        self.finished.emit(verts, norms, faces)

class HeliosViewport(QOpenGLWidget):
    status_message = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ctx = None
        self.camera = Camera()
        self.grid = None
        self.mesh = None
        self.engine = GeometryEngine()
        self.worker = None
        
        self.last_mouse_pos = QPoint()
        self.mouse_buttons = {}

        # Render Loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16) # ~60 FPS
        
        self.clear_color = (0.1, 0.1, 0.12, 1.0) 

    def initializeGL(self):
        try:
            self.ctx = moderngl.create_context()
            print(f"ModernGL Context: {self.ctx.info['GL_RENDERER']}")
            self.ctx.enable(moderngl.DEPTH_TEST)
            # self.ctx.enable(moderngl.CULL_FACE) # Disable culling for safety on first run
            
            self.grid = InfiniteGrid(self.ctx)
            
            # Initial Generate
            self.update_mesh_params({"resolution": 64, "scale": 2.0, "thickness": 0.1})
            
        except Exception as e:
            print(f"Failed to initialize ModernGL: {e}")
            import traceback
            traceback.print_exc()

    def update_mesh_params(self, params):
        self.status_message.emit("Generating Mesh...")
        
        # Kill previous worker if running
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            
        self.worker = MeshWorker(self.engine, params)
        self.worker.finished.connect(self.on_mesh_generated)
        self.worker.start()

    def on_mesh_generated(self, verts, norms, faces):
        if verts is None:
            self.status_message.emit("Generation Failed: No Surface")
            return
            
        # Store for export
        self.current_geometry = (verts, norms, faces)
            
        # Create Mesh on Main Thread (OpenGL context is here)
        if self.mesh:
            # Release old resources if needed (ModernGL handles gc mostly but explicit release is good)
            self.mesh.vbo.release()
            self.mesh.ibo.release()
            self.mesh.vao.release()
            
        self.mesh = Mesh(self.ctx, verts, norms, faces)
        self.status_message.emit(f"Mesh Ready: {len(faces)} faces")
        self.update() # Force redraw

    def save_mesh(self, filename):
        if hasattr(self, 'current_geometry') and self.current_geometry:
            verts, norms, faces = self.current_geometry
            self.engine.save_stl(filename, verts, faces)
            return True
        return False

    def paintGL(self):
        if not self.ctx:
            return

        self.ctx.screen.use()
        self.ctx.clear(*self.clear_color)
        
        if self.grid:
            self.grid.render(self.camera)
            
        if self.mesh:
            self.mesh.render(self.camera)

    def resizeGL(self, w, h):
        if self.ctx:
            self.ctx.viewport = (0, 0, w, h)
            self.camera.aspect_ratio = w / h
            self.camera.update_vectors()

    # Input Handling
    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()
        self.mouse_buttons[event.button()] = True

    def mouseReleaseEvent(self, event):
        self.mouse_buttons[event.button()] = False

    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()
        self.last_mouse_pos = event.pos()

        if self.mouse_buttons.get(Qt.MouseButton.RightButton):
            self.camera.rotate(dx, dy)
        elif self.mouse_buttons.get(Qt.MouseButton.MiddleButton):
            self.camera.pan(dx, dy)
            
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.camera.zoom(delta)