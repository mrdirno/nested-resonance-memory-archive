/*
 * BittWare S5 10GbE Network Interface Module
 * Low-level hardware control for dual 10GbE interfaces
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/delay.h>
#include <linux/phy.h>
#include "bittware_s5.h"

/* 10GbE PHY register offsets */
#define PHY_CTRL_REG            0x0000
#define PHY_STATUS_REG          0x0001
#define PHY_ID1_REG             0x0002
#define PHY_ID2_REG             0x0003
#define PHY_AUTONEG_ADV_REG     0x0004
#define PHY_LINK_PARTNER_REG    0x0005
#define PHY_AUTONEG_EXP_REG     0x0006
#define PHY_EXTENDED_STATUS_REG 0x000F

/* 10GbE specific registers */
#define XGMII_CTRL_REG          0x8000
#define XGMII_STATUS_REG        0x8001
#define PCS_CTRL_REG            0x8020
#define PCS_STATUS_REG          0x8021

/* Control bits */
#define PHY_CTRL_RESET          (1 << 15)
#define PHY_CTRL_LOOPBACK       (1 << 14)
#define PHY_CTRL_SPEED_SEL      (1 << 13)
#define PHY_CTRL_AUTONEG        (1 << 12)
#define PHY_CTRL_POWER_DOWN     (1 << 11)
#define PHY_CTRL_ISOLATE        (1 << 10)
#define PHY_CTRL_RESTART_AN     (1 << 9)
#define PHY_CTRL_DUPLEX         (1 << 8)

/* Status bits */
#define PHY_STATUS_100T4        (1 << 15)
#define PHY_STATUS_100TX_FD     (1 << 14)
#define PHY_STATUS_100TX_HD     (1 << 13)
#define PHY_STATUS_10T_FD       (1 << 12)
#define PHY_STATUS_10T_HD       (1 << 11)
#define PHY_STATUS_EXTENDED     (1 << 8)
#define PHY_STATUS_MF_PREAMBLE  (1 << 6)
#define PHY_STATUS_AN_COMPLETE  (1 << 5)
#define PHY_STATUS_REMOTE_FAULT (1 << 4)
#define PHY_STATUS_AN_CAPABLE   (1 << 3)
#define PHY_STATUS_LINK_UP      (1 << 2)
#define PHY_STATUS_JABBER       (1 << 1)
#define PHY_STATUS_EXTENDED_CAP (1 << 0)

/* 10GbE MAC register offsets (relative to port base) */
#define MAC_CONFIG_REG          0x0000
#define MAC_FRAME_FILTER_REG    0x0004
#define MAC_HASH_HIGH_REG       0x0008
#define MAC_HASH_LOW_REG        0x000C
#define MAC_GMII_ADDR_REG       0x0010
#define MAC_GMII_DATA_REG       0x0014
#define MAC_FLOW_CTRL_REG       0x0018
#define MAC_VLAN_TAG_REG        0x001C

/* MAC configuration bits */
#define MAC_CONFIG_PRELEN_MASK  (0x3 << 24)
#define MAC_CONFIG_RE           (1 << 2)   /* Receiver Enable */
#define MAC_CONFIG_TE           (1 << 3)   /* Transmitter Enable */
#define MAC_CONFIG_DC           (1 << 4)   /* Deferral Check */
#define MAC_CONFIG_BL_MASK      (0x3 << 5) /* Back-Off Limit */
#define MAC_CONFIG_ACS          (1 << 7)   /* Automatic Pad/CRC Stripping */
#define MAC_CONFIG_LUD          (1 << 8)   /* Link Up/Down */
#define MAC_CONFIG_DR           (1 << 9)   /* Disable Retry */
#define MAC_CONFIG_IPC          (1 << 10)  /* Checksum Offload */
#define MAC_CONFIG_DM           (1 << 11)  /* Duplex Mode */
#define MAC_CONFIG_LM           (1 << 12)  /* Loopback Mode */
#define MAC_CONFIG_DO           (1 << 13)  /* Disable Receive Own */
#define MAC_CONFIG_FES          (1 << 14)  /* Fast Ethernet Speed */
#define MAC_CONFIG_PS           (1 << 15)  /* Port Select */
#define MAC_CONFIG_DCRS         (1 << 16)  /* Disable Carrier Sense */
#define MAC_CONFIG_IFG_MASK     (0x7 << 17) /* Inter-Frame Gap */
#define MAC_CONFIG_JE           (1 << 20)  /* Jumbo Frame Enable */
#define MAC_CONFIG_BE           (1 << 21)  /* Frame Burst Enable */
#define MAC_CONFIG_JD           (1 << 22)  /* Jabber Disable */
#define MAC_CONFIG_WD           (1 << 23)  /* Watchdog Disable */

