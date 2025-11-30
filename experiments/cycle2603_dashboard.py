#!/usr/bin/env python3
"""
Experiment: Cycle 2603 - The Dashboard
Goal: Implement a TUI dashboard to monitor agent states in real-time using curses.
"""

import curses
import sys
import time
import random
import math
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

# Reuse Hive Logic classes
sys.path.append(str(Path(__file__).parent))
try:
    from cycle2602_hive import Vector2, HiveAgent
    from cycle2600_protocol import AgentMessage, MessageType
except ImportError:
    # Define mocks if imports fail (fallback for standalone execution)
    @dataclass
    class Vector2:
        x: float
        y: float
        def normalize(self): return self
        def scale(self, f): return self
        def __add__(self, o): return self
        def __sub__(self, o): return self

    class HiveAgent:
        def __init__(self, aid, pos):
            self.agent_id = aid
            self.position = pos
            self.known_target = None
        def update(self, t): return None
        def receive_message(self, m): pass


class DashboardApp:
    def __init__(self):
        self.agents: List[HiveAgent] = []
        self.target = Vector2(50.0, 20.0) # Scaled for text screen
        self.running = True
        self.logs = []
        
        # Initialize simulation
        for i in range(5):
            pos = Vector2(random.uniform(5, 40), random.uniform(5, 15))
            self.agents.append(HiveAgent(f"AG-{i:02d}", pos))
            
        # Adjust physics for TUI scale (slower speed)
        for a in self.agents:
            a.speed = 0.5 
            a.sensor_range = 10.0

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 10:
            self.logs.pop(0)

    def update_simulation(self):
        broadcasts = []
        for agent in self.agents:
            msg = agent.update(self.target)
            if msg:
                broadcasts.append(msg)
                self.log(f"{agent.agent_id} found target!")
        
        for msg in broadcasts:
            for agent in self.agents:
                agent.receive_message(msg)

        # Check convergence
        near_count = 0
        for agent in self.agents:
            dist = math.sqrt((agent.position.x - self.target.x)**2 + 
                             (agent.position.y - self.target.y)**2)
            if dist < 5.0:
                near_count += 1
        
        if near_count == len(self.agents):
            self.log("ALL AGENTS CONVERGED.")

    def draw_map(self, win, height, width):
        win.box()
        win.addstr(0, 2, " [ MAP VIEW ] ")
        
        # Draw Target
        # Map coordinates: x [0, 100] -> [1, width-2], y [0, 40] -> [1, height-2]
        def map_coord(x, y):
            screen_x = int(1 + (x / 100.0) * (width - 3))
            screen_y = int(1 + (y / 40.0) * (height - 3))
            return screen_x, screen_y

        tx, ty = map_coord(self.target.x, self.target.y)
        if 0 < tx < width-1 and 0 < ty < height-1:
            try:
                win.addch(ty, tx, 'X', curses.A_BOLD | curses.A_REVERSE)
            except curses.error:
                pass

        # Draw Agents
        for agent in self.agents:
            ax, ay = map_coord(agent.position.x, agent.position.y)
            if 0 < ax < width-1 and 0 < ay < height-1:
                try:
                    char = '@' if agent.known_target else 'o'
                    win.addch(ay, ax, char)
                except curses.error:
                    pass

    def draw_status(self, win):
        win.box()
        win.addstr(0, 2, " [ AGENT STATUS ] ")
        
        for i, agent in enumerate(self.agents):
            status = "SEARCHING"
            if agent.known_target:
                status = "CONVERGING"
                dist = math.sqrt((agent.position.x - self.target.x)**2 + 
                                 (agent.position.y - self.target.y)**2)
                if dist < 2.0:
                    status = "ARRIVED"
            
            line = f"{agent.agent_id}: {status:<10} Pos({agent.position.x:.1f}, {agent.position.y:.1f})"
            try:
                win.addstr(i + 1, 2, line)
            except curses.error:
                pass

    def draw_logs(self, win):
        win.box()
        win.addstr(0, 2, " [ SYSTEM LOGS ] ")
        for i, log in enumerate(self.logs):
            try:
                win.addstr(i + 1, 2, log)
            except curses.error:
                pass

    def run(self, stdscr):
        # Setup curses
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100) # 10ms refresh

        while self.running:
            # Handle Input
            try:
                key = stdscr.getch()
                if key == ord('q'):
                    self.running = False
            except:
                pass

            # Update Sim
            self.update_simulation()

            # Draw
            stdscr.erase()
            height, width = stdscr.getmaxyx()
            
            # Partition screen
            # Top Left: Map (60% width, 100% height)
            # Top Right: Status (40% width, 50% height)
            # Bottom Right: Logs (40% width, 50% height)
            
            map_width = int(width * 0.6)
            stat_width = width - map_width
            stat_height = int(height * 0.5)
            
            try:
                map_win = stdscr.subwin(height, map_width, 0, 0)
                self.draw_map(map_win, height, map_width)
                
                stat_win = stdscr.subwin(stat_height, stat_width, 0, map_width)
                self.draw_status(stat_win)
                
                log_win = stdscr.subwin(height - stat_height, stat_width, stat_height, map_width)
                self.draw_logs(log_win)
            except curses.error:
                # Terminal too small
                stdscr.addstr(0, 0, "Terminal too small for dashboard.")

            stdscr.refresh()
            
            # Limit simulation speed
            time.sleep(0.1)

def main():
    print("Cycle 2603: The Dashboard - Launching TUI...")
    print("Press 'q' to exit the dashboard.")
    time.sleep(1)
    
    app = DashboardApp()
    try:
        curses.wrapper(app.run)
        print("Dashboard exited cleanly.")
    except Exception as e:
        print(f"Dashboard crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
