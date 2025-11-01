"""
PC002: Regime Detection in Population Dynamics
==============================================

Compositional Principle Card depending on PC001 for baseline dynamics.
Classifies population regimes: baseline, growth, collapse, oscillatory.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json

from ..base import PrincipleCard, PCMetadata, ValidationResult
from .features import RegimeFeatureExtractor, BaselineParams, RegimeFeatures
from .classifier import RegimeClassifier, ClassificationMetrics, REGIME_TYPES


class PC002_RegimeDetection(PrincipleCard):
    """
    PC002: Regime Detection in Population Dynamics

    Depends on PC001 for baseline dynamics.
    Classifies population regimes: baseline, growth, collapse, oscillatory.

    Compositional Nature: PC002 requires PC001 to establish baseline.
    Regime detection identifies deviations from PC001-predicted baseline.
    """

    def __init__(
        self,
        window_size: int = 100,
        n_estimators: int = 100,
        random_state: int = 42
    ):
        """
        Initialize PC002.

        Args:
            window_size: Window size for feature extraction (points)
            n_estimators: Number of trees in random forest
            random_state: Random seed for reproducibility
        """
        metadata = PCMetadata(
            pc_id="PC002",
            version="1.0.0",
            title="Regime Detection in Population Dynamics",
            author="Aldrin Payopay <aldrin.gdf@gmail.com>",
            created="2025-11-01",
            status="draft",
            dependencies=["PC001"],  # Strong compositional dependency
            domain="NRM"
        )
        super().__init__(metadata)

        self.window_size = window_size
        self.feature_extractor: Optional[RegimeFeatureExtractor] = None
        self.classifier = RegimeClassifier(
            n_estimators=n_estimators,
            random_state=random_state
        )
        self.baseline_params: Optional[BaselineParams] = None

    def set_baseline(self, pc001_instance) -> None:
        """
        Set baseline parameters from validated PC001.

        Args:
            pc001_instance: Validated PC001_NRMPopulationDynamics instance

        Raises:
            ValueError: If PC001 not validated
            AttributeError: If PC001 missing required attributes
        """
        # Check PC001 validation status
        if pc001_instance.metadata.status != "validated":
            raise ValueError(
                f"PC001 must be validated before PC002 can use it. "
                f"Current status: {pc001_instance.metadata.status}"
            )

        # Extract baseline parameters
        try:
            K = pc001_instance.carrying_capacity
            r = pc001_instance.growth_rate
            sigma = pc001_instance.noise_intensity
            CV_baseline = pc001_instance.predict_cv()
        except AttributeError as e:
            raise AttributeError(
                f"PC001 instance missing required attributes: {e}"
            )

        # Create baseline params
        self.baseline_params = BaselineParams(
            K=K,
            r=r,
            sigma=sigma,
            CV_baseline=CV_baseline
        )

        # Create feature extractor
        self.feature_extractor = RegimeFeatureExtractor(self.baseline_params)

    def train(
        self,
        population_data: np.ndarray,
        regime_labels: np.ndarray
    ) -> ClassificationMetrics:
        """
        Train classifier on labeled regime data.

        Args:
            population_data: 2D array (n_windows, window_size) of population time series
            regime_labels: 1D array (n_windows,) of regime labels

        Returns:
            ClassificationMetrics from training data evaluation

        Raises:
            RuntimeError: If baseline not set
            ValueError: If data invalid
        """
        if self.feature_extractor is None:
            raise RuntimeError(
                "Baseline must be set via set_baseline() before training"
            )

        if len(population_data) == 0:
            raise ValueError("Population data is empty")

        if len(regime_labels) == 0:
            raise ValueError("Regime labels are empty")

        if len(population_data) != len(regime_labels):
            raise ValueError(
                f"Population data ({len(population_data)}) and labels "
                f"({len(regime_labels)}) must have same length"
            )

        # Extract features from each window
        features_list = []
        for window in population_data:
            features = self.feature_extractor.extract(window)
            features_list.append(features.to_array())

        features_array = np.array(features_list)

        # Train classifier
        self.classifier.train(features_array, regime_labels)

        # Evaluate on training data (for diagnostics)
        metrics = self.classifier.evaluate(features_array, regime_labels)

        return metrics

    def classify_regime(self, population_window: np.ndarray) -> str:
        """
        Classify regime for a single population window.

        Args:
            population_window: 1D array of population values

        Returns:
            Regime label (string)

        Raises:
            RuntimeError: If baseline not set or classifier not trained
        """
        if self.feature_extractor is None:
            raise RuntimeError("Baseline must be set via set_baseline()")

        if not self.classifier.is_trained:
            raise RuntimeError("Classifier must be trained before classification")

        # Extract features
        features = self.feature_extractor.extract(population_window)

        # Classify
        regime = self.classifier.predict(features.to_array())[0]

        return regime

    def classify_time_series(
        self,
        population_series: np.ndarray,
        step_size: Optional[int] = None
    ) -> Tuple[List[str], List[RegimeFeatures]]:
        """
        Classify regimes across full time series using sliding windows.

        Args:
            population_series: 1D array of population time series
            step_size: Step size between windows (default: window_size)

        Returns:
            Tuple of (regime_labels, features) for each window

        Raises:
            RuntimeError: If baseline not set or classifier not trained
        """
        if self.feature_extractor is None:
            raise RuntimeError("Baseline must be set via set_baseline()")

        if not self.classifier.is_trained:
            raise RuntimeError("Classifier must be trained before classification")

        # Extract features from sliding windows
        features_list = self.feature_extractor.extract_sliding_windows(
            population_series,
            window_size=self.window_size,
            step_size=step_size
        )

        # Convert to array for classification
        features_array = np.array([f.to_array() for f in features_list])

        # Classify all windows
        regime_labels = self.classifier.predict(features_array)

        return list(regime_labels), features_list

    # ========================================================================
    # PrincipleCard Abstract Methods
    # ========================================================================

    def principle_statement(self) -> str:
        """Return natural language statement of principle."""
        return (
            "Population dynamics exhibit distinct behavioral regimes "
            "characterized by baseline (near carrying capacity), growth "
            "(sustained increase), collapse (rapid decrease), and oscillatory "
            "(periodic fluctuations) patterns. Regimes can be detected from "
            "time-series data with ≥90% accuracy using statistical features "
            "(mean deviation, variance ratio, linear trend, CV deviation) and "
            "PC001 baseline predictions."
        )

    def mathematical_formulation(self) -> Dict[str, str]:
        """Return mathematical formulation of principle."""
        return {
            'equations': r"""
