
import os

# Configuration
output_file = "papers/PAPER3_MASTER_MANUSCRIPT.md"
files_to_combine = [
    "papers/PAPER3_ABSTRACT.md",
    "papers/PAPER3_SECTION1_INTRODUCTION.md",
    "papers/PAPER3_SECTION2_THEORETICAL_FRAMEWORK.md",
    "papers/PAPER3_SECTION3_METHODS.md",
    "papers/PAPER3_SECTION4_RESULTS.md",
    "papers/PAPER3_SECTION5_DISCUSSION.md",
    "papers/PAPER3_SECTION6_CONCLUSIONS.md",
    "papers/PAPER3_REFERENCES.md"
]

# Main Title Block
title_block = """# Encoding Discoverable Patterns: Temporal Stewardship in Computational Research Systems

**Authors:** Aldrin Payopay, Claude (DUALITY-ZERO-V2)
**Date:** November 25, 2025

---

"""

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the start of the actual content (first H2 header '## ')
    # This skips the H1 title and metadata block
    start_index = content.find('\n## ')
    if start_index == -1:
        # Fallback: try looking for just '## ' at the start if no newline preceeds it (rare)
        start_index = content.find('## ')
    
    if start_index != -1:
        # Return content including the '## '
        # The +1 is to skip the newline character if we found '\n## '
        if content[start_index] == '\n':
             return content[start_index+1:]
        return content[start_index:]
    else:
        # If no H2 found, return whole file (fallback)
        print(f"Warning: No '## ' header found in {filepath}. Appending whole file.")
        return content

def main():
    full_content = title_block
    
    for filepath in files_to_combine:
        if os.path.exists(filepath):
            print(f"Processing {filepath}...")
            section_content = process_file(filepath)
            full_content += section_content + "\n\n"
        else:
            print(f"Error: File not found: {filepath}")
            return

    with open(output_file, 'w') as f:
        f.write(full_content)
    
    print(f"\nSuccessfully created {output_file}")
    print(f"Total size: {len(full_content)} characters")

if __name__ == "__main__":
    main()
