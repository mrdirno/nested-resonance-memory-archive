# setup_signaltap.tcl
# Automates the association of a SignalTap II file (.stp) with a Quartus Project

load_package flow
load_package project

set project_name "breathing_led"
set project_path "fpga/de10-nano/projects/breathing_led/"
set stp_file "breathing_led.stp"

# Open Project - Explicitly pointing to the .qpf
if {[file exists "$project_path$project_name.qpf"]} {
    project_open "$project_path$project_name"
} else {
    puts "Error: Project file $project_path$project_name.qpf not found."
    exit 1
}

# enable SignalTap
set_global_assignment -name ENABLE_SIGNALTAP ON
set_global_assignment -name USE_SIGNALTAP_FILE $stp_file
set_global_assignment -name SIGNALTAP_FILE $stp_file

# Commit assignments
export_assignments

puts "SignalTap file $stp_file associated with $project_name."
puts "Ready for recompilation."

project_close
