/*
 * BittWare S5 FPGA Main Driver
 * 
 * This driver provides support for BittWare S5 FPGA cards with:
 * - PCIe Gen3 x8 interface
 * - 32GB DDR3 memory
 * - Dual 10GbE network interfaces
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/pci.h>
#include <linux/device.h>
#include <linux/cdev.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/interrupt.h>
#include <linux/dma-mapping.h>
#include <linux/delay.h>
#include <linux/slab.h>
#include <linux/ioctl.h>

#include "bittware_s5.h"

#define DRIVER_NAME "bittware_s5"
#define DRIVER_VERSION "1.0.0"

/* PCI device IDs for BittWare S5 cards */
#define PCI_VENDOR_ID_ALTERA 0x1172
#define PCI_DEVICE_ID_S5_FPGA 0x0005  /* Generic ID, adjust based on actual hardware */

/* Maximum number of devices supported */
#define MAX_DEVICES 4

/* Device structure */
struct bittware_s5_dev {
    struct pci_dev *pdev;
    void __iomem *bar0;  /* BAR0 - Control registers */
    void __iomem *bar2;  /* BAR2 - Memory mapped region */
    void __iomem *bar4;  /* BAR4 - DMA region */
    
    /* Character device */
    struct cdev cdev;
    dev_t devno;
    struct class *class;
    struct device *device;
    
    /* Interrupt handling */
    int irq;
    int msi_enabled;
    
    /* DMA */
    dma_addr_t dma_handle;
    void *dma_buffer;
    size_t dma_size;
    
    /* Memory info */
    u64 ddr3_base;
    u64 ddr3_size;
    
    /* Device state */
    int initialized;
    struct mutex lock;
    
    /* Statistics */
    struct {
        u64 interrupts;
        u64 dma_transfers;
        u64 errors;
    } stats;
};

/* Global variables */
static struct bittware_s5_dev *devices[MAX_DEVICES];
static int num_devices = 0;
static dev_t dev_major;
static struct class *bittware_class;

/* PCI device table */
static struct pci_device_id bittware_s5_pci_ids[] = {
    { PCI_DEVICE(PCI_VENDOR_ID_ALTERA, PCI_DEVICE_ID_S5_FPGA) },
    { 0, }
};
MODULE_DEVICE_TABLE(pci, bittware_s5_pci_ids);

/* File operations */
static int bittware_s5_open(struct inode *inode, struct file *filp)
{
    struct bittware_s5_dev *dev;
    
    dev = container_of(inode->i_cdev, struct bittware_s5_dev, cdev);
    filp->private_data = dev;
    
    dev_info(&dev->pdev->dev, "Device opened\n");
    return 0;
}

static int bittware_s5_release(struct inode *inode, struct file *filp)
{
    struct bittware_s5_dev *dev = filp->private_data;
    
    dev_info(&dev->pdev->dev, "Device closed\n");
    return 0;
}

static ssize_t bittware_s5_read(struct file *filp, char __user *buf, 
                                size_t count, loff_t *f_pos)
{
    struct bittware_s5_dev *dev = filp->private_data;
    void __iomem *addr;
    u32 value;
    
    if (count != sizeof(u32))
        return -EINVAL;
    
    if (*f_pos >= BITTWARE_S5_BAR0_SIZE)
        return -EINVAL;
    
    addr = dev->bar0 + *f_pos;
    value = ioread32(addr);
    
    if (copy_to_user(buf, &value, sizeof(u32)))
        return -EFAULT;
    
    *f_pos += sizeof(u32);
    return sizeof(u32);
}

static ssize_t bittware_s5_write(struct file *filp, const char __user *buf,
                                 size_t count, loff_t *f_pos)
{
    struct bittware_s5_dev *dev = filp->private_data;
    void __iomem *addr;
    u32 value;
    
    if (count != sizeof(u32))
        return -EINVAL;
    
    if (*f_pos >= BITTWARE_S5_BAR0_SIZE)
        return -EINVAL;
    
    if (copy_from_user(&value, buf, sizeof(u32)))
        return -EFAULT;
    
    addr = dev->bar0 + *f_pos;
    iowrite32(value, addr);
    
    *f_pos += sizeof(u32);
    return sizeof(u32);
}

