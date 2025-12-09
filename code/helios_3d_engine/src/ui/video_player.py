from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QBrush
from PySide6.QtCore import Qt, QTimer, Signal
import os
import imageio.v3 as iio
import numpy as np
from ..core.segmentation import SegmentationEngine

class FrameViewer(QWidget):
    click_signal = Signal(int, int) # x, y

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_frame = None # QImage
        self.current_mask = None # Numpy array (HxW)
        self.scaled_pixmap = None
        
    def set_frame(self, frame_np):
        """Updates the current video frame."""
        h, w, ch = frame_np.shape
        bytes_per_line = ch * w
        # frame_np is RGB. QImage expects data.
        self.current_frame = QImage(frame_np.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
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
        self.scale_factor_x = self.current_frame.width() / scaled.width()
        self.scale_factor_y = self.current_frame.height() / scaled.height()

        # Draw Mask Overlay
        if self.current_mask is not None:
            # Mask is HxW boolean or float.
            # Convert to RGBA: Red overlay (255, 0, 0, 128)
            
            h, w = self.current_mask.shape
            
            # Create RGBA buffer
            # Initialize with zeros (transparent)
            rgba = np.zeros((h, w, 4), dtype=np.uint8)
            
            # Set Red channel where mask is True
            mask_indices = self.current_mask > 0
            rgba[mask_indices, 0] = 255 # R
            rgba[mask_indices, 3] = 128 # Alpha (50% opacity)
            
            # Create QImage
            # Must keep reference to buffer or QImage crashes
            self._mask_buffer = rgba
            mask_img = QImage(rgba.data, w, h, w * 4, QImage.Format.Format_RGBA8888)
            
            # Scale and Draw
            rect = self.rect()
            scaled_mask = mask_img.scaled(rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            # Calculate position (same as video)
            x = (rect.width() - scaled_mask.width()) // 2
            y = (rect.height() - scaled_mask.height()) // 2
            
            painter.drawImage(x, y, scaled_mask)
                
    def mousePressEvent(self, event):
        if self.current_frame is None or not hasattr(self, 'img_rect'):
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
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        # Custom Frame Viewer
        self.viewer = FrameViewer()
        self.layout.addWidget(self.viewer)
        
        # Controls
        controls_layout = QHBoxLayout()
        
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

    def on_reconstruct(self):
        self.reconstruction_requested.emit()

class VideoPlayer(QWidget):
    reconstruction_requested = Signal()
    
    def __init__(self, parent=None):
        
        # State
        self.frames = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.current_idx = 0
        self.is_playing = False
        
        # Logic
        self.seg_engine = SegmentationEngine()
        self.seg_engine.model_loaded.connect(self.on_model_ready)
        
        self.viewer.click_signal.connect(self.on_video_click)
        
        # Async Init
        QTimer.singleShot(100, self.load_default_asset)

    def load_default_asset(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        asset_path = os.path.join(base_dir, "assets", "test_data", "default_subject.mp4")
        self.frames_dir = os.path.join(base_dir, "assets", "test_data", "frames")
        
        if os.path.exists(asset_path):
            self.label_status.setText("Loading Video...")
            # Load frames (we need them on disk for SAM 2 anyway)
            # If frames don't exist, extract them.
            if not os.path.exists(self.frames_dir) or len(os.listdir(self.frames_dir)) == 0:
                print("Extracting frames for SAM 2...")
                os.makedirs(self.frames_dir, exist_ok=True)
                raw_frames = iio.imread(asset_path, plugin="pyav", index=None)
                self.frames = raw_frames
                
                # Save to disk for SAM 2
                for i, f in enumerate(raw_frames):
                    iio.imwrite(os.path.join(self.frames_dir, f"{i:05d}.jpg"), f, plugin="pillow")
            else:
                print("Loading frames from disk...")
                # Load from disk to ensure match
                files = sorted([f for f in os.listdir(self.frames_dir) if f.endswith('.jpg')])
                self.frames = [iio.imread(os.path.join(self.frames_dir, f)) for f in files]

            self.slider.setRange(0, len(self.frames) - 1)
            self.show_frame(0)
            self.label_status.setText("Loading AI...")
            
            # Init SAM 2
            self.seg_engine.initialize(self.frames_dir)
            
        else:
            self.label_status.setText("No Asset Found")

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
