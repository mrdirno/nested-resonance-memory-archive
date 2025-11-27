# SignalTap II Setup Script for Breathing LED (Fixed Path)
# Usage: quartus_stp -t setup_signaltap.tcl (Run from project dir)

package require ::quartus::project
package require ::quartus::stp

set project_name "breathing_led"
set revision_name "breathing_led"

# Open project
if {[catch {project_open $project_name -revision $revision_name} result]} {
    puts "Error opening project: $result"
    exit 1
}

puts "Enabling SignalTap in QSF..."
set_global_assignment -name ENABLE_SIGNALTAP ON
set_global_assignment -name USE_SIGNALTAP_FILE breathing_led.stp
set_global_assignment -name SIGNALTAP_FILE breathing_led.stp

# Commit changes
export_assignments

puts "SignalTap enabled in project settings."
project_close