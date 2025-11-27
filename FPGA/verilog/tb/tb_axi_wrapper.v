`timescale 1ns / 1ps

module tb_axi_wrapper;

    // Parameters
    parameter DATA_WIDTH = 32;
    parameter ADDR_WIDTH = 6;

    // Signals
    reg clk;
    reg rst_n;

    // AXI Write
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

    // AXI Read
    reg [ADDR_WIDTH-1:0] s_axi_araddr;
    reg s_axi_arvalid;
    wire s_axi_arready;
    wire [DATA_WIDTH-1:0] s_axi_rdata;
    wire [1:0] s_axi_rresp;
    wire s_axi_rvalid;
    reg s_axi_rready;

    // Core Interface (Mock)
    wire start_core;
    wire reset_core;
    wire irq_enable;
    reg core_busy;
    reg core_done;
    reg core_error;
    wire [31:0] emitter_cnt;
    wire [31:0] voxel_cnt;
    wire [63:0] phase_addr;
    wire [63:0] voxel_addr;
    wire [63:0] result_addr;

    // Instantiate DUT
    gorkov_axi_wrapper #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH)
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
        .s_axi_rready(s_axi_rready),
        .start_core(start_core),
        .reset_core(reset_core),
        .irq_enable(irq_enable),
        .core_busy(core_busy),
        .core_done(core_done),
        .core_error(core_error),
        .emitter_cnt(emitter_cnt),
        .voxel_cnt(voxel_cnt),
        .phase_addr(phase_addr),
        .voxel_addr(voxel_addr),
        .result_addr(result_addr)
    );

    // Clock
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Task: Write Register
    task axi_write;
        input [ADDR_WIDTH-1:0] addr;
        input [DATA_WIDTH-1:0] data;
        begin
            @(posedge clk);
            s_axi_awaddr = addr;
            s_axi_awvalid = 1;
            s_axi_wdata = data;
            s_axi_wvalid = 1;
            s_axi_wstrb = 4'hF;
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

    // Task: Read Register
    task axi_read;
        input [ADDR_WIDTH-1:0] addr;
        input [DATA_WIDTH-1:0] expected;
        begin
            @(posedge clk);
            s_axi_araddr = addr;
            s_axi_arvalid = 1;
            s_axi_rready = 1;

            wait(s_axi_arready);
            @(posedge clk);
            s_axi_arvalid = 0;

            wait(s_axi_rvalid);
            if (s_axi_rdata !== expected) begin
                $display("[TB] FAIL: Read Addr %h, Expected %h, Got %h", addr, expected, s_axi_rdata);
            end else begin
                $display("[TB] PASS: Read Addr %h == %h", addr, s_axi_rdata);
            end
            @(posedge clk);
            s_axi_rready = 0;
        end
    endtask

    // Test Sequence
    initial begin
        // Init
        rst_n = 0;
        s_axi_awaddr = 0; s_axi_awvalid = 0;
        s_axi_wdata = 0; s_axi_wvalid = 0; s_axi_wstrb = 0;
        s_axi_bready = 0;
        s_axi_araddr = 0; s_axi_arvalid = 0;
        s_axi_rready = 0;
        core_busy = 0; core_done = 0; core_error = 0;

        #100;
        rst_n = 1;
        #20;

        $display("[TB] Test 1: Write/Read Emitter Count (0x08)");
        axi_write(6'h08, 32'd128);
        axi_read(6'h08, 32'd128);

        $display("[TB] Test 2: Write/Read Phase Addr L (0x10)");
        axi_write(6'h10, 32'hDEADBEEF);
        axi_read(6'h10, 32'hDEADBEEF);

        $display("[TB] Test 3: Check Status Reg (0x04) - Mock Core");
        core_busy = 1;
        // Status bit 1 is Busy. Logic: {error, done, busy, idle} -> {0,0,1,0} -> 0x2 (Shifted? No, layout is bits)
        // Layout in wrapper: {28'b0, core_error, core_done, core_busy, 1'b0}
        // So Busy is Bit 1.
        // Value = 0...0010 = 0x02.
        axi_read(6'h04, 32'h00000002);

        $display("[TB] Test 4: Start Pulse (0x00)");
        axi_write(6'h00, 32'h00000001); // Set Start Bit
        #10;
        if (start_core == 1) $display("[TB] PASS: Start Core signal asserted.");
        else $display("[TB] FAIL: Start Core signal NOT asserted.");

        $display("[TB] Simulation Complete.");
        $finish;
    end

endmodule
