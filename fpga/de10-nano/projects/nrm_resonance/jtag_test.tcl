# JTAG Validation Script for NRM Resonance Wrapper
# Connects to JTAG Master and drives PIO injection port

puts "=================================================="
puts "      NRM Resonance JTAG Injection Test           "
puts "=================================================="

# 1. Initialize
set master_paths [get_service_paths master]
if {[llength $master_paths] == 0} {
    puts "Error: No JTAG Master found. Is the FPGA programmed?"
    exit
}

set master_path [lindex $master_paths 0]
puts "Found Master: $master_path"

open_service master $master_path

# 2. Test Sequence
# PIO Map:
# Bit 8: inject_en
# Bits 7-0: inject_data

proc inject_val {val} {
    global master_path
    # Set Enable=1 (Bit 8) + Value
    set data [expr 0x100 | ($val & 0xFF)]
    puts "Injecting: 0x[format %03X $data] (Val: [format %02X $val])"
    master_write_32 $master_path 0x0000 [list $data]
}

proc disable_injection {} {
    global master_path
    puts "Disabling Injection (Control to Internal LFSR)"
    master_write_32 $master_path 0x0000 [list 0x000]
}

# 3. Execution
puts "--- Starting Pattern Injection ---"

# Strong Pulse (should light up all LEDs)
inject_val 0xFF
after 1000

# Medium Pulse
inject_val 0x80
after 1000

# Low Pulse
inject_val 0x10
after 1000

# Return to internal LFSR
disable_injection

puts "--- Test Complete ---"
close_service master $master_path
puts "Service Closed."
