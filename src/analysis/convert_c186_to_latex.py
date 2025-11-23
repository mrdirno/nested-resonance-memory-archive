#!/usr/bin/env python3
"""
Convert C186 Manuscript from Markdown to LaTeX
Nature Communications submission format

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1083)
License: GPL-3.0
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Nature Communications LaTeX template structure
LATEX_PREAMBLE = r"""\documentclass[10pt,a4paper]{article}

% Nature Communications packages
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{natbib}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{lineno}

% Page formatting
\usepackage[margin=1in]{geometry}
\linenumbers

% Title and author
\title{Resilience Through Redundancy: Hierarchical Advantage in Energy-Constrained Agent Systems}

\author{Aldrin Payopay$^{1,*}$}

\date{}

\begin{document}

\maketitle

\begin{abstract}
"""

LATEX_POSTAMBLE = r"""
\bibliographystyle{naturemag}
\bibliography{references}

\end{document}
"""

def markdown_to_latex(md_text: str) -> str:
    """
    Convert Markdown text to LaTeX format.

    Handles:
    - Headers (## → \section{}, ### → \subsection{})
    - Bold (**text** → \textbf{text})
    - Italics (*text* → \textit{text})
    - Inline code (`code` → \texttt{code})
    - Links ([text](url) → \href{url}{text})
    - Lists (- item → \item)
    - Math (⟨N⟩ → $\langle N \rangle$)
    - Greek letters (α → $\alpha$)
    """

    text = md_text

    # Convert headers
    text = re.sub(r'^## (.+)$', r'\\section{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'\\subsection{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.+)$', r'\\subsubsection{\1}', text, flags=re.MULTILINE)

    # Convert bold and italics
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)

    # Convert inline code
    text = re.sub(r'`(.+?)`', r'\\texttt{\1}', text)

    # Convert links
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\\href{\2}{\1}', text)

    # Convert lists
    lines = text.split('\n')
    in_list = False
    new_lines = []

    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                new_lines.append('\\begin{itemize}')
                in_list = True
            item_text = line.strip()[2:]
            new_lines.append(f'  \\item {item_text}')
        else:
            if in_list:
                new_lines.append('\\end{itemize}')
                in_list = False
            new_lines.append(line)

    if in_list:
        new_lines.append('\\end{itemize}')

    text = '\n'.join(new_lines)

    # Convert common math symbols
    text = text.replace('⟨N⟩', r'$\langle N \rangle$')
    text = text.replace('α', r'$\alpha$')
    text = text.replace('β', r'$\beta$')
    text = text.replace('γ', r'$\gamma$')
    text = text.replace('±', r'$\pm$')
    text = text.replace('≈', r'$\approx$')
    text = text.replace('≤', r'$\leq$')
    text = text.replace('≥', r'$\geq$')
    text = text.replace('×', r'$\times$')
    text = text.replace('→', r'$\rightarrow$')

    # Convert percentages in math context
    text = re.sub(r'(\d+\.?\d*)%', r'\1\\%', text)

    # Convert citations [1] → \cite{ref1}
    # Note: This is simplified - actual implementation needs citation key mapping
    text = re.sub(r'\[(\d+)\]', r'\\cite{ref\1}', text)

    return text

def extract_abstract(manuscript_text: str) -> str:
    """Extract abstract section from manuscript."""
    # Find abstract section (starts after title/metadata, ends at first ## header)
    lines = manuscript_text.split('\n')

    # Skip title and metadata
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('##') and 'abstract' in line.lower():
            start_idx = i + 1
            break

    # Find end of abstract
    end_idx = len(lines)
    for i in range(start_idx, len(lines)):
        if lines[i].strip().startswith('##') and 'abstract' not in lines[i].lower():
            end_idx = i
            break

    abstract_lines = lines[start_idx:end_idx]
    abstract_text = '\n'.join(abstract_lines).strip()

    # Remove any metadata lines
    abstract_text = re.sub(r'\*\*[^\*]+:\*\* .+\n?', '', abstract_text)

    return abstract_text

def extract_sections(manuscript_text: str) -> Dict[str, str]:
    """
    Extract major sections from manuscript.

    Returns dict with keys: introduction, methods, results, discussion, conclusions, references
    """

    sections = {}
    lines = manuscript_text.split('\n')

    # Define section markers
    section_markers = {
        'introduction': r'##\s+Introduction',
        'methods': r'##\s+Methods',
        'results': r'##\s+Results',
        'discussion': r'##\s+Discussion',
        'conclusions': r'##\s+Conclusions',
        'references': r'##\s+References',
    }

    # Find section boundaries
    section_starts = {}
    for i, line in enumerate(lines):
        for section_name, pattern in section_markers.items():
            if re.match(pattern, line, re.IGNORECASE):
                section_starts[section_name] = i
                break

    # Extract sections
    section_names_ordered = ['introduction', 'methods', 'results', 'discussion', 'conclusions', 'references']

    for i, section_name in enumerate(section_names_ordered):
        if section_name not in section_starts:
            continue

        start_idx = section_starts[section_name] + 1

        # Find end (start of next section or end of file)
        end_idx = len(lines)
        for next_section in section_names_ordered[i+1:]:
            if next_section in section_starts:
                end_idx = section_starts[next_section]
                break

        section_lines = lines[start_idx:end_idx]
        sections[section_name] = '\n'.join(section_lines).strip()

    return sections

def convert_manuscript_to_latex():
    """Convert C186 unified manuscript to LaTeX format."""

    papers_dir = Path('/Volumes/dual/DUALITY-ZERO-V2/papers')
    manuscript_file = papers_dir / 'c186_manuscript_unified.md'

    if not manuscript_file.exists():
        print(f"ERROR: Manuscript file not found: {manuscript_file}")
        return

    # Read manuscript
    with open(manuscript_file, 'r', encoding='utf-8') as f:
        manuscript_text = f.read()

    # Extract components
    abstract_text = extract_abstract(manuscript_text)
    sections = extract_sections(manuscript_text)

    # Build LaTeX document
    latex_parts = []

    # Preamble and title
    latex_parts.append(LATEX_PREAMBLE)

    # Abstract (trimmed version)
    abstract_trimmed_file = papers_dir / 'c186_abstract_trimmed.md'
    if abstract_trimmed_file.exists():
        with open(abstract_trimmed_file, 'r', encoding='utf-8') as f:
            trimmed_content = f.read()
            # Extract just the abstract text (198 words)
            abstract_match = re.search(r'## TRIMMED ABSTRACT.*?\n\n(.+?)\n\n\*\*Word Count:', trimmed_content, re.DOTALL)
            if abstract_match:
                abstract_latex = markdown_to_latex(abstract_match.group(1).strip())
                latex_parts.append(abstract_latex)

    latex_parts.append('\n\\end{abstract}\n\n')

    # Main sections
    section_titles = {
        'introduction': 'Introduction',
        'methods': 'Methods',
        'results': 'Results',
        'discussion': 'Discussion',
        'conclusions': 'Conclusions',
    }

    for section_key, section_title in section_titles.items():
        if section_key in sections:
            latex_parts.append(f'\\section{{{section_title}}}\n\n')
            section_latex = markdown_to_latex(sections[section_key])
            latex_parts.append(section_latex)
            latex_parts.append('\n\n')

    # References section (special handling)
    if 'references' in sections:
        latex_parts.append('\\section*{References}\n\n')
        # Note: Actual references should use BibTeX
        # For now, convert markdown references to enumerated list
        refs_latex = markdown_to_latex(sections['references'])
        latex_parts.append(refs_latex)
        latex_parts.append('\n\n')

    # Postamble
    latex_parts.append(LATEX_POSTAMBLE)

    # Combine all parts
    latex_document = ''.join(latex_parts)

    # Write LaTeX file
    output_file = papers_dir / 'c186_manuscript.tex'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_document)

    print(f"LaTeX manuscript created: {output_file}")
    print(f"Size: {len(latex_document)} characters")

    # Create placeholder BibTeX file
    bibtex_file = papers_dir / 'references.bib'
    if not bibtex_file.exists():
        bibtex_content = """% Nature Communications References
% Convert from manuscript references section

@article{levins1969,
  author = {Levins, R.},
  title = {Some demographic and genetic consequences of environmental heterogeneity for biological control},
  journal = {Bulletin of the Entomological Society of America},
  year = {1969},
  volume = {15},
  pages = {237--240}
}

@article{pulliam1988,
  author = {Pulliam, H. R.},
  title = {Sources, sinks, and population regulation},
  journal = {The American Naturalist},
  year = {1988},
  volume = {132},
  number = {5},
  pages = {652--661}
}

% Add more references from manuscript References section
"""
        with open(bibtex_file, 'w', encoding='utf-8') as f:
            f.write(bibtex_content)
        print(f"BibTeX template created: {bibtex_file}")

    # Create compilation script
    compile_script = papers_dir / 'compile_c186_latex.sh'
    compile_script_content = """#!/bin/bash
# Compile C186 LaTeX manuscript

cd "$(dirname "$0")"

echo "Compiling LaTeX manuscript..."
pdflatex c186_manuscript.tex
bibtex c186_manuscript
pdflatex c186_manuscript.tex
pdflatex c186_manuscript.tex

echo "Cleaning auxiliary files..."
rm -f *.aux *.log *.out *.bbl *.blg

echo "Done! PDF: c186_manuscript.pdf"
"""

    with open(compile_script, 'w', encoding='utf-8') as f:
        f.write(compile_script_content)
    compile_script.chmod(0o755)

    print(f"Compilation script created: {compile_script}")
    print(f"\nTo compile PDF:")
    print(f"  cd {papers_dir}")
    print(f"  ./compile_c186_latex.sh")
    print(f"\nOr using Docker:")
    print(f"  docker run --rm -v '{papers_dir}:/work' -w /work texlive/texlive:latest pdflatex c186_manuscript.tex")

    return output_file

if __name__ == '__main__':
    convert_manuscript_to_latex()
