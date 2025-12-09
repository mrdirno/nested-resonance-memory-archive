import moderngl
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QTimer
import struct

class HeliosViewport(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ctx = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16) # ~60 FPS
        
        self.clear_color = (0.1, 0.1, 0.12, 1.0) # Dark Slate Blue tint

    def initializeGL(self):
        """Called once when the window is created."""
        try:
            # Create ModernGL context from existing Qt context
            self.ctx = moderngl.create_context()
            print(f"ModernGL Context Created: {self.ctx.info['GL_RENDERER']}")
        except Exception as e:
            print(f"Failed to initialize ModernGL: {e}")
            return

    def paintGL(self):
        """Called every frame."""
        if not self.ctx:
            return

        # Clear screen
        self.ctx.screen.use()
        self.ctx.clear(*self.clear_color)
        
        # TODO: Render Scene

    def resizeGL(self, w, h):
        """Called on resize."""
        if self.ctx:
            self.ctx.viewport = (0, 0, w, h)
            
    def set_clear_color(self, r, g, b, a=1.0):
        self.clear_color = (r, g, b, a)
