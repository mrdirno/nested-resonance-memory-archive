/*
 * BittWare S5 DMA Buffer Management Module
 * Handles allocation and management of DMA buffers
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/dma-mapping.h>
#include <linux/mm.h>
#include <linux/list.h>
#include <linux/spinlock.h>
#include <linux/scatterlist.h>
#include <linux/vmalloc.h>
#include "bittware_s5.h"

/* DMA buffer structure */
struct dma_buffer {
    struct list_head list;
    void *virt_addr;
    dma_addr_t dma_addr;
    size_t size;
    struct page **pages;
    int nr_pages;
    struct sg_table *sgt;
    int direction;
    bool coherent;
    atomic_t refcount;
};

/* DMA buffer pool */
struct dma_buffer_pool {
    struct list_head free_list;
    struct list_head used_list;
    spinlock_t lock;
    struct device *dev;
    size_t total_size;
    size_t free_size;
    int num_buffers;
};

static struct dma_buffer_pool *buffer_pool = NULL;

/* Allocate coherent DMA buffer */
struct dma_buffer *bittware_s5_dma_alloc_coherent(struct device *dev, size_t size)
{
    struct dma_buffer *buf;
    
    buf = kzalloc(sizeof(*buf), GFP_KERNEL);
    if (!buf)
        return NULL;
    
    buf->virt_addr = dma_alloc_coherent(dev, size, &buf->dma_addr, GFP_KERNEL);
    if (!buf->virt_addr) {
        kfree(buf);
        return NULL;
    }
    
    buf->size = size;
    buf->coherent = true;
    atomic_set(&buf->refcount, 1);
    INIT_LIST_HEAD(&buf->list);
    
    dev_dbg(dev, "Allocated coherent DMA buffer: size=%zu, dma_addr=0x%llx\n",
            size, (u64)buf->dma_addr);
    
    return buf;
}

/* Allocate streaming DMA buffer */
struct dma_buffer *bittware_s5_dma_alloc_streaming(struct device *dev, 
                                                   size_t size, int direction)
{
    struct dma_buffer *buf;
    int i;
    
    buf = kzalloc(sizeof(*buf), GFP_KERNEL);
    if (!buf)
        return NULL;
    
    /* Calculate number of pages */
    buf->nr_pages = (size + PAGE_SIZE - 1) >> PAGE_SHIFT;
    
    /* Allocate page array */
    buf->pages = kcalloc(buf->nr_pages, sizeof(struct page *), GFP_KERNEL);
    if (!buf->pages)
        goto err_free_buf;
    
    /* Allocate pages */
    for (i = 0; i < buf->nr_pages; i++) {
        buf->pages[i] = alloc_page(GFP_KERNEL | __GFP_DMA);
        if (!buf->pages[i])
            goto err_free_pages;
    }
    
    /* Map pages to kernel virtual address */
    buf->virt_addr = vmap(buf->pages, buf->nr_pages, 0, PAGE_KERNEL);
    if (!buf->virt_addr)
        goto err_free_pages;
    
    /* Create scatter-gather table */
    buf->sgt = kmalloc(sizeof(*buf->sgt), GFP_KERNEL);
    if (!buf->sgt)
        goto err_vunmap;
    
    if (sg_alloc_table_from_pages(buf->sgt, buf->pages, buf->nr_pages,
                                  0, size, GFP_KERNEL) < 0)
        goto err_free_sgt;
    
    /* Map for DMA */
    if (dma_map_sg(dev, buf->sgt->sgl, buf->sgt->nents, direction) == 0)
        goto err_free_sg_table;
    
    buf->dma_addr = sg_dma_address(buf->sgt->sgl);
    buf->size = size;
    buf->direction = direction;
    buf->coherent = false;
    atomic_set(&buf->refcount, 1);
    INIT_LIST_HEAD(&buf->list);
    
    dev_dbg(dev, "Allocated streaming DMA buffer: size=%zu, dma_addr=0x%llx\n",
            size, (u64)buf->dma_addr);
    
    return buf;
    
err_free_sg_table:
    sg_free_table(buf->sgt);
err_free_sgt:
    kfree(buf->sgt);
err_vunmap:
    vunmap(buf->virt_addr);
err_free_pages:
    for (i--; i >= 0; i--)
        __free_page(buf->pages[i]);
    kfree(buf->pages);
err_free_buf:
    kfree(buf);
    return NULL;
}

