import moderngl
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QTimer, QPoint
from .camera import Camera
from .grid import InfiniteGrid

class HeliosViewport(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ctx = None
        self.camera = Camera()
        self.grid = None
        
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
            
            self.grid = InfiniteGrid(self.ctx)
            
        except Exception as e:
            print(f"Failed to initialize ModernGL: {e}")

    def paintGL(self):
        if not self.ctx:
            return

        self.ctx.screen.use()
        self.ctx.clear(*self.clear_color)
        self.ctx.enable(moderngl.DEPTH_TEST)
        
        if self.grid:
            self.grid.render(self.camera)

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