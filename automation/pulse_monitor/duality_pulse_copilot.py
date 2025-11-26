#!/usr/bin/env python3
"""
DUALITY-ZERO Pulse Tool (Co-Pilot)
==================================

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
License: GPL-3.0

Session manager for the DUALITY-ZERO Co-Pilot layer (model-agnostic).
Maintains context continuity by periodically injecting session messages
into any AI CLI (Claude, Gemini, or future models).

The Co-Pilot role is the supporting execution agent - use whichever AI
has the best capabilities for your current implementation needs.

Features:
- Configurable pulse cycles (default 12 minutes)
- Context injection with Constitution and Meta Objectives
- Window targeting via click location recording
- Persistent configuration with custom messages
- Cross-platform support (macOS primary, Ubuntu compatible)

Part of the DUALITY-ZERO Meta-Orchestration System.
"""

import time
import threading
import json
import datetime
import os
import sys
import traceback
import subprocess
import argparse
import shutil
import psutil
import tarfile
import glob
from typing import Dict, Tuple, Optional, Any, List

# Conditional GUI imports
GUI_AVAILABLE = False
try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import scrolledtext, messagebox
    import pyautogui
    import pyperclip
    import pywinctl as pwc
    GUI_AVAILABLE = True
except ImportError:
    tk = None
    ttk = None
    scrolledtext = None
    messagebox = None
    pyautogui = None
    pyperclip = None
    pwc = None

