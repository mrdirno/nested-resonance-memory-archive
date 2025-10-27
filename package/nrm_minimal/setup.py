#!/usr/bin/env python3
"""
Setup script for Nested Resonance Memory (Minimal Package)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="nrm-minimal",
    version="1.0.0",
    author="Aldrin Payopay",
    author_email="aldrin.gdf@gmail.com",
    description="Minimal Nested Resonance Memory implementation for demonstration and reproducibility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrdirno/nested-resonance-memory-archive",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "psutil>=5.8.0",
        "matplotlib>=3.3.0",
    ],
    entry_points={
        "console_scripts": [
            "nrm-minimal=examples.run_minimal_experiment:main",
        ],
    },
    keywords="nested-resonance-memory fractal-agents composition-decomposition reality-grounding emergence",
    project_urls={
        "Bug Reports": "https://github.com/mrdirno/nested-resonance-memory-archive/issues",
        "Source": "https://github.com/mrdirno/nested-resonance-memory-archive",
        "Documentation": "https://github.com/mrdirno/nested-resonance-memory-archive/tree/main/package/nrm_minimal",
    },
)
