# Dockerfile for Nested Resonance Memory Research
#
# Build: docker build -t nested-resonance-memory .
# Run:   docker run -it nested-resonance-memory
#
# Author: Aldrin Payopay <aldrin.gdf@gmail.com>
# Repository: https://github.com/mrdirno/nested-resonance-memory-archive
# License: GPL-3.0

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Set Python path to include code directory
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Default working directory for experiments
WORKDIR /app/code/experiments

# Default command: interactive bash
CMD ["/bin/bash"]
