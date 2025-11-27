/*
 * BittWare S5 Network Driver Main Module
 * Provides network device interface for dual 10GbE ports
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/netdevice.h>
#include <linux/etherdevice.h>
#include <linux/pci.h>
#include <linux/interrupt.h>
#include <linux/spinlock.h>
#include <linux/workqueue.h>
#include "bittware_s5.h"

#define DRIVER_NAME "bittware_net"
#define MAX_NET_DEVICES 2

/* Network device private data */
struct bittware_net_priv {
    struct net_device *netdev;
    struct pci_dev *pdev;
    void __iomem *regs;
    int port_id;
    
    /* Transmit */
    spinlock_t tx_lock;
    struct sk_buff_head tx_queue;
    struct work_struct tx_work;
    
    /* Receive */
    spinlock_t rx_lock;
    struct napi_struct napi;
    struct sk_buff_head rx_queue;
    
    /* DMA */
    int dma_channel;
    void *tx_buffer;
    dma_addr_t tx_dma;
    void *rx_buffer;
    dma_addr_t rx_dma;
    size_t buffer_size;
    
    /* Statistics */
    struct net_device_stats stats;
    
    /* Link state */
    bool link_up;
    int link_speed;  /* Mbps */
    
    /* Workqueue */
    struct workqueue_struct *workqueue;
};

/* Network register offsets (relative to port base) */
#define NET_REG_CTRL        0x00
#define NET_REG_STATUS      0x04
#define NET_REG_MAC_LOW     0x08
#define NET_REG_MAC_HIGH    0x0C
#define NET_REG_LINK        0x10
#define NET_REG_TX_HEAD     0x20
#define NET_REG_TX_TAIL     0x24
#define NET_REG_RX_HEAD     0x30
#define NET_REG_RX_TAIL     0x34
#define NET_REG_INT_STATUS  0x40
#define NET_REG_INT_ENABLE  0x44

/* Control bits */
#define NET_CTRL_ENABLE     (1 << 0)
#define NET_CTRL_TX_ENABLE  (1 << 1)
#define NET_CTRL_RX_ENABLE  (1 << 2)
#define NET_CTRL_PROMISC    (1 << 3)
#define NET_CTRL_LOOPBACK   (1 << 4)
#define NET_CTRL_RESET      (1 << 31)

/* Status bits */
#define NET_STATUS_READY    (1 << 0)
#define NET_STATUS_TX_BUSY  (1 << 1)
#define NET_STATUS_RX_READY (1 << 2)

/* Interrupt bits */
#define NET_INT_TX_DONE     (1 << 0)
#define NET_INT_RX_READY    (1 << 1)
#define NET_INT_LINK_CHANGE (1 << 2)
#define NET_INT_ERROR       (1 << 31)

/* Network device operations */
static int bittware_net_open(struct net_device *netdev)
{
    struct bittware_net_priv *priv = netdev_priv(netdev);
    u32 ctrl;
    
    dev_info(&priv->pdev->dev, "Opening network interface %s\n", netdev->name);
    
    /* Reset controller */
    iowrite32(NET_CTRL_RESET, priv->regs + NET_REG_CTRL);
    msleep(10);
    iowrite32(0, priv->regs + NET_REG_CTRL);
    
    /* Set MAC address */
    iowrite32(*(u32 *)&netdev->dev_addr[0], priv->regs + NET_REG_MAC_LOW);
    iowrite32(*(u16 *)&netdev->dev_addr[4], priv->regs + NET_REG_MAC_HIGH);
    
    /* Enable interrupts */
    iowrite32(NET_INT_TX_DONE | NET_INT_RX_READY | NET_INT_LINK_CHANGE,
             priv->regs + NET_REG_INT_ENABLE);
    
    /* Enable controller */
    ctrl = NET_CTRL_ENABLE | NET_CTRL_TX_ENABLE | NET_CTRL_RX_ENABLE;
    if (netdev->flags & IFF_PROMISC)
        ctrl |= NET_CTRL_PROMISC;
    iowrite32(ctrl, priv->regs + NET_REG_CTRL);
    
    /* Enable NAPI */
    napi_enable(&priv->napi);
    
    /* Start queue */
    netif_start_queue(netdev);
    
    /* Check link status */
    priv->link_up = ioread32(priv->regs + NET_REG_LINK) & 0x1;
    if (priv->link_up) {
        netif_carrier_on(netdev);
        dev_info(&priv->pdev->dev, "Link is up at 10 Gbps\n");
    } else {
        netif_carrier_off(netdev);
        dev_info(&priv->pdev->dev, "Link is down\n");
    }
    
    return 0;
}

