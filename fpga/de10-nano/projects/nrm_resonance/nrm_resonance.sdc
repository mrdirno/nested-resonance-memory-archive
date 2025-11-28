# =============================================================================
# Timing Constraints - NRM Resonance Detector
# =============================================================================

# 50 MHz clock input
create_clock -name clk -period 20.000 [get_ports clk]

# Derive PLL clocks (if any added later)
derive_pll_clocks

# Derive clock uncertainty
derive_clock_uncertainty

# Set false paths for asynchronous inputs
set_false_path -from [get_ports rst_n]

# Output delay constraints (relaxed for LED outputs)
set_output_delay -clock clk -max 10 [get_ports led[*]]
set_output_delay -clock clk -min 0 [get_ports led[*]]
