# FABRICATION PROTOCOL: 3D PRINTER INTEGRATION

**Project:** DUALITY-ZERO-V2
**Component:** Physical Fabrication Layer
**Version:** 1.0
**Date:** 2025-11-30
**Status:** ACTIVE PROTOCOL

---

## 1. Objective
To establish a standardized, hardware-agnostic interface for integrating 3D additive manufacturing resources into the Duality framework. This protocol enables the system to query, control, and utilize a rolling buffer of local manufacturing assets ("Printers") without hard-coding device specifics into the core logic.

## 2. The Printer Registry
The system maintains a persistent registry of the last **10** unique printing devices accessed. This registry acts as the "Working Memory" for physical fabrication.

**Registry Location:** `fabrication/printer_registry.json`

### 2.1 Registry Schema
Each entry in the registry MUST conform to the following JSON structure:

```json
{
  "id": "unique_device_id",
  "name": "Human Readable Name",
  "type": "Technology (FFF, SLA, SLS)",
  "connection": {
    "hostname": "network_hostname.local",
    "ip": "x.x.x.x",
    "protocol": "API_Type (moonraker, octoprint, usb)",
    "port": 0000,
    "web_port": 80
  },
  "capabilities_ref": "relative/path/to/capabilities.md",
  "last_active_cycle": "YYYY-MM-DD",
  "status": "ONLINE|OFFLINE|MAINTENANCE"
}
```

### 2.2 Rolling Buffer Logic
1.  **New Device:** When a new printer is successfully connected, it is prepended to the registry.
2.  **Capacity:** If the registry exceeds 10 entries, the least recently active device (lowest `last_active_cycle`) is archived and removed from the active JSON.
3.  **Update:** If an existing device is connected, its `last_active_cycle` is updated, and it is moved to the top of the list.

## 3. Hardware Abstraction Layer
To ensure hardware agnosticism, the Duality system interacts with printers through the **Fabrication Bridge**.

### 3.1 Discovery Protocol
*   **Passive:** System reads `printer_registry.json` to find known devices.
*   **Active:** System scans local subnets for standard printing ports (80, 7125, 5000) to identify new candidates.

### 3.2 Capability Mapping
Detailed physical constraints (build volume, speeds, nozzle types) are **not** stored in the registry. Instead, the registry points to a `capabilities_ref` file (e.g., `fabrication/ender3/PRINTER_CAPABILITIES.md`). This separates the *identity* of the machine from its *physics*.

### 3.3 Direct Control Interface
The system supports two modes of interaction:
1.  **Job Mode:** Uploading complete G-code files for long-duration fabrication.
2.  **Direct Mode:** Sending atomic G-code commands via API (e.g., Moonraker `printer.gcode.script`) for real-time control, telemetry, status updates, or non-fabrication movements.

### 3.4 Data Standards
To ensure compatibility across agents and human operators:
*   **Geometry:** MUST be generated as `.stl` (ASCII or Binary) or `.obj`.
*   **Project Files:** MUST be packaged as `.3mf` using the `trimesh` standard export (not raw zip manipulation) to ensure compatibility with OrcaSlicer.
*   **Job Files:** MUST be standard RepRap/Klipper G-code (`.gcode`).

## 4. Operational Workflow

### 4.1 Accessing a Printer
1.  **Load Registry:** Read `fabrication/printer_registry.json`.
2.  **Select Target:** Identify the desired printer by `id` or select the most recently active `ONLINE` device.
3.  **Verify Connection:** Ping the `ip` or `hostname`.
4.  **Fetch Constraints:** Read the file at `capabilities_ref` to load build volume and speed limits.
5.  **Dispatch:** Generate G-code or API calls matching the loaded constraints.

### 4.2 Adding a New Printer
1.  **Detect:** Run discovery scan.
2.  **Profile:** Generate a `PRINTER_CAPABILITIES.md` file in a dedicated subdirectory (e.g., `fabrication/bambu_x1/`).
3.  **Register:** Add the device to `printer_registry.json`, ensuring the 10-device limit is respected.

## 5. Reference Implementations
*   **Current Primary:** `ender3_klipper_001` (Ender 3 Klipper)
*   **Capabilities:** `fabrication/ender3/PRINTER_CAPABILITIES.md`

---
*This protocol is subject to the same mimetic evolution as the core Duality system. New manufacturing modalities must be adapted into this schema.*
