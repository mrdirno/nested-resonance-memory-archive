#!/bin/bash
# BittWare S5 Driver Installation Verification Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   BittWare S5 Driver Installation Verification${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check 1: Directory structure
echo -e "${YELLOW}Checking directory structure...${NC}"
required_dirs=("scripts" "src" "tools" "config" "docs")
required_files=("README.md" "scripts/install_driver.sh" "src/Makefile" "tools/bittware_diagnostics.py")

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} Directory: $dir"
    else
        echo -e "${RED}✗${NC} Missing directory: $dir"
    fi
done

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} File: $file"
    else
        echo -e "${RED}✗${NC} Missing file: $file"
    fi
done

echo ""

# Check 2: Source code files
echo -e "${YELLOW}Checking source code files...${NC}"
src_files=(
    "src/bittware_s5_main.c"
    "src/bittware_s5_pcie.c" 
    "src/bittware_s5_mem.c"
    "src/bittware_dma_engine.c"
    "src/bittware_dma_buffer.c"
    "src/bittware_net_main.c"
    "src/bittware_net_10gbe.c"
    "src/bittware_s5.h"
    "src/Makefile"
)

for file in "${src_files[@]}"; do
    if [ -f "$file" ]; then
        size=$(stat --printf="%s" "$file")
        echo -e "${GREEN}✓${NC} $file (${size} bytes)"
    else
        echo -e "${RED}✗${NC} Missing: $file"
    fi
done

echo ""

# Check 3: Tools and scripts
echo -e "${YELLOW}Checking tools and scripts...${NC}"
tools=(
    "tools/bittware_diagnostics.py"
    "tools/test_memory_map.sh"
    "tools/test_dma.sh"
    "tools/bittware_init.sh"
    "tools/bittware_stop.sh"
    "scripts/install_driver.sh"
)

for tool in "${tools[@]}"; do
    if [ -f "$tool" ]; then
        if [ -x "$tool" ]; then
            echo -e "${GREEN}✓${NC} $tool (executable)"
        else
            echo -e "${YELLOW}!${NC} $tool (not executable)"
        fi
    else
        echo -e "${RED}✗${NC} Missing: $tool"
    fi
done

echo ""

# Check 4: Configuration files
echo -e "${YELLOW}Checking configuration files...${NC}"
config_files=(
    "config/bittware_s5.conf"
)

for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo -e "${GREEN}✓${NC} $file (${lines} lines)"
    else
        echo -e "${RED}✗${NC} Missing: $file"
    fi
done

echo ""

# Check 5: Documentation
echo -e "${YELLOW}Checking documentation...${NC}"
doc_files=(
    "README.md"
    "docs/INSTALLATION_GUIDE.md"
)

for file in "${doc_files[@]}"; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo -e "${GREEN}✓${NC} $file (${lines} lines)"
    else
        echo -e "${RED}✗${NC} Missing: $file"
    fi
done

echo ""

# Check 6: Code syntax validation
echo -e "${YELLOW}Checking code syntax...${NC}"

# Check C files for basic syntax
if command -v gcc &> /dev/null; then
    echo "Checking C source files..."
    cd src/
    for c_file in *.c; do
        if [ -f "$c_file" ]; then
            gcc -fsyntax-only -I. "$c_file" 2>/dev/null && \
                echo -e "${GREEN}✓${NC} $c_file syntax OK" || \
                echo -e "${YELLOW}!${NC} $c_file syntax warnings/errors"
        fi
    done
    cd ..
else
    echo -e "${YELLOW}!${NC} GCC not available, skipping C syntax check"
fi