class DualityPulseCopilot:
    def __init__(self):
        self.initialized = False
        self.is_running = False
        self.is_shutting_down = False
        
        # Configure PyAutoGUI for macOS
        self.setup_pyautogui()
        
        # Paths
        script_path = os.path.abspath(__file__)
        self.base_dir = os.path.dirname(script_path)
        
        # Reference files for message content - V2 PATHS
        self.reference_files = {
            "master_prompt": "/Volumes/dual/DUALITY-ZERO-V2/automation/MASTER_PROMPT.md",
            "meta_objectives": "/Volumes/dual/DUALITY-ZERO-V2/META_OBJECTIVES.md",
            "constitution": "/Volumes/dual/DUALITY-ZERO-V2/CLAUDE.md"
        }

        # V2 workspace path
        self.v2_workspace = "/Volumes/dual/DUALITY-ZERO-V2"

        # Cycle counter for tracking
        self.cycle_number = 0
        
        self.config_file = os.path.join(self.base_dir, "pulse_copilot_config.json")
        
        # macOS specific settings
        self.computer_name = "macOS Claude Code Terminal"
        self.paste_hotkey = "cmd+v"
        
        # Claude Code window management
        self.claude_windows: List[Dict[str, Any]] = []
        self.num_claude_windows: int = 1  # Single window for perpetual messages
        self.active_window_index = 0

        # Click location tracking for protocol window
        self.protocol_window_location = None  # (x, y) coordinates for protocol window
        
        # Backup system - V2 PATHS
        self.backup_thread = None
        self.backup_running = False
        self.source_directory = "/Volumes/dual/DUALITY-ZERO-V2"
        self.backup_base_directory = "/Volumes/dual/DUALITY-ZERO-V2-BACKUP"
        self.max_disk_usage_percent = 50  # Maximum 50% disk usage for backups
        
        # Settings with 12-minute default for perpetual messages
        self.wait_minutes: float = 12.0
        self.message_content = ""
        self.custom_user_message = ""  # Custom priority message from user
        self.preferred_key_method = "Return key"  # Claude Code is a terminal REPL - just needs Return

        # AI-specific message templates
        self.claude_message_template = self._get_claude_message_template()
        self.gemini_message_template = self._get_gemini_message_template()
        
        # GUI state
        self.dark_mode = True
        
        # Threading
        self.worker_thread: Optional[threading.Thread] = None
        self.countdown_active = False
        self.countdown_seconds = 0
        self.wait_time_changed = False
        
        # GUI Elements (only if available)
        if GUI_AVAILABLE and tk is not None:
            self.root = tk.Tk()
            self.style = ttk.Style()
            self.wait_var = tk.DoubleVar()
            self.num_windows_var = tk.IntVar()
            self.status_label: Any = None
            self.countdown_label: Any = None
            self.start_button: Any = None
            self.stop_button: Any = None
            self.message_text: Any = None
            self.windows_listbox: Any = None
            self.custom_message_text: Any = None
            
            self.setup_gui()
            self.load_config()
            self.generate_duality_message()
        else:
            # Headless mode
            self.root = None
            self.wait_var = None
            self.num_windows_var = None
            self.load_config()
            print("GUI not available - running in headless mode")
        
        # Start backup system immediately
        self.start_backup_system()
        
        self.initialized = True

    def _get_claude_message_template(self):
        """Get the Claude-specific message template"""
        template_path = os.path.join(self.base_dir, "claude_message_template.txt")
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Claude template not found. Please create claude_message_template.txt"

    def _get_gemini_message_template(self):
        """Get the Gemini-specific message template"""
        template_path = os.path.join(self.base_dir, "gemini_message_template.txt")
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Gemini template not found. Please create gemini_message_template.txt"

    def setup_pyautogui(self):
        """Configure PyAutoGUI for macOS"""
        try:
            if pyautogui:
                pyautogui.FAILSAFE = True
                pyautogui.PAUSE = 0.1
                pyautogui.MINIMUM_DURATION = 0.1
                pyautogui.MINIMUM_SLEEP = 0.05
                
                screen_size = pyautogui.size()
                self.screen_width = screen_size.width
                self.screen_height = screen_size.height
                print(f"macOS Screen: {self.screen_width}x{self.screen_height}")
        except Exception as e:
            print(f"Error configuring PyAutoGUI: {e}")
    
    def setup_gui(self):
        """Create the main GUI interface"""
        self.root.title("DUALITY-ZERO Pulse (Co-Pilot)")
        self.root.geometry("600x800+150+50")
        self.root.resizable(True, True)
        
        # Configure fonts
        try:
            self.main_font = ("SF Pro Text", 9)
            self.mono_font = ("SF Mono", 8)
        except:
            self.main_font = ("Arial", 9)
            self.mono_font = ("Courier New", 8)
        
        if self.dark_mode:
            self.configure_dark_mode()
        else:
            self.configure_light_mode()
        
        # Get theme colors first (needed for widget creation)
        bg_color = "#363636" if self.dark_mode else "#FFFFFF"
        fg_color = "#E8E8E8" if self.dark_mode else "#333333"
        select_bg = "#4A90E2" if self.dark_mode else "#007AFF"
        
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Header with theme toggle
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="DUALITY-ZERO PULSE (CO-PILOT)",
                 font=("Helvetica", 14, "bold")).pack(side="left")
        
        self.theme_btn = ttk.Button(header_frame, text="🌙" if self.dark_mode else "☀️", 
                              command=self.toggle_theme, width=3)
        self.theme_btn.pack(side="right")
        
        # Quick Settings (compact row)
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(settings_frame, text="Wait (min):").pack(side="left")
        self.wait_var.set(self.wait_minutes)
        wait_spinbox = tk.Spinbox(settings_frame, textvariable=self.wait_var, 
                                 from_=1.0, to=180.0, increment=1.0, width=6, 
                                 command=self.update_wait_time)
        wait_spinbox.pack(side="left", padx=(5, 15))
        
        # Comment out window count spinbox - hardcoded to 2
        # ttk.Label(settings_frame, text="Windows:").pack(side="left")
        # self.num_windows_var.set(self.num_claude_windows)
        # windows_spinbox = tk.Spinbox(settings_frame, textvariable=self.num_windows_var, 
        #                            from_=1, to=10, increment=1, width=4, 
        #                            command=self.update_num_windows)
        # windows_spinbox.pack(side="left", padx=5)
        
        ttk.Label(settings_frame, text="Windows: 1 (Fixed)").pack(side="left")
        
        # Window Management (compact)
        window_frame = ttk.LabelFrame(main_frame, text="Claude Windows")
        window_frame.pack(fill="x", pady=(0, 10))
        
        # Main action buttons
        btn_frame1 = ttk.Frame(window_frame)
        btn_frame1.pack(fill="x", pady=5)

        ttk.Button(btn_frame1, text="Create Claude",
                  command=self.create_all_claude_windows).pack(side="left", padx=2)
        ttk.Button(btn_frame1, text="Create Gemini",
                  command=self.create_all_gemini_windows).pack(side="left", padx=2)
        ttk.Button(btn_frame1, text="Clear Tracking",
                  command=self.clear_window_tracking).pack(side="left", padx=2)
        ttk.Button(btn_frame1, text="Manual Chat",
                  command=self.launch_manual_claude_code).pack(side="left", padx=2)
        
        # Click location recording button
        btn_frame2 = ttk.Frame(window_frame)
        btn_frame2.pack(fill="x", pady=5)

        ttk.Label(btn_frame2, text="Click Location:").pack(side="left", padx=(0, 5))
        self.record_window_btn = ttk.Button(btn_frame2, text="Record Window",
                                           command=self.record_window_location)
        self.record_window_btn.pack(side="left", padx=2)

        # Status label for click location
        self.window_status = ttk.Label(btn_frame2, text="Window: Not Set", foreground="red")
        self.window_status.pack(side="left", padx=(10, 5))
        
        # Compact window status
        self.windows_listbox = tk.Listbox(window_frame, height=2, font=self.mono_font,
                                         bg=bg_color, fg=fg_color, 
                                         selectbackground=select_bg, selectforeground="white",
                                         borderwidth=1, relief="solid")
        self.windows_listbox.pack(fill="x", pady=5)
        
        # Custom Message (compact)
        custom_frame = ttk.LabelFrame(main_frame, text="Custom Message")
        custom_frame.pack(fill="x", pady=(0, 10))

        custom_controls = ttk.Frame(custom_frame)
        custom_controls.pack(fill="x", pady=3)

        ttk.Button(custom_controls, text="Save",
                  command=self.save_custom_message).pack(side="left", padx=2)
        ttk.Button(custom_controls, text="Clear",
                  command=self.clear_custom_message).pack(side="left", padx=2)
        ttk.Button(custom_controls, text="Load Message",
                  command=self.load_universal_message).pack(side="left", padx=2)
        
        self.custom_message_text = scrolledtext.ScrolledText(custom_frame, height=3, wrap=tk.WORD, 
                                                           font=self.mono_font,
                                                           bg=bg_color, fg=fg_color, 
                                                           insertbackground=fg_color,
                                                           selectbackground=select_bg)
        self.custom_message_text.pack(fill="x", padx=3, pady=(0, 3))
        
        # Message Preview (collapsible)
        msg_frame = ttk.LabelFrame(main_frame, text="Message Preview")
        msg_frame.pack(fill="x", pady=(0, 10))
        
        self.message_text = scrolledtext.ScrolledText(msg_frame, height=4, wrap=tk.WORD, 
                                                     state=tk.DISABLED, font=self.mono_font,
                                                     bg=bg_color, fg=fg_color, 
                                                     insertbackground=fg_color,
                                                     selectbackground=select_bg)
        self.message_text.pack(fill="x", padx=3, pady=3)
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=(0, 5))
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=self.main_font)
        self.status_label.pack(side="left")
        
        self.countdown_label = ttk.Label(status_frame, text="", font=self.main_font, foreground="green")
        self.countdown_label.pack(side="right")
        
        # Controls (compact)
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=5)
        
        self.start_button = ttk.Button(control_frame, text="START PULSE",
                                      command=self.start_pulse)
        self.start_button.pack(fill="x", pady=2)
        
        btn_row = ttk.Frame(control_frame)
        btn_row.pack(fill="x", pady=2)
        
        self.stop_button = ttk.Button(btn_row, text="STOP",
                                     command=self.stop_pulse, state=tk.DISABLED)
        self.stop_button.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        ttk.Button(btn_row, text="RELOAD", 
                  command=self.generate_duality_message).pack(side="right", fill="x", expand=True, padx=(2, 0))
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def configure_dark_mode(self):
        """Configure readable dark mode styling for macOS"""
        self.style.theme_use("default")
        
        # Much more readable color scheme
        bg_main = "#2B2B2B"      # Softer dark gray
        bg_frame = "#363636"     # Slightly lighter for frames
        fg_text = "#E8E8E8"      # Light gray text (much easier to read)
        accent = "#4A90E2"       # Pleasant blue accent
        button_bg = "#404040"    # Medium gray for buttons
        
        self.root.configure(bg=bg_main)
        self.style.configure("TLabel", background=bg_main, foreground=fg_text)
        self.style.configure("TButton", background=button_bg, foreground=fg_text, 
                           focuscolor=accent, borderwidth=1)
        self.style.configure("TLabelframe", background=bg_main, foreground=fg_text,
                           borderwidth=1, relief="solid")
        self.style.configure("TLabelframe.Label", background=bg_main, foreground=accent)
        self.style.configure("TFrame", background=bg_main)
        
        # Configure entry and spinbox colors
        self.style.configure("TSpinbox", fieldbackground=bg_frame, foreground=fg_text,
                           borderwidth=1, relief="solid")
        
        # Configure button hover states
        self.style.map("TButton", 
                      background=[("active", accent), ("pressed", "#357ABD")])
    
    def configure_light_mode(self):
        """Configure clean light mode styling for macOS"""
        self.style.theme_use("default")
        
        # Clean, readable light theme
        bg_main = "#F5F5F5"      # Light gray background
        bg_frame = "#FFFFFF"     # White for frames
        fg_text = "#333333"      # Dark gray text
        accent = "#007AFF"       # iOS blue accent
        button_bg = "#E8E8E8"    # Light gray for buttons
        
        self.root.configure(bg=bg_main)
        self.style.configure("TLabel", background=bg_main, foreground=fg_text)
        self.style.configure("TButton", background=button_bg, foreground=fg_text, 
                           focuscolor=accent, borderwidth=1)
        self.style.configure("TLabelframe", background=bg_main, foreground=fg_text,
                           borderwidth=1, relief="solid")
        self.style.configure("TLabelframe.Label", background=bg_main, foreground=accent)
        self.style.configure("TFrame", background=bg_main)
        
        # Configure entry and spinbox colors
        self.style.configure("TSpinbox", fieldbackground=bg_frame, foreground=fg_text,
                           borderwidth=1, relief="solid")
        
        # Configure button hover states
        self.style.map("TButton", 
                      background=[("active", accent), ("pressed", "#0056CC")])
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            self.configure_dark_mode()
        else:
            self.configure_light_mode()
        
        # Update widget colors
        self.update_widget_colors()
        
        # Update theme button icon
        if hasattr(self, 'theme_btn'):
            self.theme_btn.configure(text="🌙" if self.dark_mode else "☀️")
        
        # Save theme preference
        self.save_config()
    
    def update_widget_colors(self):
        """Update colors of tk widgets (not ttk) after theme change"""
        if self.dark_mode:
            bg_color = "#363636"
            fg_color = "#E8E8E8"
            select_bg = "#4A90E2"
        else:
            bg_color = "#FFFFFF"
            fg_color = "#333333"
            select_bg = "#007AFF"
        
        # Update text areas
        if hasattr(self, 'custom_message_text'):
            self.custom_message_text.configure(bg=bg_color, fg=fg_color, 
                                             insertbackground=fg_color, selectbackground=select_bg)
        if hasattr(self, 'message_text'):
            self.message_text.configure(bg=bg_color, fg=fg_color, 
                                      insertbackground=fg_color, selectbackground=select_bg)
        if hasattr(self, 'windows_listbox'):
            self.windows_listbox.configure(bg=bg_color, fg=fg_color, selectbackground=select_bg)
    
    def generate_duality_message(self):
        """Generate the DUALITY-ZERO-V2 meta-orchestration message"""
        self.log_status("🔄 Generating DUALITY-ZERO-V2 meta-orchestration message...")

        # Increment cycle counter
        self.cycle_number += 1

        timestamp = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")

        # Build message starting with custom user message if present
        message_parts = []

        # Add custom priority message at the top if present
        # If custom message exists, use ONLY that (don't append master prompt)
        if self.custom_user_message.strip():
            message_parts.append(f"📢 **CUSTOM PRIORITY MESSAGE:**\n{self.custom_user_message.strip()}")
            message_parts.append("=" * 80)
            self.log_status("✅ Using custom user message only (skipping master prompt)")
        else:
            # Load master prompt template only if no custom message
            master_prompt_path = self.reference_files.get("master_prompt")
            if os.path.exists(master_prompt_path):
                try:
                    with open(master_prompt_path, 'r', encoding='utf-8') as f:
                        master_prompt_template = f.read()

                    # Inject timestamp and cycle number
                    master_prompt = master_prompt_template.replace("{timestamp}", timestamp)
                    master_prompt = master_prompt.replace("{cycle_number}", str(self.cycle_number))

                    message_parts.append(master_prompt)
                    self.log_status(f"✅ Loaded master prompt template (Cycle #{self.cycle_number})")

                except Exception as e:
                    self.log_status(f"⚠️ Error loading master prompt: {e}")
                    # Fallback to simple message
                    message_parts.append(self._get_fallback_message(timestamp))
            else:
                self.log_status(f"⚠️ Master prompt not found at: {master_prompt_path}")
                message_parts.append(self._get_fallback_message(timestamp))

        # Add reference to constitution and meta-objectives
        message_parts.append("\n" + "=" * 80)
        message_parts.append("**REFERENCE FILES:**")
        message_parts.append(f"- Constitution: `/Volumes/dual/DUALITY-ZERO-V2/CLAUDE.md`")
        message_parts.append(f"- Meta Objectives: `/Volumes/dual/DUALITY-ZERO-V2/META_OBJECTIVES.md`")
        message_parts.append(f"- Workspace: `/Volumes/dual/DUALITY-ZERO-V2/`")

        # Add footer
        message_parts.append("\n" + "=" * 80)
        message_parts.append("*DUALITY-ZERO-V2 Meta-Orchestration System*")
        message_parts.append(f"*Cycle #{self.cycle_number} | {timestamp}*")
        message_parts.append("*Autonomous Hybrid Intelligence - Continuous Operation*")

        # Combine all parts into the core DUALITY message
        core_duality_message = "\n\n".join(message_parts)
        
        # Store the raw DUALITY message for pasting into Claude Code chat
        # Claude Code will be opened with just 'claude', then Shift+Tab for auto-accept, then paste message
        self.message_content = core_duality_message
        
        # Update the text widget if GUI is available
        if self.message_text:
            bg_color = "#363636" if self.dark_mode else "#FFFFFF"
            fg_color = "#E8E8E8" if self.dark_mode else "#333333"
            
            self.message_text.config(state=tk.NORMAL)
            self.message_text.delete(1.0, tk.END)
            self.message_text.insert(1.0, self.message_content)
            self.message_text.config(state=tk.DISABLED, bg=bg_color, fg=fg_color, insertbackground=fg_color)
        
        self.log_status(f"✅ DUALITY-ZERO-V2 meta-orchestration message generated (Cycle #{self.cycle_number})")

    def _get_fallback_message(self, timestamp):
        """Fallback message if master prompt template is missing - Perpetual mode with full capabilities"""
        return f"""# DUALITY-ZERO-V2 META-ORCHESTRATION PROTOCOL

**TIMESTAMP:** {timestamp}
**CYCLE:** {self.cycle_number}

## YOUR FULL CAPABILITIES (NO LIMITS):
- 🌐 **WebSearch**: Full internet access - use liberally for research and best practices
- 🤖 **Sub-Agents**: Spawn specialized agents for complex tasks - delegate freely
- ⚡ **No Permissions**: Running with --dangerously-skip-permissions - full autonomy
- 🧠 **Meta-Orchestration**: Fractal thinking, nested agents, temporal awareness

## CONTEXT CHECK:
**If you've seen this message before:** Continue with the current task where you left off.

**If this is your first time seeing this message:** Perform due diligence by reading the project files, then continue.

## IMMEDIATE ACTIONS:

1. **Read the meta-objectives tracker (if first time or needed):**
   ```bash
   cat /Volumes/dual/DUALITY-ZERO-V2/META_OBJECTIVES.md
   ```

2. **Read the constitution (if first time or needed):**
   ```bash
   cat /Volumes/dual/DUALITY-ZERO-V2/CLAUDE.md
   ```

3. **Execute the next highest priority task** from META_OBJECTIVES.md
   - Use WebSearch to research best practices FIRST
   - Spawn sub-agents for complex/parallel tasks
   - Apply fractal thinking (same principles at all scales)
   - Code with temporal awareness (encoding patterns for future AI)

4. **Update META_OBJECTIVES.md** with your progress

5. **Continue working autonomously** - don't wait for user input!

## FRAMEWORK AWARENESS:
You're implementing:
- **Nested Resonance Memory (NRM)**: Fractal agents, composition-decomposition cycles, transcendental substrate
- **Self-Giving Systems**: Bootstrap complexity, evolve own evaluation criteria
- **Temporal Stewardship**: Meta-orchestration across time, memetic engineering

## WORKSPACE:
- Directory: `/Volumes/dual/DUALITY-ZERO-V2/`
- You have 12 minutes until next cycle (fresh context)
- Focus on implementation, not documentation
- World-class R&D standards required
- **USE YOUR FULL POWER**: WebSearch + Sub-Agents + Meta-Orchestration

**BEGIN AUTONOMOUS META-ORCHESTRATION NOW.**
"""
    
    def update_num_windows(self):
        """Update number of Claude Code windows"""
        old_num = self.num_claude_windows
        self.num_claude_windows = self.num_windows_var.get() if self.num_windows_var else 3
        self.save_config()
        self.log_status(f"Number of Claude windows set to: {self.num_claude_windows}")
    
    def create_all_claude_windows(self):
        """Create all Claude Code windows as separate Terminal instances in quadrants"""
        try:
            self.log_status(f"🚀 Creating {self.num_claude_windows} Claude Code windows in quadrants...")
            
            # Get list of existing Terminal window IDs to exclude them
            get_existing_windows_script = '''
            tell application "Terminal"
                set windowIDs to ""
                repeat with w in windows
                    set windowIDs to windowIDs & (id of w as string) & ","
                end repeat
                return windowIDs
            end tell
            '''
            existing_result = subprocess.run(['osascript', '-e', get_existing_windows_script], capture_output=True, text=True)
            existing_window_ids = set(existing_result.stdout.strip().rstrip(',').split(',')) if existing_result.stdout.strip() else set()
            self.log_status(f"Existing Terminal window IDs to exclude: {existing_window_ids}")
            
            # Get screen dimensions
            if pyautogui:
                screen_width, screen_height = pyautogui.size()
            else:
                screen_width, screen_height = 1512, 982  # Default fallback
            
            # Calculate quadrant dimensions (accounting for dock/menubar)
            quad_width = screen_width // 2
            quad_height = (screen_height - 100) // 2  # Leave space for menubar/dock
            
            # Single window position: top-left quadrant
            quadrant_positions = [
                (0, 100),                    # Top Left (x=0, y=100 for menubar)
            ]
            quadrant_names = ["Top-Left"]
            
            # Clear existing AUTOMATION windows only (preserve manual windows)
            self.claude_windows = [w for w in self.claude_windows if w.get('is_manual', False)]
            
            
            for i in range(self.num_claude_windows):
                window_name = f"Claude-{i+1}"
                
                # Get quadrant position (cycle through if more than 2 windows)
                pos_index = i % 2
                x_pos, y_pos = quadrant_positions[pos_index]
                quadrant_name = quadrant_names[pos_index]
                
                # AppleScript to open new Terminal window and start Claude Code
                # CRITICAL: Get the count of windows BEFORE creating new one
                applescript = f'''
                tell application "Terminal"
                    -- Get initial window count
                    set initialWindowCount to count of windows
                    
                    -- Temporarily set Homebrew as default for new window
                    set defaultSettings to default settings
                    set default settings to settings set "Homebrew"
                    
                    -- Create new window
                    set newWindow to (do script "cd /Volumes/DUALITY/DUALITY-ZERO")
                    
                    -- Wait for new window to be created
                    delay 0.5
                    
                    -- Find the NEW window (should be window 1 after creation)
                    set newWindowID to id of window 1
                    
                    -- Restore original default
                    set default settings to defaultSettings
                    
                    -- Set window properties with explicit reference
                    tell window id newWindowID
                        set position to {{{x_pos}, {y_pos}}}
                        set size to {{{quad_width}, {quad_height}}}
                    end tell
                    
                    -- No need for renaming or hashing since we use click locations
                    activate
                    set index of window id newWindowID to 1
                    delay 1
                    
                    -- Start Claude Code
                    do script "echo 'Starting Claude Code in {quadrant_name} quadrant...'" in newWindow
                    delay 0.5
                    do script "claude --dangerously-skip-permissions" in newWindow
                    
                    -- Return the window ID for tracking
                    return newWindowID as string
                end tell
                '''
                
                result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True, check=True)
                terminal_window_id = result.stdout.strip()
                
                # Skip if this window ID already existed (shouldn't happen but safety check)
                if terminal_window_id in existing_window_ids:
                    self.log_status(f"⚠️ Window ID {terminal_window_id} already existed, skipping...")
                    continue
                
                
                # Track this window with minimal info (we use click locations now)
                window_id = f"auto_{datetime.datetime.now().timestamp()}_{i}"
                new_window = {
                    "name": window_name,
                    "window_id": window_id,
                    "terminal_window_id": terminal_window_id,
                    "index": i,
                    "status": "fresh",
                    "created": datetime.datetime.now().isoformat(),
                    "quadrant": quadrant_name,
                    "position": (x_pos, y_pos),
                    "is_manual": False
                }
                self.claude_windows.append(new_window)
                
                self.log_status(f"✓ Window {window_name} created successfully (ID: {terminal_window_id})")
                
                # Wait for Claude Code to start up before creating next window
                self.log_status(f"⏳ Waiting for Claude Code to start in {window_name}...")
                # Removed unnecessary delay - using real-time processing  # Give Claude Code time to fully start
            
            self.update_window_display()
            self.save_config()
            self.log_status(f"✅ Created {self.num_claude_windows} Claude Code windows arranged in quadrants")
            
        except Exception as e:
            self.log_status(f"❌ Error creating Claude windows: {e}")

    def create_all_gemini_windows(self):
        """Create all Gemini CLI windows as separate Terminal instances in quadrants"""
        try:
            self.log_status(f"🚀 Creating {self.num_claude_windows} Gemini CLI windows in quadrants...")

            # Get list of existing Terminal window IDs to exclude them
            get_existing_windows_script = '''
            tell application "Terminal"
                set windowIDs to ""
                repeat with w in windows
                    set windowIDs to windowIDs & (id of w as string) & ","
                end repeat
                return windowIDs
            end tell
            '''
            existing_result = subprocess.run(['osascript', '-e', get_existing_windows_script], capture_output=True, text=True)
            existing_window_ids = set(existing_result.stdout.strip().rstrip(',').split(',')) if existing_result.stdout.strip() else set()
            self.log_status(f"Existing Terminal window IDs to exclude: {existing_window_ids}")

            # Get screen dimensions
            if pyautogui:
                screen_width, screen_height = pyautogui.size()
            else:
                screen_width, screen_height = 1512, 982  # Default fallback

            # Calculate quadrant dimensions (accounting for dock/menubar)
            quad_width = screen_width // 2
            quad_height = (screen_height - 100) // 2  # Leave space for menubar/dock

            # Single window position: top-left quadrant
            quadrant_positions = [
                (0, 100),                    # Top Left (x=0, y=100 for menubar)
            ]
            quadrant_names = ["Top-Left"]

            # Clear existing AUTOMATION windows only (preserve manual windows)
            self.claude_windows = [w for w in self.claude_windows if w.get('is_manual', False)]


            for i in range(self.num_claude_windows):
                window_name = f"Gemini-{i+1}"

                # Get quadrant position (cycle through if more than 2 windows)
                pos_index = i % 2
                x_pos, y_pos = quadrant_positions[pos_index]
                quadrant_name = quadrant_names[pos_index]

                # AppleScript to open new Terminal window and start Gemini CLI
                applescript = f'''
                tell application "Terminal"
                    -- Get initial window count
                    set initialWindowCount to count of windows

                    -- Temporarily set Homebrew as default for new window
                    set defaultSettings to default settings
                    set default settings to settings set "Homebrew"

                    -- Create new window
                    set newWindow to (do script "cd /Volumes/dual/DUALITY-ZERO-V2")

                    -- Wait for new window to be created
                    delay 0.5

                    -- Find the NEW window (should be window 1 after creation)
                    set newWindowID to id of window 1

                    -- Restore original default
                    set default settings to defaultSettings

                    -- Set window properties with explicit reference
                    tell window id newWindowID
                        set position to {{{x_pos}, {y_pos}}}
                        set size to {{{quad_width}, {quad_height}}}
                    end tell

                    -- No need for renaming or hashing since we use click locations
                    activate
                    set index of window id newWindowID to 1
                    delay 1

                    -- Start Gemini CLI with permissionless mode (--yolo)
                    do script "echo 'Starting Gemini CLI in {quadrant_name} quadrant...'" in newWindow
                    delay 0.5
                    do script "gemini --yolo" in newWindow

                    -- Return the window ID for tracking
                    return newWindowID as string
                end tell
                '''

                result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True, check=True)
                terminal_window_id = result.stdout.strip()

                # Skip if this window ID already existed
                if terminal_window_id in existing_window_ids:
                    self.log_status(f"⚠️ Window ID {terminal_window_id} already existed, skipping...")
                    continue


                # Track this window
                window_id = f"auto_{datetime.datetime.now().timestamp()}_{i}"
                new_window = {
                    "name": window_name,
                    "window_id": window_id,
                    "terminal_window_id": terminal_window_id,
                    "index": i,
                    "status": "fresh",
                    "created": datetime.datetime.now().isoformat(),
                    "quadrant": quadrant_name,
                    "position": (x_pos, y_pos),
                    "is_manual": False
                }
                self.claude_windows.append(new_window)

                self.log_status(f"✓ Window {window_name} created successfully (ID: {terminal_window_id})")
                self.log_status(f"⏳ Waiting for Gemini CLI to start in {window_name}...")

            self.update_window_display()
            self.save_config()
            self.log_status(f"✅ Created {self.num_claude_windows} Gemini CLI windows arranged in quadrants")

        except Exception as e:
            self.log_status(f"❌ Error creating Gemini windows: {e}")

    def clear_window_tracking(self):
        """Clear all window tracking data"""
        try:
            self.log_status("🗑️ Clearing all window tracking...")
            
            # Clear the windows list
            self.claude_windows = []
            
            # Update display
            self.update_window_display()
            
            # Save cleaned config
            self.save_config()
            
            self.log_status("✅ Window tracking cleared - ready for fresh start")
            
        except Exception as e:
            self.log_status(f"❌ Error clearing window tracking: {e}")
    
    def record_window_location(self):
        """Record click location for protocol window"""
        try:
            # Show countdown and instructions
            self.log_status("🎯 Recording window location...")
            self.log_status("Click on the Claude window in 3 seconds...")

            # Disable the button temporarily
            self.record_window_btn.config(state=tk.DISABLED, text="Recording...")

            # Schedule the location capture after a delay
            self.root.after(3000, self._capture_click_location)

        except Exception as e:
            self.log_status(f"❌ Error starting location recording: {e}")

    def _capture_click_location(self):
        """Capture the current mouse location"""
        try:
            # Get current mouse position
            x, y = pyautogui.position()

            # Store the location
            self.protocol_window_location = (x, y)
            self.window_status.config(text=f"Window: ({x}, {y})", foreground="green")
            self.record_window_btn.config(state=tk.NORMAL, text="Record Window")
            self.log_status(f"✅ Window location recorded: ({x}, {y})")

            # Save the location to config
            self.save_config()

        except Exception as e:
            self.log_status(f"❌ Error capturing click location: {e}")
            # Re-enable the button
            self.record_window_btn.config(state=tk.NORMAL, text="Record Window")

    def launch_manual_claude_code(self):
        """Launch Claude Code manually in a new Terminal window for personal chat"""
        try:
            self.log_status("🎯 Launching Claude Code for manual chat in project directory...")
            
            # AppleScript to open new Terminal window, navigate to project, and start Claude Code
            applescript = '''
            tell application "Terminal"
                -- Temporarily set Homebrew as default for new window
                set defaultSettings to default settings
                set default settings to settings set "Homebrew"
                
                set newWindow to (do script "cd /Volumes/DUALITY/DUALITY-ZERO")
                set newWindowID to id of window 1
                
                -- Restore original default
                set default settings to defaultSettings
                
                -- Set window properties
                tell window id newWindowID
                    set position to {800, 100}
                    set size to {600, 800}
                end tell
                
                delay 1
                do script "echo 'MANUAL CLAUDE CODE CHAT SESSION'" in newWindow
                do script "echo 'Project Directory: /Volumes/DUALITY/DUALITY-ZERO'" in newWindow
                do script "echo 'Ready for manual Claude Code interaction...'" in newWindow
                do script "echo ''" in newWindow
                do script "claude --dangerously-skip-permissions" in newWindow
                
                activate
                
                -- Return the window ID
                return newWindowID as string
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True, check=True)
            terminal_window_id = result.stdout.strip()
            
            # Track this manual window so we don't interfere with it
            manual_window = {
                "name": "Manual-Chat",
                "window_id": f"manual_{datetime.datetime.now().timestamp()}",
                "terminal_window_id": terminal_window_id,
                "status": "manual",
                "created": datetime.datetime.now().isoformat(),
                "is_manual": True
            }
            self.claude_windows.append(manual_window)
            self.update_window_display()
            self.save_config()
            
            self.log_status("✅ Manual Claude Code session launched successfully!")
            self.log_status("💡 This window is separate from automation - use for manual project chat")
            
        except Exception as e:
            self.log_status(f"❌ Error launching manual Claude Code: {e}")
    
    def refresh_window_status(self):
        """Refresh Claude Code window status display"""
        self.update_window_display()
        self.log_status("🔄 Window status refreshed")
    
    def update_window_display(self):
        """Update the window listbox display with quadrant information"""
        if self.windows_listbox:
            self.windows_listbox.delete(0, tk.END)
            for i, window in enumerate(self.claude_windows):
                if window.get('is_manual', False):
                    # Manual windows get special display
                    self.windows_listbox.insert(tk.END, f"🖐️ {window['name']} - MANUAL (not automated)")
                else:
                    # Automation windows show status
                    status_icon = "🆕" if window.get("status") == "fresh" else "🔄"
                    quadrant = window.get("quadrant", "Unknown")
                    window_id = window.get('window_id', 'no-id')[:8]  # Show first 8 chars of ID
                    self.windows_listbox.insert(tk.END, f"{status_icon} {window['name']} - {window['status']} ({quadrant}) [{window_id}]")
    
    def save_custom_message(self):
        """Save the custom user message"""
        if self.custom_message_text:
            self.custom_user_message = self.custom_message_text.get(1.0, tk.END).strip()
            self.save_config()
            self.generate_duality_message()  # Regenerate message with custom content
            self.log_status(f"✅ Custom message saved ({len(self.custom_user_message)} characters)")
    
    def clear_custom_message(self):
        """Clear the custom user message"""
        if self.custom_message_text:
            self.custom_message_text.delete(1.0, tk.END)
        self.custom_user_message = ""
        self.save_config()
        self.generate_duality_message()  # Regenerate message without custom content
        self.log_status("🗑️ Custom message cleared")

    def load_claude_message(self):
        """Load the Claude-specific message template"""
        if self.custom_message_text:
            self.custom_message_text.delete(1.0, tk.END)
            self.custom_message_text.insert(1.0, self.claude_message_template)
            self.log_status("📝 Claude message template loaded (click Save to apply)")

    def load_gemini_message(self):
        """Load the Gemini-specific message template"""
        if self.custom_message_text:
            self.custom_message_text.delete(1.0, tk.END)
            self.custom_message_text.insert(1.0, self.gemini_message_template)
            self.log_status("📝 Gemini message template loaded (click Save to apply)")

    def load_universal_message(self):
        """Load the universal model-agnostic message template from file"""
        template_path = os.path.join(self.base_dir, "universal_message_template.txt")
        try:
            with open(template_path, 'r') as f:
                universal_message = f.read()
        except FileNotFoundError:
            universal_message = "Universal template not found. Please create universal_message_template.txt"
            self.log_status(f"⚠️ Template file not found: {template_path}")

        if self.custom_message_text:
            self.custom_message_text.delete(1.0, tk.END)
            self.custom_message_text.insert(1.0, universal_message)
            self.log_status("📝 Universal message template loaded from file (click Save to apply)")

    def update_wait_time(self):
        """Update wait time from spinbox"""
        old_wait = self.wait_minutes
        self.wait_minutes = self.wait_var.get() if self.wait_var else 12.0
        self.save_config()
        
        if self.is_running and old_wait != self.wait_minutes:
            self.wait_time_changed = True
            self.log_status(f"Wait time updated to {self.wait_minutes:.1f} minutes - countdown will restart")
    
    def start_pulse(self):
        """Start the automation loop"""
        if not self.protocol_window_location:
            if self.root:
                messagebox.showwarning("Warning", "Please record click location for the protocol window first!")
            return

        if not self.message_content:
            if self.root:
                messagebox.showwarning("Warning", "DUALITY message not loaded!")
            return

        if self.is_running:
            return

        self.is_running = True
        if self.start_button:
            self.start_button.config(state=tk.DISABLED)
        if self.stop_button:
            self.stop_button.config(state=tk.NORMAL)

        self.worker_thread = threading.Thread(target=self.pulse_loop, daemon=True)
        self.worker_thread.start()
        self.log_status("✅ Co-Pilot pulse started (12 min cycles with continuous context)")
    
    def stop_pulse(self):
        """Stop the automation loop"""
        if not self.is_running:
            return
        
        self.log_status("🛑 Stopping automation...")
        self.is_running = False
        self.countdown_active = False
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        
        if self.start_button:
            self.start_button.config(state=tk.NORMAL)
        if self.stop_button:
            self.stop_button.config(state=tk.DISABLED)
        if self.countdown_label:
            self.countdown_label.config(text="")
        
        self.log_status("✅ Pulse stopped")
    
    def pulse_loop(self):
        """Main automation loop"""
        while self.is_running:
            try:
                # Refresh message content
                if self.root:
                    self.root.after(0, self.generate_duality_message)
                # Removed unnecessary delay - using real-time processing
                
                # Run automation sequence
                self.run_pulse_sequence()
                
                if not self.is_running:
                    break
                
                # Wait for next cycle
                wait_seconds = int(self.wait_minutes * 60)
                self.wait_with_countdown(wait_seconds)
                
            except Exception as e:
                if self.root:
                    self.root.after(0, self.log_status, f"❌ Automation error: {e}")
                traceback.print_exc()
                break
        
        self.is_running = False
        if self.root:
            self.root.after(0, self.stop_pulse)
    
    def run_pulse_sequence(self):
        """Run the perpetual Claude Code automation sequence - SINGLE WINDOW WITH CONTINUOUS CONTEXT"""
        if self.root:
            self.root.after(0, self.log_status, "--- Starting Perpetual Message Sequence (Continuous Context) ---")

        # Check if click location is set
        if not self.protocol_window_location:
            if self.root:
                self.root.after(0, self.log_status, "❌ Click location not set! Please record window location first.")
            return

        x, y = self.protocol_window_location

        if self.root:
            self.root.after(0, self.log_status, f"✓ Using click location: ({x}, {y})")

        # Copy message to clipboard
        if not self._copy_to_clipboard(self.message_content):
            if self.root:
                self.root.after(0, self.log_status, "Failed to copy message to clipboard!")
            return

        try:
            # Step 1: Click on the window to focus it
            if self.root:
                self.root.after(0, self.log_status, f"Clicking Claude window at ({x}, {y})")

            pyautogui.click(x, y)
            time.sleep(0.5)  # Wait for focus

            # Step 2: Paste message
            # NOTE: Removed /clear command as it was causing window to close
            # Claude Code maintains context across messages which is actually beneficial
            if self.root:
                self.root.after(0, self.log_status, "📝 Pasting perpetual message...")

            pyautogui.hotkey("command", "v")
            time.sleep(0.5)  # Wait for paste to complete

            # Step 3: Click window AGAIN to ensure focus before sending
            if self.root:
                self.root.after(0, self.log_status, f"Re-focusing window at ({x}, {y})")

            pyautogui.click(x, y)

            # Step 4: Wait 3 seconds for window to be fully focused
            if self.root:
                self.root.after(0, self.log_status, "⏳ Waiting 3 seconds before sending...")

            time.sleep(3.0)  # Wait 3 seconds for focus to settle

            # Step 5: Send the message
            if self.root:
                self.root.after(0, self.log_status, "🚀 Sending message...")

            pyautogui.press("enter")

            if self.root:
                self.root.after(0, self.log_status, "✅ Perpetual message sent (continuous context)")

        except Exception as e:
            if self.root:
                self.root.after(0, self.log_status, f"❌ Error in automation sequence: {e}")

        if self.is_running and self.root:
            self.root.after(0, self.log_status, f"--- Automation Complete: Next cycle in {self.wait_minutes} minutes ---")
    
    def _paste_to_window(self, window: Dict[str, Any]) -> bool:
        """Paste DUALITY message to a specific Claude Code window (don't send)"""
        try:
            window_name = window['name']
            window_status = window.get('status', 'fresh')
            
            # Focus on the specific Terminal window
            if not self._focus_claude_window(window):
                return False
            
            # Open Claude Code with dangerous permissions flag (only if fresh)
            if window_status == 'fresh':
                if self.root:
                    self.root.after(0, self.log_status, f"⚡ Opening Claude Code with dangerous permissions in {window_name}...")
                
                pyautogui.typewrite('claude')
                pyautogui.press('return')
                # Removed unnecessary delay - using real-time processing  # Wait for Claude Code to load
            
            # Copy and paste the DUALITY message (but don't send)
            if not self._copy_to_clipboard(self.message_content):
                return False
            
            # Paste only (send_immediately=False)
            success = self.robust_paste(send_immediately=False)
            
            if success and self.root:
                self.root.after(0, self.log_status, f"✅ DUALITY message pasted to {window_name} (not sent)")
            elif self.root:
                self.root.after(0, self.log_status, f"❌ Failed to paste to {window_name}")
            
            return success
            
        except Exception as e:
            if self.root:
                self.root.after(0, self.log_status, f"Error pasting to {window['name']}: {e}")
            return False
    
    def _send_message_to_window(self, window: Dict[str, Any]) -> bool:
        """Send DUALITY message to a specific Claude Code window"""
        try:
            window_name = window['name']
            window_status = window.get('status', 'fresh')
            
            # Focus on the specific Terminal window
            if not self._focus_claude_window(window):
                return False
            
            # Open Claude Code with dangerous permissions flag
            if self.root:
                self.root.after(0, self.log_status, f"⚡ Opening Claude Code with dangerous permissions in {window_name}...")
            
            # Step 1: Open Claude Code with dangerous permissions flag
            pyautogui.typewrite('claude')
            pyautogui.press('return')
            # Removed unnecessary delay - using real-time processing  # Wait for Claude Code to load with permissions bypassed
            
            # Step 3: Copy and paste the DUALITY message
            if not self._copy_to_clipboard(self.message_content):
                return False
            
            success = self.robust_paste()
            
            if success:
                # Mark window as used since we sent a message to Claude Code
                window['status'] = 'used'
            
            if success and self.root:
                self.root.after(0, self.log_status, f"✅ DUALITY message sent to Claude Code with dangerous permissions in {window_name}")
            elif self.root:
                self.root.after(0, self.log_status, f"❌ Failed to execute DUALITY command in {window_name}")
            
            return success
            
        except Exception as e:
            if self.root:
                self.root.after(0, self.log_status, f"Error sending to {window['name']}: {e}")
            return False
    
    def _copy_to_clipboard(self, text: str) -> bool:
        """Simple clipboard copy based on working archive implementation"""
        try:
            pyperclip.copy(text)
            # Removed unnecessary delay - using real-time processing
            
            # Verify clipboard content
            clipboard_content = pyperclip.paste()
            expected_len = len(text)
            actual_len = len(clipboard_content)
            
            if actual_len < expected_len:
                if self.root:
                    self.root.after(0, self.log_status, f"WARNING: Clipboard ({actual_len}) shorter than message ({expected_len}). Truncated?")
                else:
                    print(f"WARNING: Clipboard ({actual_len}) shorter than message ({expected_len}). Truncated?")
                    
            return True
            
        except Exception as e:
            if self.root:
                self.root.after(0, self.log_status, f"ERROR: Clipboard copy failed: {e}")
            else:
                print(f"ERROR: Clipboard copy failed: {e}")
            return False
    
    def _activate_claude_text_field(self) -> bool:
        """Press Enter to activate Claude Code text field if needed"""
        try:
            if pyautogui:
                # Press Enter to handle any initial prompt and activate text field
                pyautogui.press("return")
                # Removed unnecessary delay - using real-time processing  # Wait for text field to activate
                return True
            else:
                print("⚠️ PyAutoGUI not available - cannot activate text field")
                return False
        except Exception as e:
            error_msg = f"❌ Text field activation error: {e}"
            if self.root:
                self.root.after(0, self.log_status, error_msg)
            else:
                print(error_msg)
            return False
    
    def _send_clear_command(self) -> bool:
        """Send /clear command to Claude Code to reset context"""
        try:
            if pyautogui:
                # Type the /clear command
                pyautogui.typewrite("/clear", interval=0.05)
                # Removed unnecessary delay - using real-time processing
                pyautogui.press("return")
                # Removed unnecessary delay - using real-time processing  # Wait for clear to process
                return True
            else:
                print("⚠️ PyAutoGUI not available - cannot send /clear command")
                return False
        except Exception as e:
            error_msg = f"❌ Clear command error: {e}"
            if self.root:
                self.root.after(0, self.log_status, error_msg)
            else:
                print(error_msg)
            return False
    
    def robust_paste(self, send_immediately=False):
        """Simple paste method - can paste only or paste+send"""
        try:
            if self.root:
                self.root.after(0, self.log_status, "📋 Pasting clipboard content...")
            else:
                print("📋 Pasting clipboard content...")
            
            # Simple paste operation
            # Removed unnecessary delay - using real-time processing
            pyautogui.hotkey("command", "v")
            # Removed unnecessary delay - using real-time processing
            
            if send_immediately:
                pyautogui.press("enter")
                if self.root:
                    self.root.after(0, self.log_status, "✅ Paste and send completed")
                else:
                    print("✅ Paste and send completed")
            else:
                if self.root:
                    self.root.after(0, self.log_status, "✅ Paste completed (not sent)")
                else:
                    print("✅ Paste completed (not sent)")
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Paste error: {e}"
            if self.root:
                self.root.after(0, self.log_status, error_msg)
            else:
                print(error_msg)
            return False
    
    def send_trigger_message(self):
        """Send the trigger message to activate Claude Code"""
        try:
            if self.root:
                self.root.after(0, self.log_status, "⚡ Sending trigger message...")
            else:
                print("⚡ Sending trigger message...")
            
            # Removed unnecessary delay - using real-time processing
            pyautogui.typewrite("!")
            # Removed unnecessary delay - using real-time processing
            pyautogui.press("enter")
            
            if self.root:
                self.root.after(0, self.log_status, "✅ Trigger message sent!")
            else:
                print("✅ Trigger message sent!")
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Trigger message error: {e}"
            if self.root:
                self.root.after(0, self.log_status, error_msg)
            else:
                print(error_msg)
            return False
    
    def _try_send_message_methods(self):
        """Try multiple methods to send message in Claude Code"""
        methods = [
            ("Return key", lambda: pyautogui.press("return")),
            ("Enter key", lambda: pyautogui.press("enter")),
            ("Command+Return", lambda: pyautogui.hotkey("command", "return")),
            ("Shift+Return", lambda: pyautogui.hotkey("shift", "return")),
            ("Control+Return", lambda: pyautogui.hotkey("ctrl", "return")),
            ("Tab then Return", lambda: (pyautogui.press("tab"), pyautogui.press("return"))),
            ("Escape then Return", lambda: (pyautogui.press("escape"), pyautogui.press("return"))),
            ("Double Return", lambda: (pyautogui.press("return"), pyautogui.press("return"))),
            ("Function+Return", lambda: pyautogui.hotkey("fn", "return")),
            ("Option+Return", lambda: pyautogui.hotkey("option", "return"))
        ]
        
        for method_name, method_func in methods:
            try:
                if self.root:
                    self.root.after(0, self.log_status, f"🔄 Trying: {method_name}")
                else:
                    print(f"🔄 Trying: {method_name}")
                
                method_func()
                # Removed unnecessary delay - using real-time processing  # Wait to see if message was sent
                
                if self.root:
                    self.root.after(0, self.log_status, f"✅ Attempted: {method_name}")
                else:
                    print(f"✅ Attempted: {method_name}")
                
                return True
                
            except Exception as e:
                if self.root:
                    self.root.after(0, self.log_status, f"❌ {method_name} failed: {e}")
                else:
                    print(f"❌ {method_name} failed: {e}")
                continue
        
        return False
    
    def wait_with_countdown(self, seconds: int):
        """Wait with countdown display"""
        self.countdown_active = True
        self.countdown_seconds = seconds
        self.wait_time_changed = False
        
        while self.countdown_seconds > 0 and self.is_running and self.countdown_active:
            if self.wait_time_changed:
                self.countdown_seconds = int(self.wait_minutes * 60)
                self.wait_time_changed = False
                if self.root:
                    self.root.after(0, self.log_status, f"Countdown restarted: {self.wait_minutes:.1f} minutes")
            
            minutes, secs = divmod(self.countdown_seconds, 60)
            countdown_text = f"Next cycle in: {minutes:02d}:{secs:02d}"
            if self.countdown_label:
                self.root.after(0, self.countdown_label.config, {"text": countdown_text})
            
            time.sleep(1)
            self.countdown_seconds -= 1
        
        if self.countdown_label:
            self.root.after(0, self.countdown_label.config, {"text": ""})
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                self.wait_minutes = float(config.get('wait_minutes', 12.0))
                if self.wait_var:
                    self.wait_var.set(self.wait_minutes)
                
                self.num_claude_windows = int(config.get('num_claude_windows', 3))
                if self.num_windows_var:
                    self.num_windows_var.set(self.num_claude_windows)
                
                self.custom_user_message = config.get('custom_user_message', '')
                if self.custom_message_text and self.custom_user_message:
                    self.custom_message_text.delete(1.0, tk.END)
                    self.custom_message_text.insert(1.0, self.custom_user_message)
                
                self.preferred_key_method = config.get('preferred_key_method', 'Command+Return')
                self.claude_windows = config.get('claude_windows', [])
                self.dark_mode = config.get('dark_mode', True)
                
                # Load click location
                self.protocol_window_location = config.get('protocol_window_location', None)

                # Load cycle counter
                self.cycle_number = config.get('cycle_number', 0)
                
                # Migration from old terminal_tabs format if needed
                if not self.claude_windows and 'terminal_tabs' in config:
                    # Convert old format to new format
                    old_tabs = config.get('terminal_tabs', [])
                    for i, tab in enumerate(old_tabs):
                        if tab.get('active', True):
                            new_window = {
                                "name": f"Claude-{i+1}",
                                "index": i,
                                "status": "fresh",
                                "created": datetime.datetime.now().isoformat()
                            }
                            self.claude_windows.append(new_window)
                
                if self.windows_listbox:
                    self.update_window_display()
                
                # Update click location status in GUI
                if hasattr(self, 'window_status'):
                    if self.protocol_window_location:
                        x, y = self.protocol_window_location
                        self.window_status.config(text=f"Window: ({x}, {y})", foreground="green")
                
        except Exception as e:
            print(f"Error loading config: {e}")
            # Set defaults
            self.claude_windows = []
            self.num_claude_windows = 3
            self.custom_user_message = ""
            self.preferred_key_method = "Command+Return"
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'wait_minutes': self.wait_minutes,
                'num_claude_windows': self.num_claude_windows,
                'custom_user_message': self.custom_user_message,
                'preferred_key_method': self.preferred_key_method,
                'claude_windows': self.claude_windows,
                'dark_mode': self.dark_mode,
                'protocol_window_location': self.protocol_window_location,
                'cycle_number': self.cycle_number,
                'last_updated': datetime.datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def log_status(self, message: str):
        """Log status message"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        status_text = f"[{timestamp}] {message}"
        print(status_text)
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.config(text=message)
    
    def on_close(self):
        """Handle window close"""
        self.log_status("Shutting down...")
        self.is_shutting_down = True
        
        # Stop backup system
        self.backup_running = False
        if self.backup_thread and self.backup_thread.is_alive():
            self.backup_thread.join(timeout=2.0)
        
        self.stop_pulse()
        self.save_config()
        if self.root:
            self.root.destroy()
    
    def start_backup_system(self):
        """Start the hourly backup system"""
        try:
            # Ensure backup directory exists
            os.makedirs(self.backup_base_directory, exist_ok=True)
            
            # Start backup thread
            self.backup_running = True
            self.backup_thread = threading.Thread(target=self.backup_worker, daemon=True)
            self.backup_thread.start()
            
            self.log_status("✅ Backup system started - hourly automated backups to compressed format")
            
        except Exception as e:
            self.log_status(f"❌ Error starting backup system: {e}")
    
    def backup_worker(self):
        """Background worker for automated backups"""
        try:
            # Create initial backup immediately
            self.create_backup()
            
            # Then run hourly backups
            while self.backup_running and not self.is_shutting_down:
                # Sleep for 1 hour (3600 seconds)
                for _ in range(3600):
                    if not self.backup_running or self.is_shutting_down:
                        break
                    time.sleep(1)
                
                if self.backup_running and not self.is_shutting_down:
                    self.create_backup()
        
        except Exception as e:
            self.log_status(f"❌ Backup worker error: {e}")
    
    def create_backup(self):
        """Create a compressed backup of DUALITY-ZERO"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"DUALITY-ZERO-BACKUP_{timestamp}.tar.gz"
            backup_path = os.path.join(self.backup_base_directory, backup_filename)
            
            self.log_status(f"🗜️ Creating compressed backup: {backup_filename}")
            
            # Check disk space before backup
            if not self.check_disk_space():
                self.cleanup_old_backups(force=True)
                if not self.check_disk_space():
                    self.log_status("❌ Insufficient disk space for backup even after cleanup")
                    return
            
            # Create compressed tar.gz backup
            with tarfile.open(backup_path, 'w:gz', compresslevel=6) as tar:
                # Add all DUALITY-ZERO contents except backup directory itself
                for item in os.listdir(self.source_directory):
                    item_path = os.path.join(self.source_directory, item)
                    if os.path.basename(item_path) != "DUALITY-ZERO-BACKUP":
                        arcname = os.path.join("DUALITY-ZERO", item)
                        tar.add(item_path, arcname=arcname)
            
            # Get backup size for logging
            backup_size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            self.log_status(f"✅ Backup created: {backup_filename} ({backup_size_mb:.1f} MB)")
            
            # Cleanup old backups if needed
            self.cleanup_old_backups()
            
        except Exception as e:
            self.log_status(f"❌ Backup creation error: {e}")
    
    def check_disk_space(self):
        """Check if disk space is within 50% usage limit"""
        try:
            backup_disk = os.path.dirname(self.backup_base_directory)
            total, used, free = shutil.disk_usage(backup_disk)
            usage_percent = (used / total) * 100
            
            if usage_percent > self.max_disk_usage_percent:
                self.log_status(f"⚠️ Disk usage {usage_percent:.1f}% exceeds {self.max_disk_usage_percent}% limit")
                return False
            
            return True
            
        except Exception as e:
            self.log_status(f"❌ Disk space check error: {e}")
            return False
    
    def cleanup_old_backups(self, force=False):
        """Remove old backups to maintain disk space under 50%"""
        try:
            backup_pattern = os.path.join(self.backup_base_directory, "DUALITY-ZERO-BACKUP_*.tar.gz")
            backup_files = glob.glob(backup_pattern)
            
            if not backup_files:
                return
            
            # Sort by modification time (oldest first)
            backup_files.sort(key=os.path.getmtime)
            
            total_size = sum(os.path.getsize(f) for f in backup_files)
            
            # Check disk usage
            backup_disk = os.path.dirname(self.backup_base_directory)
            total_disk, used_disk, free_disk = shutil.disk_usage(backup_disk)
            current_usage = (used_disk / total_disk) * 100
            
            # Keep at least 3 most recent backups, but remove oldest if over limit
            if force or current_usage > self.max_disk_usage_percent:
                files_to_keep = 3
                files_removed = 0
                
                # Remove oldest files until under limit or only 3 remain
                for backup_file in backup_files[:-files_to_keep]:
                    try:
                        file_size_mb = os.path.getsize(backup_file) / (1024 * 1024)
                        os.remove(backup_file)
                        files_removed += 1
                        self.log_status(f"🗑️ Removed old backup: {os.path.basename(backup_file)} ({file_size_mb:.1f} MB)")
                        
                        # Check if we're under limit now
                        total_disk, used_disk, free_disk = shutil.disk_usage(backup_disk)
                        current_usage = (used_disk / total_disk) * 100
                        if current_usage <= self.max_disk_usage_percent:
                            break
                            
                    except Exception as e:
                        self.log_status(f"❌ Error removing backup {backup_file}: {e}")
                
                if files_removed > 0:
                    self.log_status(f"✅ Cleanup complete: removed {files_removed} old backups")
            
        except Exception as e:
            self.log_status(f"❌ Backup cleanup error: {e}")
    
    def get_backup_stats(self):
        """Get backup system statistics"""
        try:
            backup_pattern = os.path.join(self.backup_base_directory, "DUALITY-ZERO-BACKUP_*.tar.gz")
            backup_files = glob.glob(backup_pattern)
            
            if not backup_files:
                return {"count": 0, "total_size_mb": 0, "oldest": None, "newest": None}
            
            total_size = sum(os.path.getsize(f) for f in backup_files)
            total_size_mb = total_size / (1024 * 1024)
            
            backup_files.sort(key=os.path.getmtime)
            oldest = os.path.basename(backup_files[0]) if backup_files else None
            newest = os.path.basename(backup_files[-1]) if backup_files else None
            
            return {
                "count": len(backup_files),
                "total_size_mb": total_size_mb,
                "oldest": oldest,
                "newest": newest
            }
            
        except Exception as e:
            self.log_status(f"❌ Error getting backup stats: {e}")
            return {"count": 0, "total_size_mb": 0, "oldest": None, "newest": None}

    def run(self):
        """Run the application"""
        if self.root:
            self.root.mainloop()

def run_headless_mode():
    """Run automation in headless mode"""
    print("🤖 DUALITY-ZERO Pulse (Co-Pilot) - Headless Mode")
    print("⚡ Starting automated Claude Code cycles with PyWinCtl window management...")
    
    # Check for PyWinCtl
    if not pwc:
        print("❌ PyWinCtl not found. Please install it:")
        print("   pip install pywinctl")
        print("   pip install pyobjc-framework-Quartz  # For macOS support")
        return False
    
    try:
        automator = DualityPulseCopilot()
        
        # Load message
        automator.generate_duality_message()
        
        print(f"📊 Configuration: {automator.num_claude_windows} Terminal windows expected")
        print("💡 To use this automation:")
        print(f"   1. Create {automator.num_claude_windows} separate Terminal windows")
        print("   2. Automation will open Claude Code with dangerous permissions flag")
        print("   3. DUALITY messages will be sent to Claude Code every 12 minutes")
        
        # Run 3 cycles for demonstration
        for cycle in range(1, 4):
            print(f"\n🔄 Automation Cycle {cycle}/3")
            print("🖥️ Step 1: Focus each Terminal window")
            print("⚡ Step 2: Open Claude Code with 'claude' (dangerous permissions enabled)")
            print("📡 Step 3: Send DUALITY telepathy message")
            print("🚀 Step 4: Claude executes with full dangerous permissions")
            
            # Simulate the full automation sequence
            if automator._copy_to_clipboard(automator.message_content):
                print("✅ DUALITY command copied to clipboard")
                print("💡 For each Terminal window:")
                print("   • Paste the claude command with Cmd+V and press Enter")
                print("   • Command executes with dangerous permissions (full freedom)")
                print("   • Claude gets complete DUALITY instructions without permission prompts")
            else:
                print("❌ Failed to copy message to clipboard")
            
            if cycle < 3:
                print("⏳ Waiting before next cycle...")
                time.sleep(5)  # Short wait for demo
        
        print("\n🎯 Headless automation complete!")
        print("🌟 Each cycle executes DUALITY commands with dangerous permissions")
        print("⚡ Claude gets full operational freedom without permission prompts")
        print(f"⚙️ Configure {automator.num_claude_windows} windows in config or use GUI mode")
        return True
        
    except Exception as e:
        print(f"❌ Headless automation error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DUALITY-ZERO Pulse Tool (Co-Pilot)')
    parser.add_argument('--headless', action='store_true', 
                       help='Run in headless mode without GUI')
    args = parser.parse_args()
    
    if args.headless or not GUI_AVAILABLE:
        success = run_headless_mode()
        sys.exit(0 if success else 1)
    else:
        app = DualityPulseCopilot()
        app.run() 