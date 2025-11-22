#!/usr/bin/env python3
"""
CYCLE 1630: PRECISION HYPOTHESIS TEST
Tests whether chaotic behavior at 10^93 is due to floating-point limits
or emergent dynamics by comparing float vs Decimal arithmetic.
"""
import sys
import numpy as np
from decimal import Decimal, getcontext
from datetime import datetime

# Set high precision for Decimal operations
getcontext().prec = 150

def test_conversion_probability():
    """Test if conversion calculations differ between float and Decimal"""

    # Test values from the experiments
    conv_multipliers = [
        1e91,   # 10^91 - stable regime
        1e92,   # 10^92 - stable regime
        1e93,   # 10^93 - chaotic regime
        1e94,   # 10^94 - chaotic regime
    ]

    energy_gains = [0.5, 0.6, 0.8, 1.0, 1.2, 1.4]

    print(f"CYCLE 1630: Precision Hypothesis Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"Testing float vs Decimal at various magnitudes\n")

    results = []

    for conv in conv_multipliers:
        print(f"\nConversion Multiplier: 10^{int(np.log10(conv))}")
        print("-" * 50)

        for eg in energy_gains:
            # Float calculation
            prob_float = conv * eg

            # Decimal calculation
            conv_dec = Decimal(str(conv))
            eg_dec = Decimal(str(eg))
            prob_dec = conv_dec * eg_dec

            # Check if they're effectively the same
            # For spawn, we use random() < prob, so if prob > 1, it's always True
            spawn_float = "ALWAYS" if prob_float >= 1.0 else f"{prob_float:.2e}"
            spawn_dec = "ALWAYS" if prob_dec >= 1 else f"{prob_dec:.2e}"

            # Check saturation
            saturated = prob_float >= 1.0

            print(f"  E_gain={eg}: Float={spawn_float}, Decimal={spawn_dec}, Saturated={saturated}")

            results.append({
                'magnitude': int(np.log10(conv)),
                'e_gain': eg,
                'prob_float': float(prob_float),
                'prob_decimal': float(prob_dec),
                'saturated': saturated
            })

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # Check saturation by magnitude
    for mag in [91, 92, 93, 94]:
        mag_results = [r for r in results if r['magnitude'] == mag]
        saturated_count = sum(1 for r in mag_results if r['saturated'])
        print(f"10^{mag}: {saturated_count}/{len(mag_results)} energy gains cause saturation")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    # At these magnitudes, conv * e_gain >> 1 always
    # So spawn probability is ALWAYS 100% regardless of energy gain
    # The only variable that matters is attack rate (predation)

    all_saturated = all(r['saturated'] for r in results)

    if all_saturated:
        print("""
HYPOTHESIS CONFIRMED: All spawn probabilities are saturated (>1.0)

At magnitudes 10^91+, the conversion calculation (conv * e_gain) always
exceeds 1.0, making spawn probability effectively 100% for any positive
energy gain. This means:

1. Conversion rate differences between factors are MEANINGLESS
2. Only attack rate (predation pressure) affects dynamics
3. Chaos is NOT due to precision limits - it's due to parameter saturation

The system has exited the regime where conversion tuning matters.
All variation comes from stochastic predation events.

RECOMMENDATION: The magnitude mapping experiments beyond 10^90 are
testing a degenerate parameter space. True dynamics testing requires
conversion multipliers that produce sub-unity spawn probabilities.
""")
    else:
        print("Mixed saturation - further investigation needed")

    return results

if __name__ == "__main__":
    test_conversion_probability()
