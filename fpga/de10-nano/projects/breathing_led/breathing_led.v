module breathing_led (
    input wire CLOCK_50,
    output wire LED
);

reg [24:0] counter;
reg [24:0] pwm_threshold;
reg direction; // 0 = up, 1 = down

// PWM Update Frequency: 50MHz / 2^16 ~= 762Hz
always @(posedge CLOCK_50) begin
    counter <= counter + 1;
    
    // Update Threshold every 2^16 cycles for smooth transition
    if (counter[15:0] == 0) begin
        if (direction == 0) begin
            pwm_threshold <= pwm_threshold + 256;
            if (pwm_threshold >= 25'd33554432) direction <= 1; // Cap check logic simplified
        end else begin
            pwm_threshold <= pwm_threshold - 256;
            if (pwm_threshold <= 25'd256) direction <= 0;
        end
    end
end

// PWM Logic: Using upper bits for comparison
assign LED = (counter[24:0] < pwm_threshold);

endmodule