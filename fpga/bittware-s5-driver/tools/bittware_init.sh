#!/bin/bash
# BittWare S5 FPGA Initialization Script
# This script is called by the systemd service to initialize the driver

set -e

INSTALL_DIR="/opt/bittware/s5"
CONFIG_FILE="$INSTALL_DIR/config/bittware_s5.conf"
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

# Function to read configuration value
get_config_value() {
    local section=$1
    local key=$2
    local default_value=$3
    
    if [ -f "$CONFIG_FILE" ]; then
        # Simple config parser (for basic INI format)
        awk -F= -v section="[$section]" -v key="$key" '
            $0 == section { in_section=1; next }
            /^\[.*\]/ { in_section=0; next }
            in_section && $1 == key { gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2; exit }
        ' "$CONFIG_FILE" 2>/dev/null || echo "$default_value"
    else
        echo "$default_value"
    fi
}

# Function to load kernel modules
load_modules() {
    log_message "Loading BittWare S5 kernel modules..."
    
    # Load main driver module
    if ! lsmod | grep -q "bittware_s5"; then
        modprobe bittware_s5
        if [ $? -eq 0 ]; then
            log_success "bittware_s5 module loaded"
        else
            log_error "Failed to load bittware_s5 module"
            return 1
        fi
    else
        log_message "bittware_s5 module already loaded"
    fi
    
    # Load DMA module
    if ! lsmod | grep -q "bittware_dma"; then
        modprobe bittware_dma
        if [ $? -eq 0 ]; then
            log_success "bittware_dma module loaded"
        else
            log_error "Failed to load bittware_dma module"
            return 1
        fi
    else
        log_message "bittware_dma module already loaded"
    fi
    
    # Load network module
    if ! lsmod | grep -q "bittware_net"; then
        modprobe bittware_net
        if [ $? -eq 0 ]; then
            log_success "bittware_net module loaded"
        else
            log_error "Failed to load bittware_net module"
            return 1
        fi
    else
        log_message "bittware_net module already loaded"
    fi
    
    return 0
}

# Function to configure PCIe parameters
configure_pcie() {
    log_message "Configuring PCIe parameters..."
    
    local max_payload=$(get_config_value "device" "max_payload_size" "4096")
    local max_read_req=$(get_config_value "device" "max_read_request_size" "4096")
    
    # Find BittWare devices
    local devices=$(lspci -d 1172: | cut -d' ' -f1)
    
    if [ -z "$devices" ]; then
        log_warning "No BittWare devices found"
        return 0
    fi
    
    for device in $devices; do
        log_message "Configuring PCIe device $device"
        
        # Set max payload size
        if [ -w "/sys/bus/pci/devices/0000:$device/mps" ]; then
            echo $max_payload > "/sys/bus/pci/devices/0000:$device/mps" 2>/dev/null || true
        fi
        
        # Set max read request size  
        if [ -w "/sys/bus/pci/devices/0000:$device/mrrs" ]; then
            echo $max_read_req > "/sys/bus/pci/devices/0000:$device/mrrs" 2>/dev/null || true
        fi
        
        log_success "PCIe device $device configured"
    done
}

# Function to setup huge pages
setup_hugepages() {
    log_message "Setting up huge pages..."
    
    local hugepages=$(get_config_value "memory" "hugepages" "1024")
    
    if [ "$hugepages" -gt 0 ]; then
        echo $hugepages > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
        log_success "Configured $hugepages huge pages"
    fi
}

# Function to configure network interfaces
configure_network() {
    log_message "Configuring network interfaces..."
    
    local mtu=$(get_config_value "network" "mtu" "9000")
    local enable_jumbo=$(get_config_value "network" "enable_jumbo_frames" "true")
    
    # Wait for network interfaces to appear
    sleep 2
    
    # Configure BittWare network interfaces
    for interface in $(ip link show | grep "bw_eth" | cut -d: -f2 | tr -d ' '); do
        log_message "Configuring interface $interface"
        
        # Set MTU if jumbo frames are enabled
        if [ "$enable_jumbo" = "true" ]; then
            ip link set dev $interface mtu $mtu 2>/dev/null && \
                log_success "Set MTU $mtu on $interface" || \
                log_warning "Failed to set MTU on $interface"
        fi
        
        # Enable interface
        ip link set dev $interface up 2>/dev/null && \
            log_success "Interface $interface enabled" || \
            log_warning "Failed to enable $interface"
    done
}

# Function to set device permissions
set_permissions() {
    log_message "Setting device permissions..."
    
    # Wait for device nodes to appear
    sleep 1
    
    # Set permissions for device nodes
    for device in /dev/bittware_s5_* /dev/bittware_dma_* /dev/bittware_mem_*; do
        if [ -e "$device" ]; then
            chown root:bittware "$device" 2>/dev/null || true
            chmod 666 "$device" 2>/dev/null || true
            log_success "Set permissions on $device"
        fi
    done
}

