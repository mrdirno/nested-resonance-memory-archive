`timescale 1ns / 1ps

module tb_gorkov_potential;

    // Parameters
    parameter NUM_EMITTERS = 64;
    parameter WIDTH = 16;

    // Inputs
    reg clk;
    reg rst_n;
    reg start;
    reg signed [WIDTH-1:0] target_x;
    reg signed [WIDTH-1:0] target_y;
    reg signed [WIDTH-1:0] target_z;
    reg [NUM_EMITTERS*WIDTH-1:0] emitter_phases;

    // Outputs
    wire [31:0] potential_out;
    wire done;

    // Instantiate the Device Under Test (DUT)
    gorkov_potential #(
        .NUM_EMITTERS(NUM_EMITTERS),
        .WIDTH(WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .target_x(target_x),
        .target_y(target_y),
        .target_z(target_z),
        .emitter_phases(emitter_phases),
        .potential_out(potential_out),
        .done(done)
    );

    // Clock Generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Test Sequence
    initial begin
        // Initialize Inputs
        rst_n = 0;
        start = 0;
        target_x = 0;
        target_y = 0;
        target_z = 0;
        emitter_phases = 0;

        // Wait for reset
        #100;
        rst_n = 1;
        #20;

        // Test Case 1: Basic Accumulation
        $display("[TB] Test Case 1: Basic Accumulation");
        target_x = 16'd50;
        target_y = 16'd50;
        target_z = 16'd50;
        
        // Set all phases to 10
        // Verilog replication {64{16'd10}}
        emitter_phases = {NUM_EMITTERS{16'd10}};
        
        // Trigger Start
        start = 1;
        #10;
        start = 0;
        
        // Wait for Done
        wait(done);
        #10;
        
        $display("[TB] Calculation Complete.");
        $display("[TB] Potential Output: %d", potential_out);
        
        if (potential_out != 0) begin
            $display("[TB] PASS: Non-zero potential calculated.");
        end else begin
            $display("[TB] FAIL: Potential is zero.");
        end

        $finish;
    end

    // Waveform Dump
    initial begin
        $dumpfile("gorkov_tb.vcd");
        $dumpvars(0, tb_gorkov_potential);
    end

endmodule