module blink (
    input wire clk,
    output wire led
);

    reg [25:0] counter;

    always @(posedge clk) begin
        counter <= counter + 1;
    end

    assign led = counter[25];

endmodule
