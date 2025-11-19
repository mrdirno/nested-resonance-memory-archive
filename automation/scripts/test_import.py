import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))
print(f"Sys path: {sys.path}")
try:
    from code.core.reality_interface import RealityInterface
    print("Success: Imported RealityInterface")
except ImportError as e:
    print(f"Failed: {e}")
except Exception as e:
    print(f"Error: {e}")
