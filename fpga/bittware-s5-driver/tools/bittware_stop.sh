#!/bin/bash
# BittWare S5 FPGA Stop Script
# This script is called by the systemd service to stop the driver

set -e

LOG_FILE="/var/log/bittware_s5.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a $LOG_FILE
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a $LOG_FILE
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a $LOG_FILE
}

# Function to stop monitoring process
stop_monitoring() {
    log_message "Stopping performance monitoring..."
    
    if [ -f /var/run/bittware_s5_monitor.pid ]; then
        local pid=$(cat /var/run/bittware_s5_monitor.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            log_success "Performance monitoring stopped"
        fi
        rm -f /var/run/bittware_s5_monitor.pid
    fi
}

# Function to disable network interfaces
disable_network() {
    log_message "Disabling network interfaces..."
    
    for interface in $(ip link show | grep "bw_eth" | cut -d: -f2 | tr -d ' '); do
        log_message "Disabling interface $interface"
        ip link set dev $interface down 2>/dev/null && \
            log_success "Interface $interface disabled" || \
            log_warning "Failed to disable $interface"
    done
}

# Function to unload kernel modules
unload_modules() {
    log_message "Unloading BittWare S5 kernel modules..."
    
    # Unload in reverse order
    local modules=("bittware_net" "bittware_dma" "bittware_s5")
    
    for module in "${modules[@]}"; do
        if lsmod | grep -q "$module"; then
            log_message "Unloading module $module"
            rmmod "$module" 2>/dev/null && \
                log_success "Module $module unloaded" || \
                log_error "Failed to unload module $module"
        else
            log_message "Module $module not loaded"
        fi
    done
}

# Function to cleanup device nodes
cleanup_devices() {
    log_message "Cleaning up device nodes..."
    
    # Device nodes are automatically removed when modules are unloaded
    # Just verify they're gone
    if ls /dev/bittware_* >/dev/null 2>&1; then
        log_warning "Some device nodes still exist"
    else
        log_success "All device nodes cleaned up"
    fi
}

# Function to reset PCIe devices
reset_pcie() {
    log_message "Resetting PCIe devices..."
    
    # Find BittWare devices
    local devices=$(lspci -d 1172: | cut -d' ' -f1)
    
    for device in $devices; do
        log_message "Resetting PCIe device $device"
        
        # Reset device (if supported)
        if [ -w "/sys/bus/pci/devices/0000:$device/reset" ]; then
            echo 1 > "/sys/bus/pci/devices/0000:$device/reset" 2>/dev/null || true
            log_success "PCIe device $device reset"
        else
            log_message "PCIe device $device does not support reset"
        fi
    done
}

# Function to save statistics before shutdown
save_statistics() {
    log_message "Saving final statistics..."
    
    {
        echo "=== BittWare S5 Final Statistics $(date) ==="
        echo "Uptime: $(uptime)"
        echo ""
        echo "Memory usage:"
        free -h
        echo ""
        echo "Module usage:"
        lsmod | grep bittware || echo "No BittWare modules loaded"
        echo ""
        echo "PCIe devices:"
        lspci -d 1172: || echo "No BittWare devices found"
        echo ""
    } >> "/var/log/bittware_s5_stats.log"
    
    log_success "Final statistics saved"
}

# Main shutdown sequence
main() {
    log_message "Starting BittWare S5 FPGA shutdown..."
    
    # Check if running as root
    if [ $EUID -ne 0 ]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    # Execute shutdown steps
    stop_monitoring
    save_statistics
    disable_network
    unload_modules
    cleanup_devices
    reset_pcie
    
    log_success "BittWare S5 FPGA shutdown completed successfully"
}

# Run main function
main "$@"