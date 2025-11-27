# Makefile for BittWare S5 FPGA Linux Kernel Drivers

# Kernel build directory
KDIR ?= /lib/modules/$(shell uname -r)/build

# Module names
obj-m += bittware_s5.o
obj-m += bittware_dma.o
# obj-m += bittware_net.o  # Temporarily disabled for kernel compatibility

# Source files for main driver
bittware_s5-objs := bittware_s5_main.o bittware_s5_pcie.o bittware_s5_mem.o

# Source files for DMA driver
bittware_dma-objs := bittware_dma_engine.o bittware_dma_buffer.o

# Source files for network driver
bittware_net-objs := bittware_net_main.o bittware_net_10gbe.o

# Compilation flags
ccflags-y := -Wall -Wextra -Wno-unused-parameter
ccflags-y += -DDEBUG

# Default target
all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f *.o *.ko *.mod.c *.mod.o .*.cmd

install:
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a

.PHONY: all clean install