# Check Python files
if command -v python3 &> /dev/null; then
    echo "Checking Python files..."
    for py_file in tools/*.py; do
        if [ -f "$py_file" ]; then
            python3 -m py_compile "$py_file" 2>/dev/null && \
                echo -e "${GREEN}✓${NC} $py_file syntax OK" || \
                echo -e "${YELLOW}!${NC} $py_file syntax errors"
        fi
    done
else
    echo -e "${YELLOW}!${NC} Python3 not available, skipping Python syntax check"
fi

# Check shell scripts
echo "Checking shell scripts..."
for sh_file in scripts/*.sh tools/*.sh; do
    if [ -f "$sh_file" ]; then
        bash -n "$sh_file" 2>/dev/null && \
            echo -e "${GREEN}✓${NC} $sh_file syntax OK" || \
            echo -e "${YELLOW}!${NC} $sh_file syntax errors"
    fi
done

echo ""

# Check 7: System compatibility
echo -e "${YELLOW}Checking system compatibility...${NC}"

# Check OS
if [ -f /etc/os-release ]; then
    source /etc/os-release
    echo -e "${GREEN}✓${NC} OS: $PRETTY_NAME"
    
    if [[ "$ID" == "ubuntu" ]]; then
        echo -e "${GREEN}✓${NC} Ubuntu detected"
    else
        echo -e "${YELLOW}!${NC} Non-Ubuntu system detected (may work but not tested)"
    fi
else
    echo -e "${YELLOW}!${NC} Cannot determine OS"
fi

# Check kernel version
kernel_version=$(uname -r)
echo -e "${GREEN}✓${NC} Kernel: $kernel_version"

# Check architecture
arch=$(uname -m)
if [[ "$arch" == "x86_64" ]]; then
    echo -e "${GREEN}✓${NC} Architecture: $arch"
else
    echo -e "${YELLOW}!${NC} Architecture: $arch (x86_64 recommended)"
fi

# Check required commands
required_commands=("make" "gcc" "modprobe" "lspci" "python3")
missing_commands=()

for cmd in "${required_commands[@]}"; do
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} Command available: $cmd"
    else
        echo -e "${RED}✗${NC} Missing command: $cmd"
        missing_commands+=("$cmd")
    fi
done

echo ""

# Check 8: File sizes and completeness
echo -e "${YELLOW}Checking file completeness...${NC}"

# Check if files have reasonable sizes
declare -A min_sizes=(
    ["src/bittware_s5_main.c"]=10000
    ["src/bittware_dma_engine.c"]=8000
    ["src/bittware_net_main.c"]=8000
    ["tools/bittware_diagnostics.py"]=15000
    ["scripts/install_driver.sh"]=8000
    ["README.md"]=5000
    ["docs/INSTALLATION_GUIDE.md"]=15000
)

for file in "${!min_sizes[@]}"; do
    if [ -f "$file" ]; then
        size=$(stat --printf="%s" "$file")
        min_size=${min_sizes[$file]}
        
        if [ "$size" -ge "$min_size" ]; then
            echo -e "${GREEN}✓${NC} $file size OK (${size} bytes)"
        else
            echo -e "${YELLOW}!${NC} $file smaller than expected (${size} < ${min_size})"
        fi
    fi
done

echo ""

# Final summary
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Verification Summary${NC}"
echo -e "${BLUE}================================================${NC}"

if [ ${#missing_commands[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All required commands available${NC}"
else
    echo -e "${RED}✗ Missing commands: ${missing_commands[*]}${NC}"
    echo -e "${YELLOW}  Install with: sudo apt install build-essential linux-headers-\$(uname -r) dkms pciutils${NC}"
fi

# Count files
total_files=$(find . -type f | wc -l)
echo -e "${GREEN}✓ Total files: $total_files${NC}"

# Calculate total size
total_size=$(du -sh . | cut -f1)
echo -e "${GREEN}✓ Total package size: $total_size${NC}"

echo ""
echo -e "${GREEN}Driver package verification completed!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Install system dependencies if any are missing"
echo "2. Run: sudo ./scripts/install_driver.sh"
echo "3. Run: sudo python3 tools/bittware_diagnostics.py"
echo ""
echo -e "${BLUE}For detailed installation instructions, see: docs/INSTALLATION_GUIDE.md${NC}"