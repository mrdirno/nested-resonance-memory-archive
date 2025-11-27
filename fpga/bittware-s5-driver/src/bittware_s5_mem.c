/*
 * BittWare S5 Memory Management Module
 * Handles 32GB DDR3 memory mapping and allocation
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/mm.h>
#include <linux/rbtree.h>
#include <linux/spinlock.h>
#include <linux/list.h>
#include <linux/io.h>
#include <linux/delay.h>
#include "bittware_s5.h"

/* Memory block structure */
struct mem_block {
    struct rb_node node;
    struct list_head list;
    u64 addr;
    u64 size;
    int allocated;
    void *private_data;
};

/* Memory manager structure */
struct bittware_mem_manager {
    struct rb_root blocks;
    struct list_head free_list;
    spinlock_t lock;
    u64 base_addr;
    u64 total_size;
    u64 free_size;
    u64 min_alloc_size;
    u64 alignment;
};

/* Global memory manager */
static struct bittware_mem_manager *mem_mgr = NULL;

/* Find a memory block by address */
static struct mem_block *find_block(struct rb_root *root, u64 addr)
{
    struct rb_node *node = root->rb_node;
    
    while (node) {
        struct mem_block *block = rb_entry(node, struct mem_block, node);
        
        if (addr < block->addr)
            node = node->rb_left;
        else if (addr > block->addr)
            node = node->rb_right;
        else
            return block;
    }
    
    return NULL;
}

/* Insert a memory block into the RB tree */
static int insert_block(struct rb_root *root, struct mem_block *new_block)
{
    struct rb_node **new = &(root->rb_node), *parent = NULL;
    
    while (*new) {
        struct mem_block *this = rb_entry(*new, struct mem_block, node);
        parent = *new;
        
        if (new_block->addr < this->addr)
            new = &((*new)->rb_left);
        else if (new_block->addr > this->addr)
            new = &((*new)->rb_right);
        else
            return -EEXIST;
    }
    
    rb_link_node(&new_block->node, parent, new);
    rb_insert_color(&new_block->node, root);
    
    return 0;
}

/* Initialize memory manager */
int bittware_s5_mem_init(u64 base_addr, u64 size)
{
    struct mem_block *initial_block;
    
    if (mem_mgr) {
        pr_err("Memory manager already initialized\n");
        return -EEXIST;
    }
    
    /* Allocate memory manager structure */
    mem_mgr = kzalloc(sizeof(*mem_mgr), GFP_KERNEL);
    if (!mem_mgr)
        return -ENOMEM;
    
    /* Initialize fields */
    mem_mgr->blocks = RB_ROOT;
    INIT_LIST_HEAD(&mem_mgr->free_list);
    spin_lock_init(&mem_mgr->lock);
    mem_mgr->base_addr = base_addr;
    mem_mgr->total_size = size;
    mem_mgr->free_size = size;
    mem_mgr->min_alloc_size = PAGE_SIZE;
    mem_mgr->alignment = PAGE_SIZE;
    
    /* Create initial free block */
    initial_block = kzalloc(sizeof(*initial_block), GFP_KERNEL);
    if (!initial_block) {
        kfree(mem_mgr);
        mem_mgr = NULL;
        return -ENOMEM;
    }
    
    initial_block->addr = base_addr;
    initial_block->size = size;
    initial_block->allocated = 0;
    
    /* Add to RB tree and free list */
    insert_block(&mem_mgr->blocks, initial_block);
    list_add(&initial_block->list, &mem_mgr->free_list);
    
    pr_info("BittWare S5 memory manager initialized: base=0x%llx, size=%llu MB\n",
            base_addr, size / (1024 * 1024));
    
    return 0;
}

