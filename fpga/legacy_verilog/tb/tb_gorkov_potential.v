`timescale 1ns / 1ps

module tb_gorkov_potential;

    parameter NUM_EMITTERS = 64;
    parameter WIDTH = 16;

    reg clk;
    reg rst_n;
    reg start;
    reg signed [WIDTH-1:0] target_x;
    reg signed [WIDTH-1:0] target_y;
    reg signed [WIDTH-1:0] target_z;
    reg [NUM_EMITTERS*WIDTH-1:0] emitter_phases;
    
    wire [31:0] potential_out;
    wire done;

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

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        // Setup
        rst_n = 0;
        start = 0;
        target_x = 0; target_y = 0; target_z = 0;
        emitter_phases = 0; // All phases 0

        #100 rst_n = 1;
        #20;

        // Test 1: Constructive Interference at Origin (0,0,0)
        // Emitter 0 is at (0,0). Dist = 0. Phase = 0.
        // LUT[0] = 0 (Sin), LUT[256] = 1 (Cos).
        // If all emitters were at (0,0), we'd get SumReal = 64, SumImag = 0.
        // Since they are spread out, we expect some value.
        
        $display("[TB] Test 1: Constructive Interference at (0,0,0)");
        start = 1;
        @(posedge clk);
        start = 0;

        wait(done);
        $display("[TB] Done. Potential: %d", potential_out);
        
        // Test 2: Moving Target away
        #20;
        target_x = 100; // Far away
        
        $display("[TB] Test 2: Target at (100,0,0)");
        start = 1;
        @(posedge clk);
        start = 0;
        
        wait(done);
        $display("[TB] Done. Potential: %d", potential_out);

        $finish;
    end

endmodule