/* Initialize 10GbE PHY */
static int init_10gbe_phy(void __iomem *base, int port)
{
    u16 phy_id1, phy_id2;
    u16 ctrl, status;
    int timeout = 1000;
    
    pr_info("Initializing 10GbE PHY for port %d\n", port);
    
    /* Read PHY ID */
    phy_id1 = ioread16(base + PHY_ID1_REG);
    phy_id2 = ioread16(base + PHY_ID2_REG);
    pr_info("PHY ID: 0x%04x%04x\n", phy_id1, phy_id2);
    
    /* Reset PHY */
    iowrite16(PHY_CTRL_RESET, base + PHY_CTRL_REG);
    
    /* Wait for reset completion */
    while (timeout-- > 0) {
        ctrl = ioread16(base + PHY_CTRL_REG);
        if (!(ctrl & PHY_CTRL_RESET))
            break;
        msleep(1);
    }
    
    if (timeout <= 0) {
        pr_err("PHY reset timeout for port %d\n", port);
        return -ETIMEDOUT;
    }
    
    /* Configure for 10Gbps operation */
    ctrl = PHY_CTRL_AUTONEG | PHY_CTRL_DUPLEX;
    iowrite16(ctrl, base + PHY_CTRL_REG);
    
    /* Enable autonegotiation */
    ctrl |= PHY_CTRL_RESTART_AN;
    iowrite16(ctrl, base + PHY_CTRL_REG);
    
    /* Wait for autonegotiation to complete */
    timeout = 3000;  /* 3 seconds */
    while (timeout-- > 0) {
        status = ioread16(base + PHY_STATUS_REG);
        if (status & PHY_STATUS_AN_COMPLETE)
            break;
        msleep(1);
    }
    
    if (timeout <= 0) {
        pr_warn("Autonegotiation timeout for port %d\n", port);
        return -ETIMEDOUT;
    }
    
    /* Check link status */
    status = ioread16(base + PHY_STATUS_REG);
    if (status & PHY_STATUS_LINK_UP) {
        pr_info("PHY link up for port %d\n", port);
    } else {
        pr_warn("PHY link down for port %d\n", port);
    }
    
    return 0;
}

/* Initialize 10GbE MAC */
static int init_10gbe_mac(void __iomem *base, int port, const u8 *mac_addr)
{
    u32 config, filter;
    
    pr_info("Initializing 10GbE MAC for port %d\n", port);
    
    /* Configure MAC */
    config = MAC_CONFIG_TE | MAC_CONFIG_RE |     /* TX/RX Enable */
             MAC_CONFIG_DM |                     /* Full Duplex */
             MAC_CONFIG_ACS |                    /* Auto Pad/CRC Strip */
             MAC_CONFIG_IPC |                    /* Checksum Offload */
             MAC_CONFIG_JE;                      /* Jumbo Frame Enable */
    
    iowrite32(config, base + MAC_CONFIG_REG);
    
    /* Configure frame filter */
    filter = 0;  /* Accept all frames initially */
    iowrite32(filter, base + MAC_FRAME_FILTER_REG);
    
    /* Set MAC address */
    if (mac_addr) {
        u32 mac_low = (mac_addr[3] << 24) | (mac_addr[2] << 16) |
                      (mac_addr[1] << 8) | mac_addr[0];
        u32 mac_high = (mac_addr[5] << 8) | mac_addr[4];
        
        /* MAC address registers are at different offsets */
        iowrite32(mac_low, base + REG_NET0_MAC_LOW + (port * 0x100));
        iowrite32(mac_high, base + REG_NET0_MAC_HIGH + (port * 0x100));
        
        pr_info("MAC address set: %02x:%02x:%02x:%02x:%02x:%02x\n",
                mac_addr[0], mac_addr[1], mac_addr[2],
                mac_addr[3], mac_addr[4], mac_addr[5]);
    }
    
    /* Configure flow control */
    iowrite32(0x0000FFFF, base + MAC_FLOW_CTRL_REG);
    
    return 0;
}

