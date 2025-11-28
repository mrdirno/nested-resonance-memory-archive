package require -exact qsys 14.0

create_system {jtag_system}

set_project_property DEVICE_FAMILY "Cyclone V"
set_project_property DEVICE "5CSEBA6U23I7"

# Clock
add_instance clk_0 clock_source
set_instance_parameter_value clk_0 {clockFrequency} {50000000.0}
set_instance_parameter_value clk_0 {resetSynchronousEdges} {DEASSERT}

# JTAG Master
add_instance master_0 altera_jtag_avalon_master
set_instance_parameter_value master_0 {USE_PLI} {0}
set_instance_parameter_value master_0 {PLI_PORT} {50000}

# PIO Injection (Output to Logic)
add_instance pio_injection altera_avalon_pio
set_instance_parameter_value pio_injection {direction} {Output}
set_instance_parameter_value pio_injection {width} {32}

# Connections
add_connection clk_0.clk master_0.clk
add_connection clk_0.clk pio_injection.clk
add_connection clk_0.clk_reset master_0.clk_reset
add_connection clk_0.clk_reset pio_injection.reset
add_connection master_0.master pio_injection.s1
set_connection_parameter_value master_0.master/pio_injection.s1 baseAddress 0x0000

# Exports
add_interface clk clock sink
set_interface_property clk EXPORT_OF clk_0.clk_in
add_interface reset reset sink
set_interface_property reset EXPORT_OF clk_0.clk_in_reset
add_interface injection_external_connection conduit end
set_interface_property injection_external_connection EXPORT_OF pio_injection.external_connection

# Save
save_system {jtag_system.qsys}
