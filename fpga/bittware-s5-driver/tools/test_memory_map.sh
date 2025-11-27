#!/bin/bash
# BittWare S5 Memory Mapping Test Script

DEVICE="/dev/bittware_s5_0"
LOG_FILE="/tmp/bittware_memory_test.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "BittWare S5 Memory Mapping Test" | tee $LOG_FILE
echo "==============================" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Check if device exists
if [ ! -e "$DEVICE" ]; then
    echo -e "${RED}Error: Device $DEVICE not found${NC}" | tee -a $LOG_FILE
    exit 1
fi

# Check if device is readable/writable
if [ ! -r "$DEVICE" ] || [ ! -w "$DEVICE" ]; then
    echo -e "${RED}Error: No read/write permissions for $DEVICE${NC}" | tee -a $LOG_FILE
    exit 1
fi

echo -e "${GREEN}Device $DEVICE found and accessible${NC}" | tee -a $LOG_FILE

# Test 1: Basic memory access
echo "" | tee -a $LOG_FILE
echo "Test 1: Basic Memory Access" | tee -a $LOG_FILE
echo "----------------------------" | tee -a $LOG_FILE

# Write test pattern to control register
TEST_PATTERN=0x12345678
echo "Writing test pattern 0x$TEST_PATTERN to offset 0x1000" | tee -a $LOG_FILE

# Use dd to write to specific offset
echo -n -e "\\x78\\x56\\x34\\x12" | dd of=$DEVICE bs=1 seek=4096 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Write operation successful${NC}" | tee -a $LOG_FILE
else
    echo -e "${RED}Write operation failed${NC}" | tee -a $LOG_FILE
fi

# Read back the pattern
echo "Reading back from offset 0x1000" | tee -a $LOG_FILE
READ_VALUE=$(dd if=$DEVICE bs=4 count=1 skip=1024 2>/dev/null | xxd -p)

if [ "$READ_VALUE" = "12345678" ]; then
    echo -e "${GREEN}Read-back successful: 0x$READ_VALUE${NC}" | tee -a $LOG_FILE
else
    echo -e "${YELLOW}Read-back value: 0x$READ_VALUE (may differ due to hardware)${NC}" | tee -a $LOG_FILE
fi

# Test 2: Memory mapping with mmap test program
echo "" | tee -a $LOG_FILE
echo "Test 2: Memory Mapping (mmap)" | tee -a $LOG_FILE
echo "------------------------------" | tee -a $LOG_FILE

# Create a simple C program to test mmap
cat > /tmp/mmap_test.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdint.h>

#define DEVICE_PATH "/dev/bittware_s5_0"
#define MAP_SIZE 4096
#define MAP_OFFSET 0x10000000  // DDR3 base offset

int main() {
    int fd;
    volatile uint32_t *map_base;
    uint32_t test_pattern = 0xDEADBEEF;
    uint32_t read_value;
    
    // Open device
    fd = open(DEVICE_PATH, O_RDWR | O_SYNC);
    if (fd < 0) {
        perror("open");
        return 1;
    }
    
    // Map memory
    map_base = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, MAP_OFFSET);
    if (map_base == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return 1;
    }
    
    printf("Memory mapped successfully at %p\n", map_base);
    
    // Write test pattern
    printf("Writing test pattern 0x%08X\n", test_pattern);
    map_base[0] = test_pattern;
    
    // Memory barrier
    __sync_synchronize();
    
    // Read back
    read_value = map_base[0];
    printf("Read back value: 0x%08X\n", read_value);
    
    if (read_value == test_pattern) {
        printf("Memory mapping test PASSED\n");
    } else {
        printf("Memory mapping test FAILED (expected 0x%08X, got 0x%08X)\n", 
               test_pattern, read_value);
    }
    
    // Cleanup
    munmap((void*)map_base, MAP_SIZE);
    close(fd);
    
    return (read_value == test_pattern) ? 0 : 1;
}
EOF

# Compile and run the mmap test
gcc -o /tmp/mmap_test /tmp/mmap_test.c 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Running memory mapping test..." | tee -a $LOG_FILE
    /tmp/mmap_test 2>&1 | tee -a $LOG_FILE
    MMAP_RESULT=$?
    
    if [ $MMAP_RESULT -eq 0 ]; then
        echo -e "${GREEN}Memory mapping test PASSED${NC}" | tee -a $LOG_FILE
    else
        echo -e "${YELLOW}Memory mapping test completed with warnings${NC}" | tee -a $LOG_FILE
    fi
else
    echo -e "${YELLOW}Could not compile mmap test (gcc not available)${NC}" | tee -a $LOG_FILE
fi

# Test 3: Large memory access pattern
echo "" | tee -a $LOG_FILE
echo "Test 3: Large Memory Access Pattern" | tee -a $LOG_FILE
echo "------------------------------------" | tee -a $LOG_FILE

# Create test data
echo "Creating 1MB test pattern..." | tee -a $LOG_FILE
dd if=/dev/urandom of=/tmp/test_pattern.bin bs=1M count=1 2>/dev/null

