# HELIOS Synthesis Script (Vivado)
# Usage: vivado -mode batch -source synth_helios.tcl

# 1. Settings
set_param general.maxThreads 8
set outputDir ./bitstreams
file mkdir $outputDir

# 2. Load Source
read_verilog ./verilog/src/gorkov_potential.v

# 3. Load Constraints
read_xdc ./constraints/helios_pins.xdc

# 4. Synthesis
synth_design -top gorkov_potential -part xc7z020clg400-1
write_checkpoint -force $outputDir/post_synth.dcp
report_timing_summary -file $outputDir/post_synth_timing_summary.rpt
report_utilization -file $outputDir/post_synth_util.rpt

# 5. Opt Design
opt_design
place_design
phys_opt_design
write_checkpoint -force $outputDir/post_place.dcp
report_utilization -file $outputDir/post_place_util.rpt
report_timing_summary -file $outputDir/post_place_timing_summary.rpt

# 6. Route Design
route_design
write_checkpoint -force $outputDir/post_route.dcp
report_route_status -file $outputDir/post_route_status.rpt
report_timing_summary -file $outputDir/post_route_timing_summary.rpt
report_power -file $outputDir/post_route_power.rpt
report_drc -file $outputDir/post_imp_drc.rpt
write_verilog -force $outputDir/helios_impl_netlist.v -mode timesim -sdf_anno true

# 7. Bitstream
write_bitstream -force $outputDir/helios.bit

exit