/* Free DMA buffer */
void bittware_s5_dma_free_buffer(struct device *dev, struct dma_buffer *buf)
{
    int i;
    
    if (!buf)
        return;
    
    if (!atomic_dec_and_test(&buf->refcount))
        return;
    
    if (buf->coherent) {
        dma_free_coherent(dev, buf->size, buf->virt_addr, buf->dma_addr);
    } else {
        /* Unmap from DMA */
        dma_unmap_sg(dev, buf->sgt->sgl, buf->sgt->nents, buf->direction);
        
        /* Free scatter-gather table */
        sg_free_table(buf->sgt);
        kfree(buf->sgt);
        
        /* Unmap from kernel */
        vunmap(buf->virt_addr);
        
        /* Free pages */
        for (i = 0; i < buf->nr_pages; i++)
            __free_page(buf->pages[i]);
        
        kfree(buf->pages);
    }
    
    kfree(buf);
}

/* Get DMA buffer reference */
void bittware_s5_dma_get_buffer(struct dma_buffer *buf)
{
    atomic_inc(&buf->refcount);
}

/* Map DMA buffer to user space */
int bittware_s5_dma_mmap_buffer(struct dma_buffer *buf, struct vm_area_struct *vma)
{
    unsigned long size = vma->vm_end - vma->vm_start;
    unsigned long offset = vma->vm_pgoff << PAGE_SHIFT;
    
    if (offset + size > buf->size)
        return -EINVAL;
    
    if (buf->coherent) {
        /* Map coherent buffer */
        return dma_mmap_coherent(buffer_pool->dev, vma, 
                               buf->virt_addr, buf->dma_addr, buf->size);
    } else {
        /* Map streaming buffer page by page */
        unsigned long addr = vma->vm_start;
        int i, ret;
        
        for (i = offset >> PAGE_SHIFT; i < buf->nr_pages && addr < vma->vm_end; i++) {
            ret = vm_insert_page(vma, addr, buf->pages[i]);
            if (ret)
                return ret;
            addr += PAGE_SIZE;
        }
    }
    
    return 0;
}

/* Sync DMA buffer for CPU access */
void bittware_s5_dma_sync_for_cpu(struct device *dev, struct dma_buffer *buf)
{
    if (!buf->coherent) {
        dma_sync_sg_for_cpu(dev, buf->sgt->sgl, buf->sgt->nents, buf->direction);
    }
}

/* Sync DMA buffer for device access */
void bittware_s5_dma_sync_for_device(struct device *dev, struct dma_buffer *buf)
{
    if (!buf->coherent) {
        dma_sync_sg_for_device(dev, buf->sgt->sgl, buf->sgt->nents, buf->direction);
    }
}

/* Initialize DMA buffer pool */
int bittware_s5_dma_pool_init(struct device *dev, size_t pool_size)
{
    struct dma_buffer *buf;
    size_t buf_size = 2 * 1024 * 1024;  /* 2MB buffers */
    int num_buffers = pool_size / buf_size;
    int i;
    
    if (buffer_pool) {
        dev_err(dev, "DMA buffer pool already initialized\n");
        return -EEXIST;
    }
    
    buffer_pool = kzalloc(sizeof(*buffer_pool), GFP_KERNEL);
    if (!buffer_pool)
        return -ENOMEM;
    
    INIT_LIST_HEAD(&buffer_pool->free_list);
    INIT_LIST_HEAD(&buffer_pool->used_list);
    spin_lock_init(&buffer_pool->lock);
    buffer_pool->dev = dev;
    
    /* Pre-allocate buffers */
    for (i = 0; i < num_buffers; i++) {
        buf = bittware_s5_dma_alloc_coherent(dev, buf_size);
        if (!buf) {
            dev_warn(dev, "Failed to allocate buffer %d/%d\n", i, num_buffers);
            break;
        }
        
        list_add(&buf->list, &buffer_pool->free_list);
        buffer_pool->free_size += buf_size;
        buffer_pool->num_buffers++;
    }
    
    buffer_pool->total_size = buffer_pool->free_size;
    
    dev_info(dev, "DMA buffer pool initialized: %d buffers, %zu MB total\n",
             buffer_pool->num_buffers, buffer_pool->total_size / (1024 * 1024));
    
    return 0;
}

/* Get buffer from pool */
struct dma_buffer *bittware_s5_dma_pool_get(size_t size)
{
    struct dma_buffer *buf = NULL;
    unsigned long flags;
    
    if (!buffer_pool)
        return NULL;
    
