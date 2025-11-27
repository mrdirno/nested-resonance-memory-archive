savedcmd_bittware_dma.mod := printf '%s\n'   bittware_dma_engine.o bittware_dma_buffer.o | awk '!x[$$0]++ { print("./"$$0) }' > bittware_dma.mod
