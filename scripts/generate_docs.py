#!/usr/bin/env python3
"""
Cycle 2454: The Documentation Layer (Gate 82)
Role: Documentation Generator
Responsibility: Auto-generate API documentation from docstrings.

Phase 61 (Digital Terraforming) Standards:
- Self-Documentation.
- Markdown Output.
- Zero External Dependencies (uses inspect/pkgutil).
"""

import os
import sys
import inspect
import pkgutil
import importlib
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("DOC_GEN")

def generate_markdown_for_module(module, module_name):
    """Generates Markdown content for a single module."""
    content = []
    content.append(f"# Module: `{module_name}`\n")
    
    if module.__doc__:
        content.append(f"{module.__doc__.strip()}\n")
    
    # Inspect classes
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module_name: # Only document classes defined in this module
            content.append(f"## Class: `{name}`\n")
            if obj.__doc__:
                content.append(f"{obj.__doc__.strip()}\n")
            
            # Inspect methods
            for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                if not method_name.startswith("_"): # Skip private methods
                    content.append(f"### Method: `{method_name}`\n")
                    if method.__doc__:
                        content.append(f"{method.__doc__.strip()}\n")
                    
                    # Signature
                    try:
                        sig = inspect.signature(method)
                        content.append(f"```python\n{name}.{method_name}{sig}\n```\n")
                    except ValueError:
                        pass

    # Inspect functions
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if obj.__module__ == module_name:
            content.append(f"## Function: `{name}`\n")
            if obj.__doc__:
                content.append(f"{obj.__doc__.strip()}\n")
            
            try:
                sig = inspect.signature(obj)
                content.append(f"```python\n{name}{sig}\n```\n")
            except ValueError:
                pass

    return "\n".join(content)

def process_package(package_name, output_dir):
    """Recursively process a package and generate docs."""
    logger.info(f"📚 Processing package: {package_name}")
    
    try:
        package = importlib.import_module(package_name)
    except ImportError as e:
        logger.error(f"❌ Failed to import {package_name}: {e}")
        return

    output_file = os.path.join(output_dir, f"{package_name.replace('.', '_')}.md")
    os.makedirs(output_dir, exist_ok=True)
    
    full_content = [f"# API Documentation: {package_name}\n"]
    
    # Walk through the package
    if hasattr(package, "__path__"):
        for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            try:
                module = importlib.import_module(modname)
                logger.info(f"   📄 Documenting: {modname}")
                md = generate_markdown_for_module(module, modname)
                full_content.append(md)
                full_content.append("---\n")
            except ImportError as e:
                logger.warning(f"   ⚠️  Skipping {modname}: {e}")
            except Exception as e:
                logger.warning(f"   ⚠️  Error in {modname}: {e}")

    # Write to file
    with open(output_file, "w") as f:
        f.write("\n".join(full_content))
    
    logger.info(f"✅ Generated: {output_file}")

if __name__ == "__main__":
    # Add src to path so we can import packages
    sys.path.append(os.path.abspath("src"))
    sys.path.append(os.path.abspath(".")) # For automation/pilot

    targets = [
        ("helios", "docs/api"),
        ("automation.pilot", "docs/api")
    ]

    logger.info("🌍 CLIMATE CONTROL: Generating Atmosphere (Documentation)...")
    
    for pkg, out in targets:
        process_package(pkg, out)
        
    logger.info("✨ Atmosphere Generated.")