/* Configure 10GbE interface for optimal performance */
int bittware_s5_init_10gbe_port(void __iomem *base, int port, const u8 *mac_addr)
{
    void __iomem *port_base;
    int ret;
    
    if (port >= 2) {
        pr_err("Invalid port number: %d\n", port);
        return -EINVAL;
    }
    
    port_base = base + (port == 0 ? REG_NET0_CTRL : REG_NET1_CTRL);
    
    /* Reset the port */
    iowrite32(NET_CTRL_RESET, port_base + NET_REG_CTRL);
    msleep(10);
    iowrite32(0, port_base + NET_REG_CTRL);
    
    /* Initialize PHY */
    ret = init_10gbe_phy(port_base, port);
    if (ret) {
        pr_err("Failed to initialize PHY for port %d\n", port);
        return ret;
    }
    
    /* Initialize MAC */
    ret = init_10gbe_mac(port_base, port, mac_addr);
    if (ret) {
        pr_err("Failed to initialize MAC for port %d\n", port);
        return ret;
    }
    
    /* Configure DMA descriptors (simplified) */
    iowrite32(0, port_base + NET_REG_TX_HEAD);
    iowrite32(0, port_base + NET_REG_TX_TAIL);
    iowrite32(0, port_base + NET_REG_RX_HEAD);
    iowrite32(0, port_base + NET_REG_RX_TAIL);
    
    pr_info("10GbE port %d initialized successfully\n", port);
    return 0;
}

/* Get link status */
bool bittware_s5_get_10gbe_link_status(void __iomem *base, int port)
{
    void __iomem *port_base;
    u32 link_status;
    
    if (port >= 2)
        return false;
    
    port_base = base + (port == 0 ? REG_NET0_CTRL : REG_NET1_CTRL);
    link_status = ioread32(port_base + NET_REG_LINK);
    
    return (link_status & 0x1) != 0;
}

/* Get link speed */
int bittware_s5_get_10gbe_link_speed(void __iomem *base, int port)
{
    void __iomem *port_base;
    u32 link_status;
    
    if (port >= 2)
        return 0;
    
    port_base = base + (port == 0 ? REG_NET0_CTRL : REG_NET1_CTRL);
    link_status = ioread32(port_base + NET_REG_LINK);
    
    /* Extract speed from status register */
    switch ((link_status >> 1) & 0x7) {
    case 0: return 1000;     /* 1 Gbps */
    case 1: return 10000;    /* 10 Gbps */
    case 2: return 25000;    /* 25 Gbps */
    case 3: return 40000;    /* 40 Gbps */
    default: return 0;       /* Unknown */
    }
}

/* Configure loopback mode */
int bittware_s5_set_10gbe_loopback(void __iomem *base, int port, bool enable)
{
    void __iomem *port_base;
    u32 ctrl;
    
    if (port >= 2)
        return -EINVAL;
    
    port_base = base + (port == 0 ? REG_NET0_CTRL : REG_NET1_CTRL);
    ctrl = ioread32(port_base + NET_REG_CTRL);
    
    if (enable) {
        ctrl |= NET_CTRL_LOOPBACK;
    } else {
        ctrl &= ~NET_CTRL_LOOPBACK;
    }
    
    iowrite32(ctrl, port_base + NET_REG_CTRL);
    
    pr_info("10GbE port %d loopback %s\n", port, enable ? "enabled" : "disabled");
    return 0;
}

/* Configure promiscuous mode */
int bittware_s5_set_10gbe_promiscuous(void __iomem *base, int port, bool enable)
{
    void __iomem *port_base;
    u32 ctrl;
    
    if (port >= 2)
        return -EINVAL;
    
    port_base = base + (port == 0 ? REG_NET0_CTRL : REG_NET1_CTRL);
    ctrl = ioread32(port_base + NET_REG_CTRL);
    
    if (enable) {
        ctrl |= NET_CTRL_PROMISC;
    } else {
        ctrl &= ~NET_CTRL_PROMISC;
    }
    
    iowrite32(ctrl, port_base + NET_REG_CTRL);
    
    pr_info("10GbE port %d promiscuous mode %s\n", port, enable ? "enabled" : "disabled");
    return 0;
}