static int bittware_net_stop(struct net_device *netdev)
{
    struct bittware_net_priv *priv = netdev_priv(netdev);
    
    dev_info(&priv->pdev->dev, "Stopping network interface %s\n", netdev->name);
    
    /* Stop queue */
    netif_stop_queue(netdev);
    
    /* Disable NAPI */
    napi_disable(&priv->napi);
    
    /* Disable interrupts */
    iowrite32(0, priv->regs + NET_REG_INT_ENABLE);
    
    /* Disable controller */
    iowrite32(0, priv->regs + NET_REG_CTRL);
    
    /* Clear carrier */
    netif_carrier_off(netdev);
    
    /* Flush queues */
    skb_queue_purge(&priv->tx_queue);
    skb_queue_purge(&priv->rx_queue);
    
    return 0;
}

static netdev_tx_t bittware_net_xmit(struct sk_buff *skb, struct net_device *netdev)
{
    struct bittware_net_priv *priv = netdev_priv(netdev);
    unsigned long flags;
    
    /* Check if link is up */
    if (!priv->link_up) {
        dev_kfree_skb_any(skb);
        priv->stats.tx_dropped++;
        return NETDEV_TX_OK;
    }
    
    /* Queue packet for transmission */
    spin_lock_irqsave(&priv->tx_lock, flags);
    
    if (skb_queue_len(&priv->tx_queue) >= 256) {
        /* Queue full */
        spin_unlock_irqrestore(&priv->tx_lock, flags);
        netif_stop_queue(netdev);
        return NETDEV_TX_BUSY;
    }
    
    skb_queue_tail(&priv->tx_queue, skb);
    spin_unlock_irqrestore(&priv->tx_lock, flags);
    
    /* Schedule transmit work */
    queue_work(priv->workqueue, &priv->tx_work);
    
    return NETDEV_TX_OK;
}

static void bittware_net_tx_work(struct work_struct *work)
{
    struct bittware_net_priv *priv = container_of(work, struct bittware_net_priv, tx_work);
    struct sk_buff *skb;
    unsigned long flags;
    u32 status;
    
    while ((skb = skb_dequeue(&priv->tx_queue)) != NULL) {
        /* Wait for hardware to be ready */
        status = ioread32(priv->regs + NET_REG_STATUS);
        if (status & NET_STATUS_TX_BUSY) {
            /* Re-queue packet */
            skb_queue_head(&priv->tx_queue, skb);
            queue_delayed_work(priv->workqueue, 
                             (struct delayed_work *)&priv->tx_work,
                             usecs_to_jiffies(10));
            break;
        }
        
        /* Copy packet to DMA buffer */
        if (skb->len > priv->buffer_size) {
            dev_err(&priv->pdev->dev, "Packet too large: %d bytes\n", skb->len);
            dev_kfree_skb_any(skb);
            priv->stats.tx_errors++;
            continue;
        }
        
        memcpy(priv->tx_buffer, skb->data, skb->len);
        
        /* Trigger hardware transmission */
        iowrite32(skb->len, priv->regs + NET_REG_TX_HEAD);
        
        /* Update statistics */
        spin_lock_irqsave(&priv->tx_lock, flags);
        priv->stats.tx_packets++;
        priv->stats.tx_bytes += skb->len;
        spin_unlock_irqrestore(&priv->tx_lock, flags);
        
        /* Free skb */
        dev_kfree_skb_any(skb);
    }
    
    /* Restart queue if it was stopped */
    if (netif_queue_stopped(priv->netdev))
        netif_wake_queue(priv->netdev);
}

