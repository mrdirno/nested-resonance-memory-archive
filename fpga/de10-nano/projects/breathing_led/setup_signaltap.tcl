# SignalTap II Setup Script for Breathing LED
# Usage: quartus_stp -t setup_signaltap.tcl

package require ::quartus::project
package require ::quartus::stp

set project_name "breathing_led"
set revision_name "breathing_led"

# Open project
project_open $project_name -revision $revision_name

# Create SignalTap File if it doesn't exist
if { ![file exists "breathing_led.stp"] } {
    puts "Creating new SignalTap file: breathing_led.stp"
    
    # Create new STP file
    # Note: Tcl API for creating STP from scratch is limited. 
    # We usually rely on the GUI or 'quartus_stp --create_signaltap_hdl_file' 
    # followed by adding nodes.
    # Here we will use a system command to generate a basic one if possible, 
    # or rely on the user to create it via GUI if CLI fails.
    
    # Alternative: Enable SignalTap in QSF and let it auto-generate
    set_global_assignment -name ENABLE_SIGNALTAP ON
    set_global_assignment -name USE_SIGNALTAP_FILE breathing_led.stp
    set_global_assignment -name SIGNALTAP_FILE breathing_led.stp
    
    # Define nodes to tap (Counter and Threshold)
    # Note: This usually requires post-fitting node names. 
    # We will use a wildcard for now and refine later.
}

puts "Enabling SignalTap in QSF..."
set_global_assignment -name ENABLE_SIGNALTAP ON
set_global_assignment -name USE_SIGNALTAP_FILE breathing_led.stp
set_global_assignment -name SIGNALTAP_FILE breathing_led.stp

# Commit changes
export_assignments

puts "SignalTap enabled. Please open Quartus GUI to configure specific nodes (counter, pwm_threshold) and triggers."
puts "Run 'quartus_stpw breathing_led.stp' to open the analyzer."

project_close
