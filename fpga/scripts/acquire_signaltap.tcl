load_package stp
load_package project

set project_name "breathing_led"
set project_path "fpga/de10-nano/projects/breathing_led/"
set stp_file "breathing_led.stp"
set abs_path "/media/helios/DUALITY-GUARDIAN/DUALITY-ZERO-V2/"

# Open Project
if {[file exists "$abs_path$project_path$project_name.qpf"]} {
    project_open "$abs_path$project_path$project_name"
} else {
    puts "Error: Project file $abs_path$project_path$project_name.qpf not found."
    exit 1
}

# Open the STP file
open_session -name "$abs_path$project_path$stp_file"

# Start acquisition
puts "Starting SignalTap acquisition..."
run_session -name "$abs_path$project_path$stp_file" -device_name "@2: 5CSEBA6(.|ES)/5CSEMA6/.. (0x02D020DD)" -hardware_name {DE-SoC [1-9]}

puts "Acquisition complete."

close_session -name "$abs_path$project_path$stp_file"
project_close