#!/bin/bash
# Process results for C256-C260 batch

echo "Processing C256 (H1xH4)..."
python3 automate_batch_completion.py --cycle 256 --m1 H1 --m2 H4

echo "Processing C257 (H1xH5)..."
python3 automate_batch_completion.py --cycle 257 --m1 H1 --m2 H5

echo "Processing C258 (H2xH4)..."
python3 automate_batch_completion.py --cycle 258 --m1 H2 --m2 H4

echo "Processing C259 (H2xH5)..."
python3 automate_batch_completion.py --cycle 259 --m1 H2 --m2 H5

echo "Processing C260 (H4xH5)..."
python3 automate_batch_completion.py --cycle 260 --m1 H4 --m2 H5

echo "All processing complete."
