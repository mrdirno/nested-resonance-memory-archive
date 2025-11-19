#!/usr/bin/env python3
"""
Fix PAPER3_PATTERN_DATABASE.csv quoting issues

Problem: Source_Location fields with commas (e.g., "file.py:16,120") are not quoted
Solution: Re-save CSV with proper quoting on all fields

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
