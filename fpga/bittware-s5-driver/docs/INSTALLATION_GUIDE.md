# BittWare S5 FPGA Driver Installation Guide

## Overview

This guide provides comprehensive instructions for installing and configuring the BittWare S5 FPGA driver on Ubuntu Linux systems. The driver supports:

- PCIe Gen3 x8 interface
- 32GB DDR3 memory
- Dual 10GbE network interfaces
- High-performance DMA engine
- Memory mapping and device control

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 18.04 LTS or later (64-bit)
- **Kernel Version**: Linux 4.4.0 or later
- **CPU Architecture**: x86_64
- **Memory**: Minimum 8GB RAM (16GB+ recommended)
- **PCIe Slot**: Available PCIe Gen3 x8 slot

### Hardware Requirements

- BittWare S5 FPGA card properly installed in PCIe slot
- Adequate power supply for the FPGA card
- Proper cooling and ventilation

### Software Dependencies

```bash
# Install required packages
sudo apt update
sudo apt install -y \
    build-essential \
    linux-headers-$(uname -r) \
    dkms \
    pciutils \
    libpci-dev \
    libudev-dev \
    python3 \
    python3-pip \
    git \
    cmake \
    bc \
    xxd
```

### Python Dependencies (for diagnostic tools)

```bash
pip3 install rich tabulate click
```

## Installation Steps

### Step 1: Download and Extract Driver

```bash
# Clone or extract the driver source
cd /tmp
# If you have the source archive:
# tar -xzf bittware-s5-driver.tar.gz
# cd bittware-s5-driver

# Or if using git:
# git clone <repository-url> bittware-s5-driver
# cd bittware-s5-driver
```

### Step 2: Verify Hardware Detection

```bash
# Check if BittWare card is detected
lspci | grep -i "bittware\|fpga\|1172"

# Expected output should show the BittWare S5 card
# Example: 01:00.0 Processing accelerators: Altera Corporation Device 0005
```

### Step 3: Run Installation Script

```bash
# Make installation script executable
chmod +x scripts/install_driver.sh

# Run installation (requires root privileges)
sudo ./scripts/install_driver.sh
```

The installation script will:
- Check system requirements
- Detect the BittWare S5 card
- Backup existing drivers
- Compile and install kernel modules
- Configure udev rules
- Set up systemd services
- Run post-installation tests

### Step 4: Verify Installation

```bash
# Check if modules are loaded
lsmod | grep bittware

# Expected output:
# bittware_s5    65536  0
# bittware_dma   32768  1 bittware_s5
# bittware_net   28672  0

# Check device nodes
ls -la /dev/bittware*

# Expected output:
# crw-rw-rw- 1 root bittware 247, 0 <date> /dev/bittware_s5_0
# crw-rw-rw- 1 root bittware 248, 0 <date> /dev/bittware_dma_0
# ...
```

### Step 5: Configure Network Interfaces

```bash
# Check network interfaces
ip link show | grep bw_eth

# Configure first 10GbE interface
sudo ip link set bw_eth0 up
sudo ip addr add 192.168.1.10/24 dev bw_eth0

# Configure second 10GbE interface
sudo ip link set bw_eth1 up  
sudo ip addr add 192.168.2.10/24 dev bw_eth1
```

## Configuration

### Driver Configuration

Edit the configuration file:

```bash
sudo nano /opt/bittware/s5/config/bittware_s5.conf
```

Key configuration options:
- **Memory settings**: DDR3 size and base address
- **DMA settings**: Number of channels and buffer sizes
- **Network settings**: MTU size and performance options
- **Debug settings**: Logging and tracing options

### Kernel Parameters

Add recommended kernel parameters:

```bash
# Edit GRUB configuration
sudo nano /etc/default/grub

# Add to GRUB_CMDLINE_LINUX:
GRUB_CMDLINE_LINUX="... intel_iommu=on iommu=pt hugepages=1024"

# Update GRUB
sudo update-grub
```

### Systemd Service

The driver includes a systemd service for automatic startup:

```bash
# Enable service
sudo systemctl enable bittware-s5.service

# Start service
sudo systemctl start bittware-s5.service

# Check status
sudo systemctl status bittware-s5.service
```

## Testing and Verification

### Run Comprehensive Diagnostics

```bash
# Run full diagnostic suite
sudo python3 tools/bittware_diagnostics.py

# Run specific tests
sudo python3 tools/bittware_diagnostics.py --test memory
sudo python3 tools/bittware_diagnostics.py --test dma
sudo python3 tools/bittware_diagnostics.py --test network
```

### Memory Mapping Test

