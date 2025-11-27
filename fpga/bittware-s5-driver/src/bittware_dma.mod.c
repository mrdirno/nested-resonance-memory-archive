#include <linux/module.h>
#include <linux/export-internal.h>
#include <linux/compiler.h>

MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.arch = MODULE_ARCH_INIT,
};

KSYMTAB_FUNC(bittware_s5_dma_init, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_cleanup, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_transfer, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_alloc_request, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_free_request, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_submit, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_wait, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_get_stats, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_interrupt, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_alloc_coherent, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_alloc_streaming, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_free_buffer, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_get_buffer, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_mmap_buffer, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_sync_for_cpu, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_sync_for_device, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_pool_init, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_pool_get, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_pool_put, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_pool_stats, "_gpl", "");
KSYMTAB_FUNC(bittware_s5_dma_pool_cleanup, "_gpl", "");

SYMBOL_CRC(bittware_s5_dma_init, 0x51850b31, "_gpl");
SYMBOL_CRC(bittware_s5_dma_cleanup, 0x001be848, "_gpl");
SYMBOL_CRC(bittware_s5_dma_transfer, 0xd8d2ec72, "_gpl");
SYMBOL_CRC(bittware_s5_dma_alloc_request, 0x3224ca17, "_gpl");
SYMBOL_CRC(bittware_s5_dma_free_request, 0xbee3ab40, "_gpl");
SYMBOL_CRC(bittware_s5_dma_submit, 0xd2f0e0dd, "_gpl");
SYMBOL_CRC(bittware_s5_dma_wait, 0x4684bb3b, "_gpl");
SYMBOL_CRC(bittware_s5_dma_get_stats, 0x9bd6c013, "_gpl");
SYMBOL_CRC(bittware_s5_dma_interrupt, 0x510b3a1f, "_gpl");
SYMBOL_CRC(bittware_s5_dma_alloc_coherent, 0x0333a67e, "_gpl");
SYMBOL_CRC(bittware_s5_dma_alloc_streaming, 0xf55c8244, "_gpl");
SYMBOL_CRC(bittware_s5_dma_free_buffer, 0xbe3ea003, "_gpl");
SYMBOL_CRC(bittware_s5_dma_get_buffer, 0xe3b2d577, "_gpl");
SYMBOL_CRC(bittware_s5_dma_mmap_buffer, 0x21291d7e, "_gpl");
SYMBOL_CRC(bittware_s5_dma_sync_for_cpu, 0xbe3ea003, "_gpl");
SYMBOL_CRC(bittware_s5_dma_sync_for_device, 0xbe3ea003, "_gpl");
SYMBOL_CRC(bittware_s5_dma_pool_init, 0x94a9f547, "_gpl");
SYMBOL_CRC(bittware_s5_dma_pool_get, 0xb3dc577f, "_gpl");
SYMBOL_CRC(bittware_s5_dma_pool_put, 0xe3b2d577, "_gpl");
SYMBOL_CRC(bittware_s5_dma_pool_stats, 0xdaa12adb, "_gpl");
SYMBOL_CRC(bittware_s5_dma_pool_cleanup, 0xd272d446, "_gpl");

