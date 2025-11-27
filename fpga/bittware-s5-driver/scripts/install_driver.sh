#!/bin/bash
# BittWare S5 FPGA Driver Installation Script for Ubuntu Linux
# Supports PCIe Gen3 x8, 32GB DDR3, Dual 10GbE interfaces

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script constants
DRIVER_NAME="bittware_s5"
DRIVER_VERSION="1.0.0"
INSTALL_DIR="/opt/bittware/s5"
LOG_FILE="/var/log/bittware_s5_install.log"

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_message $RED "This script must be run as root"
        exit 1
    fi
}

# Function to check system requirements
check_system_requirements() {
    print_message $YELLOW "Checking system requirements..."
    
    # Check if running Ubuntu
    if ! command -v lsb_release &> /dev/null; then
        print_message $RED "lsb_release command not found. This script is designed for Ubuntu."
        exit 1
    fi
    
    local ubuntu_version=$(lsb_release -rs)
    print_message $GREEN "Ubuntu version: $ubuntu_version"
    
    # Check kernel version
    local kernel_version=$(uname -r)
    print_message $GREEN "Kernel version: $kernel_version"
    
    # Check for required packages
    local required_packages=(
        "build-essential"
        "linux-headers-$(uname -r)"
        "dkms"
        "pciutils"
        "libpci-dev"
        "libudev-dev"
        "python3"
        "python3-pip"
        "git"
        "cmake"
    )
    
    print_message $YELLOW "Checking for required packages..."
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package"; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -ne 0 ]; then
        print_message $YELLOW "Installing missing packages: ${missing_packages[*]}"
        apt-get update
        apt-get install -y "${missing_packages[@]}"
    else
        print_message $GREEN "All required packages are installed"
    fi
}

# Function to detect BittWare S5 card
detect_bittware_s5() {
    print_message $YELLOW "Detecting BittWare S5 FPGA card..."
    
    # BittWare vendor ID is typically 0x1172 (Altera) or custom
    # Product ID varies by model
    local vendor_ids=("1172" "10ee" "1d0f")
    local device_found=false
    
    for vendor_id in "${vendor_ids[@]}"; do
        if lspci -d "$vendor_id:" | grep -i "fpga\|bittware\|stratix"; then
            device_found=true
            print_message $GREEN "BittWare FPGA device found:"
            lspci -d "$vendor_id:" -vnn
            break
        fi
    done
    
    if [ "$device_found" = false ]; then
        print_message $RED "No BittWare S5 FPGA device detected"
        print_message $YELLOW "Please ensure the card is properly installed in a PCIe slot"
        return 1
    fi
    
    return 0
}

# Function to backup existing drivers
backup_existing_drivers() {
    print_message $YELLOW "Backing up existing drivers..."
    
    local backup_dir="/opt/bittware/backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Check for existing kernel modules
    if lsmod | grep -q "bittware"; then
        print_message $YELLOW "Found existing BittWare modules, creating backup..."
        cp -r /lib/modules/$(uname -r)/kernel/drivers/bittware "$backup_dir/" 2>/dev/null || true
    fi
    
    print_message $GREEN "Backup completed to: $backup_dir"
}

# Function to remove old drivers
remove_old_drivers() {
    print_message $YELLOW "Removing old drivers..."
    
    # Remove kernel modules
    local modules=("bittware_s5" "bittware_dma" "bittware_net")
    for module in "${modules[@]}"; do
        if lsmod | grep -q "$module"; then
            rmmod "$module" 2>/dev/null || true
        fi
    done
    
    # Remove DKMS modules
    if dkms status | grep -q "bittware"; then
        dkms remove bittware_s5/$DRIVER_VERSION --all 2>/dev/null || true
    fi
    
    print_message $GREEN "Old drivers removed"
}

