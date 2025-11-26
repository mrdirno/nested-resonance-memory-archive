# DUALITY-ZERO Pulse Tools

Session management for AI-assisted research workflows.

## What This Does

The Pulse Tool maintains context continuity across AI CLI sessions. It periodically injects session messages containing:
- Project constitution (CLAUDE.md)
- Current objectives (META_OBJECTIVES.md)
- Custom directives

This ensures the AI agent remains aligned with project goals across context boundaries.

## Model Agnostic

These tools work with **any AI CLI** - Claude, Gemini, or future models. Use whichever AI has the best capabilities for your current task:

| Role | Description |
|------|-------------|
| **Pilot** | Primary directing agent - sets strategy, makes decisions |
| **Co-Pilot** | Supporting execution agent - implements, validates, assists |

The role determines workflow position, not which AI you use.

## Components

```
pulse_monitor/
├── duality_pulse_pilot.py    # Pilot session manager
├── duality_pulse_copilot.py  # Co-Pilot session manager
├── pulse_pilot_config.json   # Pilot settings + custom message
└── pulse_copilot_config.json # Co-Pilot settings + custom message
```

## Installation

### Dependencies

```bash
# macOS
pip install pyautogui pyperclip pywinctl psutil

# Ubuntu/Linux
pip install pyautogui pyperclip python-xlib psutil
export DISPLAY=:0  # X11 required for GUI
```

### Shell Setup

```bash
# Add to ~/.zshrc or ~/.bashrc
source /path/to/automation/shell_aliases.sh
```

## Usage

```bash
meta-pilot      # Launch Pilot session manager
meta-copilot    # Launch Co-Pilot session manager
```

### GUI Features

1. **Record Window** - Click to set target window location
2. **Custom Message** - Override default session message
3. **Pulse Interval** - Adjust timing (default 12 min)
4. **Start/Stop** - Control pulse cycle

## How It Works

1. Records target window click location
2. On each pulse cycle:
   - Copies session message to clipboard
   - Clicks recorded window location to focus
   - Pastes message (Cmd+V / Ctrl+V)
   - Sends message (Enter)
3. Waits for next cycle

## Configuration

Each tool maintains separate config for independent operation:
- Pulse interval
- Window click location
- Custom session message
- UI preferences

## License

GPL-3.0

## Author

Aldrin Payopay (aldrin.gdf@gmail.com)