static long bittware_s5_ioctl(struct file *filp, unsigned int cmd, 
                              unsigned long arg)
{
    struct bittware_s5_dev *dev = filp->private_data;
    int ret = 0;
    
    mutex_lock(&dev->lock);
    
    switch (cmd) {
    case BITTWARE_S5_IOCTL_GET_INFO:
        {
            struct bittware_s5_info info = {
                .driver_version = DRIVER_VERSION,
                .fpga_id = ioread32(dev->bar0 + REG_FPGA_ID),
                .fpga_version = ioread32(dev->bar0 + REG_FPGA_VERSION),
                .ddr3_size = dev->ddr3_size,
                .bar0_size = BITTWARE_S5_BAR0_SIZE,
                .bar2_size = BITTWARE_S5_BAR2_SIZE,
            };
            
            if (copy_to_user((void __user *)arg, &info, sizeof(info)))
                ret = -EFAULT;
        }
        break;
        
    case BITTWARE_S5_IOCTL_RESET:
        iowrite32(0x1, dev->bar0 + REG_SOFT_RESET);
        msleep(10);
        iowrite32(0x0, dev->bar0 + REG_SOFT_RESET);
        dev_info(&dev->pdev->dev, "FPGA reset completed\n");
        break;
        
    case BITTWARE_S5_IOCTL_GET_STATS:
        {
            struct bittware_s5_stats stats = {
                .interrupts = dev->stats.interrupts,
                .dma_transfers = dev->stats.dma_transfers,
                .errors = dev->stats.errors,
            };
            
            if (copy_to_user((void __user *)arg, &stats, sizeof(stats)))
                ret = -EFAULT;
        }
        break;
        
    default:
        ret = -ENOTTY;
    }
    
    mutex_unlock(&dev->lock);
    return ret;
}

static int bittware_s5_mmap(struct file *filp, struct vm_area_struct *vma)
{
    struct bittware_s5_dev *dev = filp->private_data;
    unsigned long size = vma->vm_end - vma->vm_start;
    unsigned long offset = vma->vm_pgoff << PAGE_SHIFT;
    unsigned long pfn;
    
    /* Check size and offset */
    if (offset + size > BITTWARE_S5_BAR2_SIZE)
        return -EINVAL;
    
    /* Get physical address of BAR2 */
    pfn = (pci_resource_start(dev->pdev, 2) + offset) >> PAGE_SHIFT;
    
    /* Set VM flags for device memory */
    vm_flags_set(vma, VM_IO | VM_DONTEXPAND | VM_DONTDUMP);
    vma->vm_page_prot = pgprot_noncached(vma->vm_page_prot);
    
    /* Map the physical memory */
    if (remap_pfn_range(vma, vma->vm_start, pfn, size, vma->vm_page_prot))
        return -EAGAIN;
    
    dev_info(&dev->pdev->dev, "Memory mapped: offset=0x%lx, size=0x%lx\n", 
             offset, size);
    
    return 0;
}

static const struct file_operations bittware_s5_fops = {
    .owner = THIS_MODULE,
    .open = bittware_s5_open,
    .release = bittware_s5_release,
    .read = bittware_s5_read,
    .write = bittware_s5_write,
    .unlocked_ioctl = bittware_s5_ioctl,
    .mmap = bittware_s5_mmap,
};

/* Interrupt handler */
static irqreturn_t bittware_s5_interrupt(int irq, void *dev_id)
{
    struct bittware_s5_dev *dev = dev_id;
    u32 status;
    
    /* Read interrupt status */
    status = ioread32(dev->bar0 + REG_INT_STATUS);
    
    /* Clear interrupts */
    iowrite32(status, dev->bar0 + REG_INT_CLEAR);
    
    dev->stats.interrupts++;
    
    /* Handle specific interrupts */
    if (status & INT_DMA_DONE) {
        dev->stats.dma_transfers++;
        /* Wake up any waiting DMA operations */
    }
    
    if (status & INT_ERROR) {
        dev->stats.errors++;
        dev_err(&dev->pdev->dev, "FPGA error interrupt: 0x%08x\n", status);
    }
    
    return IRQ_HANDLED;
}

/* Initialize FPGA hardware */
static int bittware_s5_init_hardware(struct bittware_s5_dev *dev)
{
    u32 id, version;
    
    /* Read FPGA identification */
    id = ioread32(dev->bar0 + REG_FPGA_ID);
    version = ioread32(dev->bar0 + REG_FPGA_VERSION);
    
    dev_info(&dev->pdev->dev, "FPGA ID: 0x%08x, Version: 0x%08x\n", 
             id, version);
    
    /* Initialize DDR3 controller */
    iowrite32(0x1, dev->bar0 + REG_DDR3_INIT);
    msleep(100);  /* Wait for DDR3 initialization */
    
    /* Check DDR3 status */
    if (!(ioread32(dev->bar0 + REG_DDR3_STATUS) & DDR3_STATUS_READY)) {
        dev_err(&dev->pdev->dev, "DDR3 initialization failed\n");
        return -EIO;
    }
    
    /* Get DDR3 size */
    dev->ddr3_size = (u64)ioread32(dev->bar0 + REG_DDR3_SIZE_LOW);
    dev->ddr3_size |= ((u64)ioread32(dev->bar0 + REG_DDR3_SIZE_HIGH)) << 32;
    
    dev_info(&dev->pdev->dev, "DDR3 size: %llu GB\n", 
             dev->ddr3_size / (1024 * 1024 * 1024));
    
    /* Enable interrupts */
    iowrite32(INT_DMA_DONE | INT_ERROR, dev->bar0 + REG_INT_ENABLE);
    
    return 0;
}

