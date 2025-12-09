from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QDockWidget, QFileDialog
from PySide6.QtCore import Qt, QThread, Signal
from src.render.viewport import HeliosViewport
from src.render.mesh import Mesh
from src.ui.controls import ControlPanel
from src.ui.video_player import VideoPlayer
from src.core.reconstruction import VoxelReconstructor

class ReconstructionWorker(QThread):
    finished = Signal(object, object, object) # verts, norms, faces
    
    def __init__(self, seg_engine, recon_engine):
        super().__init__()
        self.seg_engine = seg_engine
        self.recon_engine = recon_engine
        
    def run(self):
        # 1. Get Masks
        masks = self.seg_engine.propagate_all()
        if masks is None:
            print("Reconstruction Aborted: No Masks")
            return
            
        # 2. Carve Voxels
        voxels = self.recon_engine.project_and_carve(masks)
        
        # 3. Extract Mesh
        verts, norms, faces = self.recon_engine.extract_mesh(voxels)
        
        self.finished.emit(verts, norms, faces)

class HeliosMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Helios 3D Engine - v0.3.0 (The Reconstructor)")
        self.resize(1600, 900)
        
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

        # Controls Dock (Right)
        self.dock_controls = QDockWidget("Controls", self)
        self.dock_controls.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        self.controls = ControlPanel()
        self.dock_controls.setWidget(self.controls)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_controls)
        
        # Reference Dock (Left)
        self.dock_reference = QDockWidget("Reference", self)
        self.dock_reference.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.video_player = VideoPlayer()
        self.dock_reference.setWidget(self.video_player)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_reference)
        
        # Engines
        self.recon_engine = VoxelReconstructor(resolution=128) # Higher res for production
        
        # Connect Signals
        self.controls.params_changed.connect(self.viewport.update_mesh_params)
        self.controls.export_requested.connect(self.export_mesh)
        self.video_player.reconstruction_requested.connect(self.start_reconstruction)
        self.viewport.status_message.connect(self.status_label.setText)

    def start_reconstruction(self):
        self.status_label.setText("Starting Reconstruction Pipeline (This may take a moment)...")
        self.recon_worker = ReconstructionWorker(self.video_player.seg_engine, self.recon_engine)
        self.recon_worker.finished.connect(self.on_reconstruction_done)
        self.recon_worker.start()

    def on_reconstruction_done(self, verts, norms, faces):
        if verts is None:
            self.status_label.setText("Reconstruction Failed.")
            return
            
        self.status_label.setText(f"Reconstruction Complete: {len(faces)} faces.")
        
        # Update Viewport
        # We need to manually update the mesh in viewport
        # Viewport usually expects this from its own worker, but we can inject it.
        
        # Release old
        if self.viewport.mesh:
            self.viewport.mesh.vbo.release()
            self.viewport.mesh.ibo.release()
            self.viewport.mesh.vao.release()
            
        self.viewport.mesh = Mesh(self.viewport.ctx, verts, norms, faces)
        self.viewport.current_geometry = (verts, norms, faces) # For export
        self.viewport.update()

    def export_mesh(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export STL", "helios_export.stl", "Stereolithography (*.stl)")
        if filename:
            self.status_label.setText(f"Saving to {filename}...")
            success = self.viewport.save_mesh(filename)
            if success:
                self.status_label.setText(f"Saved: {filename}")
            else:
                self.status_label.setText("Export Failed: No Geometry")
