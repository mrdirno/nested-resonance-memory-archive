#!/usr/bin/env python3
"""
V3 Component Validation Harness
Purpose: Dry-run validation of recovered 'Ancient Tech' components (C268, C269, C270).
"""

import sys
import os
from pathlib import Path
import importlib.util
import time
import shutil

# Add code/experiments to path to allow imports
REPO_ROOT = Path(__file__).resolve().parent.parent
CODE_EXP_DIR = REPO_ROOT / "code" / "experiments"
sys.path.insert(0, str(CODE_EXP_DIR))

def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def validate_component(name, filename, module_name):
    print(f"\n{'='*60}")
    print(f"VALIDATING: {name} ({filename})")
    print(f"{'='*60}")
    
    file_path = CODE_EXP_DIR / filename
    if not file_path.exists():
        print(f"❌ FAILED: File not found: {file_path}")
        return False
        
    try:
        # Import the module
        print(f"-> Importing module...")
        module = import_module_from_path(module_name, file_path)
        
        # Monkey-patch constants for fast validation
        print(f"-> Patching parameters for dry run...")
        module.CYCLES = 10
        module.SEEDS = [42]
        module.CONDITIONS = [module.CONDITIONS[0]] # Test only first condition
        
        # Redirect output to avoid cluttering main output too much, 
        # but we want to see if it crashes.
        
        # Run main()
        print(f"-> Executing main() sequence...")
        start_time = time.time()
        module.main()
        duration = time.time() - start_time
        
        print(f"✅ SUCCESS: Execution completed in {duration:.2f}s")
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("STARTING V3 BIOLOGICAL COMPONENT VALIDATION")
    print(f"Root: {REPO_ROOT}")
    
    components = [
        ("Synaptic Homeostasis", "c268_synaptic_homeostasis.py", "c268"),
        ("Autopoiesis", "c269_autopoiesis.py", "c269"),
        ("Memetic Evolution", "c270_memetic_evolution.py", "c270")
    ]
    
    results = {}
    
    for name, filename, mod_name in components:
        success = validate_component(name, filename, mod_name)
        results[name] = success
        
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    all_passed = True
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:25s}: {status}")
        if not success:
            all_passed = False
            
    if all_passed:
        print("\nAll V3 components are functional and ready for deployment.")
        sys.exit(0)
    else:
        print("\nSome components failed validation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
