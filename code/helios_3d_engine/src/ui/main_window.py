from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QDockWidget, QFileDialog
from PySide6.QtCore import Qt, QThread, Signal
from src.render.viewport import HeliosViewport
from src.render.mesh import Mesh
from src.ui.controls import ControlPanel
from src.ui.video_player import VideoPlayer
from src.core.reconstruction import VoxelReconstructor
from src.core.ai_generator import AIGenerator

class ReconstructionWorker(QThread):
    finished = Signal(object, object, object) # verts, norms, faces
    
    def __init__(self, seg_engine, recon_engine, ai_engine, params):
        super().__init__()
        self.seg_engine = seg_engine
        self.recon_engine = recon_engine
        self.ai_engine = ai_engine
        self.params = params
        
    def run(self):
        # 1. Get Masks
        masks = self.seg_engine.propagate_all()
        if masks is None:
            print("Reconstruction Aborted: No Masks")
            return
            
        # 2. Carve Voxels
        voxels = self.recon_engine.project_and_carve(masks)
        
        # 3. Gyroid Infusion (Phase 8)
        if self.params.get("infusion_enabled", False):
            print("Infusing Gyroid Structure...")
            scale = self.params.get("infusion_scale", 8.0)
            thick = self.params.get("infusion_thickness", 0.2)
            voxels = self.ai_engine.boolean_intersection(voxels, scale, thick)
        
        # 4. Extract Mesh
        verts, norms, faces = self.recon_engine.extract_mesh(voxels)
        
        self.finished.emit(verts, norms, faces)

class HeliosMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Helios 3D Engine - v0.4.0 (The Architect)")
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
        self.recon_engine = VoxelReconstructor(resolution=128)
        self.ai_engine = AIGenerator()
        self.current_params = {}
        
        # Connect Signals
        self.controls.params_changed.connect(self.on_params_changed)
        self.controls.export_requested.connect(self.export_mesh)
        self.video_player.reconstruction_requested.connect(self.start_reconstruction)
        self.viewport.status_message.connect(self.status_label.setText)
        
        # Init params
        self.controls.emit_params()

    def on_params_changed(self, params):
        self.current_params = params
        self.viewport.update_mesh_params(params)

    def start_reconstruction(self):
        self.status_label.setText("Starting Reconstruction Pipeline (This may take a moment)...")
        self.recon_worker = ReconstructionWorker(self.video_player.seg_engine, self.recon_engine, self.ai_engine, self.current_params)
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
