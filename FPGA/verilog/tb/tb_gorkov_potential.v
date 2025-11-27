`timescale 1ns / 1ps

module tb_gorkov_potential;

    // Parameters
    parameter NUM_EMITTERS = 64;
    parameter DATA_WIDTH = 32;

    // Inputs
    reg clk;
    reg rst_n;
    reg [DATA_WIDTH-1:0] target_x;
    reg [DATA_WIDTH-1:0] target_y;
    reg [DATA_WIDTH-1:0] target_z;
    reg [NUM_EMITTERS*DATA_WIDTH-1:0] emitter_phases;

    // Outputs
    wire [DATA_WIDTH-1:0] potential_out;
    wire valid_out;

    // Instantiate the Device Under Test (DUT)
    gorkov_potential #(
        .NUM_EMITTERS(NUM_EMITTERS),
        .DATA_WIDTH(DATA_WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .target_x(target_x),
        .target_y(target_y),
        .target_z(target_z),
        .emitter_phases(emitter_phases),
        .potential_out(potential_out),
        .valid_out(valid_out)
    );

    // Clock Generation (100MHz -> 10ns period)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Test Sequence
    initial begin
        // Initialize Inputs
        rst_n = 0;
        target_x = 0;
        target_y = 0;
        target_z = 0;
        emitter_phases = 0;

        // Wait 100 ns for global reset to finish
        #100;
        
        // Release Reset
        rst_n = 1;
        #20;

        // Test Case 1: Basic Input
        $display("[TB] Test Case 1: Basic Input");
        target_x = 32'd100;
        target_y = 32'd200;
        target_z = 32'd300;
        // Set first phase to 50
        emitter_phases[31:0] = 32'd50; 
        
        #20;
        
        // Check Output
        // Based on stub logic: potential_out <= emitter_phases[DATA_WIDTH-1:0] + target_x;
        // Expected: 50 + 100 = 150
        if (potential_out == 150 && valid_out == 1) begin
            $display("[TB] PASS: Output %d matches expected 150", potential_out);
        end else begin
            $display("[TB] FAIL: Output %d expected 150", potential_out);
        end

        // Test Case 2: Change Input
        $display("[TB] Test Case 2: Change Input");
        target_x = 32'd1000;
        emitter_phases[31:0] = 32'd500;
        
        #20;
        
        // Expected: 1000 + 500 = 1500
        if (potential_out == 1500 && valid_out == 1) begin
            $display("[TB] PASS: Output %d matches expected 1500", potential_out);
        end else begin
            $display("[TB] FAIL: Output %d expected 1500", potential_out);
        end

        $display("[TB] Simulation Complete.");
        $finish;
    end

    // Waveform Dump (Optional)
    initial begin
        $dumpfile("gorkov_tb.vcd");
        $dumpvars(0, tb_gorkov_potential);
    end

endmodule
