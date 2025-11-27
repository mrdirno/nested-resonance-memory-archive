# Vivado Synthesis Script for Helios Accelerator
# Target Board: PYNQ-Z2 (xc7z020clg400-1)
# Usage: vivado -mode batch -source synth.tcl

# 1. Settings
set project_name "helios_accelerator"
set part_name "xc7z020clg400-1"
set src_dir "../verilog/src"
set constr_dir "../constraints"
set output_dir "build"

# 2. Create Project
file mkdir $output_dir
create_project -force $project_name $output_dir -part $part_name

# 3. Add Sources
puts "Adding Design Sources..."
add_files [glob $src_dir/*.v]
add_files [glob $src_dir/*.mem]

# 4. Add Constraints
puts "Adding Constraints..."
add_files -fileset constrs_1 [glob $constr_dir/*.xdc]

# 5. Set Top Module
set_property top gorkov_accelerator [current_fileset]

# 6. Run Synthesis
puts "Launching Synthesis..."
launch_runs synth_1 -jobs 4
wait_on_run synth_1

# 7. Check Status
set synth_status [get_property STATUS [get_runs synth_1]]
puts "Synthesis Status: $synth_status"

if {$synth_status != "synth_design Complete!"} {
    puts "Error: Synthesis Failed"
    exit 1
}

# 8. Report Utilization
open_run synth_1 -name synth_1
report_utilization -file $output_dir/utilization.rpt

puts "Synthesis Complete. Project saved in $output_dir/$project_name"
exit 0