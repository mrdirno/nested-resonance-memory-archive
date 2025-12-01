#!/bin/bash

# --- CONFIGURATION ---
CONTAINER_NAME="fenicsx_acoustic_sim_test"
IMAGE_NAME="duality-fenicsx"
PROJECT_ROOT="/app" # Inside container
HOST_PROJECT_ROOT="/Volumes/dual/DUALITY-ZERO-V2" # On host machine

# --- PULL OR BUILD IMAGE (IF NOT ALREADY BUILT) ---
# Check if image exists locally
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo "Image '$IMAGE_NAME' not found locally. Attempting to build..."
    docker build -t "$IMAGE_NAME" -f Dockerfile.fenicsx .
    if [ $? -ne 0 ]; then
        echo "Error: Docker image build failed. Exiting."
        exit 1
    fi
else
    echo "Image '$IMAGE_NAME' found locally."
fi

# --- RUN CONTAINER AND EXECUTE SCRIPT ---
echo "Running FEniCSx container and executing acoustic solver test script..."

# This command runs the container, mounts the volume, and executes the Python script.
# The --rm flag ensures the container is removed after execution.
docker run -ti --rm \
    -v "${HOST_PROJECT_ROOT}:${PROJECT_ROOT}" \
    --name "${CONTAINER_NAME}" \
    "${IMAGE_NAME}" \
    /bin/bash -c "conda run -n fenicsx-env python3 ${PROJECT_ROOT}/fabrication/analysis/fenicsx_acoustic_solver.py"

if [ $? -ne 0 ]; then
    echo "Error: FEniCSx test script execution failed inside Docker."
    exit 1
else
    echo "FEniCSx test script executed successfully inside Docker."
fi

echo "Docker container finished."
