#!/usr/bin/env python3
"""
HELIOS Command Line Interface
The Cockpit for the Type 3 Operating System.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 3 Pro (MOG Pilot)
"""
import cmd
import sys
import os
import time

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from code.helios.operator import UniversalOperator

class HeliosShell(cmd.Cmd):
    intro = '\n========================================\n   HELIOS TYPE 3 OS - UNIVERSAL SHELL   \n========================================\nInitializing Physics Engine...\n'
    prompt = 'HELIOS> '
    
    def preloop(self):
        try:
            self.op = UniversalOperator(resolution_mm=4.0) # Low res for interactive speed
            print(f"System Online. {len(self.op.emitters)} Emitters Active.")
            print("Type 'help' for commands.\n")
        except Exception as e:
            print(f"CRITICAL FAILURE: {e}")
            sys.exit(1)

    def do_create(self, arg):
        'Create an object: create [shape] [x] [y] [z]'
        args = arg.split()
        if len(args) != 4:
            print("Usage: create [shape] [x] [y] [z]")
            return
            
        shape = args[0]
        try:
            x = float(args[1])
            y = float(args[2])
            z = float(args[3])
            
            print(f"Compiling {shape} at ({x}, {y}, {z})...")
            start_time = time.time()
            obj_id = self.op.create_object(shape, (x, y, z))
            elapsed = time.time() - start_time
            
            stability = self.op.get_stability(obj_id)
            print(f">> Object {obj_id} Created in {elapsed:.2f}s.")
            print(f">> Stability Ratio: {stability:.4f}")
            
        except ValueError:
            print("Error: Coordinates must be numbers.")
        except Exception as e:
            print(f"Error: {e}")

    def do_list(self, arg):
        'List all active objects'
        if not self.op.active_objects:
            print("No active objects.")
            return
            
        print(f"{'ID':<5} {'TYPE':<10} {'LOCATION':<20} {'STABILITY':<10}")
        print("-" * 50)
        for oid, data in self.op.active_objects.items():
            loc = f"({data['location'][0]:.0f}, {data['location'][1]:.0f}, {data['location'][2]:.0f})"
            stab = self.op.get_stability(oid)
            print(f"{oid:<5} {data['type']:<10} {loc:<20} {stab:.4f}")

    def do_status(self, arg):
        'Check status of an object: status [id]'
        if not arg:
            print("Usage: status [id]")
            return
            
        try:
            oid = int(arg)
            stab = self.op.get_stability(oid)
            if stab < 0:
                print("Object not found.")
            else:
                print(f"Object {oid} Stability: {stab:.4f}")
        except ValueError:
            print("Error: ID must be an integer.")

    def do_exit(self, arg):
        'Exit the shell'
        print("Shutting down HELIOS...")
        return True
        
    def do_quit(self, arg):
        return self.do_exit(arg)
        
    def do_EOF(self, arg):
        print()
        return self.do_exit(arg)

if __name__ == '__main__':
    HeliosShell().cmdloop()
