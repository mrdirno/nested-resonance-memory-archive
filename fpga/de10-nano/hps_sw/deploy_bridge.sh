#!/bin/bash
set -e

TARGET_IP="192.168.68.57"
TARGET_USER="root"
REMOTE_DIR="/home/root"
LOCAL_BIN="bridge_server"

echo "========================================"
echo "Deploying Bridge Server to $TARGET_IP"
echo "========================================"

# 1. Check for binary
if [ ! -f "$LOCAL_BIN" ]; then
    echo "Error: $LOCAL_BIN not found. Run 'make' first."
    exit 1
fi

# 2. Copy binary
echo "Transferring binary..."
scp -o StrictHostKeyChecking=no "$LOCAL_BIN" "$TARGET_USER@$TARGET_IP:$REMOTE_DIR/"

# 3. Kill existing instance (if any)
echo "Stopping existing server..."
ssh -o StrictHostKeyChecking=no "$TARGET_USER@$TARGET_IP" "killall -q bridge_server || true"

# 4. Start new instance
echo "Starting bridge server..."
# using nohup and redirecting output to avoid hanging the ssh session
ssh -o StrictHostKeyChecking=no "$TARGET_USER@$TARGET_IP" "nohup $REMOTE_DIR/bridge_server > $REMOTE_DIR/bridge.log 2>&1 &"

echo "Deployment complete. Bridge server running in background."
echo "Logs available at $TARGET_IP:$REMOTE_DIR/bridge.log"
