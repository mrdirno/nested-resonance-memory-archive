# BittWare S5 FPGA Driver for Ubuntu Linux

A comprehensive driver solution for BittWare S5 FPGA cards featuring PCIe Gen3 x8 interface, 32GB DDR3 memory, and dual 10GbE network interfaces.

## Features

- **PCIe Gen3 x8 Interface**: Full-speed PCIe communication with optimal performance tuning
- **32GB DDR3 Memory Support**: Complete memory mapping and management
- **Dual 10GbE Network Interfaces**: Hardware-accelerated networking with Linux integration
- **High-Performance DMA Engine**: Multi-channel DMA with scatter-gather support
- **Comprehensive Diagnostics**: Built-in testing and verification tools
- **DKMS Integration**: Automatic kernel module rebuilding across kernel updates
- **Ubuntu LTS Support**: Tested on Ubuntu 18.04, 20.04, and 22.04

## Quick Start

### 1. Install Prerequisites

```bash
sudo apt update
sudo apt install -y build-essential linux-headers-$(uname -r) dkms pciutils
```

### 2. Install Driver

```bash
sudo ./scripts/install_driver.sh
```

### 3. Verify Installation

```bash
sudo python3 tools/bittware_diagnostics.py
```

## Directory Structure

```
bittware-s5-driver/
├── scripts/           # Installation and management scripts
│   └── install_driver.sh
├── src/              # Kernel driver source code
│   ├── bittware_s5_main.c
│   ├── bittware_s5_pcie.c
│   ├── bittware_s5_mem.c
│   ├── bittware_dma_engine.c
│   ├── bittware_dma_buffer.c
│   ├── bittware_net_main.c
│   ├── bittware_net_10gbe.c
│   ├── bittware_s5.h
│   └── Makefile
├── tools/            # Diagnostic and utility tools
│   ├── bittware_diagnostics.py
│   ├── test_memory_map.sh
│   ├── test_dma.sh
│   ├── bittware_init.sh
│   └── bittware_stop.sh
├── config/           # Configuration files
│   └── bittware_s5.conf
├── docs/             # Documentation
│   └── INSTALLATION_GUIDE.md
└── README.md
```

## Hardware Support

### Supported BittWare S5 Configurations

- **FPGA**: Intel/Altera Stratix V GX/GS series
- **Memory**: Up to 32GB DDR3 SDRAM
- **Network**: Dual 10GbE SFP+ interfaces
- **PCIe**: Gen3 x8 interface (8 GT/s)
- **Form Factor**: Half-length PCIe card

### System Requirements

- **OS**: Ubuntu 18.04 LTS or later (64-bit)
- **Kernel**: Linux 4.4.0 or later
- **CPU**: x86_64 architecture
- **Memory**: Minimum 8GB RAM
- **PCIe**: Available PCIe Gen3 x8 slot

## Driver Components

### Main Driver (`bittware_s5`)
- Device detection and initialization
- PCIe interface management  
- Register access and control
- Interrupt handling
- Device file operations

### DMA Engine (`bittware_dma`)
- Multi-channel DMA support
- Scatter-gather transfers
- Buffer management
- Performance optimization

### Network Driver (`bittware_net`)
- 10GbE interface support
- Linux network stack integration
- Hardware acceleration
- Performance monitoring

## Key Features

### PCIe Optimization
- Automatic Gen3 x8 link training
- Optimal payload and read request sizing
- MSI-X interrupt support
- Advanced error reporting (AER)

### Memory Management
- 32GB DDR3 controller support
- Memory mapping via mmap()
- Page-aligned allocations
- Memory bandwidth testing

### Network Performance
- Jumbo frame support (9KB)
- Hardware checksum offload
- NAPI polling for efficiency
- Multi-queue support

### DMA Performance
- Up to 4 independent channels
- Scatter-gather descriptors
- Interrupt coalescing
- Zero-copy transfers

## Installation Options

### Automatic Installation
```bash
sudo ./scripts/install_driver.sh
```

### Manual Installation
```bash
cd src/
make
sudo make install
sudo modprobe bittware_s5
```

### DKMS Installation
```bash
sudo dkms add .
sudo dkms build bittware_s5/1.0.0
sudo dkms install bittware_s5/1.0.0
```

## Configuration

