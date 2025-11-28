module nrm_system_wrapper(
    input wire clk,
    input wire rst_n,
    output wire [7:0] led,
    output wire resonance_detected,
    output wire heartbeat
);

    wire [31:0] pio_export;
    
    jtag_system u0 (
        .clk_clk(clk),
        .reset_reset_n(rst_n),
        .injection_external_connection_export(pio_export)
    );

    nrm_resonance u1 (
        .clk(clk),
        .rst_n(rst_n),
        .inject_data(pio_export[7:0]),
        .inject_en(pio_export[8]),
        .led(led),
        .resonance_detected(resonance_detected),
        .heartbeat(heartbeat)
    );

endmodule
