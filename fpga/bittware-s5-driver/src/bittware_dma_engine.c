/*
 * BittWare S5 DMA Engine Module
 * Handles high-performance DMA transfers between host and FPGA
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/pci.h>
#include <linux/dma-mapping.h>
#include <linux/interrupt.h>
#include <linux/spinlock.h>
#include <linux/completion.h>
#include <linux/workqueue.h>
#include <linux/list.h>
#include <linux/slab.h>
#include <linux/delay.h>
#include "bittware_s5.h"

/* DMA engine constants */
#define DMA_MAX_CHANNELS     4
#define DMA_MAX_DESC_PER_CHANNEL 256
#define DMA_MAX_TRANSFER_SIZE (16 * 1024 * 1024)  /* 16MB */
#define DMA_DESC_RING_SIZE   (DMA_MAX_DESC_PER_CHANNEL * sizeof(struct dma_descriptor))

/* DMA descriptor format (hardware specific) */
struct dma_descriptor {
    u64 src_addr;
    u64 dst_addr;
    u32 length;
    u32 control;
    u64 next_desc;
    u64 reserved;
} __packed;

/* DMA transfer request */
struct dma_request {
    struct list_head list;
    u64 src_addr;
    u64 dst_addr;
    u32 length;
    u32 direction;
    void (*callback)(void *);
    void *callback_data;
    struct completion completion;
    int status;
};

/* DMA channel structure */
struct dma_channel {
    int id;
    void __iomem *regs;
    spinlock_t lock;
    
    /* Descriptor ring */
    struct dma_descriptor *desc_ring;
    dma_addr_t desc_ring_dma;
    u32 desc_head;
    u32 desc_tail;
    
    /* Request queue */
    struct list_head pending_list;
    struct list_head active_list;
    
    /* Statistics */
    u64 transfers_completed;
    u64 bytes_transferred;
    u64 errors;
    
    /* State */
    int busy;
    struct work_struct work;
    struct pci_dev *pdev;
};

/* DMA engine structure */
struct dma_engine {
    struct dma_channel channels[DMA_MAX_CHANNELS];
    void __iomem *base;
    struct pci_dev *pdev;
    int num_channels;
    struct workqueue_struct *workqueue;
};

static struct dma_engine *dma_eng = NULL;

/* Channel register offsets */
#define DMA_CH_CTRL(ch)      (0x1000 + (ch) * 0x100)
#define DMA_CH_STATUS(ch)    (0x1004 + (ch) * 0x100)
#define DMA_CH_DESC_LOW(ch)  (0x1008 + (ch) * 0x100)
#define DMA_CH_DESC_HIGH(ch) (0x100C + (ch) * 0x100)
#define DMA_CH_HEAD(ch)      (0x1010 + (ch) * 0x100)
#define DMA_CH_TAIL(ch)      (0x1014 + (ch) * 0x100)
#define DMA_CH_ERROR(ch)     (0x1018 + (ch) * 0x100)

/* Control bits */
#define DMA_CH_CTRL_ENABLE   (1 << 0)
#define DMA_CH_CTRL_RESET    (1 << 1)
#define DMA_CH_CTRL_INT_EN   (1 << 2)

/* Status bits */
#define DMA_CH_STATUS_BUSY   (1 << 0)
#define DMA_CH_STATUS_ERROR  (1 << 1)
#define DMA_CH_STATUS_DONE   (1 << 2)

/* Descriptor control bits */
#define DMA_DESC_CTRL_VALID  (1 << 0)
#define DMA_DESC_CTRL_LAST   (1 << 1)
#define DMA_DESC_CTRL_INT    (1 << 2)
#define DMA_DESC_CTRL_TO_DEV (1 << 3)