### Driver Configuration File
Edit `/opt/bittware/s5/config/bittware_s5.conf`:

```ini
[device]
max_payload_size = 4096
max_read_request_size = 4096

[memory]
ddr3_size = 34359738368
memory_test_enable = true

[dma]
num_channels = 4
max_transfer_size = 16777216

[network]
mtu = 9000
enable_jumbo_frames = true
```

### Network Interface Configuration
```bash
# Configure 10GbE interfaces
sudo ip link set bw_eth0 up
sudo ip addr add 192.168.1.10/24 dev bw_eth0

sudo ip link set bw_eth1 up  
sudo ip addr add 192.168.2.10/24 dev bw_eth1
```

## Testing and Diagnostics

### Comprehensive Diagnostics
```bash
# Run all tests
sudo python3 tools/bittware_diagnostics.py

# Run specific tests
sudo python3 tools/bittware_diagnostics.py --test memory
sudo python3 tools/bittware_diagnostics.py --test dma
sudo python3 tools/bittware_diagnostics.py --test network
```

### Memory Testing
```bash
sudo ./tools/test_memory_map.sh
```

### DMA Testing
```bash
sudo ./tools/test_dma.sh
```

### Performance Benchmarks
```bash
# Network throughput test
iperf3 -s -B 192.168.1.10  # Server
iperf3 -c 192.168.1.10 -t 60 -P 4  # Client

# Memory bandwidth test
sudo python3 -c "
from tools.bittware_diagnostics import MemoryTester
print(f'Bandwidth: {MemoryTester.memory_bandwidth_test(\"/dev/bittware_s5_0\"):.1f} MB/s')
"
```

## Troubleshooting

### Common Issues

1. **Device not detected**
   ```bash
   lspci | grep -i "1172\|bittware"
   # Check hardware installation and power
   ```

2. **Module loading failed**
   ```bash
   dmesg | grep bittware
   # Check for dependency issues
   ```

3. **Permission denied**
   ```bash
   sudo usermod -a -G bittware $USER
   # Logout and login again
   ```

### Debug Mode
```bash
# Enable verbose logging
sudo modprobe bittware_s5 debug=1

# Monitor kernel messages
sudo dmesg -w | grep bittware
```

### Log Files
- Installation: `/var/log/bittware_s5_install.log`
- Runtime: `/var/log/bittware_s5.log`
- Statistics: `/var/log/bittware_s5_stats.log`

## Performance Optimization

### System Tuning
```bash
# CPU performance mode
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Huge pages for DMA
echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# Network buffer optimization
echo 'net.core.rmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### PCIe Tuning
```bash
# Disable ASPM for maximum performance
echo performance | sudo tee /sys/module/pcie_aspm/parameters/policy

# Set optimal PCIe parameters
echo 4096 | sudo tee /sys/bus/pci/devices/*/mps
echo 4096 | sudo tee /sys/bus/pci/devices/*/mrrs
```

## Development

### Building from Source
```bash
cd src/
make clean
make EXTRA_CFLAGS="-DDEBUG"
sudo make install
```

### Adding Custom Features
1. Modify source files in `src/`
2. Update `bittware_s5.h` for new interfaces
3. Add tests in `tools/`
4. Update documentation

### Debugging
```bash
# Enable kernel debugging
echo 'file drivers/bittware/* +p' | sudo tee /sys/kernel/debug/dynamic_debug/control

# Use ftrace for detailed tracing
echo 1 | sudo tee /sys/kernel/debug/tracing/events/bittware/enable
```

## Support and Documentation

- **Installation Guide**: `docs/INSTALLATION_GUIDE.md`
- **Hardware Manual**: Refer to BittWare S5 documentation
- **Kernel Documentation**: `/usr/src/linux-headers-$(uname -r)/Documentation/`

## Version Information

- **Driver Version**: 1.0.0
- **Supported Kernels**: 4.4.0 - 6.x
- **DKMS Compatible**: Yes
- **License**: GPL v2

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper testing
4. Submit a pull request

## License

This driver is released under the GNU General Public License v2.0. See the kernel source tree for full license text.

---

**Note**: This is a comprehensive driver solution designed for production use with BittWare S5 FPGA cards. Always refer to your specific hardware documentation and follow proper safety procedures when installing and configuring FPGA hardware.