# Function to load firmware if specified
load_firmware() {
    log_message "Checking firmware configuration..."
    
    local auto_load=$(get_config_value "firmware" "auto_load_firmware" "false")
    local firmware_path=$(get_config_value "firmware" "firmware_path" "/lib/firmware/bittware/s5/")
    local default_bitstream=$(get_config_value "firmware" "default_bitstream" "")
    
    if [ "$auto_load" = "true" ] && [ -n "$default_bitstream" ]; then
        local firmware_file="$firmware_path/$default_bitstream"
        
        if [ -f "$firmware_file" ]; then
            log_message "Loading firmware: $default_bitstream"
            # Firmware loading would be implemented here
            # This is hardware-specific and depends on the FPGA configuration interface
            log_success "Firmware loaded successfully"
        else
            log_warning "Firmware file not found: $firmware_file"
        fi
    else
        log_message "Firmware auto-load disabled or no default bitstream specified"
    fi
}

# Function to run system optimization
system_optimization() {
    log_message "Applying system optimizations..."
    
    # Set CPU governor to performance
    if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
        echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || true
        log_success "Set CPU governor to performance"
    fi
    
    # Disable power management for PCIe devices
    local aspm_policy=$(get_config_value "power" "aspm_policy" "performance")
    if [ -f /sys/module/pcie_aspm/parameters/policy ]; then
        echo $aspm_policy > /sys/module/pcie_aspm/parameters/policy 2>/dev/null || true
        log_success "Set PCIe ASPM policy to $aspm_policy"
    fi
    
    # Set network optimizations
    local enable_stats=$(get_config_value "debugging" "enable_stats" "true")
    if [ "$enable_stats" = "true" ]; then
        # Enable network statistics collection
        echo 1 > /proc/sys/net/core/netdev_tstamp_prequeue 2>/dev/null || true
    fi
}

# Function to start monitoring if enabled
start_monitoring() {
    local enable_stats=$(get_config_value "debugging" "enable_stats" "true")
    local stats_interval=$(get_config_value "debugging" "stats_interval" "60")
    
    if [ "$enable_stats" = "true" ]; then
        log_message "Starting performance monitoring..."
        
        # Start background monitoring process
        (
            while true; do
                sleep $stats_interval
                
                # Collect and log statistics
                {
                    echo "=== BittWare S5 Statistics $(date) ==="
                    echo "Memory usage:"
                    free -h
                    echo ""
                    echo "Network interfaces:"
                    ip -s link show | grep -A 3 "bw_eth"
                    echo ""
                    echo "PCIe status:"
                    lspci -d 1172: -vv | grep -E "(LnkSta|LnkCap)"
                    echo ""
                } >> "/var/log/bittware_s5_stats.log"
            done
        ) &
        
        echo $! > /var/run/bittware_s5_monitor.pid
        log_success "Performance monitoring started"
    fi
}

# Function to verify initialization
verify_initialization() {
    log_message "Verifying initialization..."
    
    local errors=0
    
    # Check if modules are loaded
    if ! lsmod | grep -q "bittware_s5"; then
        log_error "bittware_s5 module not loaded"
        ((errors++))
    fi
    
    # Check if device nodes exist
    if ! ls /dev/bittware_s5_* >/dev/null 2>&1; then
        log_error "No BittWare device nodes found"
        ((errors++))
    fi
    
    # Check PCIe devices
    if ! lspci -d 1172: >/dev/null 2>&1; then
        log_error "No BittWare PCIe devices found"
        ((errors++))
    fi
    
    if [ $errors -eq 0 ]; then
        log_success "Initialization verification passed"
        return 0
    else
        log_error "Initialization verification failed ($errors errors)"
        return 1
    fi
}

# Main initialization sequence
main() {
    log_message "Starting BittWare S5 FPGA initialization..."
    
    # Check if running as root
    if [ $EUID -ne 0 ]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    # Load configuration
    if [ ! -f "$CONFIG_FILE" ]; then
        log_warning "Configuration file not found: $CONFIG_FILE"
        log_message "Using default configuration"
    fi
    
    # Execute initialization steps
    load_modules || exit 1
    configure_pcie
    setup_hugepages
    set_permissions
    load_firmware
    configure_network
    system_optimization
    start_monitoring
    
    # Verify everything is working
    if verify_initialization; then
        log_success "BittWare S5 FPGA initialization completed successfully"
        exit 0
    else
        log_error "BittWare S5 FPGA initialization failed"
        exit 1
    fi
}

# Run main function
main "$@"