/* Initialize DMA channel */
static int dma_channel_init(struct dma_channel *ch, int id, 
                          void __iomem *base, struct pci_dev *pdev)
{
    ch->id = id;
    ch->regs = base;
    ch->pdev = pdev;
    spin_lock_init(&ch->lock);
    INIT_LIST_HEAD(&ch->pending_list);
    INIT_LIST_HEAD(&ch->active_list);
    
    /* Allocate descriptor ring */
    ch->desc_ring = dma_alloc_coherent(&pdev->dev, DMA_DESC_RING_SIZE,
                                      &ch->desc_ring_dma, GFP_KERNEL);
    if (!ch->desc_ring) {
        dev_err(&pdev->dev, "Failed to allocate descriptor ring for channel %d\n", id);
        return -ENOMEM;
    }
    
    memset(ch->desc_ring, 0, DMA_DESC_RING_SIZE);
    
    /* Reset channel */
    iowrite32(DMA_CH_CTRL_RESET, base + DMA_CH_CTRL(id));
    msleep(1);
    iowrite32(0, base + DMA_CH_CTRL(id));
    
    /* Set descriptor ring base address */
    iowrite32(lower_32_bits(ch->desc_ring_dma), base + DMA_CH_DESC_LOW(id));
    iowrite32(upper_32_bits(ch->desc_ring_dma), base + DMA_CH_DESC_HIGH(id));
    
    /* Enable channel with interrupts */
    iowrite32(DMA_CH_CTRL_ENABLE | DMA_CH_CTRL_INT_EN, base + DMA_CH_CTRL(id));
    
    dev_info(&pdev->dev, "DMA channel %d initialized\n", id);
    return 0;
}

/* Submit DMA transfer */
static void dma_submit_transfer(struct dma_channel *ch, struct dma_request *req)
{
    struct dma_descriptor *desc;
    u32 desc_idx;
    unsigned long flags;
    
    spin_lock_irqsave(&ch->lock, flags);
    
    /* Get next descriptor */
    desc_idx = ch->desc_head;
    desc = &ch->desc_ring[desc_idx];
    
    /* Fill descriptor */
    desc->src_addr = req->src_addr;
    desc->dst_addr = req->dst_addr;
    desc->length = req->length;
    desc->control = DMA_DESC_CTRL_VALID | DMA_DESC_CTRL_LAST | DMA_DESC_CTRL_INT;
    
    if (req->direction == DMA_TO_DEVICE)
        desc->control |= DMA_DESC_CTRL_TO_DEV;
    
    /* Memory barrier to ensure descriptor is written */
    wmb();
    
    /* Update head pointer */
    ch->desc_head = (ch->desc_head + 1) % DMA_MAX_DESC_PER_CHANNEL;
    iowrite32(ch->desc_head, ch->regs + DMA_CH_HEAD(ch->id));
    
    /* Move request to active list */
    list_move_tail(&req->list, &ch->active_list);
    ch->busy = 1;
    
    spin_unlock_irqrestore(&ch->lock, flags);
}

/* DMA work handler */
static void dma_work_handler(struct work_struct *work)
{
    struct dma_channel *ch = container_of(work, struct dma_channel, work);
    struct dma_request *req, *tmp;
    unsigned long flags;
    
    spin_lock_irqsave(&ch->lock, flags);
    
    /* Process pending requests */
    list_for_each_entry_safe(req, tmp, &ch->pending_list, list) {
        if (ch->busy)
            break;
        
        dma_submit_transfer(ch, req);
    }
    
    spin_unlock_irqrestore(&ch->lock, flags);
}