/* PCI probe function */
static int bittware_s5_probe(struct pci_dev *pdev, 
                             const struct pci_device_id *id)
{
    struct bittware_s5_dev *dev;
    int ret;
    int bar;
    
    dev_info(&pdev->dev, "Probing BittWare S5 FPGA\n");
    
    /* Allocate device structure */
    dev = kzalloc(sizeof(*dev), GFP_KERNEL);
    if (!dev)
        return -ENOMEM;
    
    dev->pdev = pdev;
    mutex_init(&dev->lock);
    pci_set_drvdata(pdev, dev);
    
    /* Enable PCI device */
    ret = pci_enable_device(pdev);
    if (ret) {
        dev_err(&pdev->dev, "Failed to enable PCI device\n");
        goto err_free;
    }
    
    /* Request PCI regions */
    ret = pci_request_regions(pdev, DRIVER_NAME);
    if (ret) {
        dev_err(&pdev->dev, "Failed to request PCI regions\n");
        goto err_disable;
    }
    
    /* Set DMA mask for 64-bit addressing */
    ret = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(64));
    if (ret) {
        dev_err(&pdev->dev, "Failed to set 64-bit DMA mask\n");
        ret = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(32));
        if (ret) {
            dev_err(&pdev->dev, "Failed to set 32-bit DMA mask\n");
            goto err_regions;
        }
    }
    
    /* Map BARs */
    for (bar = 0; bar < 6; bar += 2) {
        if (pci_resource_len(pdev, bar) == 0)
            continue;
        
        switch (bar) {
        case 0:
            dev->bar0 = pci_iomap(pdev, bar, 0);
            if (!dev->bar0) {
                dev_err(&pdev->dev, "Failed to map BAR0\n");
                ret = -ENOMEM;
                goto err_unmap;
            }
            break;
        case 2:
            dev->bar2 = pci_iomap(pdev, bar, 0);
            if (!dev->bar2) {
                dev_err(&pdev->dev, "Failed to map BAR2\n");
                ret = -ENOMEM;
                goto err_unmap;
            }
            break;
        case 4:
            dev->bar4 = pci_iomap(pdev, bar, 0);
            if (!dev->bar4) {
                dev_err(&pdev->dev, "Failed to map BAR4\n");
                ret = -ENOMEM;
                goto err_unmap;
            }
            break;
        }
    }
    
    /* Enable bus mastering */
    pci_set_master(pdev);
    
    /* Enable MSI */
    ret = pci_enable_msi(pdev);
    if (ret) {
        dev_warn(&pdev->dev, "Failed to enable MSI, using legacy interrupts\n");
        dev->msi_enabled = 0;
    } else {
        dev->msi_enabled = 1;
    }
    
    /* Request interrupt */
    dev->irq = pdev->irq;
    ret = request_irq(dev->irq, bittware_s5_interrupt, IRQF_SHARED,
                     DRIVER_NAME, dev);
    if (ret) {
        dev_err(&pdev->dev, "Failed to request IRQ %d\n", dev->irq);
        goto err_msi;
    }
    
    /* Initialize hardware */
    ret = bittware_s5_init_hardware(dev);
    if (ret) {
        dev_err(&pdev->dev, "Failed to initialize hardware\n");
        goto err_irq;
    }
    
    /* Allocate DMA buffer */
    dev->dma_size = 4 * 1024 * 1024;  /* 4MB */
    dev->dma_buffer = dma_alloc_coherent(&pdev->dev, dev->dma_size,
                                        &dev->dma_handle, GFP_KERNEL);
    if (!dev->dma_buffer) {
        dev_err(&pdev->dev, "Failed to allocate DMA buffer\n");
        ret = -ENOMEM;
        goto err_irq;
    }
    
    /* Create character device */
    dev->devno = MKDEV(MAJOR(dev_major), num_devices);
    cdev_init(&dev->cdev, &bittware_s5_fops);
    dev->cdev.owner = THIS_MODULE;
    
    ret = cdev_add(&dev->cdev, dev->devno, 1);
    if (ret) {
        dev_err(&pdev->dev, "Failed to add character device\n");
        goto err_dma;
    }
    
    /* Create device node */
    dev->device = device_create(bittware_class, &pdev->dev, dev->devno,
                               NULL, "bittware_s5_%d", num_devices);
    if (IS_ERR(dev->device)) {
        ret = PTR_ERR(dev->device);
        dev_err(&pdev->dev, "Failed to create device node\n");
        goto err_cdev;
    }
    
    /* Add to device list */
    devices[num_devices] = dev;
    num_devices++;
    
    dev->initialized = 1;
    
    dev_info(&pdev->dev, "BittWare S5 FPGA initialized successfully\n");
    return 0;
    
