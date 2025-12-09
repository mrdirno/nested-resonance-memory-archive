from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider, QHBoxLayout, QLabel, QSizePolicy, QInputDialog
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QBrush
from PySide6.QtCore import Qt, QTimer, Signal
import os
import imageio.v3 as iio
import numpy as np
from ..core.segmentation import SegmentationEngine
from ..bridge.vision_bridge import VisionBridge

class FrameViewer(QWidget):
    click_signal = Signal(int, int) # x, y

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_frame = None # QImage
        self.current_mask = None # Numpy array (HxW)
        self.scaled_pixmap = None
        self.img_rect = (0, 0, 1, 1) # Default to avoid crash
        self.scale_factor_x = 1.0
        self.scale_factor_y = 1.0
        
    def set_frame(self, frame_np):
        """Updates the current video frame."""
        h, w, ch = frame_np.shape
        bytes_per_line = ch * w
        # frame_np is RGB. QImage expects data.
        # Make a copy to ensure data persists
        self.current_frame = QImage(frame_np.tobytes(), w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.update() # Trigger repaint
        
    def set_mask(self, mask_np):
        """Updates the overlay mask."""
        self.current_mask = mask_np
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw Black Background
        painter.fillRect(self.rect(), Qt.GlobalColor.black)
        
        if self.current_frame is None:
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No Video Source")
            return

        # Scale to fit
        # We maintain aspect ratio
        rect = self.rect()
        scaled = self.current_frame.scaled(rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        # Center the image
        x = (rect.width() - scaled.width()) // 2
        y = (rect.height() - scaled.height()) // 2
        
        painter.drawImage(x, y, scaled)
        
        # Store offset/scale for mouse mapping
        self.img_rect = (x, y, scaled.width(), scaled.height())
        # Avoid division by zero
        if scaled.width() > 0:
            self.scale_factor_x = self.current_frame.width() / scaled.width()
        if scaled.height() > 0:
            self.scale_factor_y = self.current_frame.height() / scaled.height()

        # Draw Mask Overlay
        if self.current_mask is not None:
            # Mask is HxW boolean or float.
            h, w = self.current_mask.shape
            
            # Create RGBA buffer
            # Initialize with zeros (transparent)
            rgba = np.zeros((h, w, 4), dtype=np.uint8)
            
            # Set Red channel where mask is True
            mask_indices = self.current_mask > 0
            rgba[mask_indices, 0] = 255 # R
            rgba[mask_indices, 3] = 128 # Alpha (50% opacity)
            
            # Create QImage
            mask_img = QImage(rgba.tobytes(), w, h, w * 4, QImage.Format.Format_RGBA8888)
            
            # Scale and Draw
            scaled_mask = mask_img.scaled(rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            # Calculate position (same as video)
            # Center the image (recalculate x/y to be safe, though should be same)
            x_m = (rect.width() - scaled_mask.width()) // 2
            y_m = (rect.height() - scaled_mask.height()) // 2
            
            painter.drawImage(x_m, y_m, scaled_mask)
                
    def mousePressEvent(self, event):
        if self.current_frame is None:
            return
            
        x_offset, y_offset, w, h = self.img_rect
        click_x = event.position().x()
        click_y = event.position().y()
        
        # Check bounds
        if (click_x >= x_offset and click_x < x_offset + w and
            click_y >= y_offset and click_y < y_offset + h):
            
            # Map to video coordinates
            video_x = int((click_x - x_offset) * self.scale_factor_x)
            video_y = int((click_y - y_offset) * self.scale_factor_y)
            
            self.click_signal.emit(video_x, video_y)

class VideoPlayer(QWidget):
    reconstruction_requested = Signal()
    folder_loaded = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State
        self.frames = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.current_idx = 0
        self.is_playing = False
        self.current_folder = None # Exposed for Main Window
        
        # UI Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        # Custom Frame Viewer
        self.viewer = FrameViewer()
        self.layout.addWidget(self.viewer)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("Load Video")
        self.btn_load.setStyleSheet("background-color: #444; color: white;")
        self.btn_load.clicked.connect(self.open_video_file)
        controls_layout.addWidget(self.btn_load)
        
        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.btn_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.set_position)
        controls_layout.addWidget(self.slider)
        
        # Reconstruct Button
        self.btn_recon = QPushButton("Reconstruct 3D")
        self.btn_recon.setStyleSheet("background-color: #2da44e; color: white; font-weight: bold;")
        self.btn_recon.clicked.connect(self.on_reconstruct)
        controls_layout.addWidget(self.btn_recon)
        
        self.label_status = QLabel("Initializing...")
        controls_layout.addWidget(self.label_status)
        
        self.layout.addLayout(controls_layout)
        
        # Logic / Engine
        self.seg_engine = SegmentationEngine()
        self.seg_engine.model_loaded.connect(self.on_model_ready)
        
        self.viewer.click_signal.connect(self.on_video_click)
        
        # Async Init
        QTimer.singleShot(100, self.load_default_asset)

    def open_video_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.mov *.avi)")
        if filename:
            self.load_asset(filename)

    def load_asset(self, asset_path):
        self.label_status.setText(f"Loading {os.path.basename(asset_path)}...")
        
        # Set up frames directory unique to this video or overwrite 'current'
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.frames_dir = os.path.join(base_dir, "assets", "test_data", "frames")
        
        # Clean existing frames
        if os.path.exists(self.frames_dir):
            import shutil
            shutil.rmtree(self.frames_dir)
        os.makedirs(self.frames_dir, exist_ok=True)
        
        try:
            print(f"Extracting frames from {asset_path}...")
            # Use imageio with pyav plugin
            # Read all frames (memory intensive for large videos, but okay for prototype clips)
            # For production, we should stream or downsample.
            
            # Simple downsampling: Take every Nth frame if too long
            reader = iio.imread(asset_path, plugin="pyav", index=None)
            
            # Limit to ~100 frames to prevent memory explosion in UI
            total_frames = reader.shape[0]
            step = max(1, total_frames // 100)
            
            self.frames = []
            saved_count = 0
            for i in range(0, total_frames, step):
                frame = reader[i]
                self.frames.append(frame)
                iio.imwrite(os.path.join(self.frames_dir, f"{saved_count:05d}.jpg"), frame, plugin="pillow")
                saved_count += 1
                
            self.current_folder = self.frames_dir
            self.folder_loaded.emit(self.frames_dir)
            
            self.current_idx = 0
            self.slider.setRange(0, len(self.frames) - 1)
            self.slider.setValue(0)
            self.show_frame(0)
            
            self.label_status.setText("Initializing AI...")
            self.seg_engine.initialize(self.frames_dir)
            
        except Exception as e:
            print(f"Error loading video: {e}")
            self.label_status.setText("Error Loading Video")

    def load_default_asset(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        asset_path = os.path.join(base_dir, "assets", "test_data", "default_subject.mp4")
        if os.path.exists(asset_path):
            self.load_asset(asset_path)
        else:
            self.label_status.setText("No Default Video Found")

    def on_model_ready(self, success):
        if success:
            self.label_status.setText("Ready. Click object to mask.")
        else:
            self.label_status.setText("AI Failed.")

    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.timer.start(33) # ~30 FPS
            self.btn_play.setText("Pause")
        else:
            self.timer.stop()
            self.btn_play.setText("Play")

    def next_frame(self):
        if not self.frames: return
        self.current_idx = (self.current_idx + 1) % len(self.frames)
        self.slider.setValue(self.current_idx)
        self.show_frame(self.current_idx)

    def set_position(self, pos):
        self.current_idx = pos
        self.show_frame(pos)

    def show_frame(self, idx):
        if idx < len(self.frames):
            self.viewer.set_frame(self.frames[idx])

    def on_video_click(self, x, y):
        self.label_status.setText(f"Processing Click at {x},{y}...")
        # Pause playback
        if self.is_playing:
            self.toggle_play()
            
        # Send to engine
        self.worker = self.seg_engine.add_click(x, y, self.current_idx)
        if self.worker:
            self.worker.mask_ready.connect(self.on_mask_ready)
            self.worker.start()

    def on_mask_ready(self, mask, frame_idx):
        self.label_status.setText("Mask Generated.")
        # Only show if we are still on that frame
        if self.current_idx == frame_idx:
            self.viewer.set_mask(mask)

    def on_reconstruct(self):
        self.reconstruction_requested.emit()

    def show_slice(self, slice_data, z_height):
        """
        Displays a 2D slice (Fabrication View).
        Input: 2D numpy array (binary or float).
        """
        self.label_status.setText(f"Slice View (Z={z_height:.2f})")
        
        # Convert to RGB
        h, w = slice_data.shape
        rgb = np.zeros((h, w, 3), dtype=np.uint8)
        
        if slice_data.dtype == bool:
            rgb[slice_data] = [255, 255, 255] # White solid
        else:
            # Normalize float SDF/Density
            # Assume range -1 to 1 or 0 to 1
            norm = np.clip(slice_data, 0, 1) * 255
            rgb[:, :, 0] = norm
            rgb[:, :, 1] = norm
            rgb[:, :, 2] = norm
            
        self.viewer.set_frame(rgb)
        # Clear mask overlay when in slice mode
        self.viewer.current_mask = None