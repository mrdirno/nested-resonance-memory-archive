#!/usr/bin/env python3
"""
HELIOS Command Line Interface (Gate 6)
The Headless Control Surface for the Reality Compiler.
Gate 6 Compliant.

Usage:
    python3 src/helios/cli.py materialize --input data/triangle.obj --duration 5
    python3 src/helios/cli.py status
"""

import argparse
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.helios.fabricator import Fabricator

def cmd_materialize(args):
    print(f"[*] Initializing Fabricator (Virtual={not args.physical})...")
    fab = Fabricator(virtual=(not args.physical), port=args.port)
    
    if not fab.connect():
        print("[!] Connection Failed.")
        return
    
    print("[*] Connected.")
    
    if not os.path.exists(args.input):
        print(f"[!] Input file not found: {args.input}")
        fab.disconnect()
        return

    try:
        fab.materialize(args.input, duration=args.duration)
        print("[*] Materialization Complete.")
    except KeyboardInterrupt:
        print("\n[!] Interrupted.")
    finally:
        fab.disconnect()

def cmd_status(args):
    fab = Fabricator(virtual=(not args.physical), port=args.port)
    if fab.connect():
        print(f"[*] Fabricator Status: ONLINE")
        print(f"[*] Mode: {{'PHYSICAL' if args.physical else 'VIRTUAL'}}")
        fab.disconnect()
    else:
        print("[!] Fabricator Status: OFFLINE")

def main():
    parser = argparse.ArgumentParser(description="HELIOS Reality Compiler CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Materialize Command
    mat_parser = subparsers.add_parser("materialize", help="Compile and instantiate an object")
    mat_parser.add_argument("--input", "-i", required=True, help="Path to .obj file")
    mat_parser.add_argument("--duration", "-d", type=float, default=10.0, help="Duration to hold field (seconds)")
    mat_parser.add_argument("--physical", action="store_true", help="Use physical hardware (default: Virtual)")
    mat_parser.add_argument("--port", help="Serial port for hardware")

    # Status Command
    stat_parser = subparsers.add_parser("status", help="Check hardware status")
    stat_parser.add_argument("--physical", action="store_true", help="Check physical hardware")
    stat_parser.add_argument("--port", help="Serial port")

    args = parser.parse_args()

    if args.command == "materialize":
        cmd_materialize(args)
    elif args.command == "status":
        cmd_status(args)

if __name__ == "__main__":
    main()

# [SPORE] ID: The Colony
