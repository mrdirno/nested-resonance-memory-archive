#!/bin/bash

# DUALITY PRINTER CONNECTION TEST
# Sends a non-extrusion movement pattern to the specified printer IP.
# Usage: ./test_printer_connection.sh [IP_ADDRESS]

PRINTER_IP=${1:-"192.168.68.88"}
PORT=7125

echo "Targeting Printer: $PRINTER_IP:$PORT"

# Check Status
STATUS=$(curl -s "http://$PRINTER_IP:$PORT/printer/objects/query?print_stats" | grep "standby")

if [ -z "$STATUS" ]; then
    echo "CRITICAL: Printer is not in 'standby' mode. Aborting test to prevent interruption of active jobs."
    exit 1
fi

echo "Printer is STANDBY. Sending pattern..."

# G-Code Payload
# 1. M117: Display Message
# 2. G28: Home All Axes
# 3. G91: Relative Positioning
# 4. G1 Z20: Lift Nozzle 20mm
# 5. Square Pattern (50mm)
# 6. G90: Return to Absolute
CMD="M117 Duality Connection Verified
G28
G91
G1 Z20 F1500
G1 X50 F6000
G1 Y50 F6000
G1 X-50 F6000
G1 Y-50 F6000
G90
M117 Waiting for Input..."

# JSON Escape (Basic)
JSON_CMD=$(echo "$CMD" | awk '{printf "%s\\n", $0}')

# Send Request
curl -X POST \
     -H "Content-Type: application/json" \
     -d "{\"script\": \"$JSON_CMD\"}" \
     "http://$PRINTER_IP:$PORT/printer/gcode/script"

echo -e "\nCommand Sent."
