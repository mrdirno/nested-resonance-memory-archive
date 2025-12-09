from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
                               QPushButton, QGroupBox, QSpinBox, QDoubleSpinBox,
                               QLineEdit, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from src.core.ai_generator import AIGenerator

class ControlPanel(QWidget):
    # Signals to notify changes
    params_changed = Signal(dict)
    export_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: #2b2b2b; color: #eee;")
        
        layout = QVBoxLayout(self)
        self.ai_gen = AIGenerator()
        
        # --- AI Generator ---
        group_ai = QGroupBox("AI Generator (Text-to-3D)")
        layout_ai = QVBoxLayout(group_ai)
        
        self.txt_prompt = QLineEdit()
        self.txt_prompt.setPlaceholderText("e.g. 'Large thick sphere'")
        self.txt_prompt.setStyleSheet("padding: 5px; color: #fff; background: #444;")
        layout_ai.addWidget(self.txt_prompt)
        
        self.btn_generate = QPushButton("Generate")
        self.btn_generate.setStyleSheet("background-color: #6a00ff; padding: 5px; font-weight: bold;")
        self.btn_generate.clicked.connect(self.on_generate)
        layout_ai.addWidget(self.btn_generate)
        
        layout.addWidget(group_ai)
        
        # --- Manual Settings ---
        group_gen = QGroupBox("Manual Settings")
        layout_gen = QVBoxLayout(group_gen)
        
        # Scale
        layout_gen.addWidget(QLabel("Scale:"))
        self.spin_scale = QDoubleSpinBox()
        self.spin_scale.setRange(0.1, 10.0)
        self.spin_scale.setSingleStep(0.1)
        self.spin_scale.setValue(2.0)
        layout_gen.addWidget(self.spin_scale)
        
        # Thickness
        layout_gen.addWidget(QLabel("Thickness:"))
        self.spin_thick = QDoubleSpinBox()
        self.spin_thick.setRange(0.01, 1.0)
        self.spin_thick.setSingleStep(0.01)
        self.spin_thick.setValue(0.1)
        layout_gen.addWidget(self.spin_thick)
        
        # Resolution
        layout_gen.addWidget(QLabel("Resolution:"))
        self.spin_res = QSpinBox()
        self.spin_res.setRange(16, 128)
        self.spin_res.setValue(64)
        layout_gen.addWidget(self.spin_res)
        
        # Update Button
        self.btn_update = QPushButton("Update Mesh")
        self.btn_update.setStyleSheet("background-color: #007acc; padding: 10px; font-weight: bold;")
        self.btn_update.clicked.connect(self.emit_params)
        layout_gen.addWidget(self.btn_update)
        
        # Export Button
        self.btn_export = QPushButton("Export STL")
        self.btn_export.setStyleSheet("background-color: #2da44e; padding: 10px; font-weight: bold; margin-top: 10px;")
        self.btn_export.clicked.connect(self.emit_export)
        layout_gen.addWidget(self.btn_export)
        
        layout.addWidget(group_gen)
        layout.addStretch()

    def on_generate(self):
        prompt = self.txt_prompt.text()
        params = self.ai_gen.generate_from_text(prompt)
        
        # Update UI
        self.spin_scale.setValue(params.get('scale', 1.0))
        self.spin_thick.setValue(params.get('thickness', 0.1))
        
        # Trigger Update
        self.emit_params()

    def emit_params(self):
        params = {
            "scale": self.spin_scale.value(),
            "thickness": self.spin_thick.value(),
            "resolution": self.spin_res.value()
        }
        self.params_changed.emit(params)

    def emit_export(self):
        self.export_requested.emit()