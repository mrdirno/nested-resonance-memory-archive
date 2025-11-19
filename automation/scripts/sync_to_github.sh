#!/bin/bash
# Sync DUALITY-ZERO-V2 to nested-resonance-memory-archive
# Usage: ./sync_to_github.sh

SOURCE="/Volumes/dual/DUALITY-ZERO-V2/"
DEST="/Users/aldrinpayopay/nested-resonance-memory-archive/"

echo "Syncing from $SOURCE to $DEST..."

if [ ! -d "$DEST" ]; then
    echo "Error: Destination directory $DEST does not exist."
    exit 1
fi

# Use rsync to sync files, excluding .git and other temporary files
rsync -av --progress \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    "$SOURCE" "$DEST"

echo "Sync complete. Please check the destination and commit changes."
