savedcmd_bittware_s5.mod := printf '%s\n'   bittware_s5_main.o bittware_s5_pcie.o bittware_s5_mem.o | awk '!x[$$0]++ { print("./"$$0) }' > bittware_s5.mod
