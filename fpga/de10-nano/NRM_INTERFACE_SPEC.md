# NRM-FPGA Interface Specification (Draft 0.1)

## 1. Overview
This document defines the communication protocol between the **NRM (Nested Resonance Memory)** running on the Host (Ubuntu) and the **FPGA Subsystem** (DE10-Nano HPS + FPGA Fabric).

## 2. Architecture
```
[ NRM Core (Python) ]  <--->  [ Transport Layer ]  <--->  [ HPS Bridge (C) ]  <--->  [ FPGA Fabric ]
      (Host)                    (USB/Net/Serial)             (DE10-Nano)               (Cyclone V)
```

## 3. Transport Layer
Given the current hardware constraints, the transport layer supports two modes:

### 3.1 Mode A: High-Speed (Target)
- **Interface**: USB Gadget Ethernet (RNDIS)
- **Protocol**: TCP/IP Sockets
- **Port**: 5000 (Command), 5001 (Data Stream)
- **Status**: **Pending Hardware Configuration**

### 3.2 Mode B: Fallback (Current)
- **Interface**: UART Serial (`/dev/ttyUSB0`)
- **Protocol**: SLIP (Serial Line IP) or JSON-over-Serial
- **Baud**: 115200 (Default) -> 921600 (Target)
- **Status**: **Active (Debugging)**

## 4. Data Protocol (JSON-RPC)

### 4.1 Command Structure
Request (NRM -> HPS):
```json
{
  "id": 1,
  "method": "write_register",
  "params": {
    "offset": "0x0000",
    "value": "0xDEADBEEF"
  }
}
```

Response (HPS -> NRM):
```json
{
  "id": 1,
  "result": "ok",
  "error": null
}
```

### 4.2 Methods
| Method | Description | Params |
|--------|-------------|--------|
| `ping` | Alive check | None |
| `write_reg` | Write 32-bit CSR | `offset`, `value` |
| `read_reg` | Read 32-bit CSR | `offset` |
| `load_pattern` | Bulk load RAM | `address`, `data` (b64) |
| `get_telemetry`| Read sensors | None |

## 5. HPS Implementation Plan
1. **Listener**: Single-threaded event loop monitoring Serial/TCP.
2. **Parser**: `jsmn` (minimal C JSON parser) or simple string parsing.
3. **Bridge**: `/dev/mem` mapping to Lightweight HPS-to-FPGA Bridge (LWH2F) at base `0xFF200000`.

## 6. Memory Map (Draft)
| Offset | Name | Access | Description |
|--------|------|--------|-------------|
| `0x0000` | `CSR_CTRL` | RW | Control Register (Run/Stop/Reset) |
| `0x0010` | `CSR_STATUS`| RO | Status Register (Busy/Done/Error) |
| `0x0020` | `PWM_THRESH`| RW | LED Breathing Threshold (Debug) |
| `0x1000` | `MEM_BANK0` | RW | Shared Memory Window |

## 7. Next Steps
- [ ] Implement `bridge_server.c` on HPS.
- [ ] Implement `nrm_client.py` on Host.
- [ ] Verify LWH2F Bridge access via `devmem2`.
