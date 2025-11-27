#include <linux/module.h>
#include <linux/export-internal.h>
#include <linux/compiler.h>

MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

KSYMTAB_FUNC(bittware_s5_init_pcie, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dump_pcie_config, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_mem_init, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_mem_alloc, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_mem_free, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_mem_get_stats, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_init_ddr3, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_mem_cleanup, "_gpl", "");

SYMBOL_CRC(bittware_s5_init_pcie, 0x9cdb8899, "_gpl");
SYMBOL_CRC(bittware_s5_dump_pcie_config, 0x001be848, "_gpl");
SYMBOL_CRC(bittware_s5_mem_init, 0x86fb411b, "_gpl");
SYMBOL_CRC(bittware_s5_mem_alloc, 0x1246ead8, "_gpl");
SYMBOL_CRC(bittware_s5_mem_free, 0x700e902c, "_gpl");
SYMBOL_CRC(bittware_s5_mem_get_stats, 0x8f746e0d, "_gpl");
SYMBOL_CRC(bittware_s5_init_ddr3, 0x817ed59e, "_gpl");
SYMBOL_CRC(bittware_s5_mem_cleanup, 0xd272d446, "_gpl");

static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x9dd4105e, "free_irq" },
	{ 0x7e2232fb, "ioread32" },
	{ 0x9f222e1e, "alloc_chrdev_region" },
	{ 0x3c301583, "pci_find_ext_capability" },
	{ 0x092a35a2, "_copy_from_user" },
	{ 0x78de09ff, "pci_enable_device" },
	{ 0xfad8f384, "iowrite32" },
	{ 0xa883b72f, "pci_iomap" },
	{ 0x5490c000, "rb_next" },
	{ 0x7c77f2d5, "class_destroy" },
	{ 0x2cf3afc3, "__pci_register_driver" },
	{ 0x5a221064, "pci_disable_msi" },
	{ 0xa1ddf4ac, "pci_request_regions" },
	{ 0x25ffc95c, "remap_pfn_range" },
	{ 0xcb8b6ec6, "kfree" },
	{ 0xf5d8d228, "rb_insert_color" },
	{ 0xe1e1f979, "_raw_spin_lock_irqsave" },
	{ 0x2d01af44, "pci_unregister_driver" },
	{ 0xd272d446, "__fentry__" },
	{ 0xcb687552, "pci_read_config_dword" },
	{ 0xe8213e80, "_printk" },
	{ 0xd272d446, "__stack_chk_fail" },
	{ 0x5490c000, "rb_prev" },
	{ 0x0697a970, "pci_disable_link_state" },
	{ 0x431c3b7a, "_dev_info" },
	{ 0x90a48d82, "__ubsan_handle_out_of_bounds" },
	{ 0xae7140fb, "cdev_add" },
	{ 0x45479a90, "pci_find_capability" },
	{ 0x2546fbf4, "pci_enable_msi" },
	{ 0xa59da3c0, "down_write" },
	{ 0x431c3b7a, "_dev_err" },
	{ 0xa59da3c0, "up_write" },
	{ 0x9126ce86, "request_threaded_irq" },
	{ 0x773c4019, "device_create" },
	{ 0xfb3de43c, "class_create" },
	{ 0xbd03ed67, "random_kmalloc_seed" },
	{ 0xf46d5bf3, "mutex_lock" },
	{ 0x7954998b, "dma_alloc_attrs" },
	{ 0x408a6a48, "pci_read_config_word" },
	{ 0xf5d8d228, "rb_erase" },
	{ 0xc1e6c71e, "__mutex_init" },
	{ 0x81a1a811, "_raw_spin_unlock_irqrestore" },
	{ 0x322b068d, "pci_iounmap" },
	{ 0x431c3b7a, "_dev_warn" },
	{ 0xc5cb7f3b, "pci_set_master" },
	{ 0xd272d446, "__x86_return_thunk" },
	{ 0x092a35a2, "_copy_to_user" },
	{ 0x50629d65, "rb_first" },
	{ 0x7d9466e8, "pcie_capability_clear_and_set_word_unlocked" },
	{ 0x47650a06, "dma_set_coherent_mask" },
	{ 0x1cb3f009, "dma_free_attrs" },
	{ 0x0bc5fb0d, "unregister_chrdev_region" },
	{ 0xf46d5bf3, "mutex_unlock" },
	{ 0xd188c0bb, "pci_release_regions" },
	{ 0x89258034, "device_destroy" },
	{ 0x23f25c0a, "__dynamic_pr_debug" },
	{ 0xd1f07d8f, "__kmalloc_cache_noprof" },
	{ 0xc5cb7f3b, "pci_disable_device" },
	{ 0xb1ad3f2f, "boot_cpu_data" },
	{ 0x6d853a8c, "pcie_set_readrq" },
	{ 0x47650a06, "dma_set_mask" },
	{ 0x84f07bf7, "cachemode2protval" },
	{ 0x8b4aa116, "pci_write_config_word" },
	{ 0x67628f51, "msleep" },
	{ 0x97235f8d, "cdev_init" },
	{ 0x08aa223a, "pci_write_config_dword" },
	{ 0xa62b1cc9, "kmalloc_caches" },
	{ 0x91d81025, "cdev_del" },
	{ 0xab006604, "module_layout" },
};