    spin_lock_irqsave(&buffer_pool->lock, flags);
    
    /* Find suitable buffer */
    list_for_each_entry(buf, &buffer_pool->free_list, list) {
        if (buf->size >= size) {
            list_move(&buf->list, &buffer_pool->used_list);
            buffer_pool->free_size -= buf->size;
            atomic_inc(&buf->refcount);
            goto found;
        }
    }
    buf = NULL;
    
found:
    spin_unlock_irqrestore(&buffer_pool->lock, flags);
    
    if (!buf) {
        /* Allocate new buffer if pool is empty */
        buf = bittware_s5_dma_alloc_coherent(buffer_pool->dev, size);
    }
    
    return buf;
}

/* Return buffer to pool */
void bittware_s5_dma_pool_put(struct dma_buffer *buf)
{
    unsigned long flags;
    
    if (!buffer_pool || !buf)
        return;
    
    if (!atomic_dec_and_test(&buf->refcount))
        return;
    
    spin_lock_irqsave(&buffer_pool->lock, flags);
    
    /* Check if buffer belongs to pool */
    if (!list_empty(&buf->list)) {
        list_move(&buf->list, &buffer_pool->free_list);
        buffer_pool->free_size += buf->size;
    } else {
        /* Not from pool, free it */
        spin_unlock_irqrestore(&buffer_pool->lock, flags);
        bittware_s5_dma_free_buffer(buffer_pool->dev, buf);
        return;
    }
    
    spin_unlock_irqrestore(&buffer_pool->lock, flags);
}

/* Get pool statistics */
void bittware_s5_dma_pool_stats(size_t *total, size_t *free, int *num_buffers)
{
    unsigned long flags;
    
    if (!buffer_pool) {
        if (total) *total = 0;
        if (free) *free = 0;
        if (num_buffers) *num_buffers = 0;
        return;
    }
    
    spin_lock_irqsave(&buffer_pool->lock, flags);
    if (total) *total = buffer_pool->total_size;
    if (free) *free = buffer_pool->free_size;
    if (num_buffers) *num_buffers = buffer_pool->num_buffers;
    spin_unlock_irqrestore(&buffer_pool->lock, flags);
}

/* Cleanup DMA buffer pool */
void bittware_s5_dma_pool_cleanup(void)
{
    struct dma_buffer *buf, *tmp;
    unsigned long flags;
    
    if (!buffer_pool)
        return;
    
    spin_lock_irqsave(&buffer_pool->lock, flags);
    
    /* Free all buffers */
    list_for_each_entry_safe(buf, tmp, &buffer_pool->free_list, list) {
        list_del(&buf->list);
        spin_unlock_irqrestore(&buffer_pool->lock, flags);
        bittware_s5_dma_free_buffer(buffer_pool->dev, buf);
        spin_lock_irqsave(&buffer_pool->lock, flags);
    }
    
    list_for_each_entry_safe(buf, tmp, &buffer_pool->used_list, list) {
        list_del(&buf->list);
        spin_unlock_irqrestore(&buffer_pool->lock, flags);
        bittware_s5_dma_free_buffer(buffer_pool->dev, buf);
        spin_lock_irqsave(&buffer_pool->lock, flags);
    }
    
    spin_unlock_irqrestore(&buffer_pool->lock, flags);
    
    kfree(buffer_pool);
    buffer_pool = NULL;
}

/* Export symbols */
EXPORT_SYMBOL_GPL(bittware_s5_dma_alloc_coherent);
EXPORT_SYMBOL_GPL(bittware_s5_dma_alloc_streaming);
EXPORT_SYMBOL_GPL(bittware_s5_dma_free_buffer);
EXPORT_SYMBOL_GPL(bittware_s5_dma_get_buffer);
EXPORT_SYMBOL_GPL(bittware_s5_dma_mmap_buffer);
EXPORT_SYMBOL_GPL(bittware_s5_dma_sync_for_cpu);
EXPORT_SYMBOL_GPL(bittware_s5_dma_sync_for_device);
EXPORT_SYMBOL_GPL(bittware_s5_dma_pool_init);
EXPORT_SYMBOL_GPL(bittware_s5_dma_pool_get);
EXPORT_SYMBOL_GPL(bittware_s5_dma_pool_put);
EXPORT_SYMBOL_GPL(bittware_s5_dma_pool_stats);
EXPORT_SYMBOL_GPL(bittware_s5_dma_pool_cleanup);