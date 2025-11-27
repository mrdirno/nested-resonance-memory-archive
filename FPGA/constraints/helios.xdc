# Helios Accelerator Constraints
# Target: PYNQ-Z2 (XC7Z020)

# Clock Constraint (100 MHz)
# This is primarily for Out-of-Context (OOC) synthesis or when mapped to a physical clock pin.
# In a Zynq Block Design, this is handled by the PS/Clock Wizard.
create_clock -period 10.000 -name clk [get_ports clk]

# Reset (Active Low)
# set_property IOSTANDARD LVCMOS33 [get_ports rst_n]
# Note: No pin assignment provided as this is likely an internal IP or PS-connected block.