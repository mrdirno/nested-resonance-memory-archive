# Fuzz Loop Tcl
puts "Starting JTAG Init..."; flush stdout
set retry_count 0
while {$retry_count < 10} {
    set master_paths [get_service_paths master]
    if {[llength $master_paths] > 0} {
        break
    }
    after 1000
    incr retry_count
}

if {[llength $master_paths] == 0} {
    puts "ERROR: No JTAG Master"; flush stdout
    return
}

set master_path [lindex $master_paths 0]
puts "Master: $master_path"; flush stdout
open_service master $master_path

# Reset first
master_write_32 $master_path 0x0000 0x000
after 1000

puts "Starting Fuzz Loop..."; flush stdout

for {set i 0} {$i < 8} {incr i} {
    puts "FUZZ_PIN $i"; flush stdout
    
    # Calculate 1 << i
    set val [expr {1 << $i}]
    
    # Write
    master_write_32 $master_path 0x0000 $val
    
    # Hold 2s
    after 2000
    
    # Reset
    master_write_32 $master_path 0x0000 0
    
    # Wait 0.5s
    after 500
}

puts "FUZZ_DONE"; flush stdout
close_service master $master_path
