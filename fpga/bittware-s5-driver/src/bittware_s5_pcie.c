/*
 * BittWare S5 PCIe Interface Module
 * Handles PCIe Gen3 x8 configuration and optimization
 */

#include <linux/module.h>
#include <linux/pci.h>
#include <linux/delay.h>
#include "bittware_s5.h"

/* PCIe capability registers */
#define PCI_EXP_LNKCAP_SLS_8_0GB 0x00000003  /* Gen3 speed */
#define PCI_EXP_LNKCAP_MLW_X8    0x00000080  /* x8 width */

/* Configure PCIe link for optimal performance */
int bittware_s5_configure_pcie_link(struct pci_dev *pdev)
{
    u16 link_status, link_control;
    u32 link_cap;
    int pos;
    
    /* Find PCIe capability */
    pos = pci_find_capability(pdev, PCI_CAP_ID_EXP);
    if (!pos) {
        dev_err(&pdev->dev, "PCIe capability not found\n");
        return -ENODEV;
    }
    
    /* Read link capabilities */
    pci_read_config_dword(pdev, pos + PCI_EXP_LNKCAP, &link_cap);
    dev_info(&pdev->dev, "PCIe Link Capabilities: 0x%08x\n", link_cap);
    
    /* Read current link status */
    pci_read_config_word(pdev, pos + PCI_EXP_LNKSTA, &link_status);
    dev_info(&pdev->dev, "Current Link Status: Gen%d x%d\n",
             (link_status & PCI_EXP_LNKSTA_CLS) >> 13,
             (link_status & PCI_EXP_LNKSTA_NLW) >> 4);
    
    /* Check if we're at Gen3 x8 */
    if (((link_status & PCI_EXP_LNKSTA_CLS) != PCI_EXP_LNKSTA_CLS_8_0GB) ||
        ((link_status & PCI_EXP_LNKSTA_NLW) != PCI_EXP_LNKSTA_NLW_X8)) {
        dev_warn(&pdev->dev, "Link not at optimal Gen3 x8 configuration\n");
        
        /* Try to retrain the link */
        pci_read_config_word(pdev, pos + PCI_EXP_LNKCTL, &link_control);
        link_control |= PCI_EXP_LNKCTL_RL;  /* Retrain Link */
        pci_write_config_word(pdev, pos + PCI_EXP_LNKCTL, link_control);
        
        /* Wait for retraining to complete */
        msleep(100);
        
        /* Check status again */
        pci_read_config_word(pdev, pos + PCI_EXP_LNKSTA, &link_status);
        dev_info(&pdev->dev, "Link Status after retrain: Gen%d x%d\n",
                 (link_status & PCI_EXP_LNKSTA_CLS) >> 13,
                 (link_status & PCI_EXP_LNKSTA_NLW) >> 4);
    }
    
    return 0;
}

/* Set PCIe Max Read Request Size for optimal performance */
int bittware_s5_set_pcie_mrrs(struct pci_dev *pdev)
{
    int ret;
    int mrrs = 4096;  /* 4KB for optimal performance */
    
    ret = pcie_set_readrq(pdev, mrrs);
    if (ret) {
        dev_err(&pdev->dev, "Failed to set PCIe MRRS to %d\n", mrrs);
        return ret;
    }
    
    dev_info(&pdev->dev, "PCIe MRRS set to %d bytes\n", mrrs);
    return 0;
}

/* Enable PCIe AER (Advanced Error Reporting) */
int bittware_s5_enable_pcie_aer(struct pci_dev *pdev)
{
    int pos;
    u32 reg32;
    
    /* Find AER capability */
    pos = pci_find_ext_capability(pdev, PCI_EXT_CAP_ID_ERR);
    if (!pos) {
        dev_info(&pdev->dev, "PCIe AER capability not found\n");
        return -ENODEV;
    }
    
    /* Enable error reporting */
    pci_read_config_dword(pdev, pos + PCI_ERR_UNCOR_MASK, &reg32);
    reg32 &= ~(PCI_ERR_UNC_DLP | PCI_ERR_UNC_FCP);
    pci_write_config_dword(pdev, pos + PCI_ERR_UNCOR_MASK, reg32);
    
    /* Clear any existing errors */
    pci_write_config_dword(pdev, pos + PCI_ERR_UNCOR_STATUS, 0xffffffff);
    
    dev_info(&pdev->dev, "PCIe AER enabled\n");
    return 0;
}

/* Configure PCIe power management */
int bittware_s5_configure_pcie_power(struct pci_dev *pdev)
{
    u16 pmcsr;
    int pos;
    
    /* Find power management capability */
    pos = pci_find_capability(pdev, PCI_CAP_ID_PM);
    if (!pos) {
        dev_info(&pdev->dev, "Power management capability not found\n");
        return -ENODEV;
    }
    
    /* Read current power state */
    pci_read_config_word(pdev, pos + PCI_PM_CTRL, &pmcsr);
    
    /* Set to D0 (fully powered) */
    pmcsr &= ~PCI_PM_CTRL_STATE_MASK;
    pmcsr |= PCI_D0;
    pci_write_config_word(pdev, pos + PCI_PM_CTRL, pmcsr);
    
    /* Disable ASPM for maximum performance */
    pci_disable_link_state(pdev, PCIE_LINK_STATE_L0S | PCIE_LINK_STATE_L1 |
                          PCIE_LINK_STATE_CLKPM);
    
    dev_info(&pdev->dev, "PCIe power management configured for maximum performance\n");
    return 0;
}

/* Display PCIe configuration space */
void bittware_s5_dump_pcie_config(struct pci_dev *pdev)
{
    int i;
    u32 val;
    
    dev_info(&pdev->dev, "PCIe Configuration Space:\n");
    
    for (i = 0; i < 256; i += 4) {
        pci_read_config_dword(pdev, i, &val);
        if (i % 16 == 0)
            dev_info(&pdev->dev, "%02x: ", i);
        printk(KERN_CONT "%08x ", val);
        if (i % 16 == 12)
            printk(KERN_CONT "\n");
    }
}

/* Initialize PCIe interface */
int bittware_s5_init_pcie(struct pci_dev *pdev)
{
    int ret;
    
    dev_info(&pdev->dev, "Initializing PCIe interface\n");
    
    /* Configure PCIe link */
    ret = bittware_s5_configure_pcie_link(pdev);
    if (ret)
        return ret;
    
    /* Set optimal MRRS */
    ret = bittware_s5_set_pcie_mrrs(pdev);
    if (ret)
        return ret;
    
    /* Enable AER */
    bittware_s5_enable_pcie_aer(pdev);
    
    /* Configure power management */
    ret = bittware_s5_configure_pcie_power(pdev);
    if (ret)
        return ret;
    
    /* Enable relaxed ordering for better performance */
    pcie_capability_set_word(pdev, PCI_EXP_DEVCTL, PCI_EXP_DEVCTL_RELAX_EN);
    
    /* Enable extended tags for more outstanding transactions */
    pcie_capability_set_word(pdev, PCI_EXP_DEVCTL, PCI_EXP_DEVCTL_EXT_TAG);
    
    dev_info(&pdev->dev, "PCIe interface initialized successfully\n");
    return 0;
}

/* Export symbols for use by main driver */
EXPORT_SYMBOL_GPL(bittware_s5_init_pcie);
EXPORT_SYMBOL_GPL(bittware_s5_dump_pcie_config);