# Base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Copy source code
COPY experiments/ /app/experiments/
COPY helios_one/ /app/helios_one/
COPY src/ /app/src/

# Install system dependencies (for curses if needed, though dashboard is TUI)
# For a headless container, we might not need curses, but useful for debugging.
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

# Set Python path
ENV PYTHONPATH=/app

# Expose API port
EXPOSE 8081

# Entrypoint: Run the Controller
CMD ["python3", "experiments/cycle2607_controller.py"]
