from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QDockWidget, QFileDialog
from PySide6.QtCore import Qt, QThread, Signal
from src.render.viewport import HeliosViewport
from src.render.mesh import Mesh
from src.ui.controls import ControlPanel
from src.ui.video_player import VideoPlayer
from src.core.reconstruction import VoxelReconstructor
import os

class ReconstructionWorker(QThread):
    finished = Signal(object, object, object) # verts, norms, faces
    
    def __init__(self, seg_engine, recon_engine, use_native=True, input_folder=None):
        super().__init__()
        self.seg_engine = seg_engine
        self.recon_engine = recon_engine
        self.use_native = use_native
        self.input_folder = input_folder
        
    def run(self):
        if self.use_native and self.input_folder:
            # Native Swift Path (Request .obj)
            # RealityKit creates a folder for .obj output
            output_path = os.path.join(self.input_folder, "reconstruction.obj")
            
            success = self.recon_engine.run_native_photogrammetry(self.input_folder, output_path)
            if success:
                # Load OBJ Geometry
                print(f"Loading geometry from {output_path}...")
                verts, norms, faces = self.recon_engine.load_obj(output_path)
                if verts is not None:
                    self.finished.emit(verts, norms, faces)
                else:
                    print("Failed to parse OBJ.")
                    self.finished.emit(None, None, None)
            else:
                self.finished.emit(None, None, None)
        else:
            # Legacy Voxel Path
            masks = self.seg_engine.propagate_all()
            if masks is None: return
            voxels = self.recon_engine.project_and_carve(masks)
            verts, norms, faces = self.recon_engine.extract_mesh(voxels)
            self.finished.emit(verts, norms, faces)

class HeliosMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helios 3D Engine - v0.3.3 (The Loader)")
        self.resize(1600, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.viewport = HeliosViewport()
        layout.addWidget(self.viewport, 1)
        
        self.status_label = QLabel("System Ready.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("background-color: #222; color: #888; padding: 5px;")
        layout.addWidget(self.status_label, 0)

        self.dock_controls = QDockWidget("Controls", self)
        self.controls = ControlPanel()
        self.dock_controls.setWidget(self.controls)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_controls)
        
        self.dock_reference = QDockWidget("Reference", self)
        self.video_player = VideoPlayer()
        self.dock_reference.setWidget(self.video_player)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_reference)
        
        self.recon_engine = VoxelReconstructor(resolution=128)
        self.use_native_engine = True
        
        # Connect
        self.controls.params_changed.connect(self.viewport.update_mesh_params)
        self.controls.export_requested.connect(self.export_mesh)
        self.controls.native_mode_changed.connect(self.set_native_mode)
        self.video_player.reconstruction_requested.connect(self.start_reconstruction)
        self.viewport.status_message.connect(self.status_label.setText)

    def set_native_mode(self, enabled):
        self.use_native_engine = enabled
        self.status_label.setText(f"Engine switched to: {'Native (Swift)' if enabled else 'Voxel (Python)'}")

    def start_reconstruction(self):
        self.status_label.setText("Starting Reconstruction Pipeline...")
        folder = self.video_player.current_folder if hasattr(self.video_player, 'current_folder') else None
        
        self.recon_worker = ReconstructionWorker(
            self.video_player.seg_engine, 
            self.recon_engine, 
            self.use_native_engine,
            folder
        )
        self.recon_worker.finished.connect(self.on_reconstruction_done)
        self.recon_worker.start()

    def on_reconstruction_done(self, verts, norms, faces):
        if verts is None:
            self.status_label.setText("Reconstruction Failed.")
            return
        
        self.status_label.setText(f"Reconstruction Complete: {len(faces)} faces.")
        if self.viewport.mesh:
            self.viewport.mesh.vbo.release()
            self.viewport.mesh.ibo.release()
            self.viewport.mesh.vao.release()
        self.viewport.mesh = Mesh(self.viewport.ctx, verts, norms, faces)
        self.viewport.current_geometry = (verts, norms, faces)
        self.viewport.update()

    def export_mesh(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export STL", "helios_export.stl", "Stereolithography (*.stl)")
        if filename:
            self.status_label.setText(f"Saving to {filename}...")
            success = self.viewport.save_mesh(filename)
            if success: self.status_label.setText(f"Saved: {filename}")
            else: self.status_label.setText("Export Failed")
