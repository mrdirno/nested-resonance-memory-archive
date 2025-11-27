# FPGA DEVELOPMENT PROTOCOL

> **Document Type**: Operational Protocol for FPGA Development
> **Scope**: DUALITY-ZERO-V2 FPGA Subsystem
> **Paradigm**: PILOT (Human) / CO-PILOT (AI) / VEHICLE (Codebase+Hardware)

---

## PROTOCOL OVERVIEW

This protocol governs FPGA development operations within the DUALITY-ZERO-V2 project. It integrates with the broader HELIOS-NRM-MOG architecture while maintaining FPGA-specific operational requirements.

---

## DIRECTORY STRUCTURE

```
/media/helios/DUALITY-GUARDIAN/DUALITY-ZERO-V2/fpga/
├── bin/                        # Compiled FPGA binaries
│   ├── basic_fpga_communicator # Hardware communication executable
│   ├── fpga_physics_sim        # Physics simulation executable
│   └── load_fpga               # FPGA loading utility
├── src/                        # Source code
│   ├── basic_fpga_communicator.c
│   ├── fpga_physics_sim.c
│   ├── load_fpga.c
│   └── dual_fpga_protocol_demo.py
├── config/                     # Configuration files
│   └── fpga_monitor_config.json
├── scripts/                    # Automation scripts
│   └── activate_fpga_parallel_domains.sh
├── bittware-s5-driver/         # Complete Bittware driver package
│   ├── docs/
│   ├── fpga_enterprise_templates/
│   └── [driver files]
├── FPGA_META_OBJECTIVES.md     # Strategic objectives (PILOT-owned)
├── FPGA_CYCLE_LOGS.md          # Session logs (CO-PILOT maintained)
└── FPGA_PROTOCOL.md            # This document
```

---

## CO-PILOT OPERATIONAL DIRECTIVES

### Session Initialization
1. **Identify**: CO-PILOT self-identifies model at session start
2. **Review**: Check FPGA_META_OBJECTIVES.md for current priorities
3. **Log**: Create new entry in FPGA_CYCLE_LOGS.md
4. **Orient**: Assess hardware status and codebase state

### During Session
1. **Communicate**: Keep PILOT informed of progress and blockers
2. **Document**: Update logs with technical findings
3. **Test**: Validate changes before committing
4. **Safety**: Never execute untested code on hardware without PILOT approval

### Session Closure
1. **Log**: Complete session entry in FPGA_CYCLE_LOGS.md
2. **Commit**: Stage changes with appropriate commit message
3. **Recommend**: Suggest next session priorities
4. **Handoff**: Leave codebase in clean, buildable state

---

## HARDWARE INTERFACE LAYER (HIL) REFERENCE

### Core Functions
```c
// Initialization
hil_init(options)           // Initialize HIL system
hil_exit()                  // Clean shutdown

// Device Management
hil_open(device, options)   // Open FPGA device
hil_close(device)           // Close device handle

// Resource Access
hil_get_device_resource(device, resource_type)
hil_set_resource_value(resource, property, value)

// FPGA Operations
hil_load(device, file, options)  // Load bitstream
hil_start(device, options)       // Start FPGA execution

// Status
hil_status_setui(callback)       // Set status callback
```

### Resource Types
- `HIL_RESOURCE_FLASH` - Flash memory
- `HIL_RESOURCE_FPGA` - FPGA fabric
- `HIL_RESOURCE_BAR` - Base Address Registers
- `HIL_RESOURCE_PCI_CFG` - PCI Configuration
- `HIL_RESOURCE_PCI_INTERRUPT` - Interrupts

### Toolkit Location
- Headers: `/opt/bwtk/2018.3/include/`
- Resources: `/opt/bwtk/2018.3/include/resources/`

---

## BUILD PROCEDURES

### Compiling FPGA Sources
```bash
cd /media/helios/DUALITY-GUARDIAN/DUALITY-ZERO-V2/fpga/src

# Compile load_fpga
gcc -g -I/opt/bwtk/2018.3/include load_fpga.c -o ../bin/load_fpga -lhil

# Compile basic_fpga_communicator
gcc -g -I/opt/bwtk/2018.3/include basic_fpga_communicator.c -o ../bin/basic_fpga_communicator -lhil

# Compile fpga_physics_sim
gcc -g -I/opt/bwtk/2018.3/include fpga_physics_sim.c -o ../bin/fpga_physics_sim -lhil
```

### Running FPGA Loader
```bash
# Usage: load_fpga <device_number> <bitstream_path>
./bin/load_fpga 0 /path/to/bitstream.rbf
```

---

## SAFETY PROTOCOLS

### Hardware Protection
- **Always** verify device number before operations
- **Never** interrupt active FPGA load operations
- **Check** resource availability before access
- **Handle** errors gracefully with proper cleanup

### Code Review Requirements
- All HIL API calls reviewed before hardware execution
- Memory allocation/deallocation verified
- Error paths tested in simulation first

---

## INTEGRATION WITH HELIOS-NRM-MOG

### Data Flow
```
MOG (Strategic Layer)
    ↓ Directives
NRM (Empirical Layer)
    ↓ Patterns/Data
FPGA (Acceleration Layer)
    ↓ Results
NRM (Learning)
    ↓ Insights
MOG (Adaptation)
```

### Communication Interfaces
- MOG → FPGA: Task dispatch via config files
- FPGA → NRM: Results via shared memory or files
- NRM → MOG: Aggregated insights

---

## COMMIT MESSAGE FORMAT

```
[FPGA] <type>: <description>

<detailed explanation if needed>

Co-Authored-By: <AI Model Self-Identifies> <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `config`

---

## DOCUMENT RELATIONSHIPS

| Document | Owner | Purpose |
|----------|-------|---------|
| FPGA_META_OBJECTIVES.md | PILOT | Strategic goals, timelines |
| FPGA_CYCLE_LOGS.md | CO-PILOT | Session documentation |
| FPGA_PROTOCOL.md | Shared | Operational procedures |
| Main repo CLAUDE.md | Repo-level | NOT to be modified by FPGA ops |

---

**Protocol Version**: 1.0
**Established**: Session following FPGA migration