/* Allocate memory from DDR3 */
u64 bittware_s5_mem_alloc(u64 size)
{
    struct mem_block *block, *new_block;
    struct list_head *pos;
    unsigned long flags;
    u64 addr = 0;
    
    if (!mem_mgr)
        return 0;
    
    /* Align size to minimum allocation size */
    size = BITTWARE_S5_ALIGN(size, mem_mgr->alignment);
    
    if (size < mem_mgr->min_alloc_size)
        size = mem_mgr->min_alloc_size;
    
    spin_lock_irqsave(&mem_mgr->lock, flags);
    
    /* Find a suitable free block */
    list_for_each(pos, &mem_mgr->free_list) {
        block = list_entry(pos, struct mem_block, list);
        if (block->size >= size) {
            /* Found a suitable block */
            addr = block->addr;
            
            if (block->size == size) {
                /* Exact match - mark as allocated */
                block->allocated = 1;
                list_del(&block->list);
            } else {
                /* Split the block */
                new_block = kzalloc(sizeof(*new_block), GFP_ATOMIC);
                if (!new_block) {
                    addr = 0;
                    goto out;
                }
                
                /* Update original block */
                block->addr += size;
                block->size -= size;
                
                /* Create new allocated block */
                new_block->addr = addr;
                new_block->size = size;
                new_block->allocated = 1;
                
                /* Insert new block into RB tree */
                insert_block(&mem_mgr->blocks, new_block);
            }
            
            mem_mgr->free_size -= size;
            break;
        }
    }
    
out:
    spin_unlock_irqrestore(&mem_mgr->lock, flags);
    
    if (addr)
        pr_debug("Allocated %llu bytes at 0x%llx\n", size, addr);
    else
        pr_err("Failed to allocate %llu bytes\n", size);
    
    return addr;
}

/* Free previously allocated memory */
int bittware_s5_mem_free(u64 addr)
{
    struct mem_block *block, *prev_block = NULL, *next_block = NULL;
    struct rb_node *node;
    unsigned long flags;
    int ret = 0;
    
    if (!mem_mgr)
        return -EINVAL;
    
    spin_lock_irqsave(&mem_mgr->lock, flags);
    
    /* Find the block */
    block = find_block(&mem_mgr->blocks, addr);
    if (!block || !block->allocated) {
        ret = -EINVAL;
        goto out;
    }
    
    /* Mark as free */
    block->allocated = 0;
    mem_mgr->free_size += block->size;
    
    /* Check for adjacent free blocks to merge */
    
    /* Check previous block */
    node = rb_prev(&block->node);
    if (node) {
        prev_block = rb_entry(node, struct mem_block, node);
        if (!prev_block->allocated && 
            prev_block->addr + prev_block->size == block->addr) {
            /* Merge with previous block */
            prev_block->size += block->size;
            rb_erase(&block->node, &mem_mgr->blocks);
            kfree(block);
            block = prev_block;
        }
    }
    
    /* Check next block */
    node = rb_next(&block->node);
    if (node) {
        next_block = rb_entry(node, struct mem_block, node);
        if (!next_block->allocated && 
            block->addr + block->size == next_block->addr) {
            /* Merge with next block */
            block->size += next_block->size;
            rb_erase(&next_block->node, &mem_mgr->blocks);
            list_del(&next_block->list);
            kfree(next_block);
        }
    }
    
    /* Add to free list if not already there */
    if (list_empty(&block->list))
        list_add(&block->list, &mem_mgr->free_list);
    
    pr_debug("Freed memory at 0x%llx\n", addr);
    
out:
    spin_unlock_irqrestore(&mem_mgr->lock, flags);
    return ret;
}

/* Get memory statistics */
void bittware_s5_mem_get_stats(u64 *total, u64 *free, u64 *used)
{
    unsigned long flags;
    
    if (!mem_mgr) {
        if (total) *total = 0;
        if (free) *free = 0;
        if (used) *used = 0;
        return;
    }
    
    spin_lock_irqsave(&mem_mgr->lock, flags);
    
    if (total) *total = mem_mgr->total_size;
    if (free) *free = mem_mgr->free_size;
    if (used) *used = mem_mgr->total_size - mem_mgr->free_size;
    
    spin_unlock_irqrestore(&mem_mgr->lock, flags);
}

