from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
                               QPushButton, QGroupBox, QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, Signal

class ControlPanel(QWidget):
    # Signals to notify changes
    params_changed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: #2b2b2b; color: #eee;")
        
        layout = QVBoxLayout(self)
        
        # --- Generator Settings ---
        group_gen = QGroupBox("Generator Settings")
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

    def emit_params(self):
        params = {
            "scale": self.spin_scale.value(),
            "thickness": self.spin_thick.value(),
            "resolution": self.spin_res.value()
        }
        self.params_changed.emit(params)

    def emit_export(self):
        self.export_requested.emit()

class ControlPanel(QWidget):
    # Signals to notify changes
    params_changed = Signal(dict)
    export_requested = Signal()
    
    def __init__(self):
