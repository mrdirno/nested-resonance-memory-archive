from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
                               QPushButton, QGroupBox, QSpinBox, QDoubleSpinBox,
                               QLineEdit, QHBoxLayout, QCheckBox, QComboBox)
from PySide6.QtCore import Qt, Signal
from src.core.ai_generator import AIGenerator
from src.core.neural_generator import NeuralGenerator

class ControlPanel(QWidget):
    params_changed = Signal(dict)
    export_requested = Signal()
    native_mode_changed = Signal(bool)
    boolean_op_requested = Signal(str, str) # Op, Primitive
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: #2b2b2b; color: #eee;")
        layout = QVBoxLayout(self)
        
        self.ai_gen = AIGenerator()
        self.neural_gen = NeuralGenerator()
        
        # --- AI Generator ---
        group_ai = QGroupBox("AI Generator")
        layout_ai = QVBoxLayout(group_ai)
        self.txt_prompt = QLineEdit()
        self.txt_prompt.setPlaceholderText("e.g. 'Large thick sphere'")
        self.txt_prompt.setStyleSheet("padding: 5px; color: #fff; background: #444;")
        layout_ai.addWidget(self.txt_prompt)
        self.chk_neural = QCheckBox("Enable Neural Engine (PyTorch)")
        if str(self.neural_gen.device) == "cpu":
            self.chk_neural.setEnabled(False)
            self.chk_neural.setText("Neural Engine (MPS Not Found)")
        layout_ai.addWidget(self.chk_neural)
        self.btn_generate = QPushButton("Generate")
        self.btn_generate.setStyleSheet("background-color: #6a00ff; padding: 5px; font-weight: bold;")
        self.btn_generate.clicked.connect(self.on_generate)
        layout_ai.addWidget(self.btn_generate)
        layout.addWidget(group_ai)
        
        # --- Boolean Operations (Phase 9) ---
        group_bool = QGroupBox("Advanced Editing (Boolean)")
        layout_bool = QVBoxLayout(group_bool)
        
        layout_bool.addWidget(QLabel("Operation:"))
        self.combo_op = QComboBox()
        self.combo_op.addItems(["Union (Merge)", "Difference (Cut)", "Intersection (Mask)"])
        layout_bool.addWidget(self.combo_op)
        
        layout_bool.addWidget(QLabel("With Primitive:"))
        self.combo_prim = QComboBox()
        self.combo_prim.addItems(["Gyroid (Lattice)", "Sphere (Ball)", "Box (Cube)"])
        layout_bool.addWidget(self.combo_prim)
        
        self.btn_bool = QPushButton("Apply Boolean Op")
        self.btn_bool.setStyleSheet("background-color: #d35400; padding: 5px; font-weight: bold;")
        self.btn_bool.clicked.connect(self.emit_boolean)
        layout_bool.addWidget(self.btn_bool)
        layout.addWidget(group_bool)
        
        # --- Reconstruction ---
        group_recon = QGroupBox("Reconstruction")
        layout_recon = QVBoxLayout(group_recon)
        
        self.chk_native = QCheckBox("Use Native (Swift) Engine")
        self.chk_native.setChecked(True)
        self.chk_native.toggled.connect(self.emit_native_mode)
        layout_recon.addWidget(self.chk_native)
        
        self.chk_smart = QCheckBox("Smart Reconstruction (Gemini)")
        self.chk_smart.setToolTip("Uses Gemini Vision to analyze the video and auto-tune parameters.")
        self.chk_smart.setChecked(False)
        layout_recon.addWidget(self.chk_smart)
        
        layout.addWidget(group_recon)
        
        # --- Manual ---
        group_gen = QGroupBox("Manual Settings")
        layout_gen = QVBoxLayout(group_gen)
        layout_gen.addWidget(QLabel("Scale:"))
        self.spin_scale = QDoubleSpinBox()
        self.spin_scale.setValue(2.0)
        layout_gen.addWidget(self.spin_scale)
        layout_gen.addWidget(QLabel("Thickness:"))
        self.spin_thick = QDoubleSpinBox()
        self.spin_thick.setValue(0.1)
        layout_gen.addWidget(self.spin_thick)
        layout_gen.addWidget(QLabel("Resolution:"))
        self.spin_res = QSpinBox()
        self.spin_res.setRange(16, 128)
        self.spin_res.setValue(64)
        layout_gen.addWidget(self.spin_res)
        self.btn_update = QPushButton("Update Mesh")
        self.btn_update.clicked.connect(self.emit_params)
        layout_gen.addWidget(self.btn_update)
        self.btn_export = QPushButton("Export STL")
        self.btn_export.clicked.connect(self.emit_export)
        layout_gen.addWidget(self.btn_export)
        layout.addWidget(group_gen)
        
        layout.addStretch()

    def on_generate(self):
        prompt = self.txt_prompt.text()
        if self.chk_neural.isChecked():
            success = self.neural_gen.load_model()
            if success:
                self.btn_generate.setText("Generating... (Neural)")
                params = self.ai_gen.generate_from_text(prompt)
            else:
                self.btn_generate.setText("Neural Load Failed")
                return
        else:
            params = self.ai_gen.generate_from_text(prompt)
        
        self.spin_scale.setValue(params.get('scale', 1.0))
        self.spin_thick.setValue(params.get('thickness', 0.1))
        self.emit_params()
        if self.chk_neural.isChecked(): self.btn_generate.setText("Generate")

    def emit_params(self):
        params = {
            "scale": self.spin_scale.value(),
            "thickness": self.spin_thick.value(),
            "resolution": self.spin_res.value()
        }
        self.params_changed.emit(params)

    def emit_export(self):
        self.export_requested.emit()
        
    def emit_native_mode(self, checked):
        self.native_mode_changed.emit(checked)
        
    def emit_boolean(self):
        op = self.combo_op.currentText().split()[0].lower()
        prim = self.combo_prim.currentText().split()[0].lower()
        self.boolean_op_requested.emit(op, prim)
