"""
PC002: Regime Detection - Regime Classification
===============================================

Classify population regimes from extracted features.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
import json


# Regime types
BASELINE = 'baseline'
GROWTH = 'growth'
COLLAPSE = 'collapse'
OSCILLATORY = 'oscillatory'

REGIME_TYPES = [BASELINE, GROWTH, COLLAPSE, OSCILLATORY]


@dataclass
class ClassificationMetrics:
    """Classification performance metrics."""
    accuracy: float
    precision: float
    recall: float
    f1: float
    confusion_matrix: np.ndarray

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'accuracy': float(self.accuracy),
            'precision': float(self.precision),
            'recall': float(self.recall),
            'f1': float(self.f1),
            'confusion_matrix': self.confusion_matrix.tolist()
        }

    def passes_threshold(self, threshold: float = 0.90) -> bool:
        """Check if accuracy meets threshold."""
        return self.accuracy >= threshold


class RegimeClassifier:
    """
    Classify population regimes using supervised learning.

    Regimes:
    - baseline: Near carrying capacity with demographic noise
    - growth: Sustained population increase
    - collapse: Rapid population decrease
    - oscillatory: Periodic fluctuations

    Uses RandomForestClassifier with decision rules informed by
    PC002 specification.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = None,
        random_state: int = 42
    ):
        """
        Initialize regime classifier.

        Args:
            n_estimators: Number of trees in random forest
            max_depth: Maximum tree depth (None = unlimited)
            random_state: Random seed for reproducibility
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            class_weight='balanced'  # Handle class imbalance
        )
        self.is_trained = False
        self.feature_names = ['mu_dev', 'sigma_ratio', 'beta_norm', 'CV_dev']
        self.regime_types = REGIME_TYPES

    def train(self, features: np.ndarray, labels: np.ndarray) -> None:
        """
        Train classifier on labeled regime data.

        Args:
            features: 2D array (n_samples, n_features)
            labels: 1D array of regime labels (strings)

        Raises:
            ValueError: If features/labels invalid or mismatched
        """
        if len(features) == 0:
            raise ValueError("Training features are empty")

        if len(labels) == 0:
            raise ValueError("Training labels are empty")

        if len(features) != len(labels):
            raise ValueError(
                f"Features ({len(features)}) and labels ({len(labels)}) "
                f"must have same length"
            )

        if features.shape[1] != len(self.feature_names):
            raise ValueError(
                f"Expected {len(self.feature_names)} features, "
                f"got {features.shape[1]}"
            )

        # Validate labels
        invalid_labels = set(labels) - set(self.regime_types)
        if invalid_labels:
            raise ValueError(
                f"Invalid regime labels: {invalid_labels}. "
                f"Valid labels: {self.regime_types}"
            )

        # Train model
        self.model.fit(features, labels)
        self.is_trained = True

    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Predict regime labels.

        Args:
            features: 2D array (n_samples, n_features)

        Returns:
            1D array of predicted regime labels

        Raises:
            RuntimeError: If model not trained
            ValueError: If features invalid
        """
        if not self.is_trained:
            raise RuntimeError("Classifier must be trained before prediction")

        if len(features) == 0:
            raise ValueError("Features are empty")

        if features.ndim == 1:
            # Single sample - reshape
            features = features.reshape(1, -1)

        if features.shape[1] != len(self.feature_names):
            raise ValueError(
                f"Expected {len(self.feature_names)} features, "
                f"got {features.shape[1]}"
            )

        return self.model.predict(features)

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        """
        Predict regime probabilities.

        Args:
            features: 2D array (n_samples, n_features)

        Returns:
            2D array (n_samples, n_classes) of probabilities

        Raises:
            RuntimeError: If model not trained
        """
        if not self.is_trained:
            raise RuntimeError("Classifier must be trained before prediction")

        if features.ndim == 1:
            features = features.reshape(1, -1)

        return self.model.predict_proba(features)

    def evaluate(
        self,
        features: np.ndarray,
        true_labels: np.ndarray
    ) -> ClassificationMetrics:
        """
        Evaluate classifier performance.

        Args:
            features: 2D array (n_samples, n_features)
            true_labels: 1D array of ground truth regime labels

        Returns:
            ClassificationMetrics with accuracy, precision, recall, F1, confusion matrix

        Raises:
            RuntimeError: If model not trained
            ValueError: If features/labels invalid
        """
        if not self.is_trained:
            raise RuntimeError("Classifier must be trained before evaluation")

        if len(features) != len(true_labels):
            raise ValueError(
                f"Features ({len(features)}) and labels ({len(true_labels)}) "
                f"must have same length"
            )

        # Predict
        pred_labels = self.predict(features)

        # Compute metrics
        accuracy = accuracy_score(true_labels, pred_labels)

        # Multi-class metrics: use weighted averaging
        precision = precision_score(
            true_labels,
            pred_labels,
            average='weighted',
            zero_division=0
        )
        recall = recall_score(
            true_labels,
            pred_labels,
            average='weighted',
            zero_division=0
        )
        f1 = f1_score(
            true_labels,
            pred_labels,
            average='weighted',
            zero_division=0
        )

        # Confusion matrix
        cm = confusion_matrix(
            true_labels,
            pred_labels,
            labels=self.regime_types
        )

        return ClassificationMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1,
            confusion_matrix=cm
        )

    def get_feature_importances(self) -> Dict[str, float]:
        """
        Get feature importances from trained model.

        Returns:
            Dictionary mapping feature names to importances

        Raises:
            RuntimeError: If model not trained
        """
        if not self.is_trained:
            raise RuntimeError("Classifier must be trained before getting importances")

        importances = self.model.feature_importances_
        return dict(zip(self.feature_names, importances))

    def apply_decision_rules(self, features: np.ndarray) -> str:
        """
        Apply PC002 decision rules for regime classification.

        This is an alternative to ML-based classification, using
        explicit rules from the specification.

        Args:
            features: 1D array [mu_dev, sigma_ratio, beta_norm, CV_dev]

        Returns:
            Regime label (string)

        Raises:
            ValueError: If features invalid
        """
        if len(features) != 4:
            raise ValueError(f"Expected 4 features, got {len(features)}")

        mu_dev, sigma_ratio, beta_norm, CV_dev = features

        # Growth regime (priority 1)
        if beta_norm > 0.02 or (mu_dev > 0.15 and beta_norm > 0):
            return GROWTH

        # Collapse regime (priority 2)
        if beta_norm < -0.02 or (mu_dev < -0.15 and beta_norm < 0):
            return COLLAPSE

        # Oscillatory regime (priority 3)
        # Note: Full oscillatory detection requires autocorrelation analysis
        # This is a simplified rule
        if abs(CV_dev) > 0.3:
            return OSCILLATORY

        # Baseline regime (default)
        if (abs(mu_dev) < 0.1 and
            abs(sigma_ratio - 1) < 0.2 and
            abs(beta_norm) < 0.01 and
            abs(CV_dev) < 0.2):
            return BASELINE

        # If no clear match, default to baseline
        # (Conservative: prefer baseline over false regime detection)
        return BASELINE

    def save(self, filepath: str) -> None:
        """
        Save classifier to disk.

        Args:
            filepath: Path to save file (.json)

        Raises:
            RuntimeError: If model not trained
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained classifier")

        import joblib

        # Save sklearn model
        model_path = filepath.replace('.json', '_model.joblib')
        joblib.dump(self.model, model_path)

        # Save metadata
        metadata = {
            'is_trained': self.is_trained,
            'feature_names': self.feature_names,
            'regime_types': self.regime_types,
            'n_estimators': self.model.n_estimators,
            'max_depth': self.model.max_depth,
            'random_state': self.model.random_state,
            'model_path': model_path
        }

        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'RegimeClassifier':
        """
        Load classifier from disk.

        Args:
            filepath: Path to metadata file (.json)

        Returns:
            Loaded RegimeClassifier

        Raises:
            FileNotFoundError: If file not found
            ValueError: If file invalid
        """
        import joblib

        # Load metadata
        with open(filepath, 'r') as f:
            metadata = json.load(f)

        # Load sklearn model
        model_path = metadata['model_path']
        model = joblib.load(model_path)

        # Create classifier
        classifier = cls(
            n_estimators=metadata['n_estimators'],
            max_depth=metadata['max_depth'],
            random_state=metadata['random_state']
        )
        classifier.model = model
        classifier.is_trained = metadata['is_trained']
        classifier.feature_names = metadata['feature_names']
        classifier.regime_types = metadata['regime_types']

        return classifier
