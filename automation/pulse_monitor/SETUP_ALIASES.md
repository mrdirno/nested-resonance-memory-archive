# Pulse Monitor Setup Guide

## Philosophy
This is not an automation tool. It is a **Pulse Monitor** designed to maintain the heartbeat of the DUALITY-ZERO system.

## Setup (macOS / Linux)

Add the following aliases to your shell configuration (`~/.zshrc` or `~/.bashrc`):

```bash
# DUALITY-ZERO PULSE MONITOR
alias meta-pilot="/Volumes/dual/DUALITY-ZERO-V2/automation/pulse_monitor/meta_pilot.sh"
alias meta-copilot="/Volumes/dual/DUALITY-ZERO-V2/automation/pulse_monitor/meta_pilot.sh gemini"
```

## Usage

- **`meta-pilot`**: Launches the interactive Pulse Monitor. You can choose which AI to wake up.
- **`meta-copilot`**: Instantly wakes up the Co-Pilot (Gemini) for execution duties.
- **`meta-pilot claude`**: Instantly wakes up the Pilot (Claude) for strategic duties.