/* DDR3 memory test function */
int bittware_s5_mem_test(void __iomem *bar, u64 offset, u64 size)
{
    u32 pattern[] = {0x00000000, 0xFFFFFFFF, 0x55555555, 0xAAAAAAAA, 
                     0x12345678, 0x87654321};
    int i, j;
    u32 value;
    void __iomem *addr;
    
    pr_info("Testing DDR3 memory at offset 0x%llx, size %llu KB\n", 
            offset, size / 1024);
    
    /* Test with different patterns */
    for (i = 0; i < ARRAY_SIZE(pattern); i++) {
        /* Write pattern */
        for (j = 0; j < size; j += sizeof(u32)) {
            addr = bar + offset + j;
            iowrite32(pattern[i], addr);
            
            /* Add memory barrier for consistency */
            if ((j & 0xFFFF) == 0)
                mb();
        }
        
        /* Read and verify pattern */
        for (j = 0; j < size; j += sizeof(u32)) {
            addr = bar + offset + j;
            value = ioread32(addr);
            
            if (value != pattern[i]) {
                pr_err("Memory test failed at offset 0x%llx: "
                       "expected 0x%08x, got 0x%08x\n",
                       offset + j, pattern[i], value);
                return -EIO;
            }
        }
        
        pr_info("Pattern 0x%08x test passed\n", pattern[i]);
    }
    
    /* Walking bit test */
    for (i = 0; i < 32; i++) {
        u32 walk_pattern = 1 << i;
        
        /* Write pattern */
        for (j = 0; j < min(size, 4096ULL); j += sizeof(u32)) {
            addr = bar + offset + j;
            iowrite32(walk_pattern, addr);
        }
        
        /* Read and verify */
        for (j = 0; j < min(size, 4096ULL); j += sizeof(u32)) {
            addr = bar + offset + j;
            value = ioread32(addr);
            
            if (value != walk_pattern) {
                pr_err("Walking bit test failed at bit %d\n", i);
                return -EIO;
            }
        }
    }
    
    pr_info("DDR3 memory test completed successfully\n");
    return 0;
}

/* Initialize DDR3 controller */
int bittware_s5_init_ddr3(void __iomem *bar)
{
    u32 status;
    int timeout = 1000;  /* 1 second timeout */
    
    pr_info("Initializing DDR3 controller\n");
    
    /* Reset DDR3 controller */
    iowrite32(0x1, bar + REG_DDR3_INIT);
    msleep(10);
    
    /* Start initialization */
    iowrite32(0x3, bar + REG_DDR3_INIT);  /* Init + Cal */
    
    /* Wait for initialization to complete */
    while (timeout-- > 0) {
        status = ioread32(bar + REG_DDR3_STATUS);
        
        if (status & DDR3_STATUS_READY) {
            pr_info("DDR3 initialization completed\n");
            
            /* Run memory test */
            return bittware_s5_mem_test(bar, 0x10000000, 1024 * 1024);
        }
        
        if (status & DDR3_STATUS_ERROR) {
            pr_err("DDR3 initialization error: status=0x%08x\n", status);
            return -EIO;
        }
        
        msleep(1);
    }
    
    pr_err("DDR3 initialization timeout\n");
    return -ETIMEDOUT;
}

/* Cleanup memory manager */
void bittware_s5_mem_cleanup(void)
{
    struct rb_node *node, *next;
    struct mem_block *block;
    unsigned long flags;
    
    if (!mem_mgr)
        return;
    
    spin_lock_irqsave(&mem_mgr->lock, flags);
    
    /* Free all memory blocks */
    node = rb_first(&mem_mgr->blocks);
    while (node) {
        next = rb_next(node);
        block = rb_entry(node, struct mem_block, node);
        rb_erase(node, &mem_mgr->blocks);
        kfree(block);
        node = next;
    }
    
    spin_unlock_irqrestore(&mem_mgr->lock, flags);
    
    kfree(mem_mgr);
    mem_mgr = NULL;
    
    pr_info("BittWare S5 memory manager cleaned up\n");
}

/* Export symbols */
EXPORT_SYMBOL_GPL(bittware_s5_mem_init);
EXPORT_SYMBOL_GPL(bittware_s5_mem_alloc);
EXPORT_SYMBOL_GPL(bittware_s5_mem_free);
EXPORT_SYMBOL_GPL(bittware_s5_mem_get_stats);
EXPORT_SYMBOL_GPL(bittware_s5_init_ddr3);
EXPORT_SYMBOL_GPL(bittware_s5_mem_cleanup);