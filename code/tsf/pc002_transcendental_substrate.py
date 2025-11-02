"""
PC002: Transcendental Substrate Hypothesis Validation Framework

Exploratory hypothesis testing whether transcendental numbers (π, e, φ) provide
a richer substrate for emergence compared to pseudo-random generators (PRNGs).

This PC is currently in DESIGN status - experimental validation data not yet available.
The validate() method will return design-phase results until comparative experiments
are executed.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

from typing import Any, Dict, List
import numpy as np
from pathlib import Path

from code.tsf.principle_card import (
    PrincipleCard,
    PCMetadata,
    ValidationResult,
    PCValidationError,
    InsufficientDataError
)


class PC002_Transcendental_Substrate(PrincipleCard):
    """
    PC002: Transcendental Substrate Hypothesis Validation Framework

    Tests whether π, e, φ substrate produces richer emergence than PRNG.
    Status: DESIGN (awaiting experimental validation data)
    """

    def __init__(self):
        """Initialize PC002 with metadata."""
        metadata = PCMetadata(
            pc_id="PC002",
            version="0.1.0",
            name="Transcendental Substrate Hypothesis",
            type="exploratory_hypothesis",
            domain="nested_resonance_memory",
            phase=2,
            status="design",  # Not yet validated - experimental data needed
            design_date="2025-11-01",
            validation_date=None,  # Pending validation
            dependencies=["PC001"],  # Builds on validated NRM framework
            successors=["PC003", "PC004"],  # Future principle cards
            author="Aldrin Payopay",
            repository="https://github.com/mrdirno/nested-resonance-memory-archive",
            additional_metadata={
                "gates_encoded": [
                    "Gate 2.1: Transcendental vs PRNG Comparison",
                    "Gate 2.2: Pattern Persistence Metrics",
                    "Gate 2.3: Memory Retention Analysis",
                    "Gate 2.4: Emergence Quality Assessment"
                ],
                "research_type": "exploratory",
                "blocking": False,
                "priority": "bonus_quest",
                "timeline": "Post-Paper 3 completion",
                "null_hypothesis": "Transcendental substrate produces equivalent results to cryptographic PRNG",
                "alternative_hypothesis": "Transcendental substrate produces richer, more stable emergence than PRNG"
            }
        )
        super().__init__(metadata)

    @property
    def principle_statement(self) -> str:
        """Core principle in natural language."""
        return (
            "The emergence of persistent, complex, and self-organizing structures within "
            "the Nested Resonance Memory (NRM) framework is contingent upon the unique, "
            "coherent, and infinitely non-repeating patterns inherent to transcendental "
            "numbers (π, e, φ). These numbers generate a structured multi-dimensional "
            "'forcefield' (analogous to Chladni plate vibrations) that enables agents "
            "to find stable resonant states where patterns persist across phase shifts. "
            "This structured substrate is hypothesized to be necessary for rich emergent "
            "complexity, in contrast to pseudo-random noise which would produce only "
            "transient, incoherent patterns."
        )

    def mathematical_formulation(self) -> Dict[str, str]:
        """Mathematical/computational representation."""
        return {
            # Transcendental substrate
            "transcendental_field": "Φ(t) = [π(t mod 2π), e^(t/τ), φ·Golden_Spiral(t)]",
            "phase_space": "S ∈ ℝ³ with structure from (π, e, φ)",

            # PRNG substrate (comparison)
            "prng_field": "Φ_rand(t) = [PRNG₁(t), PRNG₂(t), PRNG₃(t)]",
            "phase_space_random": "S_rand ∈ ℝ³ with pseudorandom structure",

            # Comparison metrics
            "pattern_lifetime": "L = cycles from formation to dissolution",
            "memory_retention": "R = (patterns_recalled / patterns_formed) × 100%",
            "cluster_stability": "CV = σ(lifetimes) / μ(lifetimes)",
            "structure_complexity": "C = {D_f, H(P), Φ_coherence}",

            # Statistical tests
            "effect_size": "d = (μ_trans - μ_prng) / σ_pooled",
            "significance": "p = Mann-Whitney-U-Test(L_trans, L_prng)",
            "validation_criterion": "d > 0.5 AND p < 0.01 for ≥2 metrics"
        }

    def validation_protocol(self) -> Dict[str, Any]:
        """Validation methodology and criteria."""
        return {
            "method": "Comparative experimental validation",
            "gates": {
                "gate_2.1": {
                    "name": "Transcendental vs PRNG Comparison",
                    "criterion": "Statistically significant difference in ≥2/4 metrics",
                    "achieved": "PENDING (experimental data not available)",
                    "status": "DESIGN"
                },
                "gate_2.2": {
                    "name": "Pattern Persistence Metrics",
                    "criterion": "≥20% higher pattern lifetime than PRNG",
                    "achieved": "PENDING (experimental data not available)",
                    "status": "DESIGN"
                },
                "gate_2.3": {
                    "name": "Memory Retention Analysis",
                    "criterion": "CV at least 30% lower than PRNG",
                    "achieved": "PENDING (experimental data not available)",
                    "status": "DESIGN"
                },
                "gate_2.4": {
                    "name": "Emergence Quality Assessment",
                    "criterion": "≥15% higher complexity metrics than PRNG",
                    "achieved": "PENDING (experimental data not available)",
                    "status": "DESIGN"
                }
            },
            "data_requirements": {
                "transcendental_baseline": "20-50 runs from C175 baseline (AVAILABLE)",
                "prng_control_group": "20-50 runs matching baseline conditions (NOT AVAILABLE)",
                "matching_criteria": [
                    "Same initial population (N=10)",
                    "Same simulation duration (T=1000 cycles)",
                    "Same birth/death rates",
                    "Same composition/decomposition thresholds",
                    "Same random seed mapping"
                ]
            },
            "statistical_tests": [
                "Mann-Whitney U test (pattern lifetimes)",
                "Independent t-test (memory retention)",
                "F-test (cluster stability variance)",
                "MANOVA (multivariate complexity)"
            ],
            "required_experiments": {
                "transcendental_vs_prng": "code/experiments/transcendental_vs_prng_comparison.py",
                "status": "NOT IMPLEMENTED",
                "timeline": "Post-Paper 3 completion"
            }
        }

    def validate(self, data: Any, tolerance: float = 0.10) -> ValidationResult:
        """
        Execute PC002 validation on provided comparative data.

        CURRENT STATUS: DESIGN PHASE
        This method checks if comparative experimental data exists.
        If not, returns design-phase validation result.

        Args:
            data: Dictionary with keys:
                  - transcendental_results: dict with metrics from π,e,φ substrate
                  - prng_results: dict with metrics from PRNG substrate
                  - metrics: list of metric names to compare
            tolerance: Not used for PC002 (uses effect size thresholds)

        Returns:
            ValidationResult with pass/fail and all gate metrics

        Raises:
            InsufficientDataError: If required data fields missing
            PCValidationError: If validation cannot be completed
        """
        from datetime import datetime

        # Check if comparative data is available
        if "prng_results" not in data or data["prng_results"] is None:
            # Design-phase validation: acknowledge data not available
            return ValidationResult(
                pc_id=self.metadata.pc_id,
                pc_version=self.metadata.version,
                passes=False,  # Cannot pass without data
                metrics={
                    "design_phase": 1.0,
                    "data_available": 0.0,
                    "gates_passing": 0.0
                },
                evidence={
                    "status": "DESIGN",
                    "message": "PC002 requires comparative experimental data (transcendental vs PRNG)",
                    "required_data": {
                        "transcendental_baseline": "20-50 runs from C175 (AVAILABLE)",
                        "prng_control_group": "20-50 runs matching baseline (NOT AVAILABLE)"
                    },
                    "next_steps": [
                        "Implement code/experiments/transcendental_vs_prng_comparison.py",
                        "Execute 20-50 PRNG control experiments",
                        "Collect pattern lifetime, memory retention, cluster stability, complexity metrics",
                        "Run statistical tests (Mann-Whitney U, t-test, F-test, MANOVA)",
                        "Re-run PC002.validate() with comparative results"
                    ]
                },
                timestamp=datetime.now().isoformat(),
                error_message="Comparative experimental data not available - PC002 in design phase"
            )

        # If we have comparative data, validate it
        try:
            trans_results = data["transcendental_results"]
            prng_results = data["prng_results"]
            metrics = data.get("metrics", ["pattern_lifetime", "memory_retention", "cluster_stability", "complexity"])

            # Validate required metrics
            required = ["pattern_lifetime", "memory_retention", "cluster_stability", "complexity"]
            missing = [m for m in required if m not in metrics]
            if missing:
                raise InsufficientDataError(
                    f"Missing required metrics for PC002 validation: {missing}"
                )

            # Track gate results
            gates_passing = 0
            evidence = {}

            # Gate 2.1: Pattern Lifetime Comparison
            if "pattern_lifetime" in metrics:
                trans_lifetime = trans_results["pattern_lifetime"]["mean"]
                prng_lifetime = prng_results["pattern_lifetime"]["mean"]

                # Effect size (Cohen's d)
                pooled_std = np.sqrt((trans_results["pattern_lifetime"]["std"]**2 +
                                    prng_results["pattern_lifetime"]["std"]**2) / 2)
                effect_size = (trans_lifetime - prng_lifetime) / pooled_std

                # Statistical significance (p-value from data)
                p_value = data.get("statistical_tests", {}).get("pattern_lifetime_p", 1.0)

                gate_21_pass = (effect_size > 0.5 and p_value < 0.01)
                if gate_21_pass:
                    gates_passing += 1

                evidence["gate_2.1"] = {
                    "transcendental_mean": trans_lifetime,
                    "prng_mean": prng_lifetime,
                    "effect_size": effect_size,
                    "p_value": p_value,
                    "threshold_effect": 0.5,
                    "threshold_p": 0.01,
                    "pass": gate_21_pass
                }

            # Gate 2.2: Memory Retention
            if "memory_retention" in metrics:
                trans_retention = trans_results["memory_retention"]
                prng_retention = prng_results["memory_retention"]

                retention_improvement = ((trans_retention - prng_retention) / prng_retention) * 100

                gate_22_pass = (retention_improvement >= 20.0)
                if gate_22_pass:
                    gates_passing += 1

                evidence["gate_2.2"] = {
                    "transcendental_retention": trans_retention,
                    "prng_retention": prng_retention,
                    "improvement_pct": retention_improvement,
                    "threshold_pct": 20.0,
                    "pass": gate_22_pass
                }

            # Gate 2.3: Cluster Stability (CV comparison)
            if "cluster_stability" in metrics:
                trans_cv = trans_results["cluster_stability"]
                prng_cv = prng_results["cluster_stability"]

                cv_reduction = ((prng_cv - trans_cv) / prng_cv) * 100

                gate_23_pass = (cv_reduction >= 30.0)
                if gate_23_pass:
                    gates_passing += 1

                evidence["gate_2.3"] = {
                    "transcendental_cv": trans_cv,
                    "prng_cv": prng_cv,
                    "reduction_pct": cv_reduction,
                    "threshold_pct": 30.0,
                    "pass": gate_23_pass
                }

            # Gate 2.4: Emergence Complexity
            if "complexity" in metrics:
                trans_complexity = trans_results["complexity"]
                prng_complexity = prng_results["complexity"]

                complexity_improvement = ((trans_complexity - prng_complexity) / prng_complexity) * 100

                gate_24_pass = (complexity_improvement >= 15.0)
                if gate_24_pass:
                    gates_passing += 1

                evidence["gate_2.4"] = {
                    "transcendental_complexity": trans_complexity,
                    "prng_complexity": prng_complexity,
                    "improvement_pct": complexity_improvement,
                    "threshold_pct": 15.0,
                    "pass": gate_24_pass
                }

            # Overall validation: ≥2 gates must pass
            all_pass = (gates_passing >= 2)

            # Aggregate validation result
            return ValidationResult(
                pc_id=self.metadata.pc_id,
                pc_version=self.metadata.version,
                passes=all_pass,
                metrics={
                    "gates_passing": float(gates_passing),
                    "gates_total": 4.0,
                    "validation_rate": float(gates_passing) / 4.0
                },
                evidence=evidence,
                timestamp=datetime.now().isoformat(),
                error_message=None if all_pass else f"Only {gates_passing}/4 gates passed (need ≥2)"
            )

        except Exception as e:
            raise PCValidationError(
                f"PC002 validation failed: {e}",
                context={"error": str(e), "data_keys": list(data.keys())}
            )

    def falsification_criteria(self) -> List[str]:
        """Conditions that would falsify this principle."""
        return [
            "PRNG substrate produces equal or longer pattern lifetimes than transcendental substrate",
            "PRNG substrate achieves equal or higher memory retention than transcendental substrate",
            "PRNG substrate exhibits equal or lower cluster lifetime variance than transcendental substrate",
            "PRNG substrate generates equal or higher emergent complexity than transcendental substrate",
            "Statistical tests show no significant difference (p > 0.05) between substrates",
            "Effect sizes are small (d < 0.5) across all metrics",
            "Results cannot be reproduced on independent hardware or implementations",
            "Transcendental substrate advantage disappears with sufficient PRNG quality"
        ]

    def applications(self) -> List[str]:
        """Practical applications of this principle."""
        return [
            "Substrate selection for emergence-based systems",
            "Understanding role of structure vs noise in self-organization",
            "Validating Bridge layer theoretical foundation",
            "Informing future NRM implementations",
            "Exploring mathematical constants in computational systems",
            "Testing Chladni forcefield analogy empirically",
            "Guiding research on transcendental computation",
            "Advancing understanding of emergence mechanisms"
        ]


# Factory function for easy instantiation

def load_pc002() -> PC002_Transcendental_Substrate:
    """
    Load PC002 instance.

    Returns:
        PC002_Transcendental_Substrate instance
    """
    return PC002_Transcendental_Substrate()


# Example usage and design-phase validation

if __name__ == "__main__":
    # Create PC002 instance
    pc002 = load_pc002()

    # Print PC metadata
    print(pc002)
    print()
    print("Principle Statement:")
    print(pc002.principle_statement)
    print()
    print(f"Status: {pc002.metadata.status}")
    print(f"Blocking: {pc002.metadata.additional_metadata['blocking']}")
    print(f"Priority: {pc002.metadata.additional_metadata['priority']}")
    print()

    # Design-phase validation (no comparative data)
    print("=" * 70)
    print("Design-Phase Validation (no comparative experimental data)")
    print("=" * 70)

    design_data = {
        "transcendental_results": {"available": True},
        "prng_results": None  # Not available
    }

    result = pc002.validate(design_data)

    print(f"\nStatus: {'PASS' if result.passes else 'DESIGN PHASE'}")
    print(f"Message: {result.error_message}")
    print(f"\nEvidence:")
    print(f"  - Status: {result.evidence['status']}")
    print(f"  - Message: {result.evidence['message']}")
    print(f"\nNext Steps:")
    for i, step in enumerate(result.evidence['next_steps'], 1):
        print(f"  {i}. {step}")