static const u32 ____version_ext_crcs[]
__used __section("__version_ext_crcs") = {
	0x9dd4105e,
	0x7e2232fb,
	0x9f222e1e,
	0x3c301583,
	0x092a35a2,
	0x78de09ff,
	0xfad8f384,
	0xa883b72f,
	0x5490c000,
	0x7c77f2d5,
	0x2cf3afc3,
	0x5a221064,
	0xa1ddf4ac,
	0x25ffc95c,
	0xcb8b6ec6,
	0xf5d8d228,
	0xe1e1f979,
	0x2d01af44,
	0xd272d446,
	0xcb687552,
	0xe8213e80,
	0xd272d446,
	0x5490c000,
	0x0697a970,
	0x431c3b7a,
	0x90a48d82,
	0xae7140fb,
	0x45479a90,
	0x2546fbf4,
	0xa59da3c0,
	0x431c3b7a,
	0xa59da3c0,
	0x9126ce86,
	0x773c4019,
	0xfb3de43c,
	0xbd03ed67,
	0xf46d5bf3,
	0x7954998b,
	0x408a6a48,
	0xf5d8d228,
	0xc1e6c71e,
	0x81a1a811,
	0x322b068d,
	0x431c3b7a,
	0xc5cb7f3b,
	0xd272d446,
	0x092a35a2,
	0x50629d65,
	0x7d9466e8,
	0x47650a06,
	0x1cb3f009,
	0x0bc5fb0d,
	0xf46d5bf3,
	0xd188c0bb,
	0x89258034,
	0x23f25c0a,
	0xd1f07d8f,
	0xc5cb7f3b,
	0xb1ad3f2f,
	0x6d853a8c,
	0x47650a06,
	0x84f07bf7,
	0x8b4aa116,
	0x67628f51,
	0x97235f8d,
	0x08aa223a,
	0xa62b1cc9,
	0x91d81025,
	0xab006604,
};
static const char ____version_ext_names[]
__used __section("__version_ext_names") =
	"free_irq\0"
	"ioread32\0"
	"alloc_chrdev_region\0"
	"pci_find_ext_capability\0"
	"_copy_from_user\0"
	"pci_enable_device\0"
	"iowrite32\0"
	"pci_iomap\0"
	"rb_next\0"
	"class_destroy\0"
	"__pci_register_driver\0"
	"pci_disable_msi\0"
	"pci_request_regions\0"
	"remap_pfn_range\0"
	"kfree\0"
	"rb_insert_color\0"
	"_raw_spin_lock_irqsave\0"
	"pci_unregister_driver\0"
	"__fentry__\0"
	"pci_read_config_dword\0"
	"_printk\0"
	"__stack_chk_fail\0"
	"rb_prev\0"
	"pci_disable_link_state\0"
	"_dev_info\0"
	"__ubsan_handle_out_of_bounds\0"
	"cdev_add\0"
	"pci_find_capability\0"
	"pci_enable_msi\0"
	"down_write\0"
	"_dev_err\0"
	"up_write\0"
	"request_threaded_irq\0"
	"device_create\0"
	"class_create\0"
	"random_kmalloc_seed\0"
	"mutex_lock\0"
	"dma_alloc_attrs\0"
	"pci_read_config_word\0"
	"rb_erase\0"
	"__mutex_init\0"
	"_raw_spin_unlock_irqrestore\0"
	"pci_iounmap\0"
	"_dev_warn\0"
	"pci_set_master\0"
	"__x86_return_thunk\0"
	"_copy_to_user\0"
	"rb_first\0"
	"pcie_capability_clear_and_set_word_unlocked\0"
	"dma_set_coherent_mask\0"
	"dma_free_attrs\0"
	"unregister_chrdev_region\0"
	"mutex_unlock\0"
	"pci_release_regions\0"
	"device_destroy\0"
	"__dynamic_pr_debug\0"
	"__kmalloc_cache_noprof\0"
	"pci_disable_device\0"
	"boot_cpu_data\0"
	"pcie_set_readrq\0"
	"dma_set_mask\0"
	"cachemode2protval\0"
	"pci_write_config_word\0"
	"msleep\0"
	"cdev_init\0"
	"pci_write_config_dword\0"
	"kmalloc_caches\0"
	"cdev_del\0"
	"module_layout\0"
;

MODULE_INFO(depends, "");

MODULE_ALIAS("pci:v00001172d00000005sv*sd*bc*sc*i*");

MODULE_INFO(srcversion, "C362D56E6946E75124015DC");
