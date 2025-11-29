// =============================================================================
// NRM System Wrapper - JTAG Interface Only
// =============================================================================
// Description:
//   Top-level wrapper providing JTAG-based injection for NRM resonance testing.
//   HPS integration deferred - requires DE10-Nano GHRD as base.
//
// Target: DE10-Nano (Cyclone V 5CSEBA6U23I7)
// Author: DUALITY-ZERO-V2 Project
// License: GPL-3.0
// =============================================================================

module nrm_system_wrapper(
    // Clock and Reset
    input wire clk,
    input wire rst_n,

    // FPGA LED outputs
    output wire [7:0] led,
    output wire resonance_detected,
    output wire heartbeat,

    // Fuzz/Debug outputs (Arduino Header -> RP2040)
    output wire [31:0] fuzz_out
);

    // ==========================================================================
    // Internal Signals
    // ==========================================================================
    wire [31:0] jtag_pio_export;    // JTAG-based PIO output

    // Connect JTAG PIO to Fuzz Output for pin probing
    assign fuzz_out = jtag_pio_export;

    // ==========================================================================
    // JTAG-Based Injection (Primary interface)
    // ==========================================================================
    jtag_system jtag_inst (
        .clk_clk(clk),
        .reset_reset_n(rst_n),
        .injection_external_connection_export(jtag_pio_export)
    );

    // ==========================================================================
    // NRM Resonance Detector
    // ==========================================================================
    nrm_resonance nrm_inst (
        .clk(clk),
        .rst_n(rst_n),
        .inject_data(jtag_pio_export[7:0]),
        .inject_en(jtag_pio_export[8]),
        .led(led),
        .resonance_detected(resonance_detected),
        .heartbeat(heartbeat)
    );

endmodule