static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x1bdf2bc8, "sme_me_mask" },
	{ 0x7e2232fb, "ioread32" },
	{ 0xdf4bee3d, "alloc_workqueue" },
	{ 0x57860fb4, "wait_for_completion_timeout" },
	{ 0xfad8f384, "iowrite32" },
	{ 0xd710adbf, "__kmalloc_noprof" },
	{ 0x65026e43, "complete" },
	{ 0x49733ad6, "queue_work_on" },
	{ 0xd648ae19, "sg_free_table" },
	{ 0x60c9c0b3, "__init_swait_queue_head" },
	{ 0xf1de9e85, "vunmap" },
	{ 0xcb8b6ec6, "kfree" },
	{ 0xe1e1f979, "_raw_spin_lock_irqsave" },
	{ 0x1476ca03, "__dynamic_dev_dbg" },
	{ 0xd272d446, "__fentry__" },
	{ 0x5a844b26, "__x86_indirect_thunk_rax" },
	{ 0x64763bd1, "__free_pages" },
	{ 0x431c3b7a, "_dev_info" },
	{ 0x90a48d82, "__ubsan_handle_out_of_bounds" },
	{ 0x3ea239d3, "vm_insert_page" },
	{ 0x431c3b7a, "_dev_err" },
	{ 0x68f793b5, "__dma_sync_sg_for_device" },
	{ 0xbd03ed67, "random_kmalloc_seed" },
	{ 0xbeb1d261, "destroy_workqueue" },
	{ 0x7954998b, "dma_alloc_attrs" },
	{ 0x68f793b5, "__dma_sync_sg_for_cpu" },
	{ 0x9e6ae041, "vmap" },
	{ 0x81a1a811, "_raw_spin_unlock_irqrestore" },
	{ 0x16a27a1b, "sg_alloc_table_from_pages_segment" },
	{ 0x5fc55113, "__default_kernel_pte_mask" },
	{ 0x27683a56, "memset" },
	{ 0x431c3b7a, "_dev_warn" },
	{ 0xd272d446, "__x86_return_thunk" },
	{ 0x1cb3f009, "dma_free_attrs" },
	{ 0xd1f07d8f, "__kmalloc_cache_noprof" },
	{ 0x2d88a3ab, "cancel_work_sync" },
	{ 0x493c40b1, "alloc_pages_noprof" },
	{ 0xc4b4896d, "dma_mmap_attrs" },
	{ 0xed64bbd2, "dma_unmap_sg_attrs" },
	{ 0xe4de56b4, "__ubsan_handle_load_invalid_value" },
	{ 0x67628f51, "msleep" },
	{ 0xa62b1cc9, "kmalloc_caches" },
	{ 0x6833da74, "dma_map_sg_attrs" },
	{ 0xab006604, "module_layout" },
};

static const u32 ____version_ext_crcs[]
__used __section("__version_ext_crcs") = {
	0x1bdf2bc8,
	0x7e2232fb,
	0xdf4bee3d,
	0x57860fb4,
	0xfad8f384,
	0xd710adbf,
	0x65026e43,
	0x49733ad6,
	0xd648ae19,
	0x60c9c0b3,
	0xf1de9e85,
	0xcb8b6ec6,
	0xe1e1f979,
	0x1476ca03,
	0xd272d446,
	0x5a844b26,
	0x64763bd1,
	0x431c3b7a,
	0x90a48d82,
	0x3ea239d3,
	0x431c3b7a,
	0x68f793b5,
	0xbd03ed67,
	0xbeb1d261,
	0x7954998b,
	0x68f793b5,
	0x9e6ae041,
	0x81a1a811,
	0x16a27a1b,
	0x5fc55113,
	0x27683a56,
	0x431c3b7a,
	0xd272d446,
	0x1cb3f009,
	0xd1f07d8f,
	0x2d88a3ab,
	0x493c40b1,
	0xc4b4896d,
	0xed64bbd2,
	0xe4de56b4,
	0x67628f51,
	0xa62b1cc9,
	0x6833da74,
	0xab006604,
};
static const char ____version_ext_names[]
__used __section("__version_ext_names") =
	"sme_me_mask\0"
	"ioread32\0"
	"alloc_workqueue\0"
	"wait_for_completion_timeout\0"
	"iowrite32\0"
	"__kmalloc_noprof\0"
	"complete\0"
	"queue_work_on\0"
	"sg_free_table\0"
	"__init_swait_queue_head\0"
	"vunmap\0"
	"kfree\0"
	"_raw_spin_lock_irqsave\0"
	"__dynamic_dev_dbg\0"
	"__fentry__\0"
	"__x86_indirect_thunk_rax\0"
	"__free_pages\0"
	"_dev_info\0"
	"__ubsan_handle_out_of_bounds\0"
	"vm_insert_page\0"
	"_dev_err\0"
	"__dma_sync_sg_for_device\0"
	"random_kmalloc_seed\0"
	"destroy_workqueue\0"
	"dma_alloc_attrs\0"
	"__dma_sync_sg_for_cpu\0"
	"vmap\0"
	"_raw_spin_unlock_irqrestore\0"
	"sg_alloc_table_from_pages_segment\0"
	"__default_kernel_pte_mask\0"
	"memset\0"
	"_dev_warn\0"
	"__x86_return_thunk\0"
	"dma_free_attrs\0"
	"__kmalloc_cache_noprof\0"
	"cancel_work_sync\0"
	"alloc_pages_noprof\0"
	"dma_mmap_attrs\0"
	"dma_unmap_sg_attrs\0"
	"__ubsan_handle_load_invalid_value\0"
	"msleep\0"
	"kmalloc_caches\0"
	"dma_map_sg_attrs\0"
	"module_layout\0"
;

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "29B7C81E0FE2E83ABBF8D74");
