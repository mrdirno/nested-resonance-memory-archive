#!/bin/bash
# HELIOS FPGA Simulation Script
# Runs Icarus Verilog on the Gorkov Potential Core.

mkdir -p FPGA/sim_build

echo "Compiling Verilog..."
iverilog -o FPGA/sim_build/gorkov_sim \
    -I FPGA/verilog/src \
    FPGA/verilog/src/gorkov_potential.v \
    FPGA/verilog/tb/tb_gorkov_potential.v

if [ $? -eq 0 ]; then
    echo "Compilation Successful."
    echo "Running Simulation..."
    vvp FPGA/sim_build/gorkov_sim
else
    echo "Compilation Failed."
    exit 1
fi