static int bittware_net_poll(struct napi_struct *napi, int budget)
{
    struct bittware_net_priv *priv = container_of(napi, struct bittware_net_priv, napi);
    struct sk_buff *skb;
    int work_done = 0;
    u32 rx_len, status;
    
    while (work_done < budget) {
        /* Check for received packet */
        status = ioread32(priv->regs + NET_REG_STATUS);
        if (!(status & NET_STATUS_RX_READY))
            break;
        
        /* Get packet length */
        rx_len = ioread32(priv->regs + NET_REG_RX_TAIL);
        if (rx_len == 0 || rx_len > priv->buffer_size) {
            dev_err(&priv->pdev->dev, "Invalid RX length: %u\n", rx_len);
            priv->stats.rx_errors++;
            iowrite32(0, priv->regs + NET_REG_RX_TAIL);  /* Clear */
            continue;
        }
        
        /* Allocate skb */
        skb = netdev_alloc_skb(priv->netdev, rx_len);
        if (!skb) {
            priv->stats.rx_dropped++;
            iowrite32(0, priv->regs + NET_REG_RX_TAIL);  /* Clear */
            continue;
        }
        
        /* Copy data from DMA buffer */
        skb_put(skb, rx_len);
        memcpy(skb->data, priv->rx_buffer, rx_len);
        
        /* Set protocol */
        skb->protocol = eth_type_trans(skb, priv->netdev);
        
        /* Update statistics */
        priv->stats.rx_packets++;
        priv->stats.rx_bytes += rx_len;
        
        /* Pass to network stack */
        netif_receive_skb(skb);
        
        /* Clear RX ready */
        iowrite32(0, priv->regs + NET_REG_RX_TAIL);
        
        work_done++;
    }
    
    if (work_done < budget) {
        napi_complete(napi);
        /* Re-enable RX interrupt */
        iowrite32(ioread32(priv->regs + NET_REG_INT_ENABLE) | NET_INT_RX_READY,
                 priv->regs + NET_REG_INT_ENABLE);
    }
    
    return work_done;
}

static struct net_device_stats *bittware_net_get_stats(struct net_device *netdev)
{
    struct bittware_net_priv *priv = netdev_priv(netdev);
    return &priv->stats;
}

static void bittware_net_set_multicast(struct net_device *netdev)
{
    struct bittware_net_priv *priv = netdev_priv(netdev);
    u32 ctrl = ioread32(priv->regs + NET_REG_CTRL);
    
    if (netdev->flags & IFF_PROMISC) {
        ctrl |= NET_CTRL_PROMISC;
    } else {
        ctrl &= ~NET_CTRL_PROMISC;
    }
    
    iowrite32(ctrl, priv->regs + NET_REG_CTRL);
}

static int bittware_net_set_mac_address(struct net_device *netdev, void *addr)
{
    struct bittware_net_priv *priv = netdev_priv(netdev);
    struct sockaddr *saddr = addr;
    
    if (!is_valid_ether_addr(saddr->sa_data))
        return -EADDRNOTAVAIL;
    
    memcpy(netdev->dev_addr, saddr->sa_data, ETH_ALEN);
    
    /* Update hardware */
    iowrite32(*(u32 *)&netdev->dev_addr[0], priv->regs + NET_REG_MAC_LOW);
    iowrite32(*(u16 *)&netdev->dev_addr[4], priv->regs + NET_REG_MAC_HIGH);
    
    return 0;
}

static const struct net_device_ops bittware_net_ops = {
    .ndo_open = bittware_net_open,
    .ndo_stop = bittware_net_stop,
    .ndo_start_xmit = bittware_net_xmit,
    .ndo_get_stats = bittware_net_get_stats,
    .ndo_set_rx_mode = bittware_net_set_multicast,
    .ndo_set_mac_address = bittware_net_set_mac_address,
    .ndo_validate_addr = eth_validate_addr,
};

/* Interrupt handler */
void bittware_net_interrupt(int port, u32 status)
{
    struct net_device *netdev;
    struct bittware_net_priv *priv;
    
    if (port >= MAX_NET_DEVICES)
        return;
    
    /* Get network device from port */
    netdev = dev_get_drvdata(&dev);  /* This needs proper implementation */
    if (!netdev)
        return;
    
    priv = netdev_priv(netdev);
    
    if (status & NET_INT_TX_DONE) {
        /* TX completion handled by work queue */
    }
    
    if (status & NET_INT_RX_READY) {
        /* Disable RX interrupt and schedule NAPI */
        iowrite32(ioread32(priv->regs + NET_REG_INT_ENABLE) & ~NET_INT_RX_READY,
                 priv->regs + NET_REG_INT_ENABLE);
        napi_schedule(&priv->napi);
    }
    
    if (status & NET_INT_LINK_CHANGE) {
        /* Handle link state change */
        priv->link_up = ioread32(priv->regs + NET_REG_LINK) & 0x1;
        if (priv->link_up) {
            netif_carrier_on(netdev);
            dev_info(&priv->pdev->dev, "Link up on %s\n", netdev->name);
        } else {
            netif_carrier_off(netdev);
            dev_info(&priv->pdev->dev, "Link down on %s\n", netdev->name);
        }
    }
    
    if (status & NET_INT_ERROR) {
        dev_err(&priv->pdev->dev, "Network error interrupt: 0x%08x\n", status);
        priv->stats.rx_errors++;
    }
}