err_cdev:
    cdev_del(&dev->cdev);
err_dma:
    dma_free_coherent(&pdev->dev, dev->dma_size, dev->dma_buffer, 
                     dev->dma_handle);
err_irq:
    free_irq(dev->irq, dev);
err_msi:
    if (dev->msi_enabled)
        pci_disable_msi(pdev);
err_unmap:
    if (dev->bar0)
        pci_iounmap(pdev, dev->bar0);
    if (dev->bar2)
        pci_iounmap(pdev, dev->bar2);
    if (dev->bar4)
        pci_iounmap(pdev, dev->bar4);
err_regions:
    pci_release_regions(pdev);
err_disable:
    pci_disable_device(pdev);
err_free:
    kfree(dev);
    return ret;
}

/* PCI remove function */
static void bittware_s5_remove(struct pci_dev *pdev)
{
    struct bittware_s5_dev *dev = pci_get_drvdata(pdev);
    int i;
    
    if (!dev)
        return;
    
    /* Remove from device list */
    for (i = 0; i < num_devices; i++) {
        if (devices[i] == dev) {
            devices[i] = NULL;
            break;
        }
    }
    
    /* Disable interrupts */
    iowrite32(0, dev->bar0 + REG_INT_ENABLE);
    
    /* Remove device node */
    device_destroy(bittware_class, dev->devno);
    cdev_del(&dev->cdev);
    
    /* Free DMA buffer */
    if (dev->dma_buffer)
        dma_free_coherent(&pdev->dev, dev->dma_size, dev->dma_buffer,
                         dev->dma_handle);
    
    /* Free interrupt */
    free_irq(dev->irq, dev);
    
    /* Disable MSI */
    if (dev->msi_enabled)
        pci_disable_msi(pdev);
    
    /* Unmap BARs */
    if (dev->bar0)
        pci_iounmap(pdev, dev->bar0);
    if (dev->bar2)
        pci_iounmap(pdev, dev->bar2);
    if (dev->bar4)
        pci_iounmap(pdev, dev->bar4);
    
    /* Release PCI regions */
    pci_release_regions(pdev);
    pci_disable_device(pdev);
    
    kfree(dev);
    
    dev_info(&pdev->dev, "BittWare S5 FPGA removed\n");
}

/* PCI driver structure */
static struct pci_driver bittware_s5_driver = {
    .name = DRIVER_NAME,
    .id_table = bittware_s5_pci_ids,
    .probe = bittware_s5_probe,
    .remove = bittware_s5_remove,
};

/* Module initialization */
static int __init bittware_s5_init(void)
{
    int ret;
    
    pr_info("BittWare S5 FPGA driver v%s\n", DRIVER_VERSION);
    
    /* Allocate device numbers */
    ret = alloc_chrdev_region(&dev_major, 0, MAX_DEVICES, DRIVER_NAME);
    if (ret < 0) {
        pr_err("Failed to allocate device numbers\n");
        return ret;
    }
    
    /* Create device class */
    bittware_class = class_create("bittware");
    if (IS_ERR(bittware_class)) {
        ret = PTR_ERR(bittware_class);
        pr_err("Failed to create device class\n");
        goto err_chrdev;
    }
    
    /* Register PCI driver */
    ret = pci_register_driver(&bittware_s5_driver);
    if (ret) {
        pr_err("Failed to register PCI driver\n");
        goto err_class;
    }
    
    return 0;
    
err_class:
    class_destroy(bittware_class);
err_chrdev:
    unregister_chrdev_region(dev_major, MAX_DEVICES);
    return ret;
}

/* Module cleanup */
static void __exit bittware_s5_exit(void)
{
    pci_unregister_driver(&bittware_s5_driver);
    class_destroy(bittware_class);
    unregister_chrdev_region(dev_major, MAX_DEVICES);
    
    pr_info("BittWare S5 FPGA driver unloaded\n");
}

module_init(bittware_s5_init);
module_exit(bittware_s5_exit);

MODULE_AUTHOR("BittWare S5 Driver Team");
MODULE_DESCRIPTION("BittWare S5 FPGA PCIe Driver");
MODULE_LICENSE("GPL v2");
MODULE_VERSION(DRIVER_VERSION);