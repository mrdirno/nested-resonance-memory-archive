package require -exact qsys 14.0

create_system {hps_system}

set_project_property DEVICE_FAMILY "Cyclone V"
set_project_property DEVICE "5CSEBA6U23I7"

# Clock
add_instance clk_0 clock_source
set_instance_parameter_value clk_0 {clockFrequency} {50000000.0}
set_instance_parameter_value clk_0 {resetSynchronousEdges} {DEASSERT}

# HPS Component (Minimal Config for LWH2F)
add_instance hps_0 altera_hps
set_instance_parameter_value hps_0 {F2S_Width} {0}
set_instance_parameter_value hps_0 {S2F_Width} {0}
set_instance_parameter_value hps_0 {LWH2F_Enable} {true}
set_instance_parameter_value hps_0 {F2SCLK_SDRAM0_Enable} {false}
set_instance_parameter_value hps_0 {F2SCLK_SDRAM1_Enable} {false}
set_instance_parameter_value hps_0 {F2SCLK_SDRAM2_Enable} {false}

# PIO Injection (Output to Logic)
add_instance pio_injection altera_avalon_pio
set_instance_parameter_value pio_injection {direction} {Output}
set_instance_parameter_value pio_injection {width} {32}

# Connections
add_connection clk_0.clk hps_0.h2f_lw_axi_clock
add_connection clk_0.clk pio_injection.clk
add_connection clk_0.clk_reset pio_injection.reset

# Connect F2SDRAM clocks to system clock to satisfy validation (even if unused)
add_connection clk_0.clk hps_0.f2h_sdram0_clock

# HPS LWH2F Master -> PIO Slave
add_connection hps_0.h2f_lw_axi_master pio_injection.s1
set_connection_parameter_value hps_0.h2f_lw_axi_master/pio_injection.s1 baseAddress 0x0000

# Exports
add_interface clk clock sink
set_interface_property clk EXPORT_OF clk_0.clk_in
add_interface reset reset sink
set_interface_property reset EXPORT_OF clk_0.clk_in_reset
# add_interface memory conduit end
# set_interface_property memory EXPORT_OF hps_0.memory
add_interface injection_external_connection conduit end
set_interface_property injection_external_connection EXPORT_OF pio_injection.external_connection

# Save
save_system {hps_system.qsys}
