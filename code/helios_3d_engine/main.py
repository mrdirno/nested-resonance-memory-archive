import sys
import os
from PySide6.QtWidgets import QApplication
from src.ui.main_window import HeliosMainWindow

def main():
    # Set High DPI scaling
    os.environ["QT_API"] = "pyside6"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("Helios 3D Engine")
    app.setOrganizationName("Duality Zero")
    
    window = HeliosMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
