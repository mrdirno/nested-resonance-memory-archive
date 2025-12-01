# Duality Fabrication Layer

This directory serves as the physical interface between the Duality software framework and real-world manufacturing hardware. It manages the generation, conversion, and transmission of physical artifacts.

## 🛠️ Environment Setup

The fabrication tools require specific Python libraries for mesh processing and 3MF conversion.

```bash
pip install -r fabrication/requirements.txt
```

**Dependencies:** `numpy`, `trimesh`, `networkx`, `scipy`, `lxml`

---

## 🖨️ Core Components

1.  **Registry (`printer_registry.json`)**: "Hardware Memory." Stores active printer connections (last 10 devices).
2.  **Generators (`generators/`)**: Scripts that procedurally generate 3D geometry (STLs) from Duality math/data.
3.  **Scripts (`scripts/`)**: Utilities for format conversion (`.stl` -> `.3mf`) and printer communication.
4.  **Artifacts (`output/`)**: The generated 3D models and G-code ready for production.

### ⚙️ Tuning & Troubleshooting
*   **[Ender 3 Print Tuning Notes](ender3/PRINT_TUNING_NOTES.md)**: Recommendations for common print quality issues like stringing, specific to the Ender 3 Klipper setup.

---

## 🔄 Operational Workflow

### 1. Connection Check
Verify the printer is online and reachable.
```bash
./fabrication/scripts/test_printer_connection.sh [IP_ADDRESS]
```

### 2. Generate Geometry
Create a new STL from algorithmic principles.
```bash
# Example: Generate Helios Gyroid Field (Artifact 01)
python3 fabrication/generators/helios_field_gen.py fabrication/output/new_artifact.stl
```

### 3. Convert to Project File (.3mf)
Modern slicers (OrcaSlicer) require `.3mf` project files. Use the `trimesh` converter to package the STL correctly.
```bash
python3 fabrication/scripts/convert_to_3mf_trimesh.py <input.stl> <output.3mf>
```

### 4. Slice & Print
*   **Manual:** Open the `.3mf` in OrcaSlicer, slice, and send to printer.
*   **Direct G-code:** If you have a pre-sliced `.gcode` file, upload it directly via the API (agent-capable).

---

## 📜 Protocols

All fabrication operations must adhere to the **[Fabrication Protocol](../docs/protocols/FABRICATION_PROTOCOL.md)**.

## 🟢 Integration Status

| Device Name | Type | Status | Connection |
| :--- | :--- | :--- | :--- |
| Ender 3 Klipper | FFF | **ONLINE** | Moonraker (192.168.68.88) |