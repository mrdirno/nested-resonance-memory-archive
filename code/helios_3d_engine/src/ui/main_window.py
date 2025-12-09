from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from src.render.viewport import HeliosViewport

class HeliosMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Helios 3D Engine - v0.0.1")
        self.resize(1280, 800)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 3D Viewport
        self.viewport = HeliosViewport()
        layout.addWidget(self.viewport, 1) # Stretch factor 1
        
        # Status Bar
        self.status_label = QLabel("System Ready. GPU: Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("background-color: #222; color: #888; padding: 5px;")
        layout.addWidget(self.status_label, 0)

        # Connect viewport signal if needed
        # self.viewport.initialized.connect(self.on_gpu_ready)
        
    def on_gpu_ready(self, info):
        self.status_label.setText(f"GPU Ready: {info}")
