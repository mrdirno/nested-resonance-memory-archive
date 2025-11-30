# Ender 3 (Klipper) - Printer Capabilities

**Source Profile:** `Ender-3 - Klipper.orca_printer`
**Ingestion Date:** 2025-11-30

## Physical Constraints

### Build Volume
- **X Axis:** 220 mm
- **Y Axis:** 220 mm
- **Z Axis:** 230 mm
- **Printable Area Definition:** `[0x0, 220x0, 220x220, 0x220]`

### Extrusion System
- **Technology:** FFF (Fused Filament Fabrication)
- **Structure:** i3 Cartesian
- **Nozzle Diameter:** 0.4 mm
- **Nozzle Material:** Hardened Steel (Suitable for abrasive filaments)
- **Extruder Count:** 1 (Single Extruder)
- **Retraction Standard:** 4mm @ 60mm/s (Indicative of Bowden setup)

## Kinematics (Software Limits)

### Speed Limits
- **Max Speed X:** 500 mm/s
- **Max Speed Y:** 500 mm/s
- **Max Speed Z:** 10 mm/s
- **Max Speed Extruder:** 60 mm/s

### Acceleration Limits
- **Max Accel X:** 500 mm/s²
- **Max Accel Y:** 500 mm/s²
- **Max Accel Z:** 100 mm/s²
- **Max Accel Travel:** 1500 mm/s²
- **Max Accel Extruding:** 500 mm/s²
- **Max Accel Retracting:** 1000 mm/s²

## Firmware & Control
- **Firmware Flavor:** Klipper
- **G-code Macros:**
  - Start: `START_PRINT EXTRUDER_TEMP={...} BED_TEMP={...}`
  - End: `END_PRINT`
  - Pause: `PAUSE`
  - Filament Change: `M600`
- **Host:** OctoPrint (configured setting, may vary in practice)

## Notes
- This profile is tuned for a Klipper-modified Ender 3.
- The "Hardened Steel" nozzle designation implies capability for Carbon Fiber, Wood, or Glow-in-the-Dark filaments, assuming the hotend temperature range supports them.
