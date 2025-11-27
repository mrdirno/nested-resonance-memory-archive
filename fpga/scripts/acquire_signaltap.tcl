# acquire_signaltap.tcl
# Automates SignalTap data acquisition

load_package stp

set stp_file "fpga/de10-nano/projects/breathing_led/breathing_led.stp"
set output_log "fpga/de10-nano/projects/breathing_led/signaltap_log.txt"

# Open the STP file
open_session -name $stp_file

# Start acquisition
puts "Starting SignalTap acquisition..."
run_session -name $stp_file -device_name "@2: 5CSEBA6(.|ES)/5CSEMA6/.. (0x02D020DD)" -hardware_name "DE-SoC [1-9]"

# Note: run_session typically blocks until trigger or stop. 
# For automation, we might need to ensure the trigger condition is met or use non-blocking if available in advanced Tcl.
# Given the "Breathing LED" runs continuously, an immediate trigger or forced trigger should work.

# Export data (if supported by simple Tcl, otherwise we rely on the session state)
# In CLI mode, viewing the data usually requires opening the STP in the GUI later, 
# or using export_data_log if configured.

puts "Acquisition complete. Please open $stp_file in Quartus GUI to view waveforms."

close_session -name $stp_file
