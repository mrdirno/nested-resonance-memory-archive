# Pulse Monitor Setup Guide (Ubuntu/Linux)

## 1. Prerequisites
- **Python 3.10+** installed (`sudo apt install python3`).
- **Node.js & NPM** installed (`sudo apt install nodejs npm`).
- **Claude CLI** or **Gemini CLI**:
  - `sudo npm install -g @anthropic-ai/claude-cli`
  - `sudo npm install -g @google/gemini-cli`

## 2. Alias Configuration
Add the following to your `~/.bashrc`:

```bash
# DUALITY-ZERO PULSE MONITOR
# Update path to match your clone location
export DUALITY_ROOT="/path/to/DUALITY-ZERO-V2"
alias pulse="python3 $DUALITY_ROOT/automation/pulse_monitor/pulse_monitor.py"
alias check="pulse --ai auto"
```

## 3. Activation
Run `source ~/.bashrc`.

## 4. Usage
- Run `pulse` to initiate a heartbeat check.
- Ensure your API keys are set in your environment variables (`ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`).
