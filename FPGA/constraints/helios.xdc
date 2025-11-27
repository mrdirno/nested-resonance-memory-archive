
# HELIOS Constraints (Reference)
# Clock
create_clock -period 10.000 -name sys_clk [get_ports clk]

# PCIe (Locations depend on specific board)
# set_property PACKAGE_PIN ... [get_ports pcie_rx]