# Function to install kernel modules
install_kernel_modules() {
    print_message $YELLOW "Installing kernel modules..."
    
    # Create installation directories
    mkdir -p "$INSTALL_DIR"/{driver,lib,include,tools,docs}
    
    # Copy driver source files
    cp -r ../src/* "$INSTALL_DIR/driver/"
    
    # Build kernel modules
    cd "$INSTALL_DIR/driver"
    make clean
    make
    
    # Install modules using DKMS
    mkdir -p /usr/src/bittware_s5-$DRIVER_VERSION
    cp -r * /usr/src/bittware_s5-$DRIVER_VERSION/
    
    # Create DKMS configuration
    cat > /usr/src/bittware_s5-$DRIVER_VERSION/dkms.conf << EOF
PACKAGE_NAME="bittware_s5"
PACKAGE_VERSION="$DRIVER_VERSION"
BUILT_MODULE_NAME[0]="bittware_s5"
BUILT_MODULE_NAME[1]="bittware_dma"
BUILT_MODULE_NAME[2]="bittware_net"
DEST_MODULE_LOCATION[0]="/kernel/drivers/bittware"
DEST_MODULE_LOCATION[1]="/kernel/drivers/bittware"
DEST_MODULE_LOCATION[2]="/kernel/drivers/bittware"
AUTOINSTALL="yes"
REMAKE_INITRD="yes"
EOF
    
    # Add to DKMS
    dkms add -m bittware_s5 -v $DRIVER_VERSION
    dkms build -m bittware_s5 -v $DRIVER_VERSION
    dkms install -m bittware_s5 -v $DRIVER_VERSION
    
    print_message $GREEN "Kernel modules installed successfully"
}

# Function to configure udev rules
configure_udev_rules() {
    print_message $YELLOW "Configuring udev rules..."
    
    cat > /etc/udev/rules.d/99-bittware-s5.rules << 'EOF'
# BittWare S5 FPGA udev rules
# Create device nodes with proper permissions

# Main device
KERNEL=="bittware_s5*", MODE="0666", GROUP="bittware"

# DMA channels
KERNEL=="bittware_dma*", MODE="0666", GROUP="bittware"

# Network interfaces
KERNEL=="bw_eth*", MODE="0666", GROUP="bittware"

# Memory mapped regions
KERNEL=="bittware_mem*", MODE="0666", GROUP="bittware"

# Control interface
KERNEL=="bittware_ctrl*", MODE="0666", GROUP="bittware"
EOF
    
    # Create bittware group
    groupadd -f bittware
    
    # Reload udev rules
    udevadm control --reload-rules
    udevadm trigger
    
    print_message $GREEN "udev rules configured"
}

# Function to configure PCIe parameters
configure_pcie_parameters() {
    print_message $YELLOW "Configuring PCIe parameters..."
    
    # Set PCIe max read request size for optimal performance
    setpci -v -s $(lspci | grep -i "bittware\|fpga" | cut -d' ' -f1) 68.w=5936
    
    # Enable PCIe relaxed ordering for better performance
    setpci -v -s $(lspci | grep -i "bittware\|fpga" | cut -d' ' -f1) 50.b=10
    
    # Configure MSI-X interrupts
    echo 16 > /proc/sys/kernel/nr_hugepages
    
    print_message $GREEN "PCIe parameters configured"
}

# Function to load kernel modules
load_kernel_modules() {
    print_message $YELLOW "Loading kernel modules..."
    
    modprobe bittware_s5
    modprobe bittware_dma
    modprobe bittware_net
    
    # Verify modules are loaded
    if lsmod | grep -q "bittware"; then
        print_message $GREEN "Kernel modules loaded successfully"
        lsmod | grep bittware
    else
        print_message $RED "Failed to load kernel modules"
        return 1
    fi
    
    return 0
}

# Function to create systemd service
create_systemd_service() {
    print_message $YELLOW "Creating systemd service..."
    
    cat > /etc/systemd/system/bittware-s5.service << EOF
[Unit]
Description=BittWare S5 FPGA Driver Service
After=network.target

[Service]
Type=oneshot
ExecStart=/opt/bittware/s5/tools/bittware_init.sh
ExecStop=/opt/bittware/s5/tools/bittware_stop.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable bittware-s5.service
    
    print_message $GREEN "Systemd service created and enabled"
}

# Function to install Python tools
install_python_tools() {
    print_message $YELLOW "Installing Python management tools..."
    
    # Create Python virtual environment
    python3 -m venv "$INSTALL_DIR/venv"
    source "$INSTALL_DIR/venv/bin/activate"
    
    # Install required Python packages
    pip install --upgrade pip
    pip install numpy pyserial click rich tabulate
    
    # Copy Python tools
    cp -r ../tools/*.py "$INSTALL_DIR/tools/"
    chmod +x "$INSTALL_DIR/tools/"*.py
    
    deactivate
    
    print_message $GREEN "Python tools installed"
}

# Function to perform post-installation tests
post_installation_tests() {
    print_message $YELLOW "Running post-installation tests..."
    
    # Test device detection
    if [ -e /dev/bittware_s5_0 ]; then
        print_message $GREEN "Device node created successfully"
    else
        print_message $RED "Device node not found"
        return 1
    fi
    
    # Test memory mapping
    "$INSTALL_DIR/tools/test_memory_map.sh"
    
    # Test DMA functionality
    "$INSTALL_DIR/tools/test_dma.sh"
    
    print_message $GREEN "Post-installation tests completed"
    return 0
}

# Main installation function
main() {
    print_message $GREEN "BittWare S5 FPGA Driver Installation Script"
    print_message $GREEN "Version: $DRIVER_VERSION"
    echo ""
    
    # Start logging
    exec > >(tee -a "$LOG_FILE")
    exec 2>&1
    
    check_root
    check_system_requirements
    
    if ! detect_bittware_s5; then
        print_message $YELLOW "Continue without device? (y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    backup_existing_drivers
    remove_old_drivers
    install_kernel_modules
    configure_udev_rules
    configure_pcie_parameters
    load_kernel_modules
    create_systemd_service
    install_python_tools
    post_installation_tests
    
    print_message $GREEN "Installation completed successfully!"
    print_message $YELLOW "Please reboot your system to ensure all changes take effect."
    print_message $YELLOW "Log file: $LOG_FILE"
}

# Run main function
main "$@"