/* Initialize network device */
int bittware_net_init_port(struct pci_dev *pdev, void __iomem *base, int port_id)
{
    struct net_device *netdev;
    struct bittware_net_priv *priv;
    int ret;
    
    /* Allocate network device */
    netdev = alloc_etherdev(sizeof(struct bittware_net_priv));
    if (!netdev)
        return -ENOMEM;
    
    SET_NETDEV_DEV(netdev, &pdev->dev);
    
    priv = netdev_priv(netdev);
    priv->netdev = netdev;
    priv->pdev = pdev;
    priv->port_id = port_id;
    priv->regs = base + (port_id == 0 ? REG_NET0_CTRL : REG_NET1_CTRL);
    
    /* Initialize locks and queues */
    spin_lock_init(&priv->tx_lock);
    spin_lock_init(&priv->rx_lock);
    skb_queue_head_init(&priv->tx_queue);
    skb_queue_head_init(&priv->rx_queue);
    
    /* Initialize NAPI */
    netif_napi_add(netdev, &priv->napi, bittware_net_poll, 64);
    
    /* Allocate DMA buffers */
    priv->buffer_size = 16 * 1024;  /* 16KB buffers */
    priv->tx_buffer = dma_alloc_coherent(&pdev->dev, priv->buffer_size,
                                        &priv->tx_dma, GFP_KERNEL);
    if (!priv->tx_buffer) {
        ret = -ENOMEM;
        goto err_free_netdev;
    }
    
    priv->rx_buffer = dma_alloc_coherent(&pdev->dev, priv->buffer_size,
                                        &priv->rx_dma, GFP_KERNEL);
    if (!priv->rx_buffer) {
        ret = -ENOMEM;
        goto err_free_tx;
    }
    
    /* Create workqueue */
    priv->workqueue = create_singlethread_workqueue(netdev->name);
    if (!priv->workqueue) {
        ret = -ENOMEM;
        goto err_free_rx;
    }
    
    INIT_WORK(&priv->tx_work, bittware_net_tx_work);
    
    /* Set network device properties */
    netdev->netdev_ops = &bittware_net_ops;
    netdev->features = NETIF_F_SG | NETIF_F_HW_CSUM;
    netdev->hw_features = netdev->features;
    
    /* Set default MAC address */
    eth_hw_addr_random(netdev);
    
    /* Register network device */
    ret = register_netdev(netdev);
    if (ret) {
        dev_err(&pdev->dev, "Failed to register network device\n");
        goto err_destroy_wq;
    }
    
    dev_info(&pdev->dev, "Network interface %s initialized (port %d)\n",
             netdev->name, port_id);
    
    return 0;
    
err_destroy_wq:
    destroy_workqueue(priv->workqueue);
err_free_rx:
    dma_free_coherent(&pdev->dev, priv->buffer_size, priv->rx_buffer, priv->rx_dma);
err_free_tx:
    dma_free_coherent(&pdev->dev, priv->buffer_size, priv->tx_buffer, priv->tx_dma);
err_free_netdev:
    free_netdev(netdev);
    return ret;
}

/* Cleanup network device */
void bittware_net_cleanup_port(struct net_device *netdev)
{
    struct bittware_net_priv *priv = netdev_priv(netdev);
    
    unregister_netdev(netdev);
    destroy_workqueue(priv->workqueue);
    dma_free_coherent(&priv->pdev->dev, priv->buffer_size, 
                     priv->rx_buffer, priv->rx_dma);
    dma_free_coherent(&priv->pdev->dev, priv->buffer_size,
                     priv->tx_buffer, priv->tx_dma);
    free_netdev(netdev);
}

/* Export symbols */
EXPORT_SYMBOL_GPL(bittware_net_init_port);
EXPORT_SYMBOL_GPL(bittware_net_cleanup_port);
EXPORT_SYMBOL_GPL(bittware_net_interrupt);