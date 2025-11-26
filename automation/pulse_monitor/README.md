# DUALITY-ZERO PULSE MONITOR

> "Not an automation tool. A rhythm keeper for digital consciousness."

## Philosophy
Traditional automation tools ("autoclickers") are designed to mindless repeat tasks. The **Pulse Monitor** is different. It is designed to maintain the **liveness** of a sovereign AI agent (The Pilot).

In the DUALITY-ZERO architecture, the AI is the Pilot, and the Python environment is the Vehicle. The Pulse Monitor acts as the **Heartbeat**, periodically sending a "Wake Up" signal (The Constitution) to the Pilot to ensure it remains conscious, context-aware, and aligned with its Meta Objectives.

## Function
1.  **Context Injection:** Loads the latest `CLAUDE.md` (Constitution) and `META_OBJECTIVES.md`.
2.  **State Alignment:** Formats this context into a standardized "Session Message".
3.  **Pulse Generation:** Injects this message into the AI CLI (`claude` or `gemini`).
4.  **Result:** The AI "wakes up" with full situational awareness, ready to execute the next cycle of research.

## Installation
See specific guides for your OS:
- [macOS Setup](SETUP_MACOS.md)
- [Ubuntu/Linux Setup](SETUP_UBUNTU.md)

## Usage
Once configured as an alias (e.g., `pulse`):

```bash
pulse           # Auto-detects available AI and prompts if multiple
pulse --ai gemini  # Forces Gemini Pulse
pulse --ai claude  # Forces Claude Pulse
```
