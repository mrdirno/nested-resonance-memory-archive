# DUALITY-ZERO: Physical Rig Assembly Guide

> [!CAUTION]
> **HIGH VOLTAGE WARNING**
> The Acoustic Transducer Array operates at **40Vpp (Volts Peak-to-Peak)**.
> While not typically lethal, it can cause painful shocks and burns.
> **ALWAYS disconnect power before touching the array.**

## 1. Bill of Materials (BOM)

| Component | Specification | Role |
| :--- | :--- | :--- |
| **Transducer Array** | 16x16 (256 units) Murata 40kHz | The "Hand" (Actuator) |
| **Driver Board** | FPGA / Arduino Mega + Mosfets | The "Cortex" (Signal Gen) |
| **Camera** | Logitech C920 / Industrial USB Cam | The "Eye" (Sensor) |
| **Power Supply** | 12V-24V DC, 5A | The "Heart" (Power) |
| **Frame** | 8020 Aluminum Extrusion | The "Skeleton" (Structure) |
| **PC** | Mac/Linux with GPU | The "Pilot" (Intelligence) |

## 2. Assembly Instructions

### 2.1 Mechanical Setup
1.  **Mount the Array:** Secure the Transducer Array facing UPWARDS on the base of the frame.
2.  **Mount the Camera:** Secure the Camera facing DOWNWARDS, centered exactly above the array.
    - *Height:* 20-30 cm above the array surface.
    - *Alignment:* Ensure the camera lens is parallel to the array plane.

### 2.2 Electrical Connections
1.  **Driver -> Array:** Connect the logic pins of the Driver Board to the Transducer Array.
2.  **PC -> Driver:** Connect the Driver Board to the PC via USB.
    - *Note:* Identify the Serial Port (e.g., `/dev/ttyACM0` or `/dev/tty.usbmodem*`).
3.  **PC -> Camera:** Connect the Camera to the PC via USB.
4.  **Power -> Driver:** **ENSURE POWER IS OFF.** Connect the DC Power Supply to the Driver Board.

## 3. Verification

### 3.1 Software Check
Run the System Health Check script to verify connections:
```bash
python3 -m experiments.cycle389_hardware_check
```

### 3.2 Physical Check
1.  **Power ON.**
2.  **Listen:** You should hear a faint "click" or hum (40kHz is inaudible, but sub-harmonics might be heard).
3.  **Test:** Place a styrofoam particle in the center. It should jump or levitate if the default pattern is active.

## 4. Troubleshooting
- **Camera Not Found:** Check USB cable. Ensure permissions are granted (`cv2.VideoCapture`).
- **Serial Timeout:** Check baud rate (115200). Ensure correct port is selected.
- **No Levitation:** Check power supply voltage. Check phase alignment.