/* DMA interrupt handler */
void bittware_s5_dma_interrupt(int channel)
{
    struct dma_channel *ch;
    struct dma_request *req, *tmp;
    u32 status, error;
    unsigned long flags;
    
    if (!dma_eng || channel >= dma_eng->num_channels)
        return;
    
    ch = &dma_eng->channels[channel];
    
    spin_lock_irqsave(&ch->lock, flags);
    
    /* Read status */
    status = ioread32(ch->regs + DMA_CH_STATUS(channel));
    
    if (status & DMA_CH_STATUS_ERROR) {
        error = ioread32(ch->regs + DMA_CH_ERROR(channel));
        dev_err(&ch->pdev->dev, "DMA channel %d error: 0x%08x\n", channel, error);
        ch->errors++;
    }
    
    /* Process completed transfers */
    if (status & DMA_CH_STATUS_DONE) {
        list_for_each_entry_safe(req, tmp, &ch->active_list, list) {
            /* Update statistics */
            ch->transfers_completed++;
            ch->bytes_transferred += req->length;
            
            /* Mark as completed */
            req->status = (status & DMA_CH_STATUS_ERROR) ? -EIO : 0;
            list_del(&req->list);
            
            /* Clear busy flag */
            ch->busy = 0;
            
            spin_unlock_irqrestore(&ch->lock, flags);
            
            /* Call completion callback */
            if (req->callback)
                req->callback(req->callback_data);
            
            complete(&req->completion);
            
            spin_lock_irqsave(&ch->lock, flags);
        }
        
        /* Clear status */
        iowrite32(DMA_CH_STATUS_DONE | DMA_CH_STATUS_ERROR, 
                 ch->regs + DMA_CH_STATUS(channel));
    }
    
    spin_unlock_irqrestore(&ch->lock, flags);
    
    /* Schedule work to process pending requests */
    queue_work(dma_eng->workqueue, &ch->work);
}

/* Allocate DMA request */
struct dma_request *bittware_s5_dma_alloc_request(void)
{
    struct dma_request *req;
    
    req = kzalloc(sizeof(*req), GFP_KERNEL);
    if (!req)
        return NULL;
    
    INIT_LIST_HEAD(&req->list);
    init_completion(&req->completion);
    
    return req;
}

/* Free DMA request */
void bittware_s5_dma_free_request(struct dma_request *req)
{
    kfree(req);
}

/* Submit DMA transfer */
int bittware_s5_dma_submit(int channel, struct dma_request *req)
{
    struct dma_channel *ch;
    unsigned long flags;
    
    if (!dma_eng || channel >= dma_eng->num_channels)
        return -EINVAL;
    
    if (req->length > DMA_MAX_TRANSFER_SIZE)
        return -EINVAL;
    
    ch = &dma_eng->channels[channel];
    
    spin_lock_irqsave(&ch->lock, flags);
    list_add_tail(&req->list, &ch->pending_list);
    spin_unlock_irqrestore(&ch->lock, flags);
    
    /* Schedule work */
    queue_work(dma_eng->workqueue, &ch->work);
    
    return 0;
}

/* Wait for DMA completion */
int bittware_s5_dma_wait(struct dma_request *req, unsigned long timeout)
{
    unsigned long ret;
    
    ret = wait_for_completion_timeout(&req->completion, timeout);
    if (ret == 0)
        return -ETIMEDOUT;
    
    return req->status;
}

/* Perform synchronous DMA transfer */
int bittware_s5_dma_transfer(int channel, u64 src, u64 dst, u32 len, u32 dir)
{
    struct dma_request *req;
    int ret;
    
    req = bittware_s5_dma_alloc_request();
    if (!req)
        return -ENOMEM;
    
    req->src_addr = src;
    req->dst_addr = dst;
    req->length = len;
    req->direction = dir;
    
    ret = bittware_s5_dma_submit(channel, req);
    if (ret) {
        bittware_s5_dma_free_request(req);
        return ret;
    }
    
    ret = bittware_s5_dma_wait(req, msecs_to_jiffies(5000));
    bittware_s5_dma_free_request(req);
    
    return ret;
}

/* Get DMA channel statistics */
void bittware_s5_dma_get_stats(int channel, u64 *completed, u64 *bytes, u64 *errors)
{
    struct dma_channel *ch;
    unsigned long flags;
    
    if (!dma_eng || channel >= dma_eng->num_channels)
        return;
    
    ch = &dma_eng->channels[channel];
    
    spin_lock_irqsave(&ch->lock, flags);
    if (completed) *completed = ch->transfers_completed;
    if (bytes) *bytes = ch->bytes_transferred;
    if (errors) *errors = ch->errors;
    spin_unlock_irqrestore(&ch->lock, flags);
}

