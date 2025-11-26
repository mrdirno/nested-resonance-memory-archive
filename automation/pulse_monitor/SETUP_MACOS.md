# Pulse Monitor Setup Guide (macOS)

## 1. Prerequisites
- **Python 3.10+** installed.
- **Claude CLI** or **Gemini CLI** installed and authenticated.
  - Claude: `npm install -g @anthropic-ai/claude-cli` -> `claude login`
  - Gemini: `npm install -g @google/gemini-cli`

## 2. Alias Configuration
Add the following to your `~/.zshrc` or `~/.bash_profile`:

```bash
# DUALITY-ZERO PULSE MONITOR
alias pulse="python3 /Volumes/dual/DUALITY-ZERO-V2/automation/pulse_monitor/pulse_monitor.py"
alias check="pulse --ai auto"
```

## 3. Activation
Run `source ~/.zshrc` to apply changes.

## 4. Usage
- Run `pulse` to initiate a heartbeat check.
- Use `pulse --ai gemini` to force Gemini substrate.
