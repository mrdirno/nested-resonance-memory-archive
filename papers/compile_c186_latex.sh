#!/bin/bash
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
