# Diagnostic script to list all JTAG services
puts "========================================"
puts "JTAG Service Diagnostic"
puts "========================================"

# 1. List all masters
set masters [get_service_paths master]
puts "Masters Found: [llength $masters]"
foreach m $masters {
    puts "  - $m"
}

# 2. List all devices
set devices [get_service_paths device]
puts "Devices Found: [llength $devices]"
foreach d $devices {
    puts "  - $d"
}

# 3. List JTAG debug services
set jtag_debugs [get_service_paths jtag_debug]
puts "JTAG Debug Services: [llength $jtag_debugs]"
foreach j $jtag_debugs {
    puts "  - $j"
}

puts "========================================"
