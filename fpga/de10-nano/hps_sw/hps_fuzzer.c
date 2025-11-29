#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <stdint.h>

#define HW_REGS_BASE (0xFF200000) // LWH2F Bridge Base
#define HW_REGS_SPAN (0x00200000)
#define HW_REGS_MASK (HW_REGS_SPAN - 1)

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <hex_value>\n", argv[0]);
        return 1;
    }

    uint32_t val = (uint32_t)strtol(argv[1], NULL, 16);
    
    int fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd == -1) {
        perror("open");
        return 1;
    }

    void *virtual_base = mmap(NULL, HW_REGS_SPAN, (PROT_READ | PROT_WRITE), MAP_SHARED, fd, HW_REGS_BASE);
    if (virtual_base == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return 1;
    }

    // Offset 0 is our PIO
    void *pio_addr = virtual_base;
    
    // Write
    *((volatile uint32_t *)pio_addr) = val;
    
    // printf("Wrote 0x%08X to PIO\n", val);

    if (munmap(virtual_base, HW_REGS_SPAN) != 0) {
        perror("munmap");
    }
    close(fd);
    return 0;
}
