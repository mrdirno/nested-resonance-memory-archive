`timescale 1ns / 1ps

module gorkov_axi_wrapper #(
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 6  // Covering offsets 0x00 to 0x24
)(
    // System Signals
    input wire clk,
    input wire rst_n,

    // AXI4-Lite Slave Interface
    // Write Address Channel
    input wire [ADDR_WIDTH-1:0] s_axi_awaddr,
    input wire s_axi_awvalid,
    output reg s_axi_awready,

    // Write Data Channel
    input wire [DATA_WIDTH-1:0] s_axi_wdata,
    input wire [DATA_WIDTH/8-1:0] s_axi_wstrb,
    input wire s_axi_wvalid,
    output reg s_axi_wready,

    // Write Response Channel
    output reg [1:0] s_axi_bresp,
    output reg s_axi_bvalid,
    input wire s_axi_bready,

    // Read Address Channel
    input wire [ADDR_WIDTH-1:0] s_axi_araddr,
    input wire s_axi_arvalid,
    output reg s_axi_arready,

    // Read Data Channel
    output reg [DATA_WIDTH-1:0] s_axi_rdata,
    output reg [1:0] s_axi_rresp,
    output reg s_axi_rvalid,
    input wire s_axi_rready,

    // Internal Control Signals (To Physics Core)
    output reg start_core,
    output reg reset_core,
    output reg irq_enable,
    input wire core_busy,
    input wire core_done,
    input wire core_error,
    input wire [31:0] core_result, // Result from Core
    output reg [31:0] emitter_cnt,
    output reg [31:0] voxel_cnt,
    output reg [63:0] phase_addr,
    output reg [63:0] voxel_addr,
    output reg [63:0] result_addr,
    output reg phase_wen // Strobe when Phase L is written
);

    // Register Map Offsets (See NEURAL_LINK_SPEC.md)
    localparam ADDR_CTRL        = 6'h00;
    localparam ADDR_STATUS      = 6'h04;
    localparam ADDR_EMITTER_CNT = 6'h08;
    localparam ADDR_VOXEL_CNT   = 6'h0C;
    localparam ADDR_PHASE_L     = 6'h10;
    localparam ADDR_PHASE_H     = 6'h14;
    localparam ADDR_VOXEL_L     = 6'h18;
    localparam ADDR_VOXEL_H     = 6'h1C;
    localparam ADDR_RESULT_L    = 6'h20;
    localparam ADDR_RESULT_H    = 6'h24;

    // Internal Registers
    reg [DATA_WIDTH-1:0] reg_ctrl;
    // reg_status is constructed combinatorially from inputs
    reg [DATA_WIDTH-1:0] reg_emitter_cnt;
    reg [DATA_WIDTH-1:0] reg_voxel_cnt;
    reg [DATA_WIDTH-1:0] reg_phase_l;
    reg [DATA_WIDTH-1:0] reg_phase_h;
    reg [DATA_WIDTH-1:0] reg_voxel_l;
    reg [DATA_WIDTH-1:0] reg_voxel_h;
    reg [DATA_WIDTH-1:0] reg_result_l;
    reg [DATA_WIDTH-1:0] reg_result_h;
    
    reg sticky_done;

    // AXI State
    // Simplified Implementation: Assumes valid/ready handshake happens in one cycle if possible
    
    // Write Logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_awready <= 0;
            s_axi_wready <= 0;
            s_axi_bvalid <= 0;
            s_axi_bresp <= 0;
            
            reg_ctrl <= 0;
            reg_emitter_cnt <= 64; // Default
            reg_voxel_cnt <= 1024; // Default
            reg_phase_l <= 0;
            reg_phase_h <= 0;
            reg_voxel_l <= 0;
            reg_voxel_h <= 0;
            reg_result_l <= 0;
            reg_result_l <= 0;
            reg_result_h <= 0;
            phase_wen <= 0;
        end else begin
            // Handshake Logic
            if (!s_axi_awready && s_axi_awvalid && s_axi_wvalid) begin
                s_axi_awready <= 1;
                s_axi_wready <= 1;
                
                // Write Operation
                case (s_axi_awaddr)
                    ADDR_CTRL:        reg_ctrl <= s_axi_wdata;
                    ADDR_EMITTER_CNT: reg_emitter_cnt <= s_axi_wdata;
                    ADDR_VOXEL_CNT:   reg_voxel_cnt <= s_axi_wdata;
                    ADDR_PHASE_L:     begin
                                        reg_phase_l <= s_axi_wdata;
                                        phase_wen <= 1; // Strobe
                                      end
                    ADDR_PHASE_H:     reg_phase_h <= s_axi_wdata;
                    ADDR_VOXEL_L:     reg_voxel_l <= s_axi_wdata;
                    ADDR_VOXEL_H:     reg_voxel_h <= s_axi_wdata;
                    ADDR_RESULT_L:    reg_result_l <= s_axi_wdata;
                    ADDR_RESULT_H:    reg_result_h <= s_axi_wdata;
                    // Status is Read-Only
                endcase
            end else begin
                s_axi_awready <= 0;
                s_axi_wready <= 0;
                phase_wen <= 0; // Clear Strobe
            end

            // Response Logic
            if (s_axi_awready && s_axi_wready) begin
                s_axi_bvalid <= 1;
                s_axi_bresp <= 0; // OKAY
            end else if (s_axi_bready && s_axi_bvalid) begin
                s_axi_bvalid <= 0;
            end
            
            // Self-Clearing Control Bits (Optional, but good for Pulse generation)
            // If Start bit (0) is set, we might want to clear it after one cycle or let the core ack it.
            // For this simplified wrapper, we pass it through.
        end
    end

    // Read Logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_arready <= 0;
            s_axi_rvalid <= 0;
            s_axi_rresp <= 0;
            s_axi_rdata <= 0;
            sticky_done <= 0;
        end else begin
            // Sticky Done Logic
            if (start_core) sticky_done <= 0;
            else if (core_done) sticky_done <= 1;
            
            if (!s_axi_arready && s_axi_arvalid) begin
                s_axi_arready <= 1;
                
                // Read Operation
                case (s_axi_araddr)
                    ADDR_CTRL:        s_axi_rdata <= reg_ctrl;
                    ADDR_STATUS:      s_axi_rdata <= {28'b0, core_error, sticky_done, core_busy, 1'b0}; // Bit 2: Sticky Done
                    ADDR_EMITTER_CNT: s_axi_rdata <= reg_emitter_cnt;
                    ADDR_VOXEL_CNT:   s_axi_rdata <= reg_voxel_cnt;
                    ADDR_PHASE_L:     s_axi_rdata <= reg_phase_l;
                    ADDR_PHASE_H:     s_axi_rdata <= reg_phase_h;
                    ADDR_VOXEL_L:     s_axi_rdata <= reg_voxel_l;
                    ADDR_VOXEL_H:     s_axi_rdata <= reg_voxel_h;
                    ADDR_RESULT_L:    s_axi_rdata <= core_result; // Read from Core
                    ADDR_RESULT_H:    s_axi_rdata <= reg_result_h;
                    default:          s_axi_rdata <= 32'hDEADBEEF;
                endcase
            end else begin
                s_axi_arready <= 0;
            end

            if (s_axi_arready && !s_axi_rvalid) begin
                s_axi_rvalid <= 1;
                s_axi_rresp <= 0; // OKAY
            end else if (s_axi_rready && s_axi_rvalid) begin
                s_axi_rvalid <= 0;
            end
        end
    end

    // Output Mapping
    always @(*) begin
        start_core = reg_ctrl[0];
        reset_core = reg_ctrl[1];
        irq_enable = reg_ctrl[2];
        emitter_cnt = reg_emitter_cnt;
        voxel_cnt = reg_voxel_cnt;
        phase_addr = {reg_phase_h, reg_phase_l};
        voxel_addr = {reg_voxel_h, reg_voxel_l};
        result_addr = {reg_result_h, reg_result_l};
    end

endmodule
