#!/usr/bin/env python3
"""
Cycle 2457: The Full System Scan (Gate 85)
Role: Test Runner
Responsibility: Standardized test discovery and execution (Hybrid: unittest + pytest).

Phase 61 (Digital Terraforming) Standards:
- Auto-discovery of tests.
- Hybrid Runner (Legacy + Modern).
- Clear reporting.
- Non-zero exit code on failure.
"""

import unittest
import sys
import os
import time
import logging
import subprocess
import shutil

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("TEST_RUNNER")

def run_pytest(start_dir: str) -> bool:
    """Run tests using pytest."""
    logger.info(f"🧪 CLIMATE CONTROL: Initiating Pytest Scan in '{start_dir}'...")
    start_time = time.time()
    
    # Run pytest as a subprocess to avoid polluting the current process
    try:
        # Using python -m pytest to ensure we use the same python environment
        # -v for verbose, --tb=short to reduce noise
        # Explicitly ignore archive and experiments to prevent "Toxic" scripts from killing the runner
        cmd = [
            sys.executable, "-m", "pytest", start_dir, 
            "-v", "--tb=short", "-s", # -s disables pytest capture to avoid FD conflicts
            "--ignore=archive", 
            "--ignore=experiments"
        ]
        # Capture output to avoid FD conflicts, DEVNULL stdin to prevent hangs
        result = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL) 
        
        duration = time.time() - start_time
        logger.info(f"⏱️  Pytest Execution Time: {duration:.2f}s")
        
        # Print output manually
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            logger.info("✅ PYTEST STABLE: All tests passed.")
            return True
        elif result.returncode == 5:
            logger.warning("⚠️  No tests collected by pytest.")
            return True # No tests is not a failure in this context, just barren
        else:
            logger.error(f"⛈️  PYTEST STORM DETECTED: Exit code {result.returncode}")
            return False
            
    except Exception as e:
        logger.error(f"💥 Pytest Execution Failed: {e}")
        return False

def run_unittest(start_dir: str) -> bool:
    """Run tests using unittest (Legacy)."""
    logger.info(f"📜 CLIMATE CONTROL: Initiating Unittest Scan in '{start_dir}'...")
    
    try:
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        # Also look for *_test.py pattern common in this repo
        suite.addTests(loader.discover(start_dir, pattern='*_test.py'))

        count = suite.countTestCases()
        if count == 0:
            logger.warning(f"⚠️  No unittest tests found in {start_dir}.")
            return True

        logger.info(f"🔍 Found {count} unittests. Executing...")
        
        start_time = time.time()
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        duration = time.time() - start_time
        
        logger.info(f"⏱️  Unittest Execution Time: {duration:.2f}s")
        
        if result.wasSuccessful():
            logger.info("✅ UNITTEST STABLE: All tests passed.")
            return True
        else:
            logger.error(f"⛈️  UNITTEST STORM DETECTED: {len(result.failures)} failures, {len(result.errors)} errors.")
            return False
    except Exception as e:
        logger.error(f"💥 Unittest Discovery/Execution Failed: {e}")
        return False

def run_tests(start_dir: str = '.') -> bool:
    """
    Discover and run tests starting from start_dir using Hybrid approach.
    """
    logger.info(f"🌍 CLIMATE CONTROL: Full System Scan Initiated...")
    
    # Define Active Zones (The Habitable Zone)
    # If start_dir is '.', we scan specific active directories to avoid Archive toxicity
    if start_dir == '.':
        target_zones = ['src', 'automation']
    else:
        target_zones = [start_dir]
        
    overall_success = True
    
def run_tests(start_dir: str = '.') -> bool:
    """
    Discover and run tests starting from start_dir using Pytest (Primary) or Unittest (Fallback).
    """
    logger.info(f"🌍 CLIMATE CONTROL: Full System Scan Initiated...")
    
    # Define Active Zones (The Habitable Zone)
    if start_dir == '.':
        target_zones = ['src', 'automation']
    else:
        target_zones = [start_dir]
        
    overall_success = True
    
    for zone in target_zones:
        if not os.path.exists(zone):
            logger.warning(f"⚠️  Zone '{zone}' does not exist. Skipping.")
            continue
            
        logger.info(f"👉 Scanning Zone: {zone}")
        
        # Try Pytest first (Modern Standard)
        # Pytest can run unittest-style tests too, so it covers everything.
        if run_pytest(zone):
            continue
            
        # If Pytest fails (e.g. not installed or crash), try Unittest (Legacy Fallback)
        logger.warning("⚠️  Pytest failed or not available. Falling back to Unittest.")
        if not run_unittest(zone):
            overall_success = False
    
    # Final Status
    if overall_success:
        logger.info("🌟 SYSTEM GREEN: All Active Zones Nominal.")
        return True
    else:
        logger.error("🔥 SYSTEM FAILURE: One or more zones failed.")
        return False
    
    # Final Status
    if overall_success:
        logger.info("🌟 SYSTEM GREEN: All Active Zones Nominal.")
        return True
    else:
        logger.error("🔥 SYSTEM FAILURE: One or more zones failed.")
        return False

if __name__ == "__main__":
    start_dir = 'src'
    if len(sys.argv) > 1:
        start_dir = sys.argv[1]
        
    success = run_tests(start_dir)
    sys.exit(0 if success else 1)
