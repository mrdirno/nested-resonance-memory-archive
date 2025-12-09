from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider, QHBoxLayout, QLabel
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, Qt
import os

class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        # Video Widget
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)
        
        # Player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.btn_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.set_position)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)
        controls_layout.addWidget(self.slider)
        
        self.layout.addLayout(controls_layout)
        
        # Auto-load test asset if exists
        self.load_default_asset()

    def load_default_asset(self):
        # Locate asset relative to source
        # We assume we are in src/ui/video_player.py
        # Asset is in ../../assets/test_data/default_subject.mp4
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        asset_path = os.path.join(base_dir, "assets", "test_data", "default_subject.mp4")
        
        if os.path.exists(asset_path):
            print(f"Loading reference: {asset_path}")
            self.player.setSource(QUrl.fromLocalFile(asset_path))
        else:
            print("Default asset not found.")

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.btn_play.setText("Play")
        else:
            self.player.play()
            self.btn_play.setText("Pause")

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.player.setPosition(position)