/* Initialize DMA engine */
int bittware_s5_dma_init(void __iomem *base, struct pci_dev *pdev, int num_channels)
{
    int i, ret;
    
    if (dma_eng) {
        dev_err(&pdev->dev, "DMA engine already initialized\n");
        return -EEXIST;
    }
    
    if (num_channels > DMA_MAX_CHANNELS)
        num_channels = DMA_MAX_CHANNELS;
    
    /* Allocate DMA engine structure */
    dma_eng = kzalloc(sizeof(*dma_eng), GFP_KERNEL);
    if (!dma_eng)
        return -ENOMEM;
    
    dma_eng->base = base;
    dma_eng->pdev = pdev;
    dma_eng->num_channels = num_channels;
    
    /* Create workqueue */
    dma_eng->workqueue = create_singlethread_workqueue("bittware_dma");
    if (!dma_eng->workqueue) {
        ret = -ENOMEM;
        goto err_free;
    }
    
    /* Initialize channels */
    for (i = 0; i < num_channels; i++) {
        INIT_WORK(&dma_eng->channels[i].work, dma_work_handler);
        ret = dma_channel_init(&dma_eng->channels[i], i, base, pdev);
        if (ret)
            goto err_cleanup;
    }
    
    dev_info(&pdev->dev, "DMA engine initialized with %d channels\n", num_channels);
    return 0;
    
err_cleanup:
    for (i--; i >= 0; i--) {
        if (dma_eng->channels[i].desc_ring) {
            dma_free_coherent(&pdev->dev, DMA_DESC_RING_SIZE,
                            dma_eng->channels[i].desc_ring,
                            dma_eng->channels[i].desc_ring_dma);
        }
    }
    destroy_workqueue(dma_eng->workqueue);
err_free:
    kfree(dma_eng);
    dma_eng = NULL;
    return ret;
}

/* Cleanup DMA engine */
void bittware_s5_dma_cleanup(struct pci_dev *pdev)
{
    int i;
    
    if (!dma_eng)
        return;
    
    /* Stop all channels */
    for (i = 0; i < dma_eng->num_channels; i++) {
        struct dma_channel *ch = &dma_eng->channels[i];
        
        /* Disable channel */
        iowrite32(0, ch->regs + DMA_CH_CTRL(i));
        
        /* Cancel pending work */
        cancel_work_sync(&ch->work);
        
        /* Free descriptor ring */
        if (ch->desc_ring) {
            dma_free_coherent(&pdev->dev, DMA_DESC_RING_SIZE,
                            ch->desc_ring, ch->desc_ring_dma);
        }
    }
    
    /* Destroy workqueue */
    destroy_workqueue(dma_eng->workqueue);
    
    kfree(dma_eng);
    dma_eng = NULL;
    
    dev_info(&pdev->dev, "DMA engine cleaned up\n");
}

/* Export symbols */
EXPORT_SYMBOL_GPL(bittware_s5_dma_init);
EXPORT_SYMBOL_GPL(bittware_s5_dma_cleanup);
EXPORT_SYMBOL_GPL(bittware_s5_dma_transfer);
EXPORT_SYMBOL_GPL(bittware_s5_dma_alloc_request);
EXPORT_SYMBOL_GPL(bittware_s5_dma_free_request);
EXPORT_SYMBOL_GPL(bittware_s5_dma_submit);
EXPORT_SYMBOL_GPL(bittware_s5_dma_wait);
EXPORT_SYMBOL_GPL(bittware_s5_dma_get_stats);
EXPORT_SYMBOL_GPL(bittware_s5_dma_interrupt);
MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("BittWare S5 Driver Team");
MODULE_DESCRIPTION("BittWare S5 FPGA DMA Engine Driver");
MODULE_VERSION("1.0.0");
