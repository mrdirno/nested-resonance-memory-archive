# Standalone JTAG Test without socket
puts "Scanning for JTAG Master..."
set master_paths [get_service_paths master]
if {[llength $master_paths] == 0} {
    puts "Error: No JTAG Master found."
    exit
}
set master_path [lindex $master_paths 0]
puts "JTAG Master: $master_path"
open_service master $master_path

puts "Writing 0xFF to 0x0000..."
master_write_32 $master_path 0x0000 [list 0x1FF]
puts "Done."
after 1000
puts "Writing 0x00 to 0x0000..."
master_write_32 $master_path 0x0000 [list 0x000]
puts "Done."
