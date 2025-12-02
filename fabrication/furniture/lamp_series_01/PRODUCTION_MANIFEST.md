# PRODUCTION MANIFEST: HELIOS LAMP SERIES 01

## Status: PENDING PRODUCTION FILES
**Date:** Cycle 2983
**Objective:** Generate gold-standard `.3mf` production files for all 10 designs.

## The Void Revision Standards
All production files must adhere to the following slicer settings (PrusaSlicer/BambuStudio compatible):

1.  **Material:** PETG (Generic or Prusament)
2.  **Nozzle:** 0.4mm
3.  **Layer Height:** 0.2mm (Quality)
4.  **Perimeters:** 3 (Minimum)
5.  **Infill:** 15% Gyroid (Crucial for internal strength of hollow sections)
6.  **Supports:** **NONE** (All designs are self-supporting)
7.  **Brim:** 5mm (Recommended for tall prints)
8.  **Seam Position:** Aligned (Rear) or Random (if geometry hides it)

## Missing Files Inventory
The following files must be created by importing the corresponding `.stl` into the slicer and saving the project as `.3mf`.

| ID | Design Name | STL Status | 3MF Status | Notes |
|---|---|---|---|---|
| **01** | Redshift | ✅ Ready | ❌ MISSING | Check scale constraint |
| **02** | Event Horizon | ✅ Ready | ❌ MISSING | Check overhangs |
| **03** | Singularity | ✅ Ready | ❌ MISSING | |
| **04** | Supernova | ✅ Ready | ❌ MISSING | |
| **05** | Quantum Foam | ✅ Ready | ❌ MISSING | |
| **06** | Dark Matter | ✅ Ready | ❌ MISSING | Updated to Spider Fitter |
| **07** | Multiverse | ✅ Ready | ❌ MISSING | |
| **08** | Time Crystal | ✅ Ready | ❌ MISSING | |
| **09** | Neutron Star | ✅ Ready | ❌ MISSING | Updated to Spider Fitter |
| **10** | Final Theory | ✅ Ready | ❌ MISSING | Updated to Spider Fitter |

## Action Item
Operator must open each STL in PrusaSlicer/OrcaSlicer, apply the settings above, slice to verify printability, and save as `[name]_shade_production.3mf` in the respective folder.