/* Get network statistics */
void bittware_s5_get_10gbe_stats(void __iomem *base, int port, 
                                 struct bittware_s5_net_stats *stats)
{
    void __iomem *stats_base;
    
    if (port >= 2 || !stats)
        return;
    
    stats_base = base + (port == 0 ? REG_NET0_STATS : REG_NET1_STATS);
    
    /* Read hardware statistics registers */
    stats->rx_packets = ioread32(stats_base + 0x00);
    stats->tx_packets = ioread32(stats_base + 0x04);
    stats->rx_bytes = ((u64)ioread32(stats_base + 0x0C) << 32) | 
                      ioread32(stats_base + 0x08);
    stats->tx_bytes = ((u64)ioread32(stats_base + 0x14) << 32) | 
                      ioread32(stats_base + 0x10);
    stats->rx_errors = ioread32(stats_base + 0x18);
    stats->tx_errors = ioread32(stats_base + 0x1C);
    stats->rx_dropped = ioread32(stats_base + 0x20);
    stats->tx_dropped = ioread32(stats_base + 0x24);
}

/* Perform cable diagnostics */
int bittware_s5_10gbe_cable_test(void __iomem *base, int port)
{
    void __iomem *port_base;
    u16 ctrl, status;
    int i, fault_distance = 0;
    bool cable_ok = true;
    
    if (port >= 2)
        return -EINVAL;
    
    port_base = base + (port == 0 ? REG_NET0_CTRL : REG_NET1_CTRL);
    
    pr_info("Starting cable diagnostics for port %d\n", port);
    
    /* Enable cable diagnostic mode */
    ctrl = ioread16(port_base + PHY_CTRL_REG);
    ctrl |= (1 << 8);  /* Cable diagnostic enable bit */
    iowrite16(ctrl, port_base + PHY_CTRL_REG);
    
    /* Wait for test completion */
    msleep(1000);
    
    /* Read test results */
    for (i = 0; i < 4; i++) {  /* Test 4 pairs */
        status = ioread16(port_base + (0x8100 + i * 2));  /* Cable test result registers */
        
        switch ((status >> 13) & 0x7) {
        case 0:
            pr_info("Pair %d: OK\n", i);
            break;
        case 1:
            pr_warn("Pair %d: Open circuit at %d meters\n", i, (status & 0xFF) * 0.8);
            cable_ok = false;
            break;
        case 2:
            pr_warn("Pair %d: Short circuit at %d meters\n", i, (status & 0xFF) * 0.8);
            cable_ok = false;
            break;
        case 3:
            pr_warn("Pair %d: Impedance mismatch at %d meters\n", i, (status & 0xFF) * 0.8);
            break;
        default:
            pr_warn("Pair %d: Test failed\n", i);
            cable_ok = false;
        }
        
        if (!cable_ok)
            fault_distance = (status & 0xFF) * 0.8;
    }
    
    /* Disable cable diagnostic mode */
    ctrl &= ~(1 << 8);
    iowrite16(ctrl, port_base + PHY_CTRL_REG);
    
    pr_info("Cable diagnostics completed for port %d: %s\n", 
            port, cable_ok ? "PASS" : "FAIL");
    
    return cable_ok ? 0 : fault_distance;
}

/* Export symbols */
EXPORT_SYMBOL_GPL(bittware_s5_init_10gbe_port);
EXPORT_SYMBOL_GPL(bittware_s5_get_10gbe_link_status);
EXPORT_SYMBOL_GPL(bittware_s5_get_10gbe_link_speed);
EXPORT_SYMBOL_GPL(bittware_s5_set_10gbe_loopback);
EXPORT_SYMBOL_GPL(bittware_s5_set_10gbe_promiscuous);
EXPORT_SYMBOL_GPL(bittware_s5_get_10gbe_stats);
EXPORT_SYMBOL_GPL(bittware_s5_10gbe_cable_test);