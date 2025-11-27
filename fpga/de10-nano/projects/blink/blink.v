module blink (
    input wire CLOCK_50,
    output wire LED
);

reg [24:0] counter;
reg led_out;

always @(posedge CLOCK_50) begin
    if (counter == 25000000) begin // 0.5 second blink (50MHz / 2 = 25M cycles)
        led_out <= ~led_out;
        counter <= 0;
    end else begin
        counter <= counter + 1;
    end
end

assign LED = led_out;

endmodule