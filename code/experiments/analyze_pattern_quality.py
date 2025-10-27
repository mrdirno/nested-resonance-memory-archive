#!/usr/bin/env python3
"""
Pattern Quality Evolution Analysis - Cycle 43
Analyzes how pattern confidence evolves over time in memory system.

Tests Self-Giving prediction: Successful patterns persist with higher quality.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from integration.system_integrator import SystemIntegrator
from memory.pattern_evolution import PatternQualityAnalyzer

def analyze_pattern_quality_evolution(cycles: int = 50):
    """
    Run experiment to track pattern quality evolution.

    Measures:
    - Average pattern confidence over time
    - Pattern persistence rates
    - Quality distribution shifts
    """
    print("="*70)
    print("PATTERN QUALITY EVOLUTION ANALYSIS")
    print("="*70)
    print(f"Cycles: {cycles}")
    print()

    # Initialize system
    integrator = SystemIntegrator()

    # Track metrics
    quality_history = []
    high_quality_counts = []
    low_quality_counts = []

    print("Running cycles...")
    for cycle in range(1, cycles + 1):
        # Run hybrid cycle
        integrator.run_hybrid_cycle()

        # Analyze quality every 5 cycles
        if cycle % 5 == 0:
            patterns = integrator.memory.search_patterns()

            if patterns:
                # Calculate quality metrics
                confidences = [p.confidence for p in patterns]
                avg_confidence = sum(confidences) / len(confidences)

                # Count high vs low quality
                high_quality = sum(1 for c in confidences if c >= 0.7)
                low_quality = sum(1 for c in confidences if c < 0.5)

                quality_history.append(avg_confidence)
                high_quality_counts.append(high_quality)
                low_quality_counts.append(low_quality)

                if cycle % 10 == 0:
                    print(f"Cycle {cycle}: Avg confidence: {avg_confidence:.2%}, "
                          f"High quality: {high_quality}, Low quality: {low_quality}")

    print()
    print("="*70)
    print("ANALYSIS RESULTS")
    print("="*70)

    if len(quality_history) >= 2:
        # Calculate trend
        early_avg = sum(quality_history[:2]) / 2
        late_avg = sum(quality_history[-2:]) / 2
        improvement = late_avg - early_avg

        print(f"\nQuality Evolution:")
        print(f"  Early average (cycles 5-10): {early_avg:.2%}")
        print(f"  Late average (last 10 cycles): {late_avg:.2%}")
        print(f"  Improvement: {improvement:+.2%}")
        print(f"  Trend: {'IMPROVING' if improvement > 0 else 'DECLINING'}")

        print(f"\nHigh Quality Patterns:")
        print(f"  Early count: {high_quality_counts[0]}")
        print(f"  Late count: {high_quality_counts[-1]}")
        print(f"  Change: {high_quality_counts[-1] - high_quality_counts[0]:+d}")

        print(f"\nLow Quality Patterns:")
        print(f"  Early count: {low_quality_counts[0]}")
        print(f"  Late count: {low_quality_counts[-1]}")
        print(f"  Change: {low_quality_counts[-1] - low_quality_counts[0]:+d}")

        # Verdict
        print(f"\n{'='*70}")
        if improvement > 0.02:  # >2% improvement
            print("✅ SELF-GIVING VALIDATED: Pattern quality improves over time")
            print("   Successful patterns persist, unsuccessful fade")
        elif improvement < -0.02:
            print("❌ UNEXPECTED: Pattern quality declined")
        else:
            print("⚠️  NEUTRAL: No significant quality change")
        print("="*70)

        return {
            'early_avg': early_avg,
            'late_avg': late_avg,
            'improvement': improvement,
            'validated': improvement > 0.02
        }
    else:
        print("Insufficient data for analysis")
        return None

if __name__ == "__main__":
    result = analyze_pattern_quality_evolution(cycles=50)