Feature 1 (Mean Deviation):
μ_dev = (<N>_window - K) / K

Feature 2 (Variance Ratio):
σ_ratio = Var(N)_window / (σ²·<N>_window)

Feature 3 (Linear Trend):
β = slope of linear regression N(t) on t
β_norm = β / <N>_window

Feature 4 (CV Deviation):
CV_obs = √Var(N)_window / <N>_window
CV_dev = (CV_obs - CV_baseline) / CV_baseline

Decision Rules:
- Baseline: |μ_dev| < 0.1 AND |σ_ratio - 1| < 0.2 AND |β_norm| < 0.01 AND |CV_dev| < 0.2
- Growth: β_norm > 0.02 OR (μ_dev > 0.15 AND β_norm > 0)
- Collapse: β_norm < -0.02 OR (μ_dev < -0.15 AND β_norm < 0)
- Oscillatory: Periodicity detected AND |CV_dev| > 0.3
""",
            'parameters': {
                'K': 'Carrying capacity from PC001',
                'σ': 'Noise intensity from PC001',
                'CV_baseline': 'Baseline CV from PC001',
                'window_size': 'Window size for feature extraction (default: 100 points)'
            },
            'predictions': 'Accuracy ≥ 90% on test data with balanced regime distribution'
        }

    def validation_protocol(self) -> Dict[str, Any]:
        """Return validation protocol specification."""
        return {
            'criterion': 'Accuracy ≥ 0.90 (90% correct classification)',
            'procedure': [
                '1. Validate PC001 on baseline data (compositional requirement)',
                '2. Extract baseline parameters (K, r, σ, CV_baseline) from PC001',
                '3. Create feature extractor with baseline parameters',
                '4. Generate or load labeled regime data (train + test split)',
                '5. Train classifier on training set',
                '6. Evaluate on independent test set',
                '7. Compute accuracy, precision, recall, F1-score',
                '8. Check if accuracy ≥ 90%',
                '9. Verify compositional dependency (PC002 fails if PC001 not validated)'
            ],
            'required_data': {
                'baseline_data': 'Time series for PC001 validation (≥1000 points)',
                'regime_data': 'Labeled time windows (≥500 test samples)',
                'train_test_split': '70% train, 30% test (or cross-validation)',
                'regime_balance': 'All 4 regime types represented'
            },
            'equipment': {
                'hardware': 'Standard (no special requirements)',
                'software': 'Python 3.9+, numpy, scipy, scikit-learn',
                'dependencies': 'PC001 (validated)',
                'runtime': '~2 minutes per validation'
            }
        }

    def reality_grounding(self) -> Dict[str, Any]:
        """Return reality grounding specification."""
        return {
            'system_interfaces': [
                'numpy arrays (actual data, not simulated)',
                'scikit-learn models (real training, not mocked)',
                'filesystem (JSON data, model persistence)',
                'SQLite (optional: feature/label storage)',
                'psutil (optional: classification runtime monitoring)'
            ],
            'validation_method': (
                'Every classification operates on real numpy arrays. '
                'Every training uses actual scikit-learn fit(). '
                'No mocked predictions or random labels. '
                'Validation accuracy is measured, not simulated.'
            ),
            'prohibited': [
                'Mock classifiers with random predictions',
                'Simulated accuracy without actual data',
                'Regime labels without ground truth',
                'Pure simulation without validation data'
            ],
            'required': [
                'Every feature computed from actual population data',
                'Every classification uses trained sklearn model',
                'Every validation compares predictions to ground truth',
                'PC001 dependency enforced (fails if PC001 not validated)'
            ]
        }

    def validate(
        self,
        data: Dict[str, Any],
        tolerance: float = 0.90
    ) -> ValidationResult:
        """
        Execute validation protocol on data.

        Args:
            data: Dictionary with keys:
                - 'pc001': Validated PC001 instance
                - 'train_data': (population_windows, labels) for training
                - 'test_data': (population_windows, labels) for testing
            tolerance: Minimum accuracy threshold (default: 0.90)

        Returns:
            ValidationResult with pass/fail and evidence

        Raises:
            ValueError: If data invalid or missing required keys
        """
        # Validate input data structure
        required_keys = ['pc001', 'train_data', 'test_data']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

        pc001 = data['pc001']
        train_windows, train_labels = data['train_data']
        test_windows, test_labels = data['test_data']

        try:
            # Step 1: Set baseline from PC001
            self.set_baseline(pc001)

            # Step 2: Train classifier
            train_metrics = self.train(train_windows, train_labels)

            # Step 3: Evaluate on test set
            test_features = np.array([
                self.feature_extractor.extract(window).to_array()
                for window in test_windows
            ])
            test_metrics = self.classifier.evaluate(test_features, test_labels)

            # Step 4: Check if accuracy meets threshold
            passes = test_metrics.accuracy >= tolerance
            error = 1.0 - test_metrics.accuracy

            # Collect evidence
            evidence = {
                'test_accuracy': test_metrics.accuracy,
                'test_precision': test_metrics.precision,
                'test_recall': test_metrics.recall,
                'test_f1': test_metrics.f1,
                'test_confusion_matrix': test_metrics.confusion_matrix.tolist(),
                'train_accuracy': train_metrics.accuracy,
                'n_train_samples': len(train_labels),
                'n_test_samples': len(test_labels),
                'window_size': self.window_size,
                'baseline_params': {
                    'K': self.baseline_params.K,
                    'r': self.baseline_params.r,
                    'sigma': self.baseline_params.sigma,
                    'CV_baseline': self.baseline_params.CV_baseline
                },
                'feature_importances': self.classifier.get_feature_importances()
            }

            # Update metadata status
            if passes:
                self.metadata.status = "validated"
            else:
                self.metadata.status = "falsified"

            return ValidationResult(
                pc_id=self.metadata.pc_id,
                passes=passes,
                error=error,
                criterion=tolerance,
                evidence=evidence,
                metadata={
                    'pc001_status': pc001.metadata.status,
                    'version': self.metadata.version
                }
            )

        except Exception as e:
            # Validation failed due to error
            self.metadata.status = "falsified"
            return ValidationResult(
                pc_id=self.metadata.pc_id,
                passes=False,
                error=1.0,
                criterion=tolerance,
                evidence={'error': str(e)},
                metadata={'validation_error': str(e)}
            )

    def temporal_encoding(self) -> Dict[str, Any]:
        """Return temporal encoding for future AI systems."""
        return {
            'template_patterns': [
                'Compositional validation: PC_B depends on PC_A for baseline',
                'Baseline + deviation: Establish normal, detect deviations',
                'Supervised learning for time series classification',
                'Feature engineering: Extract domain-relevant features'
            ],
            'validation_patterns': [
                'Train/test split prevents overfitting',
                'Multi-metric evaluation (not just accuracy)',
                'Confusion matrix reveals per-regime performance',
                'Feature importances guide interpretation'
            ],
            'composition_patterns': [
                'PC001 → PC002: Baseline dynamics → Regime detection',
                'PC002 → PC005: Single regime → Multi-regime dynamics',
                'PC002 → PC006: Regime classification → Regime prediction',
                'Strong compositional dependency enforced by TEG'
            ],
            'training_awareness': {
                'if_validated': (
                    'Compositional validation is robust. '
                    'Baseline + deviation framework is generalizable. '
                    'Supervised learning works for regime detection. '
                    'Future AI learns: compose validated principles.'
                ),
                'if_falsified': (
                    'Baseline + deviation insufficient for regime detection. '
                    'Supervised learning has limits. '
                    'Alternative approaches needed (unsupervised, deep learning). '
                    'Future AI learns: explore beyond standard methods.'
                )
            }
        }

    def enables(self) -> List[str]:
        """Return list of PC IDs this enables."""
        return ["PC005", "PC006"]  # Multi-Regime Dynamics, Regime Prediction

    def save_classifier(self, filepath: str) -> None:
        """
        Save trained classifier to disk.

        Args:
            filepath: Path to save classifier (.json)

        Raises:
            RuntimeError: If classifier not trained
        """
        if not self.classifier.is_trained:
            raise RuntimeError("Cannot save untrained classifier")

        self.classifier.save(filepath)

    def load_classifier(self, filepath: str) -> None:
        """
        Load trained classifier from disk.

        Args:
            filepath: Path to classifier file (.json)

        Raises:
            FileNotFoundError: If file not found
        """
        self.classifier = RegimeClassifier.load(filepath)
