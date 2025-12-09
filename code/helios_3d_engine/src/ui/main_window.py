from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QDockWidget, QFileDialog, QApplication
from PySide6.QtCore import Qt, QThread, Signal
from src.render.viewport import HeliosViewport
from src.render.mesh import Mesh
from src.ui.controls import ControlPanel
from src.ui.video_player import VideoPlayer
from src.core.reconstruction import VoxelReconstructor
from src.core.sdf import SDFEngine
from src.bridge.vision_bridge import VisionBridge
import os
import numpy as np

class BooleanWorker(QThread):
    finished = Signal(object, object, object)
    
    def __init__(self, recon_engine, current_geometry, operation, primitive_type):
        super().__init__()
        self.recon_engine = recon_engine
        self.current_geometry = current_geometry
        self.operation = operation
        self.primitive = primitive_type
        self.sdf_engine = SDFEngine()
        
    def run(self):
        if self.current_geometry is None:
            return
            
        # 1. Mesh to SDF
        # We need the voxels. If we came from Native, we have OBJ but no voxels.
        # If we came from Python, we have voxels.
        # For MVP, let's assume Python path or re-voxelize OBJ (complex).
        # Simplified: Only works if we have `self.recon_engine.voxels`.
        
        if not hasattr(self.recon_engine, 'voxels') or self.recon_engine.voxels is None:
            print("Error: No voxel data available for boolean op. Run Python Reconstruction first.")
            # Todo: Voxelize OBJ
            return
            
        # Convert to SDF
        sdf_grid = self.sdf_engine.voxels_to_sdf(self.recon_engine.voxels)
        
        # 2. Generate Primitive SDF
        # Match grid resolution/bounds
        points = self.recon_engine.points.cpu().numpy()
        x = points[:, 0].reshape(sdf_grid.shape)
        y = points[:, 1].reshape(sdf_grid.shape)
        z = points[:, 2].reshape(sdf_grid.shape)
        
        if self.primitive == 'gyroid':
            prim_sdf = self.sdf_engine.gyroid(x, y, z, scale=2.0)
        elif self.primitive == 'sphere':
            prim_sdf = self.sdf_engine.sphere(x, y, z, radius=0.5)
        else:
            prim_sdf = self.sdf_engine.box(x, y, z, size=0.5)
            
        # 3. Apply Boolean
        if self.operation == 'union':
            final_sdf = self.sdf_engine.union(sdf_grid, prim_sdf)
        elif self.operation == 'difference':
            final_sdf = self.sdf_engine.difference(sdf_grid, prim_sdf)
        else:
            final_sdf = self.sdf_engine.intersection(sdf_grid, prim_sdf)
            
        # 4. Extract Mesh
        # Convert SDF back to boolean for Marching Cubes?
        # MC works on scalar fields (iso-surface 0.0).
        # Our extract_mesh expects binary voxels, let's update it or convert SDF < 0 to boolean.
        
        # Update extract_mesh to handle scalar field?
        # Let's convert SDF < 0 -> True
        new_voxels = final_sdf < 0
        
        # Use torch for consistency
        import torch
        new_voxels_t = torch.from_numpy(new_voxels).to(self.recon_engine.device)
        
        verts, norms, faces = self.recon_engine.extract_mesh(new_voxels_t)
        self.finished.emit(verts, norms, faces)

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
            # Native Swift Path
            output_path = os.path.join(self.input_folder, "reconstruction.obj")
            success = self.recon_engine.run_native_photogrammetry(self.input_folder, output_path)
            if success:
                print(f"Loading geometry from {output_path}...")
                verts, norms, faces = self.recon_engine.load_obj(output_path)
                if verts is not None:
                    self.finished.emit(verts, norms, faces)
                else:
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
        self.setWindowTitle("Helios 3D Engine - v1.0.2 (The Singularity)")
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
        self.vision_bridge = VisionBridge()
        
        # Connect
        self.controls.params_changed.connect(self.viewport.update_mesh_params)
        self.controls.export_requested.connect(self.export_mesh)
        self.controls.native_mode_changed.connect(self.set_native_mode)
        self.controls.boolean_op_requested.connect(self.start_boolean_op)
        self.controls.slice_requested.connect(self.preview_slice)
        self.video_player.reconstruction_requested.connect(self.start_reconstruction)
        self.viewport.status_message.connect(self.status_label.setText)

    def set_native_mode(self, enabled):
        self.use_native_engine = enabled
        self.status_label.setText(f"Engine switched to: {'Native (Swift)' if enabled else 'Voxel (Python)'}")

    def preview_slice(self, z_ratio):
        """
        Extracts a 2D slice from the current Voxel/SDF grid and displays it.
        """
        if not hasattr(self.recon_engine, 'voxels') or self.recon_engine.voxels is None:
            # self.status_label.setText("No Voxel Data for Slicing.")
            # Be silent if dragging slider without data, or log once
            return
            
        # Calculate Z index
        # voxels is shape (D, H, W) or (X, Y, Z)?
        # Usually (X, Y, Z). Let's assume Z is last dim.
        # But slicing usually happens along Z (Height).
        
        # If voxels are (X, Y, Z), we slice [:, :, z]
        
        depth = self.recon_engine.voxels.shape[2]
        z_idx = int(z_ratio * (depth - 1))
        z_idx = max(0, min(z_idx, depth - 1))
        
        # Extract slice
        # Convert tensor to numpy
        import torch
        if isinstance(self.recon_engine.voxels, torch.Tensor):
            vol = self.recon_engine.voxels.cpu().numpy()
        else:
            vol = self.recon_engine.voxels
            
        slice_data = vol[:, :, z_idx]
        
        # Send to Video Player
        self.video_player.show_slice(slice_data, z_ratio)

    def start_reconstruction(self):
        self.status_label.setText("Starting Reconstruction Pipeline...")
        folder = self.video_player.current_folder if hasattr(self.video_player, 'current_folder') else None
        
        # Smart Scan Check
        if hasattr(self.controls, 'chk_smart') and self.controls.chk_smart.isChecked() and folder:
            self.status_label.setText("Smart Scan: Analyzing Visuals...")
            QApplication.processEvents()
            
            try:
                # Expects tuple (params, reasoning)
                result = self.vision_bridge.analyze_scene(folder)
                if isinstance(result, tuple):
                    params, reasoning = result
                else:
                    params, reasoning = result, "Legacy Mode"

                if params:
                    msg = f"Smart Scan: {reasoning} "
                    if 'scale' in params:
                        self.controls.spin_scale.setValue(params['scale'])
                    if 'concavity' in params:
                        # self.controls.spin_concavity.setValue(params['concavity']) # If control exists
                        pass
                    
                    self.status_label.setText(msg + "| Optimizing...")
                    QApplication.processEvents()
            except Exception as e:
                print(f"Smart Scan Error: {e}")
                self.status_label.setText("Smart Scan Failed. Proceeding...")
        
        self.recon_worker = ReconstructionWorker(
            self.video_player.seg_engine, 
            self.recon_engine, 
            self.use_native_engine,
            folder
        )
        self.recon_worker.finished.connect(self.on_reconstruction_done)
        self.recon_worker.start()

    def start_boolean_op(self, op, prim):
        self.status_label.setText(f"Calculating Boolean {op} with {prim}...")
        self.bool_worker = BooleanWorker(self.recon_engine, self.viewport.current_geometry, op, prim)
        self.bool_worker.finished.connect(self.on_reconstruction_done)
        self.bool_worker.start()

    def on_reconstruction_done(self, verts, norms, faces):
        if verts is None:
            self.status_label.setText("Operation Failed.")
            return
        
        self.status_label.setText(f"Operation Complete: {len(faces)} faces.")
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