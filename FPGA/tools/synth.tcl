
# Vivado Synthesis Script for HELIOS
# Gate 12

# 1. Set Project
set_part xc7k325tffg900-2
read_verilog [glob FPGA/verilog/src/*.v]
read_xdc FPGA/constraints/helios.xdc

# 2. Synthesize
synth_design -top gorkov_potential -part xc7k325tffg900-2

# 3. Report
report_timing_summary -file FPGA/bitstreams/timing.rpt
report_utilization -file FPGA/bitstreams/utilization.rpt

# 4. Write Bitstream (Stub)
# write_bitstream -force FPGA/bitstreams/helios.bit
