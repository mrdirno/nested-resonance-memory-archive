/*
 * BittWare S5 FPGA Driver Header File
 */

#ifndef _BITTWARE_S5_H_
#define _BITTWARE_S5_H_

#include <linux/types.h>
#include <linux/ioctl.h>

/* Register offsets for BAR0 (Control registers) */
#define REG_FPGA_ID          0x0000
#define REG_FPGA_VERSION     0x0004
#define REG_BOARD_ID         0x0008
#define REG_BUILD_DATE       0x000C
#define REG_SOFT_RESET       0x0010
#define REG_CONTROL          0x0014
#define REG_STATUS           0x0018

/* Interrupt registers */
#define REG_INT_STATUS       0x0020
#define REG_INT_ENABLE       0x0024
#define REG_INT_CLEAR        0x0028

/* DDR3 control registers */
#define REG_DDR3_INIT        0x0100
#define REG_DDR3_STATUS      0x0104
#define REG_DDR3_SIZE_LOW    0x0108
#define REG_DDR3_SIZE_HIGH   0x010C
#define REG_DDR3_TEST        0x0110

/* DMA control registers */
#define REG_DMA_CTRL         0x0200
#define REG_DMA_STATUS       0x0204
#define REG_DMA_SRC_LOW      0x0208
#define REG_DMA_SRC_HIGH     0x020C
#define REG_DMA_DST_LOW      0x0210
#define REG_DMA_DST_HIGH     0x0214
#define REG_DMA_LENGTH       0x0218
#define REG_DMA_INTERRUPT    0x021C

/* 10GbE network interface registers */
#define REG_NET0_CTRL        0x0300
#define REG_NET0_STATUS      0x0304
#define REG_NET0_MAC_LOW     0x0308
#define REG_NET0_MAC_HIGH    0x030C
#define REG_NET0_LINK        0x0310
#define REG_NET0_STATS       0x0320

#define REG_NET1_CTRL        0x0400
#define REG_NET1_STATUS      0x0404
#define REG_NET1_MAC_LOW     0x0408
#define REG_NET1_MAC_HIGH    0x040C
#define REG_NET1_LINK        0x0410
#define REG_NET1_STATS       0x0420

/* PCIe configuration registers */
#define REG_PCIE_CTRL        0x0500
#define REG_PCIE_STATUS      0x0504
#define REG_PCIE_LINK_STATUS 0x0508
#define REG_PCIE_ERROR       0x050C

/* Status bit definitions */
#define DDR3_STATUS_READY    (1 << 0)
#define DDR3_STATUS_CAL_DONE (1 << 1)
#define DDR3_STATUS_ERROR    (1 << 31)

/* Interrupt bit definitions */
#define INT_DMA_DONE         (1 << 0)
#define INT_DMA_ERROR        (1 << 1)
#define INT_NET0_RX          (1 << 8)
#define INT_NET0_TX          (1 << 9)
#define INT_NET1_RX          (1 << 10)
#define INT_NET1_TX          (1 << 11)
#define INT_ERROR            (1 << 31)

/* DMA control bits */
#define DMA_CTRL_START       (1 << 0)
#define DMA_CTRL_ABORT       (1 << 1)
#define DMA_CTRL_RESET       (1 << 2)
#define DMA_CTRL_DIR_TO_FPGA (1 << 8)
#define DMA_CTRL_DIR_FROM_FPGA (0 << 8)

/* Network control bits */
#define NET_CTRL_ENABLE      (1 << 0)
#define NET_CTRL_RESET       (1 << 1)
#define NET_CTRL_LOOPBACK    (1 << 2)
#define NET_CTRL_PROMISC     (1 << 3)

/* BAR sizes */
#define BITTWARE_S5_BAR0_SIZE  (64 * 1024)      /* 64KB */
#define BITTWARE_S5_BAR2_SIZE  (256 * 1024 * 1024)  /* 256MB */
#define BITTWARE_S5_BAR4_SIZE  (16 * 1024 * 1024)   /* 16MB */

/* IOCTL definitions */
#define BITTWARE_S5_MAGIC 0xB5

/* Device information structure */
struct bittware_s5_info {
    char driver_version[32];
    u32 fpga_id;
    u32 fpga_version;
    u64 ddr3_size;
    u32 bar0_size;
    u32 bar2_size;
    u32 num_dma_channels;
    u32 num_net_interfaces;
};

/* DMA transfer structure */
struct bittware_s5_dma_transfer {
    u64 src_addr;      /* Source address (host or FPGA) */
    u64 dst_addr;      /* Destination address (host or FPGA) */
    u32 length;        /* Transfer length in bytes */
    u32 direction;     /* 0: to FPGA, 1: from FPGA */
    u32 channel;       /* DMA channel to use */
    u32 flags;         /* Transfer flags */
};

/* Memory allocation structure */
struct bittware_s5_mem_alloc {
    u64 size;          /* Size to allocate */
    u64 addr;          /* Returned address */
    u32 flags;         /* Allocation flags */
};

/* Statistics structure */
struct bittware_s5_stats {
    u64 interrupts;
    u64 dma_transfers;
    u64 dma_bytes;
    u64 errors;
    u64 net0_rx_packets;
    u64 net0_tx_packets;
    u64 net1_rx_packets;
    u64 net1_tx_packets;
};

/* IOCTL commands */
#define BITTWARE_S5_IOCTL_GET_INFO      _IOR(BITTWARE_S5_MAGIC, 0, struct bittware_s5_info)
#define BITTWARE_S5_IOCTL_RESET         _IO(BITTWARE_S5_MAGIC, 1)
#define BITTWARE_S5_IOCTL_DMA_TRANSFER  _IOWR(BITTWARE_S5_MAGIC, 2, struct bittware_s5_dma_transfer)
#define BITTWARE_S5_IOCTL_MEM_ALLOC     _IOWR(BITTWARE_S5_MAGIC, 3, struct bittware_s5_mem_alloc)
#define BITTWARE_S5_IOCTL_MEM_FREE      _IOW(BITTWARE_S5_MAGIC, 4, u64)
#define BITTWARE_S5_IOCTL_GET_STATS     _IOR(BITTWARE_S5_MAGIC, 5, struct bittware_s5_stats)
#define BITTWARE_S5_IOCTL_NET_CONFIG    _IOW(BITTWARE_S5_MAGIC, 6, struct bittware_s5_net_config)

/* Network configuration structure */
struct bittware_s5_net_config {
    u32 interface;     /* 0 or 1 */
    u32 enable;        /* Enable/disable interface */
    u8 mac_addr[6];    /* MAC address */
    u16 mtu;           /* Maximum transmission unit */
    u32 flags;         /* Configuration flags */
};

/* DMA buffer descriptor */
struct bittware_s5_dma_desc {
    u64 addr;          /* Physical address */
    u32 length;        /* Buffer length */
    u32 flags;         /* Descriptor flags */
    u64 next;          /* Next descriptor address */
};

/* Helper macros */
#define BITTWARE_S5_ALIGN(x, a) (((x) + (a) - 1) & ~((a) - 1))
#define BITTWARE_S5_PAGE_SIZE 4096

#endif /* _BITTWARE_S5_H_ */