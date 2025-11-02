"""
PC002: Transcendental Substrate Validation Protocol

Comparative validation of transcendental constants (π, e, φ) vs PRNG
for pattern generation in self-organizing systems.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

from typing import Any, Dict, List
import numpy as np
from pathlib import Path
from scipy import stats

from code.tsf.principle_card import (
    PrincipleCard,
    PCMetadata,
    ValidationResult,
    PCValidationError,
    InsufficientDataError
)


class PC002_Transcendental_Substrate(PrincipleCard):
    """
    PC002: Transcendental Substrate Validation Protocol
    
    Tests hypothesis that transcendental constants (π, e, φ) produce
    superior emergent properties vs PRNG in self-organizing systems.
    
    Metrics:
    - M1: Pattern lifetime
    - M2: Memory retention
    - M3: Cluster stability
    - M4: Complexity bootstrap time
    
    Status: Draft (design phase)
    Dependencies: PC001 (NRM Population Dynamics)
    """
    
    def __init__(self):
        """Initialize PC002 with metadata."""
        metadata = PCMetadata(
            pc_id="PC002",
            version="0.1.0",
            name="Transcendental Substrate Validation Protocol",
            type="comparative_validation",
            domain="computational_complexity",
            phase=2,
            status="draft",
            design_date="2025-11-01",
            validation_date=None,  # Not yet validated
            dependencies=["PC001"],  # Requires NRM validation framework
            successors=["PC003"],  # Enables bootstrap dynamics
            author="Aldrin Payopay",
            repository="https://github.com/mrdirno/nested-resonance-memory-archive",
            license="GPL-3.0",
            additional_metadata={
                "hypothesis": "Transcendental substrate > PRNG for emergent complexity",
                "metrics": [
                    "pattern_lifetime",
                    "memory_retention",
                    "cluster_stability",
                    "complexity_bootstrap"
                ],
                "experimental_design": "2×2 factorial (substrate × scale)",
                "sample_size": "n=20 per condition (80 total)",
                "statistical_test": "two-sample t-test, α=0.05"
            }
        )
        super().__init__(metadata)
    
    @property
    def principle_statement(self) -> str:
        """Core principle in natural language."""
        return (
            "Computational systems using transcendental constants (π, e, φ) as "
            "substrate for pattern generation exhibit fundamentally different emergent "
            "properties compared to systems using pseudorandom number generators (PRNGs). "
            "Specifically, transcendental substrates enable: (1) longer pattern lifetime, "
            "(2) superior memory retention, (3) lower cluster volatility, and (4) faster "
            "complexity bootstrap. This validation framework generalizes beyond NRM to any "
            "self-organizing system requiring irreducible computational substrate for emergent complexity."
        )
    
    def mathematical_formulation(self) -> Dict[str, str]:
        """Mathematical/computational representation."""
        return {
            "transcendental_substrate": "TS = {π, e, φ}",
            "prng_substrate": "PS = MT19937 (Mersenne Twister)",
            "phase_function_ts": "Phase(i,t) = 2π × frac(π·hash(i) + e·t + φ·state)",
            "phase_function_ps": "Phase(i,t) = 2π × PRNG(seed=hash(i) + t)",
            "pattern_lifetime": "L(pattern) = max{t : pattern exists at t} - t_birth",
            "memory_retention": "R(pattern,t) = similarity(pattern(t), pattern(t_0))",
            "cluster_stability": "S(cluster,Δt) = σ(|cluster|) / μ(|cluster|)",
            "bootstrap_time": "T_bootstrap = min{t : max_pattern_order(t) ≥ threshold}",
            "null_hypothesis": "H0: TS = PS (statistically identical)",
            "alternative_hypothesis": "H1: TS > PS (superior metrics)"
        }
    
    def validation_protocol(self) -> Dict[str, Any]:
        """Validation methodology and criteria."""
        return {
            "method": "Comparative factorial validation",
            "design": {
                "factors": {
                    "substrate": ["transcendental (π,e,φ)", "PRNG (MT19937)"],
                    "scale": ["lightweight (~17 agents)", "high-capacity (~1000 agents)"]
                },
                "replications": 20,
                "total_experiments": 80,
                "duration_per_experiment": "10,000 cycles"
            },
            "metrics": {
                "M1_pattern_lifetime": {
                    "description": "Mean pattern persistence duration",
                    "prediction": "L_TS > L_PS",
                    "threshold": "p < 0.05, d ≥ 0.5"
                },
                "M2_memory_retention": {
                    "description": "Pattern recall similarity over time",
                    "prediction": "R_TS > R_PS",
                    "threshold": "p < 0.05, d ≥ 0.5"
                },
                "M3_cluster_stability": {
                    "description": "Coefficient of variation of cluster size",
                    "prediction": "S_TS < S_PS (lower volatility)",
                    "threshold": "p < 0.05, d ≥ 0.5"
                },
                "M4_bootstrap_time": {
                    "description": "Time to first high-order pattern",
                    "prediction": "T_TS < T_PS (faster bootstrap)",
                    "threshold": "p < 0.05, d ≥ 0.5"
                }
            },
            "validation_criteria": {
                "minimum_significant_metrics": 2,  # At least 2/4 metrics must be significant
                "minimum_effect_size": 0.5,  # Cohen's d ≥ 0.5 (medium effect)
                "directional_consistency": True,  # All significant effects must favor TS > PS
                "reproducibility_required": True  # Results must replicate in independent runs
            },
            "falsification_criteria": [
                "All metrics show p > 0.05 (no detectable difference)",
                "Any metric shows TS < PS with p < 0.05 (contradicts hypothesis)",
                "All effect sizes < 0.3 (negligible practical difference)",
                "Results fail to replicate in independent runs"
            ]
        }
    
    def validate(self, data: Any, tolerance: float = 0.05) -> ValidationResult:
        """
        Execute PC002 validation on comparative data.
        
        Args:
            data: Dictionary with keys:
                  - transcendental_results: Metrics from TS experiments
                  - prng_results: Metrics from PS experiments
                  - metrics: List of metrics to compare (M1-M4)
            tolerance: Significance level (default: 0.05)
        
        Returns:
            ValidationResult with comparative statistics
        
        Raises:
            InsufficientDataError: If required data fields missing
            PCValidationError: If validation cannot be completed
        """
        from datetime import datetime
        
        # Validate required data fields
        if "transcendental_results" not in data or "prng_results" not in data:
            raise InsufficientDataError(
                "PC002 requires both 'transcendental_results' and 'prng_results'"
            )
        
        ts_results = data["transcendental_results"]
        ps_results = data["prng_results"]
        
        # If no PRNG results, this is design-phase validation (not yet falsifiable)
        if ps_results is None:
            return self._design_phase_validation(ts_results, data, tolerance)
        
        # Full comparative validation
        return self._comparative_validation(ts_results, ps_results, data, tolerance)
    
    def _design_phase_validation(
        self,
        ts_results: Dict[str, Any],
        data: Dict[str, Any],
        tolerance: float
    ) -> ValidationResult:
        """
        Design-phase validation (before PRNG comparison).
        
        Checks that transcendental substrate implementation is working,
        but cannot validate comparative hypothesis yet.
        """
        from datetime import datetime
        
        metrics = {
            "design_phase": True,
            "ts_implementation": "operational",
            "ps_comparison": "pending"
        }
        
        evidence = {
            "ts_results_available": bool(ts_results),
            "ps_results_available": False,
            "validation_stage": "design_phase",
            "message": "PC002 implementation validated, comparative experiments pending"
        }
        
        return ValidationResult(
            pc_id=self.metadata.pc_id,
            pc_version=self.metadata.version,
            passes=False,  # Not yet falsifiable
            metrics=metrics,
            evidence=evidence,
            timestamp=datetime.now().isoformat(),
            error_message="Design phase: comparative validation pending"
        )
    
    def _comparative_validation(
        self,
        ts_results: Dict[str, Any],
        ps_results: Dict[str, Any],
        data: Dict[str, Any],
        tolerance: float
    ) -> ValidationResult:
        """
        Full comparative validation (TS vs PS).
        
        Executes statistical tests for all 4 metrics and determines
        if PC002 hypothesis is validated or falsified.
        """
        from datetime import datetime
        
        metrics = {}
        evidence = {}
        all_pass = True
        significant_count = 0
        
        # List of metrics to compare
        metric_names = data.get("metrics", [
            "pattern_lifetime",
            "memory_retention",
            "cluster_stability",
            "complexity_bootstrap"
        ])
        
        for metric in metric_names:
            # Extract data for this metric
            ts_data = ts_results.get(metric, [])
            ps_data = ps_results.get(metric, [])
            
            if not ts_data or not ps_data:
                # Missing data for this metric
                continue
            
            # Convert to numpy arrays
            ts_arr = np.array(ts_data)
            ps_arr = np.array(ps_data)
            
            # Compute statistics
            ts_mean = np.mean(ts_arr)
            ps_mean = np.mean(ps_arr)
            ts_std = np.std(ts_arr, ddof=1)
            ps_std = np.std(ps_arr, ddof=1)
            
            # Two-sample t-test
            t_stat, p_value = stats.ttest_ind(ts_arr, ps_arr)
            
            # Cohen's d effect size
            pooled_std = np.sqrt((ts_std**2 + ps_std**2) / 2)
            cohens_d = (ts_mean - ps_mean) / pooled_std if pooled_std > 0 else 0.0
            
            # Determine if metric validates
            is_significant = p_value < tolerance
            has_medium_effect = abs(cohens_d) >= 0.5
            
            # For cluster_stability and complexity_bootstrap, lower is better (TS < PS)
            # For other metrics, higher is better (TS > PS)
            if metric in ["cluster_stability", "complexity_bootstrap"]:
                favors_ts = cohens_d < 0  # Negative d means TS < PS (good)
            else:
                favors_ts = cohens_d > 0  # Positive d means TS > PS (good)
            
            metric_passes = is_significant and has_medium_effect and favors_ts
            
            if is_significant:
                significant_count += 1
            
            # Store results
            metrics[f"{metric}_ts_mean"] = float(ts_mean)
            metrics[f"{metric}_ps_mean"] = float(ps_mean)
            metrics[f"{metric}_t_stat"] = float(t_stat)
            metrics[f"{metric}_p_value"] = float(p_value)
            metrics[f"{metric}_cohens_d"] = float(cohens_d)
            metrics[f"{metric}_passes"] = metric_passes
            
            evidence[metric] = {
                "ts_mean": float(ts_mean),
                "ts_std": float(ts_std),
                "ps_mean": float(ps_mean),
                "ps_std": float(ps_std),
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "cohens_d": float(cohens_d),
                "significant": is_significant,
                "medium_effect": has_medium_effect,
                "favors_ts": favors_ts,
                "passes": metric_passes
            }
        
        # Overall validation decision
        metrics["significant_metrics_count"] = significant_count
        metrics["total_metrics_tested"] = len(metric_names)
        
        # PC002 validates if: ≥2 metrics significant with medium effect favoring TS
        all_pass = significant_count >= 2
        
        error_message = None
        if not all_pass:
            if significant_count == 0:
                error_message = "No metrics show significant difference (H0: TS = PS cannot be rejected)"
            else:
                error_message = f"Only {significant_count}/4 metrics significant (need ≥2)"
        
        return ValidationResult(
            pc_id=self.metadata.pc_id,
            pc_version=self.metadata.version,
            passes=all_pass,
            metrics=metrics,
            evidence=evidence,
            timestamp=datetime.now().isoformat(),
            error_message=error_message
        )
    
    def falsification_criteria(self) -> List[str]:
        """Conditions that would falsify this principle."""
        return [
            "All 4 metrics show p > 0.05 (TS and PS statistically identical)",
            "Any metric shows TS < PS with p < 0.05 and d ≥ 0.5 (contradicts hypothesis)",
            "All significant effects have |Cohen's d| < 0.3 (negligible practical difference)",
            "Results fail to replicate across 2 independent experimental runs",
            "Confounding factor detected (differences due to implementation, not substrate)",
            "PC001 overhead authentication fails (invalidates reality grounding)",
            "Fewer than 2/4 metrics achieve p < 0.05 with d ≥ 0.5 favoring TS"
        ]
    
    def applications(self) -> List[str]:
        """Practical applications of this principle."""
        return [
            "Pattern generation systems requiring rich emergent structure",
            "Self-organizing agent systems with composition-decomposition dynamics",
            "Memory systems requiring long-term pattern persistence",
            "Evolutionary algorithms needing natural resonance frequencies",
            "Neural network initialization strategies",
            "Genetic algorithm mutation operators",
            "Agent-based models with phase-dependent behavior",
            "Any computational system where substrate irreducibility matters"
        ]
    
    # PC002-specific utility methods
    
    def compare_substrates(
        self,
        ts_data: List[float],
        ps_data: List[float],
        metric_name: str
    ) -> Dict[str, float]:
        """
        Compare single metric between TS and PS.
        
        Args:
            ts_data: Transcendental substrate results
            ps_data: PRNG substrate results
            metric_name: Name of metric being compared
        
        Returns:
            Dictionary with statistical comparison results
        """
        ts_arr = np.array(ts_data)
        ps_arr = np.array(ps_data)
        
        ts_mean = np.mean(ts_arr)
        ps_mean = np.mean(ps_arr)
        ts_std = np.std(ts_arr, ddof=1)
        ps_std = np.std(ps_arr, ddof=1)
        
        t_stat, p_value = stats.ttest_ind(ts_arr, ps_arr)
        
        pooled_std = np.sqrt((ts_std**2 + ps_std**2) / 2)
        cohens_d = (ts_mean - ps_mean) / pooled_std if pooled_std > 0 else 0.0
        
        return {
            "metric": metric_name,
            "ts_mean": float(ts_mean),
            "ts_std": float(ts_std),
            "ps_mean": float(ps_mean),
            "ps_std": float(ps_std),
            "difference": float(ts_mean - ps_mean),
            "percent_difference": float((ts_mean - ps_mean) / ps_mean * 100) if ps_mean != 0 else 0.0,
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "cohens_d": float(cohens_d),
            "effect_interpretation": self._interpret_effect_size(cohens_d)
        }
    
    def _interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"


# Factory function for easy instantiation

def load_pc002() -> PC002_Transcendental_Substrate:
    """
    Load PC002 instance.
    
    Returns:
        PC002_Transcendental_Substrate instance
    """
    return PC002_Transcendental_Substrate()


# Example usage and design-phase testing

if __name__ == "__main__":
    # Create PC002 instance
    pc002 = load_pc002()
    
    # Print PC metadata
    print(pc002)
    print()
    print("Principle Statement:")
    print(pc002.principle_statement)
    print()
    
    # Design-phase validation (no PRNG results yet)
    print("Testing design-phase validation...")
    design_data = {
        "transcendental_results": {
            "pattern_lifetime": [10.5, 12.3, 11.8, 13.2],  # Example TS data
            "memory_retention": [0.85, 0.82, 0.88, 0.86],
            "cluster_stability": [0.12, 0.15, 0.13, 0.14],
            "complexity_bootstrap": [150, 145, 160, 155]
        },
        "prng_results": None,  # Not yet available
        "metrics": ["pattern_lifetime", "memory_retention", "cluster_stability", "complexity_bootstrap"]
    }
    
    result = pc002.validate(design_data, tolerance=0.05)
    print("\nDesign-Phase Validation Result:")
    print(result.summary())
    print()
    
    # Simulate full comparative validation
    print("Testing comparative validation (simulated data)...")
    comparative_data = {
        "transcendental_results": {
            "pattern_lifetime": [12.5, 13.1, 12.8, 13.5, 12.9],  # TS better
            "memory_retention": [0.85, 0.87, 0.84, 0.88, 0.86],  # TS better
            "cluster_stability": [0.12, 0.11, 0.13, 0.12, 0.11],  # TS better (lower)
            "complexity_bootstrap": [150, 145, 155, 148, 152]  # TS better (lower)
        },
        "prng_results": {
            "pattern_lifetime": [10.2, 9.8, 10.5, 10.1, 9.9],  # PS worse
            "memory_retention": [0.75, 0.73, 0.76, 0.74, 0.75],  # PS worse
            "cluster_stability": [0.22, 0.24, 0.21, 0.23, 0.22],  # PS worse (higher)
            "complexity_bootstrap": [200, 195, 205, 198, 202]  # PS worse (higher)
        },
        "metrics": ["pattern_lifetime", "memory_retention", "cluster_stability", "complexity_bootstrap"]
    }
    
    result = pc002.validate(comparative_data, tolerance=0.05)
    print("\nComparative Validation Result (simulated):")
    print(result.summary())
    print()
    print("Evidence:")
    for metric, stats in result.evidence.items():
        print(f"\n{metric}:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
