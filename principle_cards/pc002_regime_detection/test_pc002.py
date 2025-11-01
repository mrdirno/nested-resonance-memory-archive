"""
PC002: Regime Detection - Test Suite
====================================

Comprehensive tests for PC002 implementation.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import json

from principle_cards.pc002_regime_detection import (
    PC002_RegimeDetection,
    RegimeFeatureExtractor,
    BaselineParams,
    RegimeFeatures,
    RegimeClassifier,
    ClassificationMetrics,
    BASELINE,
    GROWTH,
    COLLAPSE,
    OSCILLATORY
)
from principle_cards.base import ValidationResult


# ========================================================================
# Fixtures
# ========================================================================

@pytest.fixture
def baseline_params():
    """Standard baseline parameters."""
    return BaselineParams(K=50.0, r=0.1, sigma=0.5, CV_baseline=0.10)


@pytest.fixture
def feature_extractor(baseline_params):
    """Create feature extractor."""
    return RegimeFeatureExtractor(baseline_params)


@pytest.fixture
def classifier():
    """Create untrained classifier."""
    return RegimeClassifier(n_estimators=10, random_state=42)


@pytest.fixture
def synthetic_baseline_data():
    """Generate synthetic baseline regime data."""
    np.random.seed(42)
    # Near K=50 with demographic noise
    return np.random.normal(50, 2.5, 100)


@pytest.fixture
def synthetic_growth_data():
    """Generate synthetic growth regime data."""
    # Linear growth from 30 to 60
    return np.linspace(30, 60, 100)


@pytest.fixture
def synthetic_collapse_data():
    """Generate synthetic collapse regime data."""
    # Exponential decay from 60 to 20
    return 60 * np.exp(-0.03 * np.arange(100))


@pytest.fixture
def synthetic_oscillatory_data():
    """Generate synthetic oscillatory regime data."""
    # Sinusoidal oscillation around K=50
    t = np.arange(100)
    return 50 + 10 * np.sin(2 * np.pi * t / 20)


@pytest.fixture
def mock_pc001():
    """Mock PC001 instance with validated status."""
    class MockPC001:
        def __init__(self):
            from principle_cards.base import PCMetadata
            self.metadata = PCMetadata(
                pc_id="PC001",
                version="1.0.0",
                title="NRM Population Dynamics",
                author="Test",
                created="2025-11-01",
                status="validated",
                dependencies=[],
                domain="NRM"
            )
            self.carrying_capacity = 50.0
            self.growth_rate = 0.1
            self.noise_intensity = 0.5

        def predict_cv(self):
            return 0.10

    return MockPC001()


# ========================================================================
# Feature Extraction Tests
# ========================================================================

def test_baseline_params_validation():
    """Test BaselineParams validation."""
    # Valid params
    params = BaselineParams(K=50, r=0.1, sigma=0.5, CV_baseline=0.10)
    assert params.K == 50
    assert params.r == 0.1
    assert params.sigma == 0.5
    assert params.CV_baseline == 0.10


def test_feature_extractor_initialization(baseline_params):
    """Test RegimeFeatureExtractor initialization."""
    extractor = RegimeFeatureExtractor(baseline_params)
    assert extractor.K == 50.0
    assert extractor.sigma == 0.5
    assert extractor.CV_baseline == 0.10


def test_feature_extractor_invalid_params():
    """Test RegimeFeatureExtractor rejects invalid params."""
    # Negative K
    with pytest.raises(ValueError, match="Carrying capacity must be positive"):
        RegimeFeatureExtractor(BaselineParams(K=-10, r=0.1, sigma=0.5, CV_baseline=0.10))

    # Negative sigma
    with pytest.raises(ValueError, match="Noise intensity must be non-negative"):
        RegimeFeatureExtractor(BaselineParams(K=50, r=0.1, sigma=-0.5, CV_baseline=0.10))


def test_extract_baseline_features(feature_extractor, synthetic_baseline_data):
    """Test feature extraction on baseline regime."""
    features = feature_extractor.extract(synthetic_baseline_data)

    assert isinstance(features, RegimeFeatures)
    assert abs(features.mu_dev) < 0.15  # Near K
    assert features.sigma_ratio > 0  # Positive variance ratio
    assert abs(features.beta_norm) < 0.05  # Small trend
    assert abs(features.CV_dev) < 1.0  # CV near baseline


def test_extract_growth_features(feature_extractor, synthetic_growth_data):
    """Test feature extraction on growth regime."""
    features = feature_extractor.extract(synthetic_growth_data)

    assert features.mu_dev < 0  # Below K initially
    assert features.beta_norm > 0  # Positive trend


def test_extract_collapse_features(feature_extractor, synthetic_collapse_data):
    """Test feature extraction on collapse regime."""
    features = feature_extractor.extract(synthetic_collapse_data)

    # Collapse data decays from 60 to ~3, mean is below K=50
    assert features.beta_norm < 0  # Negative trend (the key feature)
    assert features.mu_dev < 0  # Mean below K due to decay


def test_extract_empty_window(feature_extractor):
    """Test feature extraction rejects empty window."""
    with pytest.raises(ValueError, match="Population window is empty"):
        feature_extractor.extract(np.array([]))


def test_extract_negative_values(feature_extractor):
    """Test feature extraction rejects negative populations."""
    with pytest.raises(ValueError, match="negative values"):
        feature_extractor.extract(np.array([50, 40, -10, 30]))


def test_extract_sliding_windows(feature_extractor):
    """Test sliding window feature extraction."""
    series = np.random.normal(50, 5, 500)
    window_size = 100
    step_size = 50

    features_list = feature_extractor.extract_sliding_windows(
        series, window_size, step_size
    )

    # Check number of windows
    expected_windows = (len(series) - window_size) // step_size + 1
    assert len(features_list) == expected_windows

    # Check all features are RegimeFeatures
    assert all(isinstance(f, RegimeFeatures) for f in features_list)


def test_extract_sliding_windows_invalid():
    """Test sliding windows with invalid parameters."""
    extractor = RegimeFeatureExtractor(BaselineParams(K=50, r=0.1, sigma=0.5, CV_baseline=0.10))
    series = np.random.normal(50, 5, 100)

    # Window larger than series
    with pytest.raises(ValueError, match="shorter than window size"):
        extractor.extract_sliding_windows(series, window_size=200)

    # Invalid window size
    with pytest.raises(ValueError, match="Window size must be positive"):
        extractor.extract_sliding_windows(series, window_size=-10)


def test_features_to_array():
    """Test RegimeFeatures.to_array()."""
    features = RegimeFeatures(mu_dev=0.05, sigma_ratio=1.1, beta_norm=0.01, CV_dev=0.02)
    array = features.to_array()

    assert isinstance(array, np.ndarray)
    assert len(array) == 4
    assert array[0] == 0.05
    assert array[1] == 1.1
    assert array[2] == 0.01
    assert array[3] == 0.02


def test_features_to_dict():
    """Test RegimeFeatures.to_dict()."""
    features = RegimeFeatures(mu_dev=0.05, sigma_ratio=1.1, beta_norm=0.01, CV_dev=0.02)
    d = features.to_dict()

    assert d == {
        'mu_dev': 0.05,
        'sigma_ratio': 1.1,
        'beta_norm': 0.01,
        'CV_dev': 0.02
    }


# ========================================================================
# Classifier Tests
# ========================================================================

def test_classifier_initialization():
    """Test RegimeClassifier initialization."""
    clf = RegimeClassifier(n_estimators=50, max_depth=10, random_state=123)
    assert clf.model.n_estimators == 50
    assert clf.model.max_depth == 10
    assert clf.model.random_state == 123
    assert not clf.is_trained


def test_classifier_train(classifier):
    """Test classifier training."""
    # Create synthetic training data
    np.random.seed(42)
    features = np.random.randn(100, 4)
    labels = np.random.choice([BASELINE, GROWTH, COLLAPSE, OSCILLATORY], 100)

    # Train
    classifier.train(features, labels)

    assert classifier.is_trained


def test_classifier_train_invalid_data(classifier):
    """Test classifier rejects invalid training data."""
    # Empty features
    with pytest.raises(ValueError, match="Training features are empty"):
        classifier.train(np.array([]), np.array([]))

    # Mismatched lengths
    with pytest.raises(ValueError, match="must have same length"):
        classifier.train(np.random.randn(10, 4), np.array([BASELINE] * 5))

    # Wrong number of features
    with pytest.raises(ValueError, match="Expected 4 features"):
        classifier.train(np.random.randn(10, 3), np.array([BASELINE] * 10))

    # Invalid labels
    with pytest.raises(ValueError, match="Invalid regime labels"):
        classifier.train(np.random.randn(10, 4), np.array(['invalid'] * 10))


def test_classifier_predict(classifier):
    """Test classifier prediction."""
    # Train on synthetic data
    np.random.seed(42)
    features = np.random.randn(100, 4)
    labels = np.random.choice([BASELINE, GROWTH], 100)
    classifier.train(features, labels)

    # Predict
    test_features = np.random.randn(10, 4)
    predictions = classifier.predict(test_features)

    assert len(predictions) == 10
    assert all(p in [BASELINE, GROWTH, COLLAPSE, OSCILLATORY] for p in predictions)


def test_classifier_predict_single_sample(classifier):
    """Test classifier prediction on single sample."""
    # Train
    np.random.seed(42)
    features = np.random.randn(100, 4)
    labels = np.array([BASELINE] * 100)
    classifier.train(features, labels)

    # Predict single sample (1D array)
    single_sample = np.random.randn(4)
    prediction = classifier.predict(single_sample)

    assert len(prediction) == 1
    assert prediction[0] in [BASELINE, GROWTH, COLLAPSE, OSCILLATORY]


def test_classifier_predict_untrained(classifier):
    """Test prediction fails on untrained classifier."""
    with pytest.raises(RuntimeError, match="must be trained before prediction"):
        classifier.predict(np.random.randn(10, 4))


def test_classifier_predict_proba(classifier):
    """Test classifier probability prediction."""
    # Train on all 4 regime types
    np.random.seed(42)
    features = np.random.randn(100, 4)
    labels = np.random.choice([BASELINE, GROWTH, COLLAPSE, OSCILLATORY], 100)
    classifier.train(features, labels)

    # Predict probabilities
    test_features = np.random.randn(10, 4)
    proba = classifier.predict_proba(test_features)

    assert proba.shape == (10, 4)  # 10 samples, 4 classes
    assert np.allclose(proba.sum(axis=1), 1.0)  # Probabilities sum to 1


def test_classifier_evaluate(classifier):
    """Test classifier evaluation."""
    # Train
    np.random.seed(42)
    features = np.random.randn(100, 4)
    labels = np.random.choice([BASELINE, GROWTH], 100)
    classifier.train(features, labels)

    # Evaluate on same data (should have high accuracy)
    metrics = classifier.evaluate(features, labels)

    assert isinstance(metrics, ClassificationMetrics)
    assert 0 <= metrics.accuracy <= 1
    assert 0 <= metrics.precision <= 1
    assert 0 <= metrics.recall <= 1
    assert 0 <= metrics.f1 <= 1
    assert metrics.confusion_matrix.shape == (4, 4)


def test_classifier_evaluate_untrained(classifier):
    """Test evaluation fails on untrained classifier."""
    with pytest.raises(RuntimeError, match="must be trained before evaluation"):
        classifier.evaluate(np.random.randn(10, 4), np.array([BASELINE] * 10))


def test_classification_metrics_passes_threshold():
    """Test ClassificationMetrics.passes_threshold()."""
    metrics = ClassificationMetrics(
        accuracy=0.95,
        precision=0.92,
        recall=0.90,
        f1=0.91,
        confusion_matrix=np.zeros((4, 4))
    )

    assert metrics.passes_threshold(0.90)
    assert not metrics.passes_threshold(0.96)


def test_classifier_get_feature_importances(classifier):
    """Test feature importance extraction."""
    # Train
    np.random.seed(42)
    features = np.random.randn(100, 4)
    labels = np.random.choice([BASELINE, GROWTH], 100)
    classifier.train(features, labels)

    # Get importances
    importances = classifier.get_feature_importances()

    assert isinstance(importances, dict)
    assert set(importances.keys()) == {'mu_dev', 'sigma_ratio', 'beta_norm', 'CV_dev'}
    assert all(0 <= v <= 1 for v in importances.values())
    assert abs(sum(importances.values()) - 1.0) < 1e-6  # Sum to 1


def test_classifier_apply_decision_rules(classifier):
    """Test decision rule application."""
    # Baseline regime features
    baseline_features = np.array([0.05, 1.0, 0.005, 0.1])
    assert classifier.apply_decision_rules(baseline_features) == BASELINE

    # Growth regime features
    growth_features = np.array([0.2, 1.5, 0.03, 0.2])
    assert classifier.apply_decision_rules(growth_features) == GROWTH

    # Collapse regime features
    collapse_features = np.array([-0.2, 0.8, -0.03, -0.1])
    assert classifier.apply_decision_rules(collapse_features) == COLLAPSE

    # Oscillatory regime features
    oscillatory_features = np.array([0.05, 1.2, 0.01, 0.5])
    assert classifier.apply_decision_rules(oscillatory_features) == OSCILLATORY


def test_classifier_save_load(classifier):
    """Test classifier save/load."""
    # Train classifier
    np.random.seed(42)
    features = np.random.randn(100, 4)
    labels = np.random.choice([BASELINE, GROWTH], 100)
    classifier.train(features, labels)

    # Save
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "classifier.json"
        classifier.save(str(filepath))

        # Check files exist
        assert filepath.exists()
        assert Path(str(filepath).replace('.json', '_model.joblib')).exists()

        # Load
        loaded_clf = RegimeClassifier.load(str(filepath))

        # Verify loaded classifier works
        assert loaded_clf.is_trained
        test_features = np.random.randn(10, 4)
        predictions = loaded_clf.predict(test_features)
        assert len(predictions) == 10


# ========================================================================
# PC002 Integration Tests
# ========================================================================

def test_pc002_initialization():
    """Test PC002_RegimeDetection initialization."""
    pc002 = PC002_RegimeDetection(window_size=100, n_estimators=50, random_state=42)

    assert pc002.metadata.pc_id == "PC002"
    assert pc002.metadata.version == "1.0.0"
    assert pc002.metadata.status == "draft"
    assert pc002.metadata.dependencies == ["PC001"]
    assert pc002.window_size == 100
    assert pc002.feature_extractor is None
    assert pc002.baseline_params is None


def test_pc002_set_baseline(mock_pc001):
    """Test PC002.set_baseline() with validated PC001."""
    pc002 = PC002_RegimeDetection()
    pc002.set_baseline(mock_pc001)

    assert pc002.baseline_params is not None
    assert pc002.baseline_params.K == 50.0
    assert pc002.baseline_params.r == 0.1
    assert pc002.baseline_params.sigma == 0.5
    assert pc002.baseline_params.CV_baseline == 0.10
    assert pc002.feature_extractor is not None


def test_pc002_set_baseline_unvalidated():
    """Test PC002.set_baseline() rejects unvalidated PC001."""
    pc002 = PC002_RegimeDetection()

    # Create unvalidated mock PC001
    mock_pc001 = type('MockPC001', (), {
        'metadata': type('Metadata', (), {'status': 'draft'})(),
        'carrying_capacity': 50,
        'growth_rate': 0.1,
        'noise_intensity': 0.5,
        'predict_cv': lambda: 0.10
    })()

    with pytest.raises(ValueError, match="PC001 must be validated"):
        pc002.set_baseline(mock_pc001)


def test_pc002_train(mock_pc001):
    """Test PC002.train()."""
    pc002 = PC002_RegimeDetection(n_estimators=10, random_state=42)
    pc002.set_baseline(mock_pc001)

    # Create synthetic training data
    np.random.seed(42)
    windows = [np.random.normal(50, 5, 100) for _ in range(50)]
    labels = np.random.choice([BASELINE, GROWTH], 50)

    # Train
    metrics = pc002.train(np.array(windows), labels)

    assert isinstance(metrics, ClassificationMetrics)
    assert pc002.classifier.is_trained


def test_pc002_train_without_baseline():
    """Test PC002.train() fails without baseline."""
    pc002 = PC002_RegimeDetection()

    with pytest.raises(RuntimeError, match="Baseline must be set"):
        pc002.train(np.array([np.random.randn(100)]), np.array([BASELINE]))


def test_pc002_classify_regime(mock_pc001):
    """Test PC002.classify_regime()."""
    pc002 = PC002_RegimeDetection(n_estimators=10, random_state=42)
    pc002.set_baseline(mock_pc001)

    # Train
    np.random.seed(42)
    windows = [np.random.normal(50, 5, 100) for _ in range(50)]
    labels = np.array([BASELINE] * 50)
    pc002.train(np.array(windows), labels)

    # Classify single window
    test_window = np.random.normal(50, 5, 100)
    regime = pc002.classify_regime(test_window)

    assert regime in [BASELINE, GROWTH, COLLAPSE, OSCILLATORY]


def test_pc002_classify_time_series(mock_pc001):
    """Test PC002.classify_time_series()."""
    pc002 = PC002_RegimeDetection(window_size=100, n_estimators=10, random_state=42)
    pc002.set_baseline(mock_pc001)

    # Train
    np.random.seed(42)
    windows = [np.random.normal(50, 5, 100) for _ in range(50)]
    labels = np.array([BASELINE] * 50)
    pc002.train(np.array(windows), labels)

    # Classify time series
    time_series = np.random.normal(50, 5, 500)
    regime_labels, features_list = pc002.classify_time_series(time_series, step_size=100)

    assert len(regime_labels) == len(features_list)
    assert all(r in [BASELINE, GROWTH, COLLAPSE, OSCILLATORY] for r in regime_labels)


def test_pc002_principle_statement():
    """Test PC002.principle_statement()."""
    pc002 = PC002_RegimeDetection()
    statement = pc002.principle_statement()

    assert isinstance(statement, str)
    assert "regime" in statement.lower()
    assert "90%" in statement


def test_pc002_mathematical_formulation():
    """Test PC002.mathematical_formulation()."""
    pc002 = PC002_RegimeDetection()
    math_form = pc002.mathematical_formulation()

    assert 'equations' in math_form
    assert 'parameters' in math_form
    assert 'predictions' in math_form
    assert 'μ_dev' in math_form['equations']


def test_pc002_validation_protocol():
    """Test PC002.validation_protocol()."""
    pc002 = PC002_RegimeDetection()
    protocol = pc002.validation_protocol()

    assert 'criterion' in protocol
    assert 'procedure' in protocol
    assert 'required_data' in protocol
    assert 'equipment' in protocol
    assert '0.90' in protocol['criterion'] or '90%' in protocol['criterion']


def test_pc002_reality_grounding():
    """Test PC002.reality_grounding()."""
    pc002 = PC002_RegimeDetection()
    grounding = pc002.reality_grounding()

    assert 'system_interfaces' in grounding
    assert 'validation_method' in grounding
    assert 'prohibited' in grounding
    assert 'required' in grounding


def test_pc002_temporal_encoding():
    """Test PC002.temporal_encoding()."""
    pc002 = PC002_RegimeDetection()
    encoding = pc002.temporal_encoding()

    assert 'template_patterns' in encoding
    assert 'validation_patterns' in encoding
    assert 'composition_patterns' in encoding
    assert 'training_awareness' in encoding


def test_pc002_enables():
    """Test PC002.enables()."""
    pc002 = PC002_RegimeDetection()
    enabled = pc002.enables()

    assert "PC005" in enabled
    assert "PC006" in enabled


def test_pc002_validate(mock_pc001):
    """Test PC002.validate() full validation."""
    pc002 = PC002_RegimeDetection(window_size=100, n_estimators=10, random_state=42)

    # Create synthetic data
    np.random.seed(42)
    train_windows = [np.random.normal(50, 5, 100) for _ in range(100)]
    train_labels = np.random.choice([BASELINE, GROWTH], 100)

    test_windows = [np.random.normal(50, 5, 100) for _ in range(50)]
    test_labels = np.random.choice([BASELINE, GROWTH], 50)

    data = {
        'pc001': mock_pc001,
        'train_data': (np.array(train_windows), train_labels),
        'test_data': (np.array(test_windows), test_labels)
    }

    # Validate
    result = pc002.validate(data, tolerance=0.50)  # Low threshold for small synthetic data

    assert isinstance(result, ValidationResult)
    assert result.pc_id == "PC002"
    assert 'test_accuracy' in result.evidence
    assert 'test_confusion_matrix' in result.evidence  # Fixed key name


def test_pc002_validate_missing_keys():
    """Test PC002.validate() rejects missing keys."""
    pc002 = PC002_RegimeDetection()

    # Missing 'test_data'
    with pytest.raises(ValueError, match="Missing required key"):
        pc002.validate({'pc001': None, 'train_data': None}, tolerance=0.90)


def test_pc002_save_load_classifier(mock_pc001):
    """Test PC002 classifier save/load."""
    pc002 = PC002_RegimeDetection(n_estimators=10, random_state=42)
    pc002.set_baseline(mock_pc001)

    # Train
    np.random.seed(42)
    windows = [np.random.normal(50, 5, 100) for _ in range(50)]
    labels = np.array([BASELINE] * 50)
    pc002.train(np.array(windows), labels)

    # Save classifier
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "pc002_classifier.json"
        pc002.save_classifier(str(filepath))

        # Load classifier
        pc002_new = PC002_RegimeDetection()
        pc002_new.load_classifier(str(filepath))

        assert pc002_new.classifier.is_trained


# ========================================================================
# Entry Point
# ========================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