```bash
# Run memory mapping tests
sudo ./tools/test_memory_map.sh
```

### DMA Engine Test

```bash
# Run DMA tests
sudo ./tools/test_dma.sh
```

### Network Performance Test

```bash
# Test network throughput (requires iperf3)
sudo apt install iperf3

# On one machine (server)
iperf3 -s -B 192.168.1.10

# On another machine (client)
iperf3 -c 192.168.1.10 -t 60 -P 4
```

## Performance Optimization

### PCIe Optimization

```bash
# Set optimal PCIe parameters
echo 4096 > /sys/bus/pci/devices/0000:01:00.0/mps
echo 4096 > /sys/bus/pci/devices/0000:01:00.0/mrrs

# Disable ASPM for maximum performance
echo performance > /sys/module/pcie_aspm/parameters/policy
```

### Network Optimization

```bash
# Increase network buffer sizes
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf

# Apply changes
sudo sysctl -p
```

### Memory Optimization

```bash
# Configure huge pages
echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# Add to /etc/fstab for persistence
echo 'nodev /mnt/hugepages hugetlbfs defaults 0 0' >> /etc/fstab
sudo mkdir -p /mnt/hugepages
sudo mount /mnt/hugepages
```

## Troubleshooting

### Common Issues

1. **Device not detected**
   ```bash
   # Check PCIe slot
   lspci -vnn | grep -A 10 -B 10 1172
   
   # Check power and seating
   # Verify BIOS settings for PCIe
   ```

2. **Permission denied errors**
   ```bash
   # Add user to bittware group
   sudo usermod -a -G bittware $USER
   
   # Logout and login again
   ```

3. **Module loading failures**
   ```bash
   # Check kernel logs
   dmesg | grep bittware
   
   # Check dependencies
   modinfo bittware_s5
   ```

4. **Network interface not appearing**
   ```bash
   # Check network module
   sudo modprobe bittware_net
   
   # Check udev rules
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

### Log Files

- **Installation log**: `/var/log/bittware_s5_install.log`
- **Kernel messages**: `dmesg | grep bittware`
- **System log**: `/var/log/syslog`
- **Driver debug**: `/sys/kernel/debug/bittware_s5/`

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Enable debug in configuration
sudo nano /opt/bittware/s5/config/bittware_s5.conf
# Set debug_level = 4

# Restart driver
sudo systemctl restart bittware-s5.service

# Monitor logs
sudo tail -f /var/log/syslog | grep bittware
```

## Advanced Configuration

### Custom Firmware Loading

```bash
# Copy firmware to appropriate location
sudo cp your_firmware.bit /lib/firmware/bittware/s5/

# Update configuration
sudo nano /opt/bittware/s5/config/bittware_s5.conf
# Set default_bitstream = your_firmware.bit

# Reload driver
sudo rmmod bittware_s5
sudo modprobe bittware_s5
```

### Multiple Device Support

The driver supports up to 4 BittWare S5 cards:

```bash
# Check all devices
ls -la /dev/bittware_s5_*

# Configure each device independently
# Use device-specific configuration files
```

### Security Configuration

```bash
# Restrict access to root only
sudo chmod 600 /dev/bittware_s5_*

# Or allow specific group access
sudo chgrp fpga_users /dev/bittware_s5_*
sudo chmod 660 /dev/bittware_s5_*
```

## Uninstallation

To remove the driver:

```bash
# Stop services
sudo systemctl stop bittware-s5.service
sudo systemctl disable bittware-s5.service

# Remove modules
sudo modprobe -r bittware_net
sudo modprobe -r bittware_dma  
sudo modprobe -r bittware_s5

# Remove DKMS modules
sudo dkms remove bittware_s5/1.0.0 --all

# Remove files
sudo rm -rf /opt/bittware/
sudo rm /etc/udev/rules.d/99-bittware-s5.rules
sudo rm /etc/systemd/system/bittware-s5.service

# Reload udev and systemd
sudo udevadm control --reload-rules
sudo systemctl daemon-reload
```

## Support

For technical support and issues:

1. Check the troubleshooting section above
2. Review log files for error messages
3. Run diagnostic tools to identify problems
4. Contact BittWare support with diagnostic output

## Version History

- **v1.0.0**: Initial release with basic functionality
- **v1.0.1**: Added network interface support
- **v1.0.2**: Improved DMA performance and stability
- **v1.1.0**: Added multi-device support and diagnostics

---

**Note**: This driver is provided as a comprehensive solution for BittWare S5 FPGA cards. Always ensure you have proper hardware documentation and follow safety procedures when working with FPGA hardware.