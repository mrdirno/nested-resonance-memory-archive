# API Documentation: automation.pilot

# Module: `automation.pilot.pilot_monitor`

Cycle 2451: Pilot Monitor (Gate 79)
Role: The Pilot Monitor
Responsibility: Monitor Pilot Health on macOS.

Phase 61 (Digital Terraforming) Standards:
- Structured Logging
- Type Safety
- Robust Error Handling

## Class: `PilotMonitor`

Monitors the health and status of the Pilot Node (macOS).

Attributes:
    interval (int): Heartbeat interval in seconds.
    running (bool): Control flag for the main loop.

### Method: `check_identity`

Verify that the script is running on the correct node (macOS).

Raises:
    SystemExit: If running on a non-Darwin system.

```python
PilotMonitor.check_identity(self) -> None
```

### Method: `heartbeat`

Perform a single heartbeat check.

```python
PilotMonitor.heartbeat(self) -> None
```

### Method: `run`

Main execution loop.

```python
PilotMonitor.run(self) -> None
```

### Method: `shutdown`

Handle shutdown signals.

```python
PilotMonitor.shutdown(self, signum, frame) -> None
```

---
