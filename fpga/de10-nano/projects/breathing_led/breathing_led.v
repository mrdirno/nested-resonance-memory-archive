module breathing_led(
    input clk,
    output reg led
);

    reg [24:0] counter;
    reg [24:0] pwm_threshold;
    reg direction; // 0: increasing brightness, 1: decreasing

    always @(posedge clk) begin
        // PWM Counter
        counter <= counter + 1;

        // Slow update for breathing effect (every 2^14 cycles approx)
        if (counter[13:0] == 0) begin
            if (direction == 0) begin
                pwm_threshold <= pwm_threshold + 10;
                if (pwm_threshold >= 25'h1FFFFFF) direction <= 1;
            end else begin
                pwm_threshold <= pwm_threshold - 10;
                if (pwm_threshold <= 10) direction <= 0;
            end
        end

        // PWM Logic
        led <= (counter < pwm_threshold) ? 1'b1 : 1'b0;
    end

endmodule
