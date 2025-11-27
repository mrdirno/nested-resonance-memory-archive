`timescale 1ns / 1ps

module tb_accelerator;

    // Parameters
    parameter DATA_WIDTH = 32;
    parameter ADDR_WIDTH = 6;
    parameter NUM_EMITTERS = 64;
    parameter PHASE_WIDTH = 16;

    // Signals
    reg clk;
    reg rst_n;
    reg [ADDR_WIDTH-1:0] s_axi_awaddr;
    reg s_axi_awvalid;
    wire s_axi_awready;
    reg [DATA_WIDTH-1:0] s_axi_wdata;
    reg [DATA_WIDTH/8-1:0] s_axi_wstrb;
    reg s_axi_wvalid;
    wire s_axi_wready;
    wire [1:0] s_axi_bresp;
    wire s_axi_bvalid;
    reg s_axi_bready;
    reg [ADDR_WIDTH-1:0] s_axi_araddr;
    reg s_axi_arvalid;
    wire s_axi_arready;
    wire [DATA_WIDTH-1:0] s_axi_rdata;
    wire [1:0] s_axi_rresp;
    wire s_axi_rvalid;
    reg s_axi_rready;

    // DUT
    gorkov_accelerator #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH),
        .NUM_EMITTERS(NUM_EMITTERS),
        .PHASE_WIDTH(PHASE_WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .s_axi_awaddr(s_axi_awaddr),
        .s_axi_awvalid(s_axi_awvalid),
        .s_axi_awready(s_axi_awready),
        .s_axi_wdata(s_axi_wdata),
        .s_axi_wstrb(s_axi_wstrb),
        .s_axi_wvalid(s_axi_wvalid),
        .s_axi_wready(s_axi_wready),
        .s_axi_bresp(s_axi_bresp),
        .s_axi_bvalid(s_axi_bvalid),
        .s_axi_bready(s_axi_bready),
        .s_axi_araddr(s_axi_araddr),
        .s_axi_arvalid(s_axi_arvalid),
        .s_axi_arready(s_axi_arready),
        .s_axi_rdata(s_axi_rdata),
        .s_axi_rresp(s_axi_rresp),
        .s_axi_rvalid(s_axi_rvalid),
        .s_axi_rready(s_axi_rready)
    );

    // Clock Generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Tasks
    task axi_write;
        input [ADDR_WIDTH-1:0] addr;
        input [DATA_WIDTH-1:0] data;
        begin
            @(posedge clk);
            s_axi_awaddr = addr;
            s_axi_awvalid = 1;
            s_axi_wdata = data;
            s_axi_wvalid = 1;
            s_axi_bready = 1;
            
            wait(s_axi_awready && s_axi_wready);
            @(posedge clk);
            s_axi_awvalid = 0;
            s_axi_wvalid = 0;
            
            wait(s_axi_bvalid);
            @(posedge clk);
            s_axi_bready = 0;
        end
    endtask

    task axi_read;
        input [ADDR_WIDTH-1:0] addr;
        output [DATA_WIDTH-1:0] data;
        begin
            @(posedge clk);
            s_axi_araddr = addr;
            s_axi_arvalid = 1;
            s_axi_rready = 1;
            
            wait(s_axi_arready);
            @(posedge clk);
            s_axi_arvalid = 0;
            
            wait(s_axi_rvalid);
            data = s_axi_rdata;
            @(posedge clk);
            s_axi_rready = 0;
        end
    endtask

    // Test Sequence
    reg [31:0] read_val;
    integer i;
    
    initial begin
        // Initialize
        rst_n = 0;
        s_axi_awvalid = 0;
        s_axi_wvalid = 0;
        s_axi_arvalid = 0;
        s_axi_bready = 0;
        s_axi_rready = 0;
        
        #100;
        rst_n = 1;
        #100;
        
        $display("[TB] Starting Accelerator Verification...");
        
        // 1. Load Phase Memory
        // We will load 0 phase for all emitters
        // Protocol: Write Index to 0x14, Data to 0x10
        $display("[TB] Loading Phases...");
        for (i=0; i<NUM_EMITTERS; i=i+1) begin
            axi_write(6'h14, i); // Index
            axi_write(6'h10, 0); // Phase = 0
        end
        
        // 2. Set Target Voxel
        // Target = (0,0,0) -> Voxel L = 0, Voxel H = 0
        $display("[TB] Setting Target Voxel (0,0,0)...");
        axi_write(6'h18, 0); // Voxel L
        axi_write(6'h1C, 0); // Voxel H
        
        // 3. Start Core
        // Pulse Start: Write 1 then 0
        $display("[TB] Starting Core...");
        axi_write(6'h00, 1);
        axi_write(6'h00, 0); // Clear start to prevent restart
        
        // 4. Poll for Done
        // Read Status (0x04) until Bit 2 (Done) is set
        // Status Map: {..., Error, Done, Busy, 0}
        // Bit 2 = Done
        read_val = 0;
        while ((read_val & 4) == 0) begin
            axi_read(6'h04, read_val);
            #10;
        end
        $display("[TB] Core Done! Status: %h", read_val);
        
        // 5. Read Result
        // Read Result L (0x20)
        axi_read(6'h20, read_val);
        $display("[TB] Result: %d", read_val);
        
        if (read_val > 0) 
            $display("[TB] PASS: Non-zero potential calculated.");
        else
            $display("[TB] FAIL: Potential is zero (unexpected for 64 emitters).");
            
        $finish;
    end
    
    // Dump Waves
    initial begin
        $dumpfile("accelerator.vcd");
        $dumpvars(0, tb_accelerator);
    end

endmodule
