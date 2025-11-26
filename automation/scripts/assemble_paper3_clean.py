
import os

# Configuration
SOURCE_DIR = "papers"
OUTPUT_FILE = "papers/PAPER3_SUBMISSION_READY.md"

FILES = [
    "PAPER3_ABSTRACT.md",
    "PAPER3_SECTION1_INTRODUCTION.md",
    "PAPER3_SECTION2_THEORETICAL_FRAMEWORK.md",
    "PAPER3_SECTION3_METHODS.md",
    "PAPER3_SECTION4_RESULTS.md",
    "PAPER3_SECTION5_DISCUSSION.md",
    "PAPER3_SECTION6_CONCLUSIONS.md",
    "PAPER3_REFERENCES.md"
]

TITLE_BLOCK = """---
title: "Encoding Discoverable Patterns: Temporal Stewardship in Computational Research Systems"
author:
- Aldrin Payopay
- Claude (DUALITY-ZERO-V2)
date: 2025-11-26
---
"""

def clean_file_content(filename, content):
    lines = content.split('\n')
    cleaned_lines = []
    
    # Logic: 
    # 1. Find the start of real content (usually after the first '---' and a blank line, or looking for '##')
    # 2. Find the end of real content (usually before the last '---')
    
    start_index = 0
    end_index = len(lines)
    
    # Detect Start (Skip metadata block)
    # Look for the first '---' separator
    separator_count = 0
    for i, line in enumerate(lines):
        if line.strip() == '---':
            separator_count += 1
            if separator_count == 1:
                start_index = i + 1
                break
    
    # Detect End (Skip footer block)
    # Look for the last '---' separator
    # We search backwards
    for i in range(len(lines) - 1, -1, -1):
        if line.strip() == '---':
            # Check if this is the footer separator (usually followed by Status lines)
            # Heuristic: If we are near the end
            if i > len(lines) - 20:
                end_index = i
                break
                
    # Special case for References (start is ## REFERENCES, no metadata block '---' in snippet shown? 
    # actually snippet shows ### A, but let's assume consistency or check snippet)
    # Snippet for references showed "### A" starting around line 1894. 
    # Let's rely on the standard format observed in Abstract/Intro.
    
    # Extract content
    content_lines = lines[start_index:end_index]
    
    # Trim leading/trailing whitespace
    while content_lines and not content_lines[0].strip():
        content_lines.pop(0)
    while content_lines and not content_lines[-1].strip():
        content_lines.pop()
        
    return "\n".join(content_lines)

def assemble():
    full_text = [TITLE_BLOCK]
    
    for filename in FILES:
        path = os.path.join(SOURCE_DIR, filename)
        if not os.path.exists(path):
            print(f"Error: {filename} not found.")
            return
            
        with open(path, 'r') as f:
            raw_content = f.read()
            
        cleaned = clean_file_content(filename, raw_content)
        full_text.append(cleaned)
        full_text.append("\n\n") # Spacing between sections
        
    with open(OUTPUT_FILE, 'w') as f:
        f.write("".join(full_text))
        
    print(f"Successfully assembled {OUTPUT_FILE} with {len(full_text)} sections.")

if __name__ == "__main__":
    assemble()
