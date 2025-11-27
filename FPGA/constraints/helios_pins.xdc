# HELIOS Physical Constraints (Example: PYNQ-Z2 / Artix-7)

# Clock (125 MHz)
set_property -dict { PACKAGE_PIN H16   IOSTANDARD LVCMOS33 } [get_ports { clk }]; 
create_clock -add -name sys_clk_pin -period 8.00 -waveform {0 4} [get_ports { clk }];

# Reset (Btn 0)
set_property -dict { PACKAGE_PIN D19   IOSTANDARD LVCMOS33 } [get_ports { rst_n }];

# Status LED (Led 0)
set_property -dict { PACKAGE_PIN R14   IOSTANDARD LVCMOS33 } [get_ports { valid_out }];

# Note: Data inputs (target_x, phases) would typically come via AXI/DMA 
# and wouldn't be mapped to physical pins directly in the top-level wrapper 
# unless debugging via GPIO.
