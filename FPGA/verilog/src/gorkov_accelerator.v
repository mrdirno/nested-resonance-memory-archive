`timescale 1ns / 1ps

module gorkov_accelerator #(
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 6,
    parameter NUM_EMITTERS = 64,
    parameter PHASE_WIDTH = 16
)(
    // System Signals
    input wire clk,
    input wire rst_n,

    // AXI4-Lite Slave Interface
    input wire [ADDR_WIDTH-1:0] s_axi_awaddr,
    input wire s_axi_awvalid,
    output wire s_axi_awready,
    input wire [DATA_WIDTH-1:0] s_axi_wdata,
    input wire [DATA_WIDTH/8-1:0] s_axi_wstrb,
    input wire s_axi_wvalid,
    output wire s_axi_wready,
    output wire [1:0] s_axi_bresp,
    output wire s_axi_bvalid,
    input wire s_axi_bready,
    input wire [ADDR_WIDTH-1:0] s_axi_araddr,
    input wire s_axi_arvalid,
    output wire s_axi_arready,
    output wire [DATA_WIDTH-1:0] s_axi_rdata,
    output wire [1:0] s_axi_rresp,
    output wire s_axi_rvalid,
    input wire s_axi_rready
);

    // Internal Signals
    wire start_core;
    wire reset_core; // Not used by Core yet, but good to have
    wire irq_enable;
    wire [31:0] emitter_cnt; // Not used by Core (fixed 64)
    wire [31:0] voxel_cnt;   // Not used by Core (single point)
    wire [63:0] phase_addr;  // {reg_phase_h, reg_phase_l}
    wire [63:0] voxel_addr;  // {reg_voxel_h, reg_voxel_l}
    wire [63:0] result_addr; // {reg_result_h, reg_result_l}
    wire phase_wen;
    
    wire core_done;
    wire [31:0] potential_out;
    
    // Phase Memory (64 x 16-bit)
    // Mapped to flat vector for Core
    reg [PHASE_WIDTH-1:0] phase_mem [0:NUM_EMITTERS-1];
    
    // Flattening Logic
    wire [NUM_EMITTERS*PHASE_WIDTH-1:0] flat_phases;
    genvar i;
    generate
        for (i=0; i<NUM_EMITTERS; i=i+1) begin : gen_flat
            assign flat_phases[i*PHASE_WIDTH +: PHASE_WIDTH] = phase_mem[i];
        end
    endgenerate

    // Phase Write Logic
    // Protocol: 
    // reg_phase_h (Upper 32 of phase_addr) = Index (0-63)
    // reg_phase_l (Lower 32 of phase_addr) = Data (16 bits)
    always @(posedge clk) begin
        if (phase_wen) begin
            // Safety mask index
            phase_mem[phase_addr[32+:6]] <= phase_addr[15:0]; 
        end
    end

    // Core Instantiation
    gorkov_potential #(
        .NUM_EMITTERS(NUM_EMITTERS),
        .WIDTH(PHASE_WIDTH)
    ) u_core (
        .clk(clk),
        .rst_n(rst_n), // & !reset_core ?
        .start(start_core),
        .target_x(voxel_addr[15:0]),   // reg_voxel_l[15:0]
        .target_y(voxel_addr[31:16]),  // reg_voxel_l[31:16]
        .target_z(voxel_addr[47:32]),  // reg_voxel_h[15:0]
        .emitter_phases(flat_phases),
        .potential_out(potential_out),
        .done(core_done)
    );

    // Wrapper Instantiation
    gorkov_axi_wrapper #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) u_wrapper (
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
        
        // Internal
        .start_core(start_core),
        .reset_core(reset_core),
        .irq_enable(irq_enable),
        .core_busy(!core_done && start_core), // Rough busy approximation
        .core_done(core_done),
        .core_error(1'b0),
        .core_result(potential_out), // Connect Result
        .emitter_cnt(emitter_cnt),
        .voxel_cnt(voxel_cnt),
        .phase_addr(phase_addr),
        .voxel_addr(voxel_addr),
        .result_addr(result_addr), // Not used as input, but wrapper drives it? No, wrapper drives OUTPUT result_addr?
                                   // Wait, wrapper OUTPUTS result_addr (register value).
                                   // But we need to FEED result back to wrapper for reading?
                                   // The wrapper has `reg_result_l` which is writable via AXI.
                                   // BUT `s_axi_rdata` reads from `reg_result_l`.
                                   // If we want the Core to update `reg_result_l`, the wrapper needs an INPUT port for result.
                                   // CURRENTLY: `gorkov_axi_wrapper` does NOT have an input for result data from core.
                                   // It only has `reg_result_l` which is writable by AXI master.
                                   // This is a problem. The Core result needs to be readable by AXI.
        .phase_wen(phase_wen)
    );

endmodule
