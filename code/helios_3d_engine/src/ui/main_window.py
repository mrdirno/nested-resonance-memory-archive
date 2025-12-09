from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QDockWidget, QFileDialog
from PySide6.QtCore import Qt
from src.render.viewport import HeliosViewport
from src.ui.controls import ControlPanel

class HeliosMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Helios 3D Engine - v0.1.0 (Sunfire)")
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
        self.status_label = QLabel("System Ready.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("background-color: #222; color: #888; padding: 5px;")
        layout.addWidget(self.status_label, 0)

        # Controls Dock
        self.dock_controls = QDockWidget("Controls", self)
        self.dock_controls.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        self.controls = ControlPanel()
        self.dock_controls.setWidget(self.controls)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_controls)
        
        # Connect Signals
        self.controls.params_changed.connect(self.viewport.update_mesh_params)
        self.controls.export_requested.connect(self.export_mesh)
        self.viewport.status_message.connect(self.status_label.setText)

    def export_mesh(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export STL", "helios_export.stl", "Stereolithography (*.stl)")
        if filename:
            self.status_label.setText(f"Saving to {filename}...")
            success = self.viewport.save_mesh(filename)
            if success:
                self.status_label.setText(f"Saved: {filename}")
            else:
                self.status_label.setText("Export Failed: No Geometry")