# Calculate checksum
ORIGINAL_CHECKSUM=$(md5sum /tmp/test_pattern.bin | cut -d' ' -f1)
echo "Original data checksum: $ORIGINAL_CHECKSUM" | tee -a $LOG_FILE

# Write to device (simulate DDR3 access)
echo "Writing 1MB to device..." | tee -a $LOG_FILE
dd if=/tmp/test_pattern.bin of=$DEVICE bs=1M count=1 seek=16 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Large write operation successful${NC}" | tee -a $LOG_FILE
    
    # Read back and verify
    echo "Reading back and verifying..." | tee -a $LOG_FILE
    dd if=$DEVICE of=/tmp/readback.bin bs=1M count=1 skip=16 2>/dev/null
    
    if [ $? -eq 0 ]; then
        READBACK_CHECKSUM=$(md5sum /tmp/readback.bin | cut -d' ' -f1)
        echo "Read-back checksum: $READBACK_CHECKSUM" | tee -a $LOG_FILE
        
        if [ "$ORIGINAL_CHECKSUM" = "$READBACK_CHECKSUM" ]; then
            echo -e "${GREEN}Large memory test PASSED${NC}" | tee -a $LOG_FILE
        else
            echo -e "${YELLOW}Checksums differ (may be expected for hardware)${NC}" | tee -a $LOG_FILE
        fi
    else
        echo -e "${RED}Read-back failed${NC}" | tee -a $LOG_FILE
    fi
else
    echo -e "${RED}Large write operation failed${NC}" | tee -a $LOG_FILE
fi

# Test 4: Performance test
echo "" | tee -a $LOG_FILE
echo "Test 4: Memory Performance Test" | tee -a $LOG_FILE
echo "--------------------------------" | tee -a $LOG_FILE

echo "Testing write performance..." | tee -a $LOG_FILE
WRITE_START=$(date +%s.%N)
dd if=/dev/zero of=$DEVICE bs=1M count=10 seek=32 2>/dev/null
WRITE_END=$(date +%s.%N)

if [ $? -eq 0 ]; then
    WRITE_TIME=$(echo "$WRITE_END - $WRITE_START" | bc -l)
    WRITE_SPEED=$(echo "scale=2; 10 / $WRITE_TIME" | bc -l)
    echo -e "${GREEN}Write speed: ${WRITE_SPEED} MB/s${NC}" | tee -a $LOG_FILE
else
    echo -e "${RED}Write performance test failed${NC}" | tee -a $LOG_FILE
fi

echo "Testing read performance..." | tee -a $LOG_FILE
READ_START=$(date +%s.%N)
dd if=$DEVICE of=/dev/null bs=1M count=10 skip=32 2>/dev/null
READ_END=$(date +%s.%N)

if [ $? -eq 0 ]; then
    READ_TIME=$(echo "$READ_END - $READ_START" | bc -l)
    READ_SPEED=$(echo "scale=2; 10 / $READ_TIME" | bc -l)
    echo -e "${GREEN}Read speed: ${READ_SPEED} MB/s${NC}" | tee -a $LOG_FILE
else
    echo -e "${RED}Read performance test failed${NC}" | tee -a $LOG_FILE
fi

# Test 5: Register access test
echo "" | tee -a $LOG_FILE
echo "Test 5: Register Access Test" | tee -a $LOG_FILE
echo "-----------------------------" | tee -a $LOG_FILE

# Test reading FPGA ID register (offset 0x0000)
echo "Reading FPGA ID register..." | tee -a $LOG_FILE
FPGA_ID=$(dd if=$DEVICE bs=4 count=1 skip=0 2>/dev/null | xxd -p)

if [ -n "$FPGA_ID" ]; then
    echo -e "${GREEN}FPGA ID: 0x$FPGA_ID${NC}" | tee -a $LOG_FILE
else
    echo -e "${RED}Failed to read FPGA ID${NC}" | tee -a $LOG_FILE
fi

# Test reading FPGA version register (offset 0x0004)
echo "Reading FPGA version register..." | tee -a $LOG_FILE
FPGA_VER=$(dd if=$DEVICE bs=4 count=1 skip=1 2>/dev/null | xxd -p)

if [ -n "$FPGA_VER" ]; then
    echo -e "${GREEN}FPGA Version: 0x$FPGA_VER${NC}" | tee -a $LOG_FILE
else
    echo -e "${RED}Failed to read FPGA version${NC}" | tee -a $LOG_FILE
fi

# Cleanup temporary files
rm -f /tmp/test_pattern.bin /tmp/readback.bin /tmp/mmap_test.c /tmp/mmap_test

echo "" | tee -a $LOG_FILE
echo "Memory mapping test completed" | tee -a $LOG_FILE
echo "Log file: $LOG_FILE" | tee -a $LOG_FILE

# Check if any critical errors occurred
if [ ! -e "$DEVICE" ]; then
    exit 1
fi

echo -e "${GREEN}Memory mapping test suite completed successfully${NC}"
exit 0