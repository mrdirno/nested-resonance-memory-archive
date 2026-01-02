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
    slice_requested = Signal(float) # Normalized Z (0.0 - 1.0)
    
    def __init__(self):
        super().__init__()
        self.working_dir = None
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: #2b2b2b; color: #eee;")
        layout = QVBoxLayout(self)
        
        self.ai_gen = AIGenerator()
        self.neural_gen = NeuralGenerator()

    def set_working_dir(self, path):
        self.working_dir = path
        print(f"ControlPanel: Working Directory set to {path}")
        
    def on_generate(self):
        prompt = self.txt_prompt.text()
        if not prompt: return
        
        # Phase 15: Chat Bridge (Twin Engine)
        import json
        import os
        
        if self.working_dir and os.path.exists(self.working_dir):
            prompt_file = os.path.join(self.working_dir, "user_prompt.json")
            try:
                with open(prompt_file, 'w') as f:
                    json.dump({"prompt": prompt, "timestamp": str(os.path.getmtime(prompt_file) if os.path.exists(prompt_file) else 0)}, f)
                self.btn_generate.setText("Sent to Pilot")
                print(f"User Prompt written to: {prompt_file}")
            except Exception as e:
                print(f"Failed to write prompt: {e}")
                self.btn_generate.setText("Write Error")
        else:
            print("Error: No working directory set for prompts.")
            self.btn_generate.setText("No Video Loaded")
            
        # Fallback: Local Keyword Logic (Instant)
        if self.chk_neural.isChecked():
            success = self.neural_gen.load_model()
            if success:
                params = self.ai_gen.generate_from_text(prompt)
            else:
                self.btn_generate.setText("Neural Load Failed")
                return
        else:
            params = self.ai_gen.generate_from_text(prompt)
        
        self.spin_scale.setValue(params.get('scale', 1.0))
        self.spin_thick.setValue(params.get('thickness', 0.1))
        self.emit_params()
        
        # Reset button text after delay? (Requires timer, skip for now)

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
        
    def emit_slice(self, value):
        self.slice_requested.emit(value / 100